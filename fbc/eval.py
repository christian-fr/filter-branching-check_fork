import networkx as nx
from sympy import simplify, true, false, Symbol, Eq, Expr
from functools import reduce
from typing import Any, List

from fbc.util import bfs_nodes


class Category:
    """
    Defines a category with a finite set of members.
    """

    def __init__(self, name, members):
        """
        Initialize a category

        :param name: name of the category
        :param members: list of category members
        """
        self.name = name
        self.var = Symbol(name)

        self.members = members
        self.member_vars = {m: Symbol(f"{name}_{m}") for m in members}

    def subs(self, m):
        """
        Returns a substitution dict replacing the category variable with the given member

        :param m: member
        :return: substitution dict
        """
        return {self.name: self.member_vars[m]}

    @property
    def null_subs(self):
        """
        Returns a substitution dict replacing the category variable and all category literals with false.
        Using this substitution the category is effectively removed from the equation.

        :return: substitution dict
        """
        return {**{self.name: false}, **{f"{self.name}_{m}": false for m in self.member_vars}}

    def eq(self, m):
        """
        Returns predicate checking if the category variable is equal to the given member

        :param m: member
        :return: predicate
        """
        return Eq(self.var, self.member_vars[m])

    def __str__(self):
        return f"{self.name}({[m for m in self.member_vars.keys()]})"

    def __repr__(self):
        return str(self)


def evaluate_node_predicates(g: nx.DiGraph, source: Any, cats: List[Category]) -> Any:
    """
    Evaluates all node predicates in `g` reachable from `source` node. As a result each node will contain a 'pred'
    attribute containing the condition to be fulfilled in order to reach the respective node.

    Each 'pred' attribute is evaluated by following one of the two rules:

    (1) if a node has no inbound edges, 'pred' is true
    (2) otherwise 'pred' is set to (['pred' of parent 1] and ['filter' of edge from parent 1]) or
                                   (['pred' of parent 2] and ['filter' of edge from parent 2]) or
                                   ...

    :param g: graph
    :param source: node to start from
    :param cats: list of categories regarded during evaluation
    """
    nodes = bfs_nodes(g, source=source)

    # In order to process a node, each node either needs to have no inbound edges or all parent nodes already need
    # to be evaluated. For this reason we process the nodes in breadth first search node order covering most nodes in
    # the first run. The evaluation is then repeated until all nodes are covered.
    while len(nodes) != 0:
        processed_nodes = set()

        for v in nodes:
            in_edges = g.in_edges(v, data=True)

            if len(in_edges) == 0:
                g.nodes[v].update({"pred": true})

                processed_nodes.add(v)
            elif all(['pred' in g.nodes[v_parent] for v_parent, _, _ in in_edges]):
                # check if all parent nodes are already evaluated

                # get parent predicate and edge filter for all inbound edges
                in_nodes = [(g.nodes[v_parent]['pred'], g.edges[v_parent, v_child]['filter'])
                            for v_parent, v_child, data in in_edges]

                # determine node predicate via conjunction of each `node predicate`-`edge filter` pair and
                # disjunction of those results
                node_pred = simplify_cats(simplify(reduce(lambda res, p: res | (p[0] & p[1]), in_nodes, false)), cats)
                g.nodes[v].update({"pred": node_pred})

                processed_nodes.add(v)

        if len(processed_nodes) == 0:
            raise ValueError("Could not process in evaluating node predicates")

        nodes = [v for v in nodes if v not in processed_nodes]


def graph_soundness_check(g: nx.Graph, source: Any, cats: List[Category]) -> bool:
    """
    Checks weather the `soundness_check` applies to all nodes in the graph

    :param g: graph
    :param source: node to start from
    :param cats: list of categories regarded during evaluation
    :return: True, if the `soundness_check` applies to all nodes in the graph
    """
    return all([soundness_check(g, v, cats) for v in bfs_nodes(g, source)])


def soundness_check(g: nx.Graph, v: Any, cats: List[Category]) -> bool:
    """
    Checks weather the disjunction of all outbound edge filters of a node is True.

    :param g: graph
    :param v: node to evaluate
    :param cats: list of categories regarded during evaluation
    :return: True, if the disjunction of all outbound edge filters of the node is True
    """
    out_predicates = [d['filter'] for d in g[v].values()]
    if len(out_predicates) != 0:
        return simplify_cats(simplify(reduce(lambda a, b: a | b, out_predicates)), cats) == true
    else:
        return True


def simplify_cats(exp: Expr, cats: List[Category]) -> Expr:
    """
    Simplifies given expression with regard to given categories. For each category it is checked, if for all category
    members the expression becomes true. In this case this category is removed from the expression

    :param exp: expression
    :param cats: list of categories regarded during evaluation
    :return: simplified expression
    """
    for i in range(len(cats)):
        cat = cats[i]
        other_cats = cats[:i] + cats[i+1:]
        # combined null substitution for all `other_cats`
        null_subs = reduce(lambda a, b: {**a, **b.null_subs}, other_cats, {})

        if all([exp.subs({**null_subs, **cat.subs(m)}) == true for m in cat.members]):
            exp = exp.subs(cat.null_subs)

    return exp
