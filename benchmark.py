import argparse
import csv
import statistics
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from graph import read_dimacs
from search import minimize_colors

ROOT = Path(__file__).parent
INSTANCES = ROOT / "instances"
RESULTS = ROOT / "results"


def load_optimal():
    with open(INSTANCES / "optimal.csv") as f:
        return {row["instance"]: (int(row["optimum"]), row["proven"] == "yes") for row in csv.DictReader(f)}


def run_one(job):
    name, seed, time_limit, target = job
    graph = read_dimacs(INSTANCES / f"{name}.col")
    r = minimize_colors(graph, time_limit, seed, target)
    return {
        "instance": name, "n": graph.n, "m": graph.m, "seed": seed,
        "greedy_k": r["greedy_k"], "k": r["k"],
        "time_to_best": round(r["time_to_best"], 3), "time_total": round(r["time_total"], 3),
        "iterations": r["iterations"],
    }


def summarize(rows, optimal):
    lines = [
        "| Instance | n | m | Optimum | Greedy | Best | Average | Time (s) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, (opt, proven) in optimal.items():
        runs = [r for r in rows if r["instance"] == name]
        if not runs:
            continue

        first = runs[0]
        ks = [r["k"] for r in runs]
        times = [r["time_to_best"] for r in runs]
        opt_text = str(opt) if proven else f"{opt}*"

        lines.append(
            f"| {name} | {first['n']} | {first['m']} | {opt_text} | {first['greedy_k']} "
            f"| {min(ks)} | {statistics.mean(ks):.1f} | {statistics.mean(times):.2f} |"
        )
    lines.append("")
    lines.append("\\* best known value, optimum not proven. Time = average time until the best colouring was found.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--time", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--only", nargs="*", help="instance names to run")
    args = parser.parse_args()

    optimal = load_optimal()
    names = args.only or list(optimal)
    jobs = [
        (name, seed, args.time, optimal[name][0] if optimal[name][1] else None)
        for name in names for seed in range(args.runs)
    ]

    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(run_one, jobs):
            rows.append(row)
            print(f"{row['instance']:12} seed={row['seed']} k={row['k']} "
                  f"t={row['time_to_best']}s", flush=True)

    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "runs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize(rows, optimal)
    (RESULTS / "summary.md").write_text(summary + "\n")
    print(summary)


if __name__ == "__main__":
    main()
