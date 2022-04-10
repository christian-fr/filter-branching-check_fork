import networkx as nx
from networkx import bfs_successors, bfs_edges
from sympy import symbols, simplify, true, false
from sympy.logic.boolalg import to_dnf
from functools import reduce
# import matplotlib.pyplot as plt


def main():
    x = symbols("x")

    g = nx.DiGraph()
    g.add_nodes_from([1, 2, 3, 4])
    g.add_edges_from([(1, 2, {"filter": x <= 0}),
                      (1, 3, {"filter": x > 0}),
                      (2, 4, {"filter": true}),
                      (3, 4, {"filter": true})])

    successor_sanity_check(g, source=1)

    for v in bfs_nodes(g, source=1):
        in_nodes = [(g.nodes[v1]['pred'], g[v1][v2]['filter']) for v1, v2, data in g.in_edges(v, data=True)]

        if len(in_nodes) == 0:
            node_pred = true
        else:
            node_pred = reduce(lambda a, b: (a[0] & a[1]) | (b[0] & b[1]), in_nodes)

        g.nodes[v].update({"pred": node_pred})


def successor_sanity_check(g, source):
    return all([successor_soundness_check(g, v) for v in bfs_nodes(g, source)])


def successor_soundness_check(g, v):
    out_predicates = [d['filter'] for d in g[v].values()]
    if len(out_predicates) != 0:
        return simplify(reduce(lambda a, b: a | b, out_predicates)) is true
    else:
        return True


def bfs_nodes(g, source):
    return [source] + [v for _, v in bfs_edges(g, source=source)]


if __name__ == "__main__":
    main()
