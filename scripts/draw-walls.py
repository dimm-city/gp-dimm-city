"""Draw every wall tile, a few at once, then write the walls' CSS.

    python3 scripts/draw-walls.py            # every wall
    python3 scripts/draw-walls.py moss metal # just these (scripts/wall-<name>.py)
    python3 scripts/draw-walls.py --jobs 3   # how many draw at once (default 2)

Each wall script draws on its own, so they run side by side; each takes up to
about 4.5 GB, so the default of two at once fits a 16 GB machine. The cores
are shared between them (WALL_FFT_THREADS, read by scripts/wall_fft.py).
Then scripts/wall-tiles.py writes the CSS for the tiles drawn.
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WALLS = ["stone-rubble", "stone-coursed", "brick", "metal", "circuit", "moss", "surgery", "aether", "techlab", "bazaar"]


def main():
    args = sys.argv[1:]
    jobs = 2
    if "--jobs" in args:
        i = args.index("--jobs")
        jobs = int(args[i + 1])
        del args[i:i + 2]
    names = args or WALLS
    unknown = [n for n in names if not (ROOT / f"scripts/wall-{n}.py").exists()]
    if unknown:
        sys.exit(f"no scripts/wall-<name>.py for: {', '.join(unknown)}")
    env = {**os.environ, "WALL_FFT_THREADS": str(max(1, (os.cpu_count() or 1) // jobs))}

    def draw(name):
        t = time.time()
        run = subprocess.run([sys.executable, f"scripts/wall-{name}.py"], cwd=ROOT, env=env, capture_output=True, text=True)
        print(f"{name:14} {time.time() - t:6.1f}s  {'ok' if run.returncode == 0 else 'FAILED'}", flush=True)
        if run.returncode:
            print(run.stdout + run.stderr, file=sys.stderr)
        return run.returncode

    t = time.time()
    with ThreadPoolExecutor(jobs) as pool:
        failed = sum(1 for code in pool.map(draw, names) if code)
    print(f"drew {len(names) - failed} of {len(names)} in {time.time() - t:.0f}s", flush=True)
    if failed:
        sys.exit(1)
    subprocess.run([sys.executable, "scripts/wall-tiles.py"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
