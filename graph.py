from pathlib import Path


class Graph:
    def __init__(self, n, edges, name=""):
        self.n = n
        self.name = name
        self.adj = [[] for _ in range(n)]
        seen = set()
        for u, v in edges:
            if u == v:
                continue
            key = (min(u, v), max(u, v))
            if key in seen:
                continue
            seen.add(key)
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.m = len(seen)

    def conflicts(self, color):
        return sum(1 for u in range(self.n) for v in self.adj[u] if u < v and color[u] == color[v])


def read_dimacs(path):
    path = Path(path)
    n = 0
    edges = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "p":
            n = int(parts[2])
        elif parts[0] == "e":
            edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
    return Graph(n, edges, name=path.stem)
