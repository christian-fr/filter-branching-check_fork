from functools import reduce
from unittest import TestCase

from sympy import simplify, true

from fbc.eval import soundness_check, brute_force_enums, disjointness_check, evaluate_node_predicates, \
    evaluate_edge_filters
from fbc.util import draw_graph
from tests.context.graphs import get_inconsistent_graph_01, get_inconsistent_graph_02, get_consistent_graph_01, \
    get_consistent_graph_02, get_consistent_graph_03, get_inconsistent_graph_03, get_inconsistent_graph_02a


class Test(TestCase):
    def test_graph_soundness_check_01(self):
        """
        Testcase for soundness check (consistency of outgoing edges)
        """
        g, p1, p2 = get_consistent_graph_01()

        result = all([soundness_check(g, v, enums=[p1, p2], in_exp=true) for v in g.nodes])
        # wir erwarten ein result == True, weil: für Knoten 1 sind alle möglichen Kombination in den Ausgangskanten
        #  abgedeckt
        self.assertTrue(result)

    def test_graph_soundness_check_02(self):
        """
        Testcase for soundness check (consistency of outgoing edges)
        """
        g, p1, p2 = get_inconsistent_graph_01()

        result = all([soundness_check(g, v, enums=[p1, p2], in_exp=true) for v in g.nodes])
        # wir erwarten ein result == False, weil: es gibt keinen Ausgangskanten von Knoten 1 für die
        #  Kombination p1=='y' & p2=='y'
        self.assertFalse(result)
        # 2023-07-21 CF: Ist dieser Test auf False korrekt konzipiert?

    def test_graph_soundness_check_03(self):
        """
        Testcase for soundness check (consistency of outgoing edges)
        """
        # get a consistent graph with branches
        g, p1 = get_consistent_graph_03()
        # draw_graph(g, "test_graph_soundness_check_03.png")
        exit()
        # ToDo: this needs to be fully implemented & fixed.
        #  BFS tree traversal, inheritance of predicates -> filter conditions, etc.
        result = all([soundness_check(g, v, enums=[p1, p2], in_exp=expression) for v in g.nodes])
        # wir erwarten ein result == ???
        self.assertFalse(result)

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

        self.assertEqual(True, all(further_simplified_enums))

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

        self.assertEqual(False, all(further_simplified_enums))

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

        self.assertEqual(True, all(further_simplified_enums))

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

        self.assertEqual(False, all(further_simplified_enums))

    def test_disjointness_check_01(self):
        """
        Testcase for disjointness check (true disjointness of outgoing edges) - should fail
        """
        g, p1, p2 = get_inconsistent_graph_02a()

        tmp_disjointness_result = [disjointness_check(g, v, enums=[p1, p2]) for v in g.nodes]
        result = all(tmp_disjointness_result)
        # wir erwarten ein result == false, weil es eine Condition auf node 1 doppelt gibt
        self.assertFalse(result)
        # ToDo: It needs to be checked whether this actually covers the consistency conditions discussed in the paper!

    def test_disjointness_check_02(self):
        """
        Testcase for disjointness check (true disjointness of outgoing edges) - should pass
        """
        g, p1, p2 = get_consistent_graph_02()

        tmp_disjointness_result = [disjointness_check(g, v, enums=[p1, p2]) for v in g.nodes]
        result = all(tmp_disjointness_result)
        # wir erwarten ein result == true
        self.assertTrue(result)
        # ToDo: It needs to be checked whether this actually covers the consistency conditions discussed in the paper!

    def test_evaluate_node_predicates_01(self):
        g, p1 = get_consistent_graph_03()

        #draw_graph(g, "test_evaluate_node_predicates_01.png")
        g = evaluate_node_predicates(g, 1, [p1])
        #draw_graph(g, 'test_evaluate_node_predicates_01_predicates.png')
        self.fail()

    def test_evaluate_node_predicates_02(self):
        g, p1 = get_inconsistent_graph_03()

        #draw_graph(g, "test_evaluate_node_predicates_02.png")
        g = evaluate_node_predicates(g, 1, [p1])
        #draw_graph(g, 'test_evaluate_node_predicates_02_predicates.png')
        g = evaluate_edge_filters(g, [p1])
        #draw_graph(g, 'test_evaluate_node_predicates_02_filters.png')



        self.fail()
