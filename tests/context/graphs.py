import json
from typing import Tuple

import networkx as nx
from sympy import true, Interval, Eq
from sympy import oo

from fbc.eval import Enum, Interv


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


def get_inconsistent_graph_02a() -> Tuple[nx.DiGraph, Enum, Enum]:
    """
    inconsistent graph: there are two outgoing edges from node 1 (to nodes 2 and 3) with the same condition: p1.eq('n'),
    therefore they are not truly disjoint.
    @return:
    """
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n')}),
                      (1, 3, {"filter": p1.eq('n')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (1, 5, {"filter": p1.eq('y') & p2.eq('y')}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true}),
                      (5, 6, {"filter": true})])
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


def get_consistent_graph_03() -> Tuple[nx.DiGraph, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    # p2 = Enum('p2', ['1', '2', '3', '4'])
    # p3 = Enum('p3', ['1', '2'])
    # p4 = Enum('p4', ['1', '2'])

    # # g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 15, 16, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": p1.eq('a') | p1.eq('b')}),
                      (1, 12, {"filter": p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (2, 3, {"filter": p1.eq('a')}),
                      (3, 300, {"filter": true}),
                      (300, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": p1.eq('b')}),
                      (5, 500, {"filter": true}),
                      (500, 6, {"filter": true}),
                      (6, 7, {"filter": true}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}),  # end of left branch
                      (12, 13, {"filter": p1.eq('c')}),  # begin of right branch
                      (12, 15, {"filter": p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (13, 1300, {"filter": true}),
                      (1300, 14, {"filter": true}),
                      (14, 17, {"filter": true}),
                      (17, 18, {"filter": true}),
                      (15, 1500, {"filter": true}),
                      (1500, 1501, {"filter": p1.eq('d')}),
                      (1500, 1502, {"filter": p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (1501, 16, {"filter": true}),
                      (1502, 16, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 11, {"filter": true}),
                      (11, 20, {"filter": true}),
                      (20, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      ])
    return g, p1


def get_inconsistent_graph_03() -> Tuple[nx.DiGraph, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    # p2 = Enum('p2', ['1', '2', '3', '4'])
    # p3 = Enum('p3', ['1', '2'])
    # p4 = Enum('p4', ['1', '2'])

    # # g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 15, 16, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": p1.eq('a') | p1.eq('b')}),
                      (1, 12, {"filter": p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (2, 3, {"filter": p1.eq('a')}),
                      (3, 300, {"filter": true}),
                      (300, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": p1.eq('b')}),
                      (5, 500, {"filter": true}),
                      (500, 6, {"filter": true}),
                      (6, 7, {
                          "filter": p1.eq('a') | p1.eq('b') | p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq(
                              'g')}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}),  # end of left branch
                      (12, 13, {"filter": p1.eq('c')}),  # begin of right branch
                      (12, 15, {"filter": p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (13, 1300, {"filter": true}),
                      (1300, 14, {"filter": true}),
                      (14, 17, {"filter": true}),
                      (17, 18, {"filter": true}),
                      (15, 1500, {"filter": true}),
                      (1500, 1501, {"filter": p1.eq('a')}),
                      (1500, 1502, {"filter": p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (1501, 16, {"filter": true}),
                      (1502, 16, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 11, {"filter": true}),
                      (11, 20, {"filter": true}),
                      (20, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      ])
    return g, p1


def get_inconsistent_graph_03() -> Tuple[nx.DiGraph, Enum]:
    g = nx.DiGraph()

    p1 = Enum('p1', ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    # p2 = Enum('p2', ['1', '2', '3', '4'])
    # p3 = Enum('p3', ['1', '2'])
    # p4 = Enum('p4', ['1', '2'])

    # # g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 15, 16, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": p1.eq('a') | p1.eq('b')}),
                      (1, 12, {"filter": p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (2, 3, {"filter": p1.eq('a')}),
                      (3, 300, {"filter": true}),
                      (300, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": p1.eq('b')}),
                      (5, 500, {"filter": true}),
                      (500, 6, {"filter": true}),
                      (6, 7, {
                          "filter": p1.eq('a') | p1.eq('b') | p1.eq('c') | p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq(
                              'g')}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}),  # end of left branch
                      (12, 13, {"filter": p1.eq('c')}),  # begin of right branch
                      (12, 15, {"filter": p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (13, 1300, {"filter": true}),
                      (1300, 14, {"filter": true}),
                      (14, 17, {"filter": true}),
                      (17, 18, {"filter": true}),
                      (15, 1500, {"filter": true}),
                      (1500, 1501, {"filter": p1.eq('a')}),
                      (1500, 1502, {"filter": p1.eq('d') | p1.eq('e') | p1.eq('f') | p1.eq('g')}),
                      (1501, 16, {"filter": true}),
                      (1502, 16, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 11, {"filter": true}),
                      (11, 20, {"filter": true}),
                      (20, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      ])
    return g, p1


def get_consistent_graph_04() -> Tuple[nx.DiGraph, Enum]:
    """
    Graph wit gt/ge/lt/le
    @return:
    """
    g = nx.DiGraph()

    p1 = Enum('p1', [1, 2, 3, 4, 5, 6, 7])
    # p2 = Enum('p2', ['1', '2', '3', '4'])
    # p3 = Enum('p3', ['1', '2'])
    # p4 = Enum('p4', ['1', '2'])

    # # g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 15, 16, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": p1.lt(3)}),
                      (1, 12, {"filter": p1.gt(2)}),
                      (2, 3, {"filter": p1.eq(1)}),
                      (3, 300, {"filter": true}),
                      (300, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": p1.eq(2)}),
                      (5, 500, {"filter": true}),
                      (500, 6, {"filter": true}),
                      (6, 7, {"filter": true}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}),  # end of left branch
                      (12, 13, {"filter": p1.le(3)}),  # begin of right branch
                      (12, 15, {"filter": p1.ge(4)}),
                      (13, 1300, {"filter": true}),
                      (1300, 14, {"filter": true}),
                      (14, 17, {"filter": true}),
                      (17, 18, {"filter": true}),
                      (15, 1500, {"filter": true}),
                      (1500, 1501, {"filter": p1.le(4)}),
                      (1500, 1502, {"filter": p1.gt(4)}),
                      (1501, 16, {"filter": true}),
                      (1502, 16, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 11, {"filter": true}),
                      (11, 20, {"filter": true}),
                      (20, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      ])
    return g, p1


def get_consistent_graph_05() -> Tuple[nx.DiGraph, Interv]:
    """
    Graph with Interv() variables
    @return:
    """
    g = nx.DiGraph()

    v1 = Interv('v1', Interval(start=-oo, end=oo, left_open=False, right_open=False))
    # p2 = Enum('p2', ['1', '2', '3', '4'])
    # p3 = Enum('p3', ['1', '2'])
    # p4 = Enum('p4', ['1', '2'])

    # # g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17, 15, 16, 18, 19, 20, 21, 22, 23])
    g.add_edges_from([(1, 2, {"filter": v1.lt(500)}),
                      (1, 12, {"filter": v1.ge(500)}),
                      (2, 3, {"filter": v1.eq(200)}),
                      (3, 300, {"filter": true}),
                      (300, 4, {"filter": true}),
                      (4, 7, {"filter": true}),
                      (2, 5, {"filter": v1.ne(200)}),
                      (5, 500, {"filter": true}),
                      (500, 6, {"filter": true}),
                      (6, 7, {"filter": true}),
                      (7, 8, {"filter": true}),
                      (8, 9, {"filter": true}),
                      (9, 10, {"filter": true}),
                      (10, 11, {"filter": true}),  # end of left branch
                      (12, 13, {"filter": v1.le(800)}),  # begin of right branch
                      (12, 15, {"filter": v1.gt(800)}),
                      (13, 1300, {"filter": true}),
                      (1300, 14, {"filter": true}),
                      (14, 17, {"filter": true}),
                      (17, 18, {"filter": true}),
                      (15, 1500, {"filter": true}),
                      (1500, 1501, {"filter": v1.le(900)}),
                      (1500, 1502, {"filter": v1.gt(900)}),
                      (1501, 16, {"filter": true}),
                      (1502, 16, {"filter": true}),
                      (16, 17, {"filter": true}),
                      (18, 19, {"filter": true}),
                      (19, 11, {"filter": true}),
                      (11, 20, {"filter": true}),
                      (20, 21, {"filter": true}),
                      (21, 22, {"filter": true}),
                      ])
    return g, v1


result_evaluate_edge_filters_01 = json.loads(
    '[[[1, 2],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[1, 12],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[2, 3],'
    '"Eq(LIT_p1_a, p1)"], [[2, 5],'
    '"Eq(LIT_p1_b, p1)"], [[3, 300],'
    '"Eq(LIT_p1_a, p1)"], [[4, 7],'
    '"Eq(LIT_p1_a, p1)"], [[5, 500],'
    '"Eq(LIT_p1_b, p1)"], [[6, 7],'
    '"Eq(LIT_p1_b, p1)"], [[7, 8],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[8, 9],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[9, 10],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[10, 11],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[11, 20],'
    '"True"], [[12, 13],'
    '"Eq(LIT_p1_c, p1)"], [[12, 15],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[13, 1300],'
    '"Eq(LIT_p1_c, p1)"], [[14, 17],'
    '"Eq(LIT_p1_c, p1)"], [[15, 1500],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[16, 17],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[17, 18],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[18, 19],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[19, 11],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[20, 21],'
    '"True"], [[21, 22],'
    '"True"], [[300, 4],'
    '"Eq(LIT_p1_a, p1)"], [[500, 6],'
    '"Eq(LIT_p1_b, p1)"], [[1300, 14],'
    '"Eq(LIT_p1_c, p1)"], [[1500, 1501],'
    '"Eq(LIT_p1_d, p1)"], [[1500, 1502],'
    '"Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[1501, 16],'
    '"Eq(LIT_p1_d, p1)"], [[1502, 16],'
    '"Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"]]'
)

result_evaluate_node_predicates_01 = json.loads(
    '[[[1, 2],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[1, 12],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[2, 3],'
    '"Eq(LIT_p1_a, p1)"], [[2, 5],'
    '"Eq(LIT_p1_b, p1)"], [[3, 300],'
    '"True"], [[4, 7],'
    '"True"], [[5, 500],'
    '"True"], [[6, 7],'
    '"True"], [[7, 8],'
    '"True"], [[8, 9],'
    '"True"], [[9, 10],'
    '"True"], [[10, 11],'
    '"True"], [[11, 20],'
    '"True"], [[12, 13],'
    '"Eq(LIT_p1_c, p1)"], [[12, 15],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[13, 1300],'
    '"True"], [[14, 17],'
    '"True"], [[15, 1500],'
    '"True"], [[16, 17],'
    '"True"], [[17, 18],'
    '"True"], [[18, 19],'
    '"True"], [[19, 11],'
    '"True"], [[20, 21],'
    '"True"], [[21, 22],'
    '"True"], [[300, 4],'
    '"True"], [[500, 6],'
    '"True"], [[1300, 14],'
    '"True"], [[1500, 1501],'
    '"Eq(LIT_p1_d, p1)"], [[1500, 1502],'
    '"Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[1501, 16],'
    '"True"], [[1502, 16],'
    '"True"]]'
)

result_evaluate_edge_filters_02 = json.loads(
    '[[[1, 2],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[1, 12],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[2, 3],'
    '"Eq(LIT_p1_a, p1)"], [[2, 5],'
    '"Eq(LIT_p1_b, p1)"], [[3, 300],'
    '"Eq(LIT_p1_a, p1)"], [[4, 7],'
    '"Eq(LIT_p1_a, p1)"], [[5, 500],'
    '"Eq(LIT_p1_b, p1)"], [[6, 7],'
    '"Eq(LIT_p1_b, p1)"], [[7, 8],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[8, 9],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[9, 10],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[10, 11],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[11, 20],'
    '"True"], [[12, 13],'
    '"Eq(LIT_p1_c, p1)"], [[12, 15],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[13, 1300],'
    '"Eq(LIT_p1_c, p1)"], [[14, 17],'
    '"Eq(LIT_p1_c, p1)"], [[15, 1500],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[16, 17],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[17, 18],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[18, 19],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[19, 11],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[20, 21],'
    '"True"], [[21, 22],'
    '"True"], [[300, 4],'
    '"Eq(LIT_p1_a, p1)"], [[500, 6],'
    '"Eq(LIT_p1_b, p1)"], [[1300, 14],'
    '"Eq(LIT_p1_c, p1)"], [[1500, 1501],'
    '"False"], [[1500, 1502],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[1501, 16],'
    '"False"], [[1502, 16],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"]]'
)

result_evaluate_node_predicates_02 = json.loads(
    '[[[1, 2],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1)"], [[1, 12],'
    '"Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[2, 3],'
    '"Eq(LIT_p1_a, p1)"], [[2, 5],'
    '"Eq(LIT_p1_b, p1)"], [[3, 300],'
    '"True"], [[4, 7],'
    '"True"], [[5, 500],'
    '"True"], [[6, 7],'
    '"Eq(LIT_p1_a, p1) | Eq(LIT_p1_b, p1) | Eq(LIT_p1_c, p1) | Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | '
    'Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[7, 8],'
    '"True"], [[8, 9],'
    '"True"], [[9, 10],'
    '"True"], [[10, 11],'
    '"True"], [[11, 20],'
    '"True"], [[12, 13],'
    '"Eq(LIT_p1_c, p1)"], [[12, 15],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[13, 1300],'
    '"True"], [[14, 17],'
    '"True"], [[15, 1500],'
    '"True"], [[16, 17],'
    '"True"], [[17, 18],'
    '"True"], [[18, 19],'
    '"True"], [[19, 11],'
    '"True"], [[20, 21],'
    '"True"], [[21, 22],'
    '"True"], [[300, 4],'
    '"True"], [[500, 6],'
    '"True"], [[1300, 14],'
    '"True"], [[1500, 1501],'
    '"Eq(LIT_p1_a, p1)"], [[1500, 1502],'
    '"Eq(LIT_p1_d, p1) | Eq(LIT_p1_e, p1) | Eq(LIT_p1_f, p1) | Eq(LIT_p1_g, p1)"], [[1501, 16],'
    '"True"], [[1502, 16],'
    '"True"]]'
)
