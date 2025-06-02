import chess
import chess.engine
import platform

STOCKFISH_ENGINE = None
if platform.system() == "Windows":
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("stockfish\\stockfish-windows-x86-64.exe")
elif platform.system() == "Linux":  
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("stockfish-src/stockfish-ubuntu-x86-64")
    print("------- stockfish loaded for linux -------")
elif platform.system() == "Darwin":
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
else:
    print("------- Unsupported OS -------")
    raise NotImplementedError("Operating system not supported")
STOCKFISH_PARAMS = chess.engine.Limit(depth=20, time=None)
STOCKFISH_MOVES = 3
STOCKFISH_VERSION = 17
