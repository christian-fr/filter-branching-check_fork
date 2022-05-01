import networkx as nx
from functools import reduce
from typing import Any, List, Union, Dict, Set
from fbc.util import bfs_nodes, flatten
from sympy import simplify, true, false, Expr, Symbol, Eq, Ne, Not, Le, Lt, Ge, Gt, And, Or
from fbc.data import Questionnaire
from fbc.data.parse import LispParser


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


class Scope:
    def _register(self, ident: str, obj: 'Scope') -> None:
        raise NotImplemented()

    def register(self, idents: Union[List[str], str], obj: 'Scope') -> None:
        if isinstance(idents, str):
            idents = idents.split(".")

        if len(idents) == 0:
            raise ValueError('ids is empty')
        elif len(idents) == 1:
            self._register(idents[0], obj)
        else:
            sub_scope = self._lookup(idents[0])
            sub_scope.register(idents[1:], obj)

    def _lookup(self, ident: str) -> 'Scope':
        raise NotImplemented()

    def lookup(self, idents: Union[List[str], str]) -> 'Scope':
        if isinstance(idents, str):
            idents = idents.split('.')

        if len(idents) == 0:
            raise ValueError('ids is empty')
        elif len(idents) == 1:
            return self._lookup(idents[0])
        else:
            sub_scope = self._lookup(idents[0])
            return sub_scope.lookup(idents[1:])

    def ast(self):
        raise NotImplemented()


class DictScope(Scope):
    def __init__(self, d=None):
        self.d = {}

        if d is not None:
            for k, v in d.items():
                self.register(k, v)

    def _register(self, ident: str, obj: Any) -> None:
        self.d[ident] = obj

    def _lookup(self, ident):
        return self.d[ident]


class ObjScope(Scope):
    ALL = {}

    def _register(self, ident: str, obj: Any) -> None:
        raise ValueError("cannot register in `ObjScope`")

    def _lookup(self, ident: str) -> Any:
        if ident not in self.ALL:
            raise AttributeError(f'{ident} does not exist')

        return getattr(self, ident)()


class ZofarVariable(ObjScope):
    ALL = {"value"}

    def __init__(self, name: str, typ: str, value_type):
        self.name = name
        self.typ = typ
        self.value_type = value_type

    def value(self):
        return 'symbol', self.name, self.value_type

    def ast(self):
        return 'var', self, self.value_type


class StringVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'string', 'string')


class NumberVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'number', 'number')


class BooleanVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'boolean', 'boolean')


class SingleChoiceVariable(ZofarVariable):
    def __init__(self, name: str, answer_options: Dict[str, int]):
        super().__init__(name, 'singleChoiceAnswerOption', 'string')
        self.answer_options = answer_options


class MacroVariable(ZofarVariable):
    def __init__(self, name: str, ins, out, handle):
        super().__init__(name, 'macro', 'macro')
        self.ins = ins
        self.out = out
        self.handle = handle

    def value(self):
        raise NotImplemented()

    def ast(self):
        return 'macro', self.name, self.ins, self.out, self.handle


class ZofarMacroModule(DictScope):
    def __init__(self):
        super().__init__({
            'asNumber': MacroVariable('macro@asNumber', ['var'], 'symbol', self.as_number),
            'isMissing': MacroVariable('macro@isMissing', ['var'], 'symbol', self.is_missing),
            'baseUrl': MacroVariable('macro@baseUrl', [], 'symbol', self.base_url),
            'isMobile': MacroVariable('macro@isMobile', [], 'symbol', self.is_mobile)
        })

    @classmethod
    def as_number(cls, expr: tuple):
        if not isinstance(expr, tuple) or expr[0] != 'var':
            raise ValueError("`expr` must be a 'var'")

        _, var, typ = expr

        if var.typ == 'number':
            sym_name = var.name
        else:
            sym_name = f"{var.name}_NUM"

        return 'symbol', sym_name, 'number'

    @classmethod
    def is_missing(cls, expr):
        if not isinstance(expr, tuple) or expr[0] != 'var':
            raise ValueError("`expr` must be a 'var'")

        _, var, typ = expr

        return 'symbol', f"{var.name}_IS_MISSING", 'boolean'

    @classmethod
    def base_url(cls):
        return 'symbol', "ZOFAR_BASE_URL", 'string'

    @classmethod
    def is_mobile(cls):
        return 'symbol', "ZOFAR_IS_MOBILE", 'boolean'


binary_ops = {"==": Eq, "!=": Ne, "gt": Gt, "ge": Ge, "lt": Lt, "le": Le, "and": And, "or": Or}
unary_ops = {"not": Not}


def ast_type(ast):
    if isinstance(ast, tuple):
        return ast[0]
    elif isinstance(ast, list):
        return 'list'
    elif type(ast) in [int, str, bool, float]:
        return 'primitive'
    else:
        raise ValueError(f"could not determine ast type from {ast}")


def lookup(exp, s: Scope):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op == 'lookup':
            res = s.lookup(args[0])
            if isinstance(res, Scope):
                return s.lookup(args[0]).ast()
            else:
                return res
        else:
            return (op, ) + tuple([lookup(a, s) for a in args])
    elif isinstance(exp, list):
        return [lookup(i, s) for i in exp]
    else:
        return exp


def apply_macros(exp):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op == 'call':
            fun = apply_macros(args[0])
            fun_args = [apply_macros(arg) for arg in args[1]]

            if fun[0] == 'macro':
                fun_ast, name, exp_ast_types, out_ast_type, handle = fun
                ast_args = fun_args

                arg_ast_types = [ast_type(ast) for ast in ast_args]
                if not all([a == b for a, b in zip(arg_ast_types, exp_ast_types)]):
                    raise ValueError(f"error when calling macro {name}. Expected [{str(exp_ast_types)}] got "
                                     f"[{str(arg_ast_types)}]")

                result_ast = handle(*ast_args)

                if ast_type(result_ast) != out_ast_type:
                    raise ValueError(f"error when calling macro {name}. Result ast type did not match expected type."
                                     f"Expected [{out_ast_type}] got [{ast_type(result_ast)}]")

                return result_ast
            else:
                return 'call', fun, fun_args
        else:
            return (op, ) + tuple([apply_macros(a) for a in args])
    elif isinstance(exp, list):
        return [apply_macros(i) for i in exp]
    else:
        return exp


inequations = {'lt': lambda x, y: x < y,
               'le': lambda x, y: x <= y,
               'gt': lambda x, y: x > y,
               'ge': lambda x, y: x >= y}


def cat_macro(exp, enums: Dict[str, Set[Any]]):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op in ['==', '!=', 'lt', 'le', 'gt', 'ge']:
            if is_cat_tuple(args[0], enums) and is_literal(args[1]):
                sym_ast = args[0]
                lit = args[1]
            elif is_cat_tuple(args[1], enums) and is_literal(args[0]):
                lit = args[0]
                sym_ast = args[1]
            else:
                return (op, ) + tuple([cat_macro(arg, enums) for arg in args])

            _, sym_name, sym_type = sym_ast
            lit_type = type_check(lit)
            enum = enums[sym_name]

            if sym_type != lit_type:
                raise ValueError(f"types incompatible in {exp}. {sym_type} != {lit_type}")

            if op in inequations:
                if not (lit_type == sym_type == 'number'):
                    raise ValueError(f"inequation with category type can only be resolved with numbers")

                ineq = inequations[op]
                valid_lit = [e for e in enum if ineq(e, lit)]
                lit_symbols = [('symbol', f'LIT_{sym_ast[1]}_{li}', 'number') for li in valid_lit]
                preds = [("==", ('symbol', sym_ast[1], lit_type), li) for li in lit_symbols]
                if len(preds) == 0:
                    raise ValueError("empty set of literals after resolving inequation")
                elif len(preds) == 1:
                    return preds[0]
                else:
                    ast = ('or', preds[0], preds[1])
                    for pred in preds[2:]:
                        ast = ('or', ast, pred)
                    return ast
            else:
                if lit not in enum:
                    raise ValueError(f"{sym_name} must be one of {list(enum)}. Found {lit}")

                lit_val = f'LIT_{sym_ast[1]}_{lit}'
                return op, ('symbol', sym_ast[1], lit_type), ('symbol', lit_val, lit_type)
        else:
            return (op, ) + tuple([cat_macro(arg, enums) for arg in args])
    else:
        return exp


def is_cat_tuple(exp, enums):
    return isinstance(exp, tuple) and len(exp) == 3 and exp[0] == 'symbol' and exp[1] in enums


def is_literal(exp):
    return type(exp) in [int, str, bool, float]


def to_var(k, var, answer_options):
    if var.type == 'string':
        return StringVariable(k)
    elif var.type == 'number':
        return NumberVariable(k)
    elif var.type == 'boolean':
        return BooleanVariable(k)
    elif var.type == 'singleChoiceAnswerOption':
        return SingleChoiceVariable(k, answer_options.get(k))
    else:
        raise ValueError(f"unknown variable type: {var.type}")


def type_check(exp):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op in ['not']:
            if type_check(args[0]) != 'boolean':
                raise ValueError(f"expected type boolean but got {args[0]}")
            return 'boolean'
        elif op in ['and', 'or']:
            [ltype, rtype] = [type_check(arg) for arg in args]

            if not all([o == 'boolean' for o in [ltype, rtype]]):
                raise ValueError(f"expected boolean operands in {exp}")

            return 'boolean'
        elif op in ['==', '!=', 'lt', 'le', 'gt', 'ge']:
            [ltype, rtype] = [type_check(arg) for arg in args]
            if not all([o in ['boolean', 'number', 'string'] for o in [ltype, rtype]]):
                raise ValueError(f"{exp} contains an unexpected type")

            if ltype != rtype:
                raise ValueError(f"data types are not equal in {exp}")

            return 'boolean'
        elif op == 'symbol':
            return args[1]
        else:
            raise ValueError(f"unexpected operator: '{op}'")
    elif isinstance(exp, str):
        return 'string'
    elif isinstance(exp, int):
        return 'number'
    elif isinstance(exp, float):
        return 'number'
    elif isinstance(exp, bool):
        return 'boolean'
    else:
        raise ValueError("")


def group_by(li, key, val=None):
    if val is None:
        val = lambda x: x

    g = {}
    for i in li:
        k = key(i)
        if k not in g:
            g[k] = []
        g[k].append(val(i))
    return g


def resolve_vars(exp):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op == 'var':
            return args[0].value()
        else:
            return (op, ) + tuple([resolve_vars(a) for a in args])
    else:
        return exp


def evaluate(exp):
    if isinstance(exp, tuple):
        op = exp[0]
        args = exp[1:]

        if op in unary_ops:
            _args = [evaluate(a) for a in args]
            _op = unary_ops[op](*_args)
            return _op
        elif op in binary_ops:
            _args = [evaluate(a) for a in args]
            _op = binary_ops[op](*_args)
            return _op
        elif op == 'symbol':
            return Symbol(args[0])
        else:
            raise ValueError(f"unexpected operator: '{op}'")
    elif isinstance(exp, list):
        return [evaluate(it) for it in exp]
    elif type(exp) in [int, float, bool]:
        return exp
    elif type(exp) == str:
        return Symbol(f"LIT_{exp}")
    else:
        raise ValueError("")


def eval_expr(parser, spring_expr, scope, enums):
    lisp_expr = parser.parse(spring_expr)
    lisp_expr = lookup(lisp_expr, scope)
    lisp_expr = apply_macros(lisp_expr)
    lisp_expr = resolve_vars(lisp_expr)
    lisp_expr = cat_macro(lisp_expr, enums)
    final_type = type_check(lisp_expr)

    if final_type != 'boolean':
        raise ValueError("type check for transition does not result in boolean")

    return evaluate(lisp_expr)


def eval_questionnaire(q: Questionnaire):
    rds = flatten([p.response_domains for p in q.pages])
    categories = [(rd.variable.name, {ao.uid: ao.value for ao in rd.answer_options}) for rd in rds]
    cat_groups = group_by(categories, lambda x: x[0], lambda x: x[1])
    cat_groups = {c: (cgs[0] if all([cg == cgs[0] for cg in cgs[1:]]) else cgs) for c, cgs in cat_groups.items()}
    invalid_cat_groups = [(c, cgs) for c, cgs in cat_groups.items() if isinstance(cgs, list)]
    valid_cat_groups = {c: cgs for c, cgs in cat_groups.items() if isinstance(cgs, dict)}

    if len(invalid_cat_groups) != 0:
        raise ValueError("found invalid cat group")

    enums = {}
    for var, vcg in valid_cat_groups.items():
        if len(vcg) == 0:
            enums = {**enums, **{var: {}, f"{var}_NUM": {}}}
        else:
            v, n = zip(*vcg.items())
            enums = {**enums, **{var: set(v), f"{var}_NUM": set(n)}}

    scope = DictScope({**{k: to_var(k, v, valid_cat_groups) for k, v in q.variables.items()},
                       **{'zofar': ZofarMacroModule()}})

    parser = LispParser()

    sympy_pages = {}
    for page in q.pages:
        sympy_trans_list = []
        for trans in page.transitions:
            if trans.condition is not None:
                sympy_trans = eval_expr(parser, trans.condition, scope, enums)
            else:
                sympy_trans = true

            sympy_trans_list.append((trans, sympy_trans))

        sympy_pages[page.page_uid] = (page, sympy_trans_list)

    return sympy_pages
