import networkx as nx
from sympy import true, Symbol
from fbc.eval import graph_soundness_check, evaluate_node_predicates, Enum, construct_graph
from fbc.util import show_graph, draw_graph
from fbc.data.xml import read_questionnaire


def main2():
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & p2.eq('n')}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & p2.eq('n')}),
                      (1, 5, {"filter": p1.eq('y') & p2.eq('y')}),
                      (2, 6, {"filter": Symbol('x') >= 0}),
                      (2, 7, {"filter": Symbol('x') < 0}),
                      (3, 8, {"filter": true}),
                      (4, 8, {"filter": true}),
                      (5, 8, {"filter": true}),
                      (6, 8, {"filter": true}),
                      (7, 8, {"filter": true})])

    if not graph_soundness_check(g, source=1, enums=[p1, p2]):
        raise ValueError("Soundness check failed")

    evaluate_node_predicates(g, source=1, enums=[p1, p2])

    if g.nodes[8]['pred'] is not true:
        raise ValueError(f"Graph evaluation failed: final node cannot be reached unless '{g.nodes[8]['pred']}'")

    show_graph(g)


def main():
    q = read_questionnaire("data/questionnaire.xml")
    g = construct_graph(q)
    draw_graph(g, 'graph.png')


if __name__ == "__main__":
    main()
