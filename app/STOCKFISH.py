import os
import chess
import chess.engine
import platform

# Prefer an env-configured Stockfish binary, otherwise fall back to the system install from apt (in Docker)
# STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/bin/stockfish")

# try:
#     STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
#     print(f"Loaded Stockfish from {STOCKFISH_PATH}")
# except Exception as exc:
#     print(f"Failed to load Stockfish from {STOCKFISH_PATH}: {exc}")
#     STOCKFISH_ENGINE = None

STOCKFISH_ENGINE = None
if platform.system() == "Windows":
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("stockfish\\stockfish-windows-x86-64.exe")
elif platform.system() == "Linux":  
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("stockfish-src/stockfish-android-armv8-dotprod")
    print("------- stockfish loaded for linux -------")
elif platform.system() == "Darwin":
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
    print("------- stockfish loaded for Mac -------")
else:
    print("------- Unsupported OS -------")
    raise NotImplementedError("Operating system not supported")

# Depth / time / multipv can be tuned via env
STOCKFISH_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "15"))
STOCKFISH_TIME = float(os.getenv("STOCKFISH_TIME", "0"))
STOCKFISH_MOVES = int(os.getenv("STOCKFISH_MOVES", "3"))
STOCKFISH_VERSION = int(os.getenv("STOCKFISH_VERSION", "17"))

STOCKFISH_PARAMS = chess.engine.Limit(
    depth=None if STOCKFISH_TIME else STOCKFISH_DEPTH,
    time=STOCKFISH_TIME or None,
)
