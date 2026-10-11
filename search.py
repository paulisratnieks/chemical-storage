import random
import time


def greedy_coloring(graph):
    # First Fit Decreasing
    order = sorted(range(graph.n), key=lambda v: len(graph.adj[v]), reverse=True)
    color = [-1] * graph.n
    for v in order:
        used = {color[u] for u in graph.adj[v]}
        c = 0
        while c in used:
            c += 1
        color[v] = c
    return color


class State:
    # gamma[v][c] - number of neighbours of v with colour c
    def __init__(self, graph, k, color):
        self.graph = graph
        self.color = color[:]
        self.gamma = [[0] * k for _ in range(graph.n)]
        for v in range(graph.n):
            for u in graph.adj[v]:
                self.gamma[v][color[u]] += 1
        self.cost = sum(self.gamma[v][color[v]] for v in range(graph.n)) // 2
        self.conflicting = {v for v in range(graph.n) if self.gamma[v][color[v]] > 0}

    def move(self, v, c):
        old = self.color[v]
        self.cost += self.gamma[v][c] - self.gamma[v][old]
        self.color[v] = c
        for u in self.graph.adj[v]:
            g = self.gamma[u]
            g[old] -= 1
            g[c] += 1
            cu = self.color[u]
            if cu == old and g[old] == 0:
                self.conflicting.discard(u)
            elif cu == c:
                self.conflicting.add(u)
        if self.gamma[v][c] > 0:
            self.conflicting.add(v)
        else:
            self.conflicting.discard(v)


def tabu_search(graph, k, color, rng, deadline):
    state = State(graph, k, color)
    best_color = state.color[:]
    best_cost = state.cost

    # tabu_until[vertex][color] - iteration until which the vertex may not get that color back
    tabu_until = [[0] * k for _ in range(graph.n)]
    iteration = 0

    while state.cost > 0:
        if iteration % 500 == 0 and time.perf_counter() > deadline:
            break
        iteration += 1

        best_moves = find_best_moves(state, k, tabu_until, iteration, best_cost)
        if best_moves:
            vertex, new_color = rng.choice(best_moves)
        else:
            vertex = rng.choice(list(state.conflicting))
            new_color = rng.choice([c for c in range(k) if c != state.color[vertex]])

        old_color = state.color[vertex]
        state.move(vertex, new_color)

        tabu_tenure = rng.randint(0, 9) + int(0.6 * len(state.conflicting))
        tabu_until[vertex][old_color] = iteration + tabu_tenure

        if state.cost < best_cost:
            best_cost = state.cost
            best_color = state.color[:]

    return best_color, best_cost, iteration


def find_best_moves(state, k, tabu_until, iteration, best_cost):
    best_change = None
    best_moves = []

    for vertex in state.conflicting:
        current_color = state.color[vertex]
        neighbours_by_color = state.gamma[vertex]

        for new_color in range(k):
            if new_color == current_color:
                continue

            cost_change = neighbours_by_color[new_color] - neighbours_by_color[current_color]
            is_tabu = tabu_until[vertex][new_color] > iteration
            gives_new_best = state.cost + cost_change < best_cost
            if is_tabu and not gives_new_best:
                continue

            if best_change is None or cost_change < best_change:
                best_change = cost_change
                best_moves = [(vertex, new_color)]
            elif cost_change == best_change:
                best_moves.append((vertex, new_color))

    return best_moves


def minimize_colors(graph, time_limit=30.0, seed=0, target=None, log=None):
    rng = random.Random(seed)
    start = time.perf_counter()
    deadline = start + time_limit

    best = greedy_coloring(graph)
    best_k = max(best) + 1
    greedy_k = best_k
    time_to_best = time.perf_counter() - start
    total_iters = 0
    if log:
        log(f"greedy: k={best_k}")

    lower_bound = 1 if graph.m == 0 else 2
    if target is not None:
        lower_bound = max(lower_bound, target)

    while best_k > lower_bound and time.perf_counter() < deadline:
        k = best_k - 1
        init = [c if c < k else rng.randrange(k) for c in best]
        color, cost, iters = tabu_search(graph, k, init, rng, deadline)
        total_iters += iters
        if cost > 0:
            break
        best, best_k = color, k
        time_to_best = time.perf_counter() - start
        if log:
            log(f"k={k} found after {time_to_best:.2f}s")

    assert graph.conflicts(best) == 0
    return {
        "k": best_k,
        "greedy_k": greedy_k,
        "coloring": best,
        "time_to_best": time_to_best,
        "time_total": time.perf_counter() - start,
        "iterations": total_iters,
    }
