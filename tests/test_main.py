from unittest import TestCase
from tests.context import Q_A01_SOUNDNESS_FAIL, Q_A01_SOUNDNESS_SUCC
from fbc.eval import graph_soundness_check, Enum, construct_graph
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
        with self.assertRaises(expected_exception=ValueError,
                               msg="The following nodes do not pass soundness check (outgoing edges conditions): ['A01']"):
            graph_soundness_check(g=g_fail, source='index', enums=enums_fail)

        # A01 succeeding
        self.assertTrue(graph_soundness_check(g=g_succ, source='index', enums=enums_succ))
