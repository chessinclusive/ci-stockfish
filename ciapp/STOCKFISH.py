import os
import chess
import chess.engine
import platform
from typing import Optional

def resolve_stockfish_path() -> Optional[str]:
    """Return a usable Stockfish binary path for the current platform."""
    # Env override wins
    env_path = os.getenv("STOCKFISH_PATH")
    if env_path:
        return env_path

    system = platform.system()
    if system == "Windows":
        return "stockfish\\stockfish-windows-x86-64.exe"
    if system == "Darwin":
        return "/opt/homebrew/bin/stockfish"
    if system == "Linux":
        # Debian/Ubuntu package installs here; fallback to PATH lookup
        print("Checking for Stockfish binary on Linux...")
        if os.path.exists("ciapp/stockfish-src/stockfish-android-armv8-dotprod"):
            return "ciapp/stockfish-src/stockfish-android-armv8-dotprod"
        elif os.path.exists("/usr/games/stockfish"):
            return "/usr/games/stockfish"
        return "stockfish"
    return None


STOCKFISH_PATH = resolve_stockfish_path()
if not STOCKFISH_PATH:
    raise NotImplementedError("Operating system not supported or STOCKFISH_PATH unset")

try:
    STOCKFISH_ENGINE = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    print(f"Loaded Stockfish from {STOCKFISH_PATH}")
except Exception as exc:
    print(f"Failed to load Stockfish from {STOCKFISH_PATH}: {exc}")
    STOCKFISH_ENGINE = None

# Depth / time / multipv can be tuned via env
STOCKFISH_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "15"))
STOCKFISH_TIME = float(os.getenv("STOCKFISH_TIME", "0"))
STOCKFISH_MOVES = int(os.getenv("STOCKFISH_MOVES", "3"))
STOCKFISH_VERSION = int(os.getenv("STOCKFISH_VERSION", "17"))

STOCKFISH_PARAMS = chess.engine.Limit(
    depth=None if STOCKFISH_TIME else STOCKFISH_DEPTH,
    time=STOCKFISH_TIME or None,
)
