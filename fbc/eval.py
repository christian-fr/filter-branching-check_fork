import networkx as nx
from functools import reduce, cached_property
from typing import Any, List, Union, Dict
from fbc.util import bfs_nodes, flatten, group_by
from sympy import simplify, true, false, Expr, Symbol, Eq, Ne, Not, Le, Lt, Ge, Gt, And, Or, Float, Integer
from sympy.core import evaluate as sympy_evaluate
from sympy.logic.boolalg import Boolean
from fbc.data import xml
from fbc.data.parse import LispParser


class Enum:
    """
    Defines an enumeration with a finite set of members.
    """

    def __init__(self, name, members, typ=None):
        """
        Initialize an enumeration

        :param name: name of the enumeration
        :param members: list of enum members
        :param typ: type of enum (must be one of ['string', 'number', None])
        """
        if typ not in ['string', 'number', None]:
            raise ValueError("typ must be one of ['string', 'number', None]")

        self.name = name

        self.var = Symbol(name, integer=True)

        self.members = set(members)
        self.member_vars = {m: Symbol(f"LIT_{name}_{m}", integer=True) for m in members}
        self.typ = typ

    def subs(self, m):
        """
        Returns a substitution dict replacing the enum variable with the given member

        :param m: member
        :return: substitution dict
        """
        return {self.name: self.member_vars[m]}

    @property
    def null_subs(self):
        """
        Returns a substitution dict replacing the enum variable and all enum literals with false.
        Using this substitution the enum is effectively removed from the equation.

        :return: substitution dict
        """
        return {**{self.name: false}, **{f"{self.name}_{m}": false for m in self.member_vars}}

    def eq(self, m):
        """
        Returns predicate checking if the enum variable is equal to the given member

        :param m: member
        :return: predicate
        """
        return Eq(self.var, self.member_vars[m])

    def __str__(self):
        return f"{self.name}({[m for m in self.member_vars.keys()]})"

    def __repr__(self):
        return str(self)

    def __contains__(self, item):
        return item in self.members

    def __iter__(self):
        return iter(self.members)


def evaluate_node_predicates(g: nx.DiGraph, source: Any, enums: List[Enum]) -> Any:
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
    :param enums: list of enumerations regarded during evaluation
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
                node_pred = simplify_enums(simplify(reduce(lambda res, p: res | (p[0] & p[1]), in_nodes, false)), enums)
                g.nodes[v].update({"pred": node_pred})

                processed_nodes.add(v)

        if len(processed_nodes) == 0:
            raise ValueError("Could not process in evaluating node predicates")

        nodes = [v for v in nodes if v not in processed_nodes]


def graph_soundness_check(g: nx.Graph, source: Any, enums: List[Enum]) -> bool:
    """
    Checks weather the `soundness_check` applies to all nodes in the graph

    :param g: graph
    :param source: node to start from
    :param enums: list of enumerations regarded during evaluation
    :return: True, if the `soundness_check` applies to all nodes in the graph
    """
    return all([soundness_check(g, v, enums) for v in bfs_nodes(g, source)])


def soundness_check(g: nx.Graph, v: Any, enums: List[Enum]) -> bool:
    """
    Checks weather the disjunction of all outbound edge filters of a node is True.

    :param g: graph
    :param v: node to evaluate
    :param enums: list of enumerations regarded during evaluation
    :return: True, if the disjunction of all outbound edge filters of the node is True
    """
    out_predicates = [d['filter'] for d in g[v].values()]
    if len(out_predicates) != 0:
        return simplify_enums(simplify(reduce(lambda a, b: a | b, out_predicates)), enums) == true
    else:
        return True


def simplify_enums(exp: Expr, enums: List[Enum]) -> Expr:
    """
    Simplifies given expression with regard to given enums. For each enum it is checked, if for all enum
    members the expression becomes true. In this case this enum is removed from the expression

    :param exp: expression
    :param enums: list of enumerations regarded during evaluation
    :return: simplified expression
    """
    for i in range(len(enums)):
        enum = enums[i]
        other_enums = enums[:i] + enums[i + 1:]
        # combined null substitution for all `other_enums`
        null_subs = reduce(lambda a, b: {**a, **b.null_subs}, other_enums, {})

        if all([exp.subs({**null_subs, **enum.subs(m)}) == true for m in enum.members]):
            exp = exp.subs(enum.null_subs)

    return exp


primitive_types = {int, str, bool, float}


def is_lispable(obj):
    return hasattr(obj, 'to_lisp')


def is_enum_lisp(lisp, enums):
    return isinstance(lisp, tuple) and len(lisp) == 3 and lisp[0] == 'symbol' and lisp[1] in enums


def ast_type(lisp):
    if isinstance(lisp, tuple):
        return lisp[0]
    elif isinstance(lisp, list):
        return 'list'
    elif type(lisp) in primitive_types:
        return 'primitive'
    else:
        raise ValueError(f"could not determine ast type from {lisp}")


def is_primitive(lisp):
    return type(lisp) in primitive_types


inequation_ops = {'lt': lambda x, y: x < y,
                  'le': lambda x, y: x <= y,
                  'gt': lambda x, y: x > y,
                  'ge': lambda x, y: x >= y}

binary_arith_ops = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b
}

unary_arith_ops = {
    'neg': lambda a: -a
}

runtime_binary_ops = {**{"==": lambda a, b: Eq(a, b),
                         "!=": lambda a, b: Ne(a, b),
                         "gt": lambda a, b: Gt(a, b),
                         "ge": lambda a, b: Ge(a, b),
                         "lt": lambda a, b: Lt(a, b),
                         "le": lambda a, b: Le(a, b),
                         "and": lambda a, b: And(a, b),
                         "or": lambda a, b: Or(a, b)},
                      **binary_arith_ops}

runtime_unary_ops = {**{"not": lambda a: Not(a)}, **unary_arith_ops}


class Scope:
    def _register(self, ident: str, obj: Any) -> None:
        raise NotImplemented()

    def register(self, idents: Union[List[str], str], obj: Any) -> None:
        if isinstance(idents, str):
            idents = idents.split(".")

        if len(idents) == 0:
            raise ValueError('ids is empty')
        elif len(idents) == 1:
            self._register(idents[0], obj)
        else:
            sub_scope = self._lookup(idents[0])
            sub_scope.register(idents[1:], obj)

    def _lookup(self, ident: str) -> Any:
        raise NotImplemented()

    def lookup(self, idents: Union[List[str], str]) -> Any:
        if isinstance(idents, str):
            idents = idents.split('.')

        if len(idents) == 0:
            raise ValueError('ids is empty')
        elif len(idents) == 1:
            return self._lookup(idents[0])
        else:
            sub_scope = self._lookup(idents[0])
            return sub_scope.lookup(idents[1:])

    def __getitem__(self, item):
        return self.lookup(item)

    def __contains__(self, item):
        raise NotImplemented()


class DictScope(Scope):
    def __init__(self, d=None):
        self.d = {}

        if d is not None:
            for k, v in d.items():
                self.register(k, v)

    def _register(self, ident: str, obj: Any) -> None:
        self.d[ident] = obj

    def _lookup(self, ident: str) -> Any:
        return self.d[ident]

    def __contains__(self, item):
        return item in self.d


class ObjScope(Scope):
    ALL = {}

    def _register(self, ident: str, obj: Any) -> None:
        raise ValueError("cannot register in `ObjScope`")

    def _lookup(self, ident: str) -> Any:
        if ident not in self.ALL:
            raise AttributeError(f'{ident} does not exist')

        return getattr(self, ident)()

    def __contains__(self, item):
        return item in self.ALL


class ZofarVariable(ObjScope):
    ALL = {"value"}

    def __init__(self, name: str, typ: str, value_type):
        self.name = name
        self.typ = typ
        self.value_type = value_type

    def value(self):
        return 'symbol', self.name, self.value_type

    @classmethod
    def from_variable(cls, var: xml.Variable, enum_dct=None):
        if enum_dct is None:
            enum_dct = {}

        if var.type == 'string':
            return StringVariable(var.name)
        elif var.type == 'number':
            return NumberVariable(var.name)
        elif var.type == 'boolean':
            return BooleanVariable(var.name)
        elif var.type == 'enum':
            return EnumVariable(var.name, enum_dct.get(var.name))
        else:
            raise ValueError(f"unknown variable type: {var.type}")


class StringVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'string', 'string')


class NumberVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'number', 'number')


class BooleanVariable(ZofarVariable):
    def __init__(self, name: str):
        super().__init__(name, 'boolean', 'boolean')


class EnumVariable(ZofarVariable):
    def __init__(self, name: str, members: Dict[str, int]):
        super().__init__(name, 'enum', 'string')
        self.answer_options = members


class Macro:
    def __init__(self, ins, handle):
        self.ins = ins
        self.handle = handle

    def to_lisp(self):
        return 'macro', self.ins, self.handle


class ZofarModule(DictScope):
    def __init__(self):
        super().__init__({
            'asNumber': Macro(['py_obj'], self.as_number),
            'isMissing': Macro(['py_obj'], self.is_missing),
            'baseUrl': Macro([], self.base_url),
            'isMobile': Macro([], self.is_mobile)
        })

    @classmethod
    def as_number(cls, lisp: tuple):
        if not isinstance(lisp, tuple) or lisp[0] != 'py_obj':
            raise ValueError("`expr` must be a 'py_obj'")

        _, obj = lisp

        if not isinstance(obj, ZofarVariable):
            raise ValueError(f'can only transform `ZofarVariable`s into numbers. Not {type(obj)}')

        if obj.typ == 'number':
            sym_name = obj.name
        else:
            sym_name = f"{obj.name}_NUM"

        return 'symbol', sym_name, 'number'

    @classmethod
    def is_missing(cls, lisp):
        if not isinstance(lisp, tuple) or lisp[0] != 'py_obj':
            raise ValueError("`expr` must be a 'py_obj'")

        _, obj = lisp

        if not isinstance(obj, ZofarVariable):
            raise ValueError(f'can only transform `ZofarVariable`s into numbers. Not {type(obj)}')

        return 'symbol', f"{obj.name}_IS_MISSING", 'boolean'

    @classmethod
    def base_url(cls):
        return 'symbol', "ZOFAR_BASE_URL", 'string'

    @classmethod
    def is_mobile(cls):
        return 'symbol', "ZOFAR_IS_MOBILE", 'boolean'


def pre_compile(lisp, s: Scope):
    if isinstance(lisp, tuple):
        op = lisp[0]
        args = lisp[1:]

        if op == 'lookup':
            res = s.lookup(args[0])
            if is_lispable(res):
                return res.to_lisp()
            elif isinstance(res, tuple) or type(res) in primitive_types:
                return res
            else:
                return 'py_obj', res
        elif op == 'call':
            fun = pre_compile(args[0], s)
            fun_args = [pre_compile(arg, s) for arg in args[1]]

            if fun[0] == 'macro':
                fun_ast, exp_ast_types, handle = fun
                ast_args = fun_args

                arg_ast_types = [ast_type(ast) for ast in ast_args]
                if not all([a == b for a, b in zip(arg_ast_types, exp_ast_types)]):
                    raise ValueError(f"error when calling macro. Expected [{str(exp_ast_types)}] got "
                                     f"[{str(arg_ast_types)}]")

                result_ast = handle(*ast_args)
                return result_ast
            else:
                return 'call', fun, fun_args
        elif op in binary_arith_ops:
            [lop, rop] = [pre_compile(arg, s) for arg in args]
            if all([type(o) in [int, float] for o in [lop, rop]]):
                return binary_arith_ops[op](lop, rop)
            else:
                return op, lop, rop
        elif op in unary_arith_ops:
            [lop] = [pre_compile(arg, s) for arg in args]
            if type(lop) in [int, float]:
                return unary_arith_ops[op](lop)
            else:
                return op, lop
        else:
            return (op,) + tuple([pre_compile(a, s) for a in args])
    elif isinstance(lisp, list):
        return [pre_compile(i, s) for i in lisp]
    else:
        return lisp


def enum_transform(lisp, scope: Scope):
    if isinstance(lisp, tuple):
        op = lisp[0]
        args = lisp[1:]

        if op in ['==', '!=', 'lt', 'le', 'gt', 'ge']:
            enums = scope['ENUM']

            if is_enum_lisp(args[0], enums) and is_primitive(args[1]):
                sym_ast = args[0]
                lit = args[1]
            elif is_enum_lisp(args[1], enums) and is_primitive(args[0]):
                lit = args[0]
                sym_ast = args[1]
            else:
                return (op,) + tuple([enum_transform(arg, scope) for arg in args])

            _, sym_name, sym_type = sym_ast
            lit_type = type_check(lit)
            enum = enums[sym_name]

            if sym_type != lit_type:
                raise ValueError(f"types incompatible in {lisp}. {sym_type} != {lit_type}")

            if op in inequation_ops:
                if not (lit_type == sym_type == enum.typ == 'number'):
                    raise ValueError(f"inequation with enum type can only be resolved with numbers")

                ineq = inequation_ops[op]
                valid_lit = [e for e in enum if ineq(e, lit)]
                lit_symbols = [('symbol', enum.member_vars[li], lit_type) for li in valid_lit]
                preds = [("==", ('symbol', enum.var, lit_type), li) for li in lit_symbols]
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
                    raise ValueError(f"{sym_name} must be one of {enum}. Found {lit}")

                return op, ('symbol', enum.var, lit_type), ('symbol', enum.member_vars[lit], lit_type)
        else:
            return (op,) + tuple([enum_transform(arg, scope) for arg in args])
    else:
        return lisp


def type_check(lisp):
    if isinstance(lisp, tuple):
        op = lisp[0]
        args = lisp[1:]

        if op in ['not']:
            if type_check(args[0]) != 'boolean':
                raise ValueError(f"expected type boolean but got {args[0]}")
            return 'boolean'
        elif op in ['and', 'or']:
            [ltype, rtype] = [type_check(arg) for arg in args]

            if not all([o == 'boolean' for o in [ltype, rtype]]):
                raise ValueError(f"expected boolean operands in {lisp}")

            return 'boolean'
        elif op in ['==', '!=', 'lt', 'le', 'gt', 'ge']:
            [ltype, rtype] = [type_check(arg) for arg in args]
            if not all([o in ['boolean', 'number', 'string'] for o in [ltype, rtype]]):
                raise ValueError(f"{lisp} contains an unexpected type")

            if ltype != rtype:
                raise ValueError(f"data types are not equal in {lisp}")

            return 'boolean'
        elif op in ['+', '-', '*', '/']:
            [ltype, rtype] = [type_check(arg) for arg in args]
            if not all([o in ['number'] for o in [ltype, rtype]]):
                raise ValueError(f"{lisp} contains an unexpected type")

            return 'number'
        elif op in ['neg']:
            [ltype] = [type_check(arg) for arg in args]
            if not all([o in ['number'] for o in [ltype]]):
                raise ValueError(f"{lisp} contains an unexpected type")

            return 'number'
        elif op == 'symbol':
            return args[1]
        else:
            raise ValueError(f"unexpected operator: '{op}'")
    elif isinstance(lisp, str):
        return 'string'
    elif isinstance(lisp, int):
        return 'number'
    elif isinstance(lisp, float):
        return 'number'
    elif isinstance(lisp, bool):
        return 'boolean'
    else:
        raise ValueError("")


def evaluate_symbol(lisp):
    op = lisp[0]
    args = lisp[1:]

    if op != 'symbol':
        raise ValueError("`lisp` is no symbol")

    sym, typ = args

    if isinstance(sym, Symbol):
        return sym
    else:
        if typ == 'string':
            return Symbol(sym, integer=True, finite=True)
        elif typ == 'number':
            return Symbol(sym, real=True, finite=True)
        elif typ == 'boolean':
            return Symbol(sym, bool=True)
        else:
            return Symbol(sym)


def evaluate_lisp(lisp):
    if isinstance(lisp, tuple):
        op = lisp[0]
        args = lisp[1:]

        if op in runtime_unary_ops:
            _args = [evaluate_lisp(a) for a in args]
            _op = runtime_unary_ops[op](*_args)
            return _op
        elif op in runtime_binary_ops:
            _args = [evaluate_lisp(a) for a in args]
            _op = runtime_binary_ops[op](*_args)
            return _op
        elif op == 'symbol':
            return evaluate_symbol(lisp)
        else:
            raise ValueError(f"unexpected operator: '{op}'")
    elif isinstance(lisp, list):
        return [evaluate_lisp(it) for it in lisp]
    elif type(lisp) == int:
        return Integer(lisp)
    elif type(lisp) == float:
        return Float(lisp)
    elif type(lisp) == bool:
        return Boolean(lisp)
    elif type(lisp) == str:
        return Symbol(lisp, integer=True, finite=True)
    else:
        raise ValueError("")


def enum_dict(pages: List[xml.Page]):
    evs_list = flatten([p.enum_values for p in pages])
    enum_maps = [(evs.variable.name, {ev.uid: ev.value for ev in evs.values}) for evs in evs_list]
    enum_map_groups = group_by(enum_maps, lambda x: x[0], lambda x: x[1])
    enum_map_groups = {c: (cgs[0] if all([cg == cgs[0] for cg in cgs[1:]]) else cgs) for c, cgs in
                       enum_map_groups.items()}
    invalid_enum_map_groups = [(c, cgs) for c, cgs in enum_map_groups.items() if isinstance(cgs, list)]
    valid_enum_map_groups = {c: cgs for c, cgs in enum_map_groups.items() if isinstance(cgs, dict)}

    if len(invalid_enum_map_groups) != 0:
        print(invalid_enum_map_groups)
        raise ValueError("found invalid enum")

    enums = {}
    for var, veg in valid_enum_map_groups.items():
        if len(veg) == 0:
            raise ValueError(f"Empty enum found: {var}")
        else:
            v, n = zip(*veg.items())
            uid_enum = Enum(var, v, 'string')
            number_enum = Enum(f"{var}_NUM", n, 'number')
            enums = {**enums, **{var: uid_enum, f"{var}_NUM": number_enum}}

    return enums


class SpringExpEvaluator:
    def __init__(self, variables: Dict[str, ZofarVariable], enums: Dict[str, Enum], macros=None):
        if macros is None:
            macros = []

        self.variables = variables
        self.enums = enums
        self.macros = macros

    @cached_property
    def scope(self):
        return DictScope({**self.variables, **{'zofar': ZofarModule(), 'ENUM': self.enums}})

    @cached_property
    def parser(self):
        return LispParser()

    def eval(self, s):
        lisp = self.parser.parse(s)
        lisp = pre_compile(lisp, self.scope)

        for macro in self.macros:
            lisp = macro(lisp, self.scope)

        typ = type_check(lisp)

        if typ != 'boolean':
            raise ValueError("type check for transition does not result in boolean")

        with sympy_evaluate(False):
            expr = evaluate_lisp(lisp)

        expr.doit()
        return expr

    def __call__(self, s):
        return self.eval(s)


class SpringExpEnumEvaluator(SpringExpEvaluator):
    def __init__(self, variable, enums):
        super().__init__(variable, enums, [enum_transform])

    @classmethod
    def from_questionnaire(cls, q: xml.Questionnaire):
        enums = enum_dict(q.pages)
        variables = {v.name: ZofarVariable.from_variable(v) for v in q.variables.values()}

        return SpringExpEnumEvaluator(variables, enums)


def construct_graph(q: xml.Questionnaire):
    evaluator = SpringExpEnumEvaluator.from_questionnaire(q)

    g = nx.DiGraph()
    g.add_nodes_from([p.uid for p in q.pages])

    edges = []
    for page in q.pages:
        neg_trans_filters = []
        for trans in page.transitions:
            if trans.condition is not None:
                trans_filter = evaluator(trans.condition)
            else:
                trans_filter = true

            excluding_trans_filter = simplify(And(*neg_trans_filters + [trans_filter]))
            edges.append((page.uid, trans.target_uid, {'filter': excluding_trans_filter}))
            neg_trans_filters.append(Not(trans_filter))

    g.add_edges_from(edges)

    return g
