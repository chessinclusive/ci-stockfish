from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from stockfish import Stockfish
stockfish = Stockfish(path="stockfish-src/stockfish-ubuntu-x86-64")

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


@app.get("/stockfish_evaluation")
def stockfish_evaluation(fen_position: str):
    print(f"Received FEN position: {fen_position}")
    board = chess.Board(fen_position)
    if not STOCKFISH_ENGINE:
        raise HTTPException(status_code=503, detail=f"Stockfish engine not loaded at path")
    try:
        engine_analysis = {
            "best_move": stockfish.get_best_move(), 
            "top_moves": stockfish.get_top_moves(3),
            "wdl": stockfish.get_wdl_stats(),
            "current_score": stockfish.get_evaluation(),
            "stockfish_version": stockfish.get_stockfish_major_version()
        }
    except Exception as e:
        print(f"Error while getting engine analysis: {e}")
        engine_analysis = {
            "best_move": '', 
            "top_moves": [],
            "wdl": [],
            "current_score": 0,
            "stockfish_version": 17
        }

    return engine_analysis

@app.get("/")
async def root():
    return {
        "message": "Stockfish service up",
        "stockfish_engine": STOCKFISH_ENGINE,
        "engine_loaded": bool(STOCKFISH_ENGINE),
        "stockfish_version": STOCKFISH_VERSION,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
