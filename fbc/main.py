import networkx as nx
from sympy import true, Symbol
from fbc.eval import graph_soundness_check, evaluate_node_predicates, Enum, construct_graph
from fbc.util import show_graph, draw_graph
from fbc.data.xml import read_questionnaire
import re
from fbc.eval import bfs_nodes
from sympy import simplify, true, false, Expr, Symbol, Eq, Ne, Not, Le, Lt, Ge, Gt, And, Or, Float, Integer
from functools import reduce


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


def add_line_breaks_to_str(input_str: str, line_char_width: int = 20) -> str:
    if len(input_str) <= line_char_width:
        return input_str
    index = input_str[:line_char_width].rfind(' ')
    if index == -1:
        index = input_str.find(' ')
    if index == -1:
        return input_str
    input_str = input_str[:index] + '\n' + add_line_breaks_to_str(input_str[index + 1:])
    return input_str


def add_line_breaks_to_values(input_dict: dict) -> dict:
    tmp_dict = input_dict.copy()
    tmp_dict.update(
        {key: add_line_breaks_to_str(replace_sympy_expressions(str(val))) for key, val in input_dict.items()})
    return tmp_dict


def replace_sympy_expressions(input_str: str) -> str:
    input_str = re.sub(r'Ne\(LIT_([a-zA-Z0-9]+)_NUM_([0-9]+), [a-zA-Z0-9]+_NUM\)', r'\1!=\2', input_str)
    input_str = re.sub(r'Ne\(LIT_([a-zA-Z0-9]+)_([0-9]+), [a-zA-Z0-9]+_NUM\)', r'\1!=\2', input_str)
    input_str = re.sub(r'Eq\(LIT_([a-zA-Z0-9]+)_NUM_([0-9]+), [a-zA-Z0-9]+_NUM\)', r'\1==\2', input_str)
    input_str = re.sub(r'Eq\(LIT_([a-zA-Z0-9]+)_([0-9]+), [a-zA-Z0-9]+_NUM\)', r'\1==\2', input_str)
    input_str = re.sub(r'~([a-zA-Z0-9]+)_IS_MISSING', r'\1==MIS', input_str)
    input_str = re.sub(r'([a-zA-Z0-9]+)_IS_MISSING', r'\1==MIS', input_str)
    return input_str


def tweak_label_strings(g: nx.DiGraph) -> nx.DiGraph:
    h = nx.DiGraph()
    for node in g.nodes(data=True):
        h.add_node(node[0], **add_line_breaks_to_values(node[1]))

    for edge in g.edges(data=True):
        h.add_edge(edge[0], edge[1], **add_line_breaks_to_values(edge[2]))
    print()
    return h


def main():
    q = read_questionnaire("data/questionnaire02.xml")
    g = construct_graph(q)
    # h = tweak_label_strings(g)

    nodes = bfs_nodes(g, source='index')

    processed_nodes = set()

    while len(nodes) != 0:
        print(nodes)
        for v in nodes:
            print(v)
            print(len(nodes))
            in_edges = [edge for edge in g.in_edges(v, data=True) if edge[0] != v]
            print(in_edges)
            print(f'{(len(in_edges) == 0)=}')

            x = str(all(['pred' in g.nodes[v_parent] for v_parent, _, _ in in_edges]))
            print("all(['pred' in g.nodes[v_parent] for v_parent, _, _ in in_edges])=" + x)

            if len(in_edges) == 0:
                g.nodes[v].update({"pred": true})
                processed_nodes.add(v)


            elif all(['pred' in g.nodes[v_parent] for v_parent, _, _ in in_edges]):
                # check if all parent nodes are already evaluated
                print('drin')

                # get parent predicate and edge filter for all inbound edges
                in_nodes = [(g.nodes[v_parent]['pred'], g.edges[v_parent, v_child]['filter'])
                            for v_parent, v_child, data in in_edges]

                # determine node predicate via conjunction of each `node predicate`-`edge filter` pair and
                # disjunction of those results
                node_pred = simplify(reduce(lambda res, p: res | (p[0] & p[1]), in_nodes, false))
                g.nodes[v].update({"pred": node_pred})
                processed_nodes.add(v)

            if len(processed_nodes) == 0:
                raise ValueError("Could not process in evaluating node predicates")

            nodes = [v for v in nodes if v not in processed_nodes]
            print(f'{processed_nodes=}')
    draw_graph(g, 'graph.png')
    h = tweak_label_strings(g)
    draw_graph(h, 'graph_label.png')

    if not graph_soundness_check(g, source=1, enums=[p1, p2]):
        raise ValueError("Soundness check failed")

    evaluate_node_predicates(g, source=1, enums=[p1, p2])

    if g.nodes[8]['pred'] is not true:
        raise ValueError(f"Graph evaluation failed: final node cannot be reached unless '{g.nodes[8]['pred']}'")



if __name__ == "__main__":
    main()
