import traceback
from pathlib import Path

import networkx as nx
from fbc.eval import graph_soundness_check, Enum, construct_graph, evaluate_node_predicates, in_degree_soundness_check
from fbc.util import show_graph, draw_graph, flatten
from fbc.data.xml import read_questionnaire
import re
from fbc.eval import bfs_nodes
from sympy import simplify, true, false
from functools import reduce
from fbc.util import timeit


# @timeit
def main2():
    g = nx.DiGraph()

    p1 = Enum('p1', ['y', 'n'])
    p2 = Enum('p2', ['y', 'n', 'na'])

    g.add_nodes_from([1, 2, 3, 4, 5, 6])
    g.add_edges_from([(1, 2, {"filter": p1.eq('n') & (p2.eq('n') | p2.eq('na'))}),
                      (1, 3, {"filter": p1.eq('n') & p2.eq('y')}),
                      (1, 4, {"filter": p1.eq('y') & (p2.eq('y') | p2.eq('na'))}),
                      (1, 5, {"filter": p1.eq('y') & (p2.eq('n'))}),
                      (2, 6, {"filter": true}),
                      (3, 6, {"filter": true}),
                      (4, 6, {"filter": true}),
                      (5, 6, {"filter": true})])

    draw_graph(g, 'graph_main2.png')
    draw_graph(g, 'graph_main2.svg')

    try:
        if not graph_soundness_check(g, source=1, enums=[p1, p2]):
            raise ValueError("Soundness check failed")
    except ValueError as e:
        traceback.print_exc()

    evaluate_node_predicates(g, source=1, enums=[p1, p2])

    try:
        if g.nodes[8]['pred'] is not true:
            raise ValueError(f"Graph evaluation failed: final node cannot be reached unless '{g.nodes[8]['pred']}'")
    except ValueError as e:
        traceback.print_exc()

    draw_graph(g, 'graph_main2_pred.svg')
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


def main(input_path: Path):
    q = read_questionnaire(input_path)

    # call construct graph() -> create graph & add filter attribute to edges
    g = construct_graph(q)

    nodes = bfs_nodes(g, source='index')

    processed_nodes = set()

    in_degree_soundness_check(g)

    while len(nodes) != 0:
        print(f'{nodes=}')
        for v in nodes:
            print(f'{v=}')
            print(f'{len(nodes)=}')
            in_edges = [edge for edge in g.in_edges(v, data=True) if edge[0] != v]
            print(f'{in_edges=}')
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
                # disjunction of th(ose results
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

    enums = [Enum(name=enum.variable.name,
                  members={v.value for v in enum.values}) for enum in flatten([p.enum_values for p in q.pages])]

    try:
        assert graph_soundness_check(g, source='index', enums=enums)
    except ValueError as err:
        raise ValueError(err)
    except AssertionError as err:
        raise AssertionError(err)

    # evaluate_node_predicates(g, source='index', enums=enums)

    try:
        assert end_nodes_soundness_check(g, enums=enums)
    finally:
        print()

    all_end_nodes = [u for u, n in g.out_degree if n == 0]

    for u in all_end_nodes:
        # ToDo: refactor into own function
        for v, data in g.nodes(data=True):
            if v == u:
                if data['pred'] not in [true, True]:
                    raise ValueError(f'Graph evaluation failed: final node "{v}" cannot be reached unless "{data["pred"]}"')

# def end_nodes_soundness_check(g: nx.DiGraph, enums: )

if __name__ == "__main__":
    main2()
    main(Path('tests', 'context', 'questionnaire_simplified_enum.xml'))
    #main(Path('tests', 'context', 'questionnaire_simplified_enum_end_node_unreachable.xml'))
    #main(Path('tests', 'context', 'questionnaire_simplified_enum_fail.xml'))
