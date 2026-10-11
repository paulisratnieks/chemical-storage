# Chemical storage (graph colouring)

*n* chemicals have to be split into safety cabinets so that no two incompatible chemicals share a cabinet,
using as few cabinets as possible. This is the graph vertex colouring problem: chemicals are vertices,
incompatible pairs are edges and cabinets are colours.

Algorithm: Tabu Search, starting from a First Fit Decreasing solution.

## Files

| File | Contents |
|---|---|
| `graph.py` | graph data structure, DIMACS `.col` reader |
| `search.py` | initial solution (First Fit Decreasing), Tabu Search, minimising the number of cabinets |
| `main.py` | solve a single instance |
| `benchmark.py` | run all benchmark instances |
| `instances/` | DIMACS benchmark graphs and `optimal.csv` with known optimal numbers of cabinets |
| `results/` | benchmark results (`runs.csv`, `summary.md`) |

## Usage

```sh
python3 main.py instances/queen8_8.col --time 30          # solve one graph
python3 main.py instances/myciel4.col --show              # also print the chemicals in each cabinet

python3 benchmark.py --runs 5 --time 60                   # full benchmark
```

## Sources

- Benchmark graphs: <https://mat.tepper.cmu.edu/COLOR/instances.html> (DSJC graphs from <https://mat.tepper.cmu.edu/COLOR04/>)
- Optimal / best known values: <https://cedric.cnam.fr/~porumbed/graphs/>
