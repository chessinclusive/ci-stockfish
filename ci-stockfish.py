"""
Quick manual test script for the ci-stockfish API.

Exercises:
- Root endpoint (pool status/size)
- Single evaluation endpoint
- Batch evaluation endpoint with optional multipv/depth/movetime overrides
"""
import argparse
import json
import os
from time import perf_counter
from typing import List, Optional

import requests

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None  # plotting optional; skip if matplotlib is unavailable


def default_fens() -> List[str]:
    base_fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # start position
        "4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1",  # simple rook mate threat
        "r1bq1rk1/pp3ppp/2n1pn2/3p4/3P4/2PBPN2/PP3PPP/RNBQ1RK1 w - - 0 1",  # middlegame
        "r1r3k1/1p1b1pbp/p1n1p1p1/q3P3/3P4/2N2NP1/PP1QBPP1/2KR2NR w - - 0 1",
        "2r2rk1/1bqn1ppp/p2bp3/1p2N3/3P4/2N1BP2/PPQ2PBP/3RR1K1 w - - 0 1",
        "r3r1k1/1p1b1pbp/p1n1p1p1/q3P3/3P4/2N2NP1/PP1QBPP1/2KR2NR b - - 0 1",
        "r2q1rk1/1b3ppp/p1np1n2/1p1Np3/3P4/1BN1P3/PP3PPP/R1BQR1K1 w - - 0 1",
        "2r2rk1/1bqn1ppp/p2bp3/1p2N3/3P4/2N1BP2/PPQ2PBP/3RR1K1 b - - 0 1",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/3PP3/2N2N2/PPP2PPP/R1BQKB1R w KQkq - 2 3",
        "rnbq1rk1/pppp1ppp/4pn2/8/2BP4/2N5/PPP1PPPP/R1BQK1NR b KQ - 2 4",
        "r1bq1rk1/pp3ppp/2n1pn2/2bp4/3P4/2NBPN2/PP3PPP/R1BQ1RK1 w - - 0 7",
        "2r2rk1/1bqn1ppp/p2bp3/1p2N3/3P4/2N1BP2/PPQ2PBP/3RR1K1 w - - 6 12",
        "r1bqk2r/pp1n1ppp/2p1pn2/8/2BP4/2N2N2/PPP2PPP/R1BQ1RK1 w kq - 4 5",
        "r2q1rk1/pp1n1pbp/2p1p1p1/3pP3/3P4/2N2NP1/PP2PPBP/R1BQR1K1 b - - 0 9",
        "r1bq1rk1/pp3ppp/2n1pn2/2bp4/3P4/2NBPN2/PP3PPP/R1BQ1RK1 b - - 1 7",
        "8/8/2k5/8/2K5/8/8/8 w - - 0 1",  # simple king opposition
        "4k3/8/8/8/8/8/8/4K3 w - - 0 1",  # lone kings
        "8/8/8/8/8/2K5/3P4/3k4 w - - 0 1",  # king+pawn vs king
        "8/8/8/8/8/3K4/6P1/3k4 w - - 0 1",  # rook pawn race
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2BPP3/2N5/PPP2PPP/R1BQK1NR b KQkq - 2 4",
    ]
    factor = (100 + len(base_fens) - 1) // len(base_fens)
    return (base_fens * factor)[:100]


def run_root(base_url: str):
    t0 = perf_counter()
    resp = requests.get(f"{base_url}/")
    elapsed = (perf_counter() - t0) * 1000.0
    print(f"[root] status={resp.status_code} in {elapsed:.2f}ms")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)


def run_single(base_url: str, fen: str):
    t0 = perf_counter()
    resp = requests.get(f"{base_url}/stockfish_evaluation", params={"fen_position": fen})
    elapsed = (perf_counter() - t0) * 1000.0
    print(f"[single] status={resp.status_code} in {elapsed:.2f}ms (round-trip)")
    try:
        body = resp.json()
        print(json.dumps(body, indent=2))
        if isinstance(body, dict) and "analysis_time_ms" in body:
            print(f"[single] server analysis_time_ms={body['analysis_time_ms']:.2f}")
    except Exception:
        print(resp.text)


def plot_times(times: List[float], filename: str):
    if not plt:
        print("[plot] matplotlib not available; skipping plot")
        return
    if not times:
        print("[plot] no timing data to plot")
        return
    plt.figure(figsize=(10, 4))
    plt.plot(range(1, len(times) + 1), times, marker="o", linewidth=1)
    plt.title("Per-FEN analysis time (ms)")
    plt.xlabel("FEN index")
    plt.ylabel("analysis_time_ms")
    plt.grid(True, linewidth=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"[plot] saved to {filename}")


def run_batch(base_url: str, fens: List[str], multipv: int, depth: int, movetime_ms: int, plot_file: Optional[str]):
    payload = {
        "fens": fens,
        "multipv": multipv,
        "depth": depth,
        "movetime_ms": movetime_ms,
    }
    t0 = perf_counter()
    resp = requests.post(f"{base_url}/stockfish_evaluation/batch", json=payload)
    elapsed = (perf_counter() - t0) * 1000.0
    print(f"[batch] status={resp.status_code} in {elapsed:.2f}ms (round-trip)")
    try:
        body = resp.json()
        print(json.dumps(body, indent=2))
        if isinstance(body, dict):
            if "total_time_ms" in body:
                print(f"[batch] server total_time_ms={body['total_time_ms']:.2f}")
            if "results" in body:
                times = [r.get("analysis_time_ms") for r in body["results"] if isinstance(r, dict)]
                times = [t for t in times if t is not None]
                if times:
                    print(f"[batch] per-fen analysis_time_ms: min={min(times):.2f} avg={sum(times)/len(times):.2f} max={max(times):.2f}")
                    if plot_file:
                        plot_times(times, plot_file)
    except Exception:
        print(resp.text)


def main():
    parser = argparse.ArgumentParser(description="Test ci-stockfish API (single + batch).")
    parser.add_argument("--url", default=os.getenv("CI_STOCKFISH_URL", "http://127.0.0.1:8000"), help="Base URL of the API")
    parser.add_argument("--fen", default="4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1", help="FEN for single evaluation")
    parser.add_argument("--batch-fens", nargs="*", default=None, help="Space-separated FENs for batch mode")
    parser.add_argument("--multipv", type=int, default=3, help="multipv override for batch tests")
    parser.add_argument("--depth", type=int, default=None, help="Depth override for batch tests")
    parser.add_argument("--movetime-ms", type=int, default=None, help="Movetime override (ms) for batch tests")
    parser.add_argument("--plot-file", default="batch_times.png", help="Path to save per-FEN timing plot (empty to disable)")
    args = parser.parse_args()

    batch_fens = args.batch_fens if args.batch_fens else default_fens()
    print(f"Testing ci-stockfish at {args.url}")

    run_root(args.url)
    run_single(args.url, args.fen)
    plot_file = args.plot_file if args.plot_file else None
    run_batch(args.url, batch_fens, args.multipv, args.depth, args.movetime_ms, plot_file)


if __name__ == "__main__":
    main()
