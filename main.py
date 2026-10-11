import argparse

from graph import read_dimacs
from search import minimize_colors


def main():
    parser = argparse.ArgumentParser(description="Chemical storage (graph colouring) solver")
    parser.add_argument("instance", help="graph in DIMACS .col format")
    parser.add_argument("--time", type=float, default=30.0, help="time limit in seconds")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--target", type=int, default=None, help="stop when this many cabinets is reached")
    parser.add_argument("--show", action="store_true", help="print the cabinet of every chemical")
    args = parser.parse_args()

    graph = read_dimacs(args.instance)
    print(f"{graph.name}: {graph.n} chemicals, {graph.m} incompatible pairs")
    result = minimize_colors(graph, args.time, args.seed, args.target, log=print)
    print(f"cabinets: {result['k']} (greedy start: {result['greedy_k']}), "
          f"found after {result['time_to_best']:.2f}s, {result['iterations']} iterations")
    if args.show:
        for cabinet in range(result["k"]):
            members = [str(v + 1) for v in range(graph.n) if result["coloring"][v] == cabinet]
            print(f"  cabinet {cabinet + 1}: {' '.join(members)}")


if __name__ == "__main__":
    main()
