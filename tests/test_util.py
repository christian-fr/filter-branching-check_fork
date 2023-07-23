from unittest import TestCase
from context.graphs import get_consistent_graph_03
from fbc.util import bfs_nodes


class Test(TestCase):
    def test_bfs_nodes(self):
        g, p1 = get_consistent_graph_03()
        n = bfs_nodes(g, 1)
        self.fail()
