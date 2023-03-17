from unittest import TestCase
from tests.context import Q_A01_SOUNDNESS_FAIL, Q_A01_SOUNDNESS_SUCC, Q_A01_IN_DEGREE_FAIL_01, Q_A01_IN_DEGREE_FAIL_02, \
    G_IN_DEGREE_FAIL_01, G_IN_DEGREE_FAIL_02
from fbc.eval import graph_soundness_check, in_degree_soundness_check, Enum, construct_graph
from fbc.util import flatten


class Test(TestCase):
    def test_soundness_check(self):
        enums_fail = [Enum(name=enum.variable.name,
                           members={v.value for v in enum.values}) for enum in
                      flatten([p.enum_values for p in Q_A01_SOUNDNESS_FAIL.pages])]
        g_fail = construct_graph(Q_A01_SOUNDNESS_FAIL)

        enums_succ = [Enum(name=enum.variable.name,
                           members={v.value for v in enum.values}) for enum in
                      flatten([p.enum_values for p in Q_A01_SOUNDNESS_SUCC.pages])]
        g_succ = construct_graph(Q_A01_SOUNDNESS_SUCC)

        # A01 failing
        with self.assertRaises(expected_exception=ValueError) as cm:
            graph_soundness_check(g=g_fail, source='index', enums=enums_fail)
        self.assertEqual(("The following nodes do not pass soundness check (outgoing edges conditions): ['A01']",),
                         cm.exception.args)

        # A01 succeeding
        self.assertTrue(graph_soundness_check(g=g_succ, source='index', enums=enums_succ))

    def test_in_degree_soundness_check(self):
        # in_degree_soundness_check failing bc of cancel
        with self.assertRaises(expected_exception=ValueError) as cm:
            in_degree_soundness_check(g=G_IN_DEGREE_FAIL_01)
        self.assertEqual(("found more than one start node (without in edges): nodes_w_o_in_edges=['index', 'cancel']",),
                         cm.exception.args)

        # in_degree_soundness_check failing bc of cancel
        with self.assertRaises(expected_exception=ValueError) as cm:
            in_degree_soundness_check(g=G_IN_DEGREE_FAIL_02)
        self.assertEqual(('no start node found (without in edges): nodes_w_o_in_edges=[]',), cm.exception.args)
