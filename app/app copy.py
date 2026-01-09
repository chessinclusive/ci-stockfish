from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

import chess
import chess.engine
from chess.engine import Cp

from STOCKFISH import STOCKFISH_ENGINE, STOCKFISH_PARAMS, STOCKFISH_MOVES, STOCKFISH_VERSION

app = FastAPI()
handler = Mangum(app)

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
    try:
        if STOCKFISH_ENGINE:
            result = STOCKFISH_ENGINE.analyse(board, STOCKFISH_PARAMS, multipv=STOCKFISH_MOVES)
                    
            engine_analysis = []
            for idx, res in enumerate(result):
                engine_analysis.append({
                    f"top_move_{idx}": res.get('pv', [''])[0],
                    f"stockfish {STOCKFISH_VERSION} evaluation": res.get('score', chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE)).relative.score()
                })
        else:
            engine_analysis = [{'top_move_0': '', 'stockfish 17 evaluation': chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE).relative.score()}]
    except Exception as e:
        print(f"Error while getting engine analysis: {e}")
        engine_analysis = [{'top_move_0': '', 'stockfish 17 evaluation': chess.engine.PovScore(relative=Cp(0), turn=chess.WHITE).relative.score()}]

    return engine_analysis

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# if __name__ == "__main__":
#     response = stockfish_evaluation("4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1")
#     print(response)

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)