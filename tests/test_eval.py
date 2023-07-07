from unittest import TestCase

import networkx as nx
from sympy import true

from fbc.eval import Enum, graph_soundness_check, soundness_check


class Test(TestCase):
    def test_graph_soundness_check_01(self):
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
        result = [soundness_check(g, v, enums=[p1, p2]) for v in [1]]
        # wir erwarten ein result == True, weil: für Knoten 1 sind alle möglichen Kombination in den Ausgangskanten
        #  abgedeckt
        self.assertTrue(result)

    def test_graph_soundness_check_02(self):
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
        result = [soundness_check(g, v, enums=[p1, p2]) for v in [1]]
        # wir erwarten ein result == False, weil: es gibt keinen Ausgangskanten von Knoten 1 für die
        #  Kombination p1=='y' & p2=='y'
        self.assertFalse(result)

