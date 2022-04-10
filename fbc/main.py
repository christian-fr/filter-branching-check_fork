import networkx as nx
from networkx import bfs_successors, bfs_edges
from sympy import symbols, simplify, true, false
from sympy.logic.boolalg import to_dnf
from functools import reduce
# import matplotlib.pyplot as plt


def main():
    p1, p2, p3, p4 = symbols("p1 p2 p3 p4")

    g = nx.DiGraph()
    g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    g.add_edges_from([(1, 2, {"filter": p1}),
                      (1, 3, {"filter": ~p1}),
                      (2, 4, {"filter": p2}),
                      (2, 5, {"filter": ~p2}),
                      (3, 6, {"filter": p3}),
                      (3, 7, {"filter": ~p3}),
                      (4, 8, {"filter": true}),
                      (5, 8, {"filter": p4}),
                      (5, 9, {"filter": ~p4}),
                      (6, 9, {"filter": true}),
                      (7, 9, {"filter": true}),
                      (8, 10, {"filter": true}),
                      (9, 10, {"filter": true})])

    successor_sanity_check(g, source=1)

    for v in bfs_nodes(g, source=1):
        in_nodes = [(g.nodes[v1]['pred'], g[v1][v2]['filter']) for v1, v2, data in g.in_edges(v, data=True)]

        if len(in_nodes) == 0:
            node_pred = true
        else:
            node_pred = simplify(reduce(lambda res, p: res | (p[0] & p[1]), in_nodes, false))

        g.nodes[v].update({"pred": node_pred})

    for v in bfs_nodes(g, source=1):
        print(v, g.nodes[v])


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
