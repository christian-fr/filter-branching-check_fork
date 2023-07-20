from functools import reduce
from typing import Tuple, List
from unittest import TestCase

import networkx as nx
from sympy import true, simplify, false

from fbc.eval import Enum, graph_soundness_check, soundness_check, brute_force_enums


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


class Test(TestCase):
    def test_graph_soundness_check_01(self):
        g, p1, p2 = get_consistent_graph_01()

        result = all([soundness_check(g, v, enums=[p1, p2]) for v in g.nodes])
        # wir erwarten ein result == True, weil: für Knoten 1 sind alle möglichen Kombination in den Ausgangskanten
        #  abgedeckt
        self.assertTrue(result)

    def test_graph_soundness_check_02(self):
        """
        Testcase for soundness check (consistency of outgoing edges.
        """
        g, p1, p2 = get_inconsistent_graph_01()

        result = all([soundness_check(g, v, enums=[p1, p2]) for v in g.nodes])
        # wir erwarten ein result == False, weil: es gibt keinen Ausgangskanten von Knoten 1 für die
        #  Kombination p1=='y' & p2=='y'
        self.assertFalse(result)
        # 2023-07-21 CF: Ist dieser Test auf False korrekt konzipiert?

    def test_brute_force_enums_01(self):
        g, p1, p2 = get_consistent_graph_01()

        enums = [p1, p2]
        v = 1  # name of the node to check

        out_predicates = [d['filter'] for d in g[v].values()]
        tmp_veroderte_predicates = reduce(lambda a, b: a | b,
                                          out_predicates)  # Veroderung aller Ausdrücke in der Liste out_predicates
        simplified_enums = simplify(tmp_veroderte_predicates)
        # this should evaluate to true
        further_simplified_enums = brute_force_enums(simplified_enums, enums)

        self.assertEquals(True, all(further_simplified_enums))

    def test_brute_force_enums_02(self):
        g, p1, p2 = get_inconsistent_graph_01()

        enums = [p1, p2]
        v = 1  # name of the node to check

        out_predicates = [d['filter'] for d in g[v].values()]
        tmp_veroderte_predicates = reduce(lambda a, b: a | b,
                                          out_predicates)  # Veroderung aller Ausdrücke in der Liste out_predicates
        simplified_enums = simplify(tmp_veroderte_predicates)
        # this should evaluate to false
        further_simplified_enums = brute_force_enums(simplified_enums, enums)

        self.assertEquals(False, all(further_simplified_enums))

    def test_brute_force_enums_03(self):
        g, p1, p2 = get_consistent_graph_02()

        enums = [p1, p2]
        v = 1  # name of the node to check

        out_predicates = [d['filter'] for d in g[v].values()]
        tmp_veroderte_predicates = reduce(lambda a, b: a | b,
                                          out_predicates)  # Veroderung aller Ausdrücke in der Liste out_predicates
        simplified_enums = simplify(tmp_veroderte_predicates)
        # this should evaluate to true
        further_simplified_enums = brute_force_enums(simplified_enums, enums)

        self.assertEquals(True, all(further_simplified_enums))

    def test_brute_force_enums_04(self):
        g, p1, p2 = get_inconsistent_graph_02()

        enums = [p1, p2]
        v = 1  # name of the node to check

        out_predicates = [d['filter'] for d in g[v].values()]
        tmp_veroderte_predicates = reduce(lambda a, b: a | b,
                                          out_predicates)  # Veroderung aller Ausdrücke in der Liste out_predicates
        simplified_enums = simplify(tmp_veroderte_predicates)
        # this should evaluate to false
        further_simplified_enums = brute_force_enums(simplified_enums, enums)

        self.assertEquals(False, all(further_simplified_enums))
