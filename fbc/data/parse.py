import pyparsing as pp


def infix_to_lisp(tokens, op_assoc='left'):
    """
    Converts a list of tokens from infix notation to lisp notation.

    E.g. [1, '+', 2, '+', 3] -> ('+', ('+', 1, 2), 3)

    :param tokens: list of tokens. Must be of unequal length. Every token on even position is considered as operand.
                   Every token on uneven position is considered as operator.
    :param op_assoc: operator association. Must be one of ['left', 'right']
    :return: lisp representation
    """
    if len(tokens) % 2 != 1:
        raise ValueError("infix list must contain an uneven amount of items")

    if op_assoc not in ['left', 'right']:
        raise ValueError("`op_assoc` must one of ['left', 'right']")

    ops = [tokens[(2*i)+1] for i in range(len(tokens) // 2)]
    operands = [tokens[2*i] for i in range((len(tokens) // 2) + 1)]

    if op_assoc == 'right':
        ops = list(reversed(ops))
        operands = list(reversed(operands))
        if len(operands) >= 2:
            operands = [operands[1], operands[0]] + operands[2:]

    lisp = operands[0]
    operands = operands[1:]

    for op, operand in zip(ops, operands):
        lisp = (op, lisp, operand)

    return lisp


class LispParser:
    """
    Defines a `LispParser` converting spring expressions into a lisp notation
    """

    def __init__(self):
        self.keywords = {'true', 'false', 'gt', 'ge', 'lt', 'le', 'and', 'or'}
        self.scoped_identifier = pp.delimited_list(pp.common.identifier, delim='.') \
            .add_condition(lambda t: all([_t not in self.keywords for _t in t.as_list()])) \
            .add_parse_action(lambda t: ('lookup', t.as_list()))

        self.bool_lit = pp.one_of(["true", "false"]).set_parse_action(lambda t: t[0] == "true")

        self.term_plain = pp.Forward()
        self.term = self.term_plain | pp.nested_expr("(", ")", self.term_plain)

        self.predicate = (
                self.term('lterm') +
                pp.one_of(["gt", "ge", "lt", "le", "==", "!="])("pred") +
                self.term('rterm')
        ).set_parse_action(lambda t: (t['pred'], t['lterm'], t['rterm']))
        self.bool_exp_plain = pp.Forward()
        self.bool_exp = pp.infix_notation(self.bool_exp_plain, [
            ('!', 1, pp.opAssoc.RIGHT, lambda t: ('not', t[0][1])),
            ('and', 2, pp.opAssoc.LEFT, lambda t: infix_to_lisp(t[0])),
            ('or', 2, pp.opAssoc.LEFT, lambda t: infix_to_lisp(t[0]))
        ])

        self.function_argument = self.bool_exp | self.term | self.scoped_identifier
        self.function_call = (
                self.scoped_identifier +
                pp.Group(pp.Suppress("(") + pp.delimited_list(self.function_argument) + pp.Suppress(")"))
        ).set_parse_action(lambda t: ('call', t[0], t[1].as_list()))

        self.term_plain <<= (pp.common.number | pp.sgl_quoted_string | self.function_call | self.scoped_identifier)
        self.bool_exp_plain <<= (self.bool_lit | self.predicate | self.function_call | self.scoped_identifier)\
            .set_parse_action(lambda t: t[0])

    def parse(self, s):
        """
        Parses given spring expression and converts it into a lisp expression

        :param s: spring expression
        :return: lisp expression
        """
        return self.bool_exp.parse_string(s, parse_all=True)[0]
