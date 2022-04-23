import pyparsing as pp
from fbc.parse_xml import create_questionnaire


def infix_to_lisp(t):
    t = t[0]
    if len(t) % 2 != 1:
        raise ValueError("infix list must contain an uneven amount of items")
    if len(t) == 1:
        return t[0]
    if not all([t[(2*i)+1] == t[1] for i in range(len(t) // 2)]):
        raise ValueError("every second item must be the infix operator")

    op = t[1]
    operands = [t[2*i] for i in range((len(t) // 2) + 1)]

    lisp = (op, operands[0], operands[1])
    operands = operands[2:]

    for operand in operands:
        lisp = (op, lisp, operand)

    return lisp


class LispParser:
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
        self.bool_exp_and_or = pp.infix_notation(self.bool_exp_plain, [
            ('and', 2, pp.opAssoc.LEFT, infix_to_lisp),
            ('or', 2, pp.opAssoc.LEFT, infix_to_lisp)
        ])

        self.bool_exp_nested = pp.Forward()
        self.bool_exp_nested <<= pp.Group((
                                             pp.Opt("!")('not') +
                                             pp.Suppress("(") +
                                             (self.bool_exp_nested | self.bool_exp_and_or)('exp') +
                                             pp.Suppress(")")
                                     ).set_parse_action(lambda t: ('not', t['exp']) if 'not' in t else t['exp']))
        self.bool_exp = self.bool_exp_and_or | self.bool_exp_nested

        self.function_argument = self.bool_exp | self.term | self.scoped_identifier
        self.function_call = (
                self.scoped_identifier +
                pp.Group(pp.Suppress("(") + pp.delimited_list(self.function_argument) + pp.Suppress(")"))
        ).set_parse_action(lambda t: ('call', t[0], t[1].as_list()))

        self.term_plain <<= (pp.common.number | pp.sgl_quoted_string | self.function_call | self.scoped_identifier)
        self.bool_exp_plain <<= (
                pp.Opt("!")('not') +
                (self.bool_lit | self.predicate | self.function_call | self.scoped_identifier)("exp")
        ).set_parse_action(lambda t: ('not', t['exp']) if 'not' in t else t['exp'])

    def parse(self, s):
        return self.bool_exp.parse_string(s, parse_all=True)[0]


def main():
    questionnaire = create_questionnaire(input_file='data/questionnaire2.xml')
    trans_conditions = {p: [t.transition_condition for t in list(questionnaire[p].transitions)]
                        for p in questionnaire.keys()}
    p = LispParser()

    for page, trans_list in trans_conditions.items():
        for trans in trans_list:
            res = p.parse(trans)
            print(trans)
            print(res)


if __name__ == "__main__":
    main()
