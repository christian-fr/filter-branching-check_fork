import pyparsing as pp
from qml.xml_read import transitions


def main2():
    integer = pp.Word(pp.nums).set_name('integer')           # simple unsigned integer
    variable = pp.Char(pp.alphas).set_name('variable')          # single letter variable, such as x, z, m, etc.
    arith_op = pp.one_of("+ - * /").set_name('operator')      # arithmetic operators
    equation = variable + "=" + integer + arith_op + integer    # will match "x=2+2", etc.
    equation.set_name('equation')

    # equation.run_tests("""\
    # # simple plus
    # x=2+2
    #
    # # with spaces
    # x = 2+2
    #
    # # multiply and more spaces
    # a = 10   *   4
    #
    # # invalid operator
    # r= 1234^ 100000
    # """)


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


def main():
    keywords = {'true', 'false', 'gt', 'ge', 'lt', 'le', 'and', 'or'}
    scoped_identifier = pp.delimited_list(pp.common.identifier, delim='.') \
        .add_condition(lambda t: all([_t not in keywords for _t in t.as_list()])) \
        .add_parse_action(lambda t: ('lookup', t.as_list()))

    bool_lit = pp.one_of(["true", "false"]).set_parse_action(lambda t: t[0] == "true")

    term_plain = pp.Forward()
    term = term_plain | pp.nested_expr("(", ")", term_plain)

    predicate = (
            term('lterm') +
            pp.one_of(["gt", "ge", "lt", "le", "==", "!="])("pred") +
            term('rterm')
    ).set_parse_action(lambda t: (t['pred'], t['lterm'], t['rterm']))
    bool_exp_plain = pp.Forward()
    bool_exp_and_or = pp.infix_notation(bool_exp_plain, [
        ('and', 2, pp.opAssoc.LEFT, infix_to_lisp),
        ('or', 2, pp.opAssoc.LEFT, infix_to_lisp)
    ])

    bool_exp_nested = pp.Forward()
    bool_exp_nested <<= pp.Group((
            pp.Opt("!")('not') +
            pp.Suppress("(") +
            (bool_exp_nested | bool_exp_and_or)('exp') +
            pp.Suppress(")")
    ).set_parse_action(lambda t: ('not', t['exp']) if 'not' in t else t['exp']))
    bool_exp = bool_exp_and_or | bool_exp_nested

    function_argument = bool_exp | term | scoped_identifier
    function_call = (
            scoped_identifier +
            pp.Group(pp.Suppress("(") + pp.delimited_list(function_argument) + pp.Suppress(")"))
    ).set_parse_action(lambda t: ('call', t[0], t[1].as_list()))

    term_plain <<= (pp.common.number | pp.sgl_quoted_string | function_call | scoped_identifier)
    bool_exp_plain <<= (
            pp.Opt("!")('not') +
            (bool_lit | predicate | function_call | scoped_identifier)("exp")
    ).set_parse_action(lambda t: ('not', t['exp']) if 'not' in t else t['exp'])

    print(bool_exp.parse_string('zofar.foo(x.value, (u gt 5) or !v.w)', parse_all=True)[0])
    # tr = transitions('data/questionnaire.xml')
    # for page, trans_list in tr.items():
    #     for trans in trans_list:
    #         res = bool_exp.parse_string(trans, parse_all=True)
    #         print(trans)
    #         print(res[0])


if __name__ == "__main__":
    main()
