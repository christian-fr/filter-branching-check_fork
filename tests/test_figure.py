import networkx as nx
from sympy import true

from fbc.eval import Enum
from fbc.util import draw_graph


def main():
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n'])

    g.add_node(1, style="filled", fillcolor="red")
    g.add_node(5, style="filled", fillcolor="violet")
    g.add_node(7, style="filled", fillcolor="orange")
    g.add_nodes_from([1, 2, 3, 4, 6])
    g.add_edges_from([(1, 2, {"filter": 'p1=="n" & (p2=="n"|p2=="na")'}),
                      (1, 3, {"filter": 'p1=="n" & p2=="y"'}),
                      (1, 4, {"filter": 'p1=="y" & p2=="y"'}),
                      (1, 5, {"filter": 'p1=="y" & p2=="n"'}),
                      (2, 6, {"filter": 'p1=="n"'}),
                      (2, 7, {"filter": 'p1=="y"', "color": "orange", "fontcolor": "orange", "penwidth": 2}),
                      (3, 11, {"filter": 'True'}),
                      (4, 8, {"filter": 'p1=="y"'}),
                      (4, 11, {"filter": 'p1=="n"', "color": "darkred", "fontcolor": "darkred", "penwidth": 2}),
                      (5, 9, {"filter": 'p1=="y"', "color": "violet", "fontcolor": "violet", "penwidth": 2}),
                      (5, 10, {"filter": 'p1=="y" | p2=="n', "color": "violet", "fontcolor": "violet", "penwidth": 2}),
                      (9, 11, {"filter": 'True'}),
                      (10, 11, {"filter": 'True'}),
                      (6, 11, {"filter": 'True'}),
                      (7, 11, {"filter": 'True'}),
                      (8, 11, {"filter": 'True'}),
                      ])

    draw_graph(g, path="example.png")


if __name__ == '__main__':
    main()
