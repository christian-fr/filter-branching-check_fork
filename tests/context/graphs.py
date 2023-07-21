from typing import Tuple

import networkx as nx
from sympy import true

from fbc.eval import Enum


def get_inconsistent_graph_01() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n'])

    g.add_nodes_from([1, 2, 3, 4, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & p2.eq('n')}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true})])
    return g, p1, p2


def get_inconsistent_graph_02() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n', 'na'])

    g.add_nodes_from([1, 2, 3, 4, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & p2.eq('n') & p2.eq('na')}),
                      (1, 2, {"filter": p1.eq('n') & p2.eq('na')}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true})])
    return g, p1, p2


def get_consistent_graph_01() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & p2.eq('n')}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (1, 5, {"filter": p1.eq('y') & p2.eq('y')}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true}),
                      (5, 6, {"filter": true})])
    return g, p1, p2


def get_consistent_graph_02() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n', 'na'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2, {"filter": (p1.eq('n') & p2.eq('n')) | (p1.eq('n') & p2.eq('na'))}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (1, 5, {"filter": (p1.eq('y') & p2.eq('y')) | (p1.eq('y') & p2.eq('na'))}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true}),
                      (5, 6, {"filter": true})])
    return g, p1, p2


def get_consistent_graph_03() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    p2 = Enum('p2', ['1', '2', '3', '4'])
    p3 = Enum('p3', ['1', '2'])
    p4 = Enum('p4', ['1', '2'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": p1.eq('a') | p1.eq('b')}),
                      (1, 12, {"filter": p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (2, 3, {"filter": true}),
                      (3, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": true}),
                      (5, 6, {"filter": true}),
                      (6, 7, {"filter": true}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}), # end of left branch
                      (12, 13, {"filter": true}), # begin of right branch
                      (12, 16, {"filter": true}), # begin of right branch
                      (13, 14, {"filter": true}),
                      (14, 15, {"filter": true}),
                      (15, 18, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (17, 15, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 20, {"filter": true}),
                      (20, 11, {"filter": true}), # end of right branch
                      (11, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      (22, 23, {"filter": true}),
                      ])
    return g, p1, p2


def get_inconsistent_graph_03() -> Tuple[nx.DiGraph, Enum, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n', 'na'])

    g.add_nodes_from([1, 2, 3, 4, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & p2.eq('n') & p2.eq('na')}),
                      (1, 2, {"filter": p1.eq('n') & p2.eq('na')}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true})])
    return g, p1, p2
