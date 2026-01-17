import os
import platform
from typing import Iterable, List, Optional, Tuple

import chess
import chess.engine


def resolve_stockfish_candidates() -> List[str]:
    """Return an ordered list of candidate Stockfish binary paths."""
    paths: List[str] = []

    env_path = os.getenv("STOCKFISH_PATH")
    if env_path:
        paths.append(env_path)

    system = platform.system()
    if system == "Windows":
        paths.append("stockfish\\stockfish-windows-x86-64.exe")
    elif system == "Darwin":
        paths.append("/opt/homebrew/bin/stockfish")
    elif system == "Linux":
        # Debian/Ubuntu package installs here; fallback to PATH lookup
        if os.path.exists("ciapp/stockfish-src/stockfish-android-armv8-dotprod"):
            paths.append("ciapp/stockfish-src/stockfish-android-armv8-dotprod")
        elif os.path.exists("/usr/games/stockfish"):
            paths.append("/usr/games/stockfish")
        paths.append("stockfish")

    # Local fallbacks
    paths.extend([
        "ciapp/stockfish-src/stockfish-ubuntu-x86-64",
        "ciapp/stockfish-src/stockfish-ubuntu-x86-64-avx2",
    ])

    # Keep order but drop duplicates
    seen = set()
    deduped = []
    for p in paths:
        if p and p not in seen:
            deduped.append(p)
            seen.add(p)
    return deduped


def spawn_engine(preferred_path: Optional[str] = None) -> Tuple[chess.engine.SimpleEngine, str]:
    """Start a Stockfish engine, trying preferred_path first then fallbacks."""
    candidates: Iterable[str] = []
    if preferred_path:
        candidates = [preferred_path] + [p for p in resolve_stockfish_candidates() if p != preferred_path]
    else:
        candidates = resolve_stockfish_candidates()

    last_exc: Optional[Exception] = None
    for path in candidates:
        try:
            eng = chess.engine.SimpleEngine.popen_uci(path)
            print(f"Loaded Stockfish from {path}")
            return eng, path
        except Exception as exc:
            last_exc = exc
            print(f"Failed to load Stockfish from {path}: {exc}")
            continue

    raise RuntimeError(f"Unable to start Stockfish engine. Last error: {last_exc}")


# Depth / time / multipv can be tuned via env
STOCKFISH_DEPTH = int(os.getenv("STOCKFISH_DEPTH", "15"))
STOCKFISH_TIME = float(os.getenv("STOCKFISH_TIME", "0"))
STOCKFISH_MOVES = int(os.getenv("STOCKFISH_MOVES", "3"))
STOCKFISH_VERSION = int(os.getenv("STOCKFISH_VERSION", "17"))

STOCKFISH_PARAMS = chess.engine.Limit(
    depth=None if STOCKFISH_TIME else STOCKFISH_DEPTH,
    time=STOCKFISH_TIME or None,
)
