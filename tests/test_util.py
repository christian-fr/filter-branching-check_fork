from unittest import TestCase
from context.graphs import get_consistent_graph_03, get_consistent_graph_01
from fbc.util import bfs_nodes, get_mask
from fbc.eval import get_symbols
from tests.context.util import mask_2, mask_5, mask_6


class Test(TestCase):
    def test_bfs_nodes(self):
        g, p1 = get_consistent_graph_03()
        n = bfs_nodes(g, 1)
        self.fail()

    def test_get_mask(self):
        self.assertEqual(get_mask(2), mask_2)
        self.assertEqual(get_mask(5), mask_5)
        self.assertEqual(get_mask(6), mask_6)

