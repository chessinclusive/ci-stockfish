import asyncio
import os
import sys
from time import perf_counter
from typing import List, Optional

# Support running directly via `python ciapp/main.py` by ensuring the project
# root is on sys.path before importing the package.
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import chess
import chess.engine
from chess.engine import Cp

from ciapp.STOCKFISH import (
    STOCKFISH_MOVES,
    STOCKFISH_PARAMS,
    STOCKFISH_VERSION,
    spawn_engine,
)

app = FastAPI(title="Stockfish Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: method={request.method}, url={request.url}")
    response = await call_next(request)
    print(f"Response status={response.status_code}")
    return response


class BatchRequest(BaseModel):
    fens: List[str]
    multipv: Optional[int] = None
    movetime_ms: Optional[int] = None
    depth: Optional[int] = None


def _build_limit(depth_override: Optional[int] = None, movetime_ms: Optional[int] = None) -> chess.engine.Limit:
    """Construct a fresh analysis limit using defaults unless overrides are supplied."""
    depth = depth_override if depth_override is not None else STOCKFISH_PARAMS.depth
    time = (movetime_ms / 1000.0) if movetime_ms is not None else STOCKFISH_PARAMS.time
    return chess.engine.Limit(depth=depth, time=time)


def _analyse_one(engine: chess.engine.SimpleEngine, board: chess.Board, limit: chess.engine.Limit, multipv: int):
    result = engine.analyse(board, limit, multipv=multipv)
    engine_analysis = []
    for idx, res in enumerate(result):
        pv = res.get("pv") or []
        score = res.get("score", chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE)).relative.score()
        engine_analysis.append({
            "idx": idx,
            "top_move": str(pv[0]) if pv else "",
            "cp": score,
        })
    return engine_analysis


async def _analyse_board(engine: chess.engine.SimpleEngine, board: chess.Board, limit: chess.engine.Limit, multipv: int):
    return await asyncio.to_thread(_analyse_one, engine, board, limit, multipv)


class EnginePool:
    def __init__(self, size: int, preferred_path: Optional[str] = None):
        self.size = size
        self.preferred_path = preferred_path
        self.path_in_use: Optional[str] = preferred_path
        self.q: asyncio.Queue[chess.engine.SimpleEngine] = asyncio.Queue()
        self.started = False

    async def start(self):
        if self.started:
            return
        for _ in range(self.size):
            engine, used_path = spawn_engine(self.path_in_use)
            if self.path_in_use is None:
                self.path_in_use = used_path

            # Configure only options that are supported by the engine to avoid errors (e.g., Ponder auto-managed).
            options = engine.options
            config = {}
            if "Threads" in options:
                config["Threads"] = 1
            if "Hash" in options:
                config["Hash"] = int(os.getenv("SF_HASH", "128"))
            if config:
                engine.configure(config)
            await self.q.put(engine)
        self.started = True

    async def stop(self):
        while not self.q.empty():
            eng = await self.q.get()
            try:
                eng.quit()
            except Exception:
                pass
        self.started = False

    async def acquire(self):
        return await self.q.get()

    async def release(self, eng):
        await self.q.put(eng)


ENGINE_POOL: Optional[EnginePool] = None


def _pool_size() -> int:
    env_size = os.getenv("ENGINE_POOL_SIZE") or os.getenv("SF_POOL_SIZE")
    if env_size:
        try:
            val = int(env_size)
            if val > 0:
                return val
        except ValueError:
            pass
    cores = os.cpu_count() or 1
    return max(1, cores - 1)


@app.on_event("startup")
async def startup_event():
    global ENGINE_POOL
    ENGINE_POOL = EnginePool(size=_pool_size())
    await ENGINE_POOL.start()


@app.on_event("shutdown")
async def shutdown_event():
    if ENGINE_POOL:
        await ENGINE_POOL.stop()


@app.get("/stockfish_evaluation")
async def stockfish_evaluation(fen_position: str):
    print(f"Received FEN position: {fen_position}")
    if not ENGINE_POOL or not ENGINE_POOL.started:
        raise HTTPException(status_code=503, detail="Stockfish engine pool not available")
    try:
        board = chess.Board(fen_position)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc
    engine = await ENGINE_POOL.acquire()
    start = perf_counter()
    try:
        engine_analysis = await _analyse_board(engine, board, _build_limit(), STOCKFISH_MOVES)
    except Exception as e:
        print(f"Error while getting engine analysis: {e}")
        engine_analysis = [{
            "idx": 0,
            "top_move": "",
            "cp": chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE).relative.score(),
        }]
    finally:
        await ENGINE_POOL.release(engine)

    print(f"Finished analysis for FEN: {engine_analysis}")
    elapsed_ms = (perf_counter() - start) * 1000.0
    return {"analysis": engine_analysis, "analysis_time_ms": elapsed_ms}


@app.post("/stockfish_evaluation/batch")
async def stockfish_evaluation_batch(payload: BatchRequest):
    if not ENGINE_POOL or not ENGINE_POOL.started:
        raise HTTPException(status_code=503, detail="Stockfish engine pool not available")
    if not payload.fens:
        raise HTTPException(status_code=400, detail="No FEN positions provided")

    multipv = payload.multipv if payload.multipv is not None else STOCKFISH_MOVES
    limit = _build_limit(depth_override=payload.depth, movetime_ms=payload.movetime_ms)

    results = []
    batch_start = perf_counter()
    for idx, fen in enumerate(payload.fens):
        try:
            board = chess.Board(fen)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid FEN at index {idx}: {exc}") from exc

        engine = await ENGINE_POOL.acquire()
        start = perf_counter()
        try:
            analysis = await _analyse_board(engine, board, limit, multipv)
        except Exception as exc:
            print(f"Error while getting engine analysis for fen index {idx}: {exc}")
            analysis = [{
                "idx": 0,
                "top_move": "",
                "cp": chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE).relative.score(),
            }]
        finally:
            await ENGINE_POOL.release(engine)

        elapsed_ms = (perf_counter() - start) * 1000.0
        results.append({"fen": fen, "analysis": analysis, "analysis_time_ms": elapsed_ms})

    total_ms = (perf_counter() - batch_start) * 1000.0
    return {"results": results, "total_time_ms": total_ms}

@app.get("/")
async def root():
    return {
        "message": "Stockfish service up",
        "engine_loaded": bool(ENGINE_POOL and ENGINE_POOL.started),
        "stockfish_version": STOCKFISH_VERSION,
        "engine_pool_size": ENGINE_POOL.size if ENGINE_POOL else 0,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
