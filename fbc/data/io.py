from pathlib import Path
from typing import List, Dict, Union
from xml.etree import ElementTree
from fbc.util import flatten
from fbc.data import Variable, VarRef, Transition, Page, Questionnaire, AnswerOption, ResponseDomain

ns = {'zofar': 'http://www.his.de/zofar/xml/questionnaire'}


def variable_declarations(root: ElementTree.Element) -> Dict[str, Variable]:
    """
    Reads variables from `zofar:variables` and `zofar:preloads` sections

    :param root: root xml element
    :return: dictionary mapping from variable name to a `Variable`
    """
    variable_dict = {}

    # read `preloads` section
    preloads = root.find('zofar:preloads', ns)
    if preloads is not None:
        for preload in preloads.findall("zofar:preload", ns):
            for preload_item in preload.findall("zofar:preloadItem", ns):
                variable_name = preload_item.get('variable')
                if variable_name is not None:
                    variable_dict[f'PRELOAD{variable_name}'] = Variable(f'PRELOAD{variable_name}', 'string', True)

    # read `variables` section
    variables = root.find('zofar:variables', ns)
    if variables is not None:
        for variable in variables.findall("zofar:variable", ns):
            if variable.get('name') is not None and variable.get('type') is not None:
                variable_dict[variable.get('name')] = Variable(variable.get('name'), variable.get('type'), False)

    return variable_dict


def response_domains(page: ElementTree.Element, variables: Dict[str, Variable]) -> List[ResponseDomain]:
    body = page.find('zofar:body', ns)
    if body is None:
        return []

    rds = []
    for rd in body.findall(".//zofar:responseDomain[@variable]", ns):
        var = variables[rd.get('variable')]

        answer_options = [AnswerOption(ao.get('uid'), int(ao.get('value')), ao.get('label'))
                          for ao in rd.findall(".//zofar:answerOption", ns)]

        rds.append(ResponseDomain(var, answer_options))

    return rds


def var_refs(page: ElementTree.Element, variables: Dict[str, Variable]) -> List[VarRef]:
    """
    Extract variable references from a given page

    :param page: page xml element
    :param variables: dictionary mapping variable names to a `Variable` (see `variable_declarations`)
    :return: list of `VarRef`s
    """
    # define function for recursive search
    def _var_refs(_element: ElementTree.Element, _variables: Dict[str, Variable], _visible: List[str]) -> List[VarRef]:
        # add `visible` predicate if available
        if _element.get('visible') is not None:
            _visible = _visible + [_element.get('visible').strip()]

        # if a variable attribute exists, return one-element list containing the `VarRef`. Otherwise, an empty list
        if _element.get('variable') is not None:
            # check if referenced variable is declared
            if _element.get('variable') not in variables:
                raise ValueError(f"variable {_element.get('variable')} was referenced but not declared")

            ref_list = [VarRef(variables[_element.get('variable')], _visible[:])]
        else:
            ref_list = []

        # apply recursive call and flat map on all child elements
        return ref_list + flatten([_var_refs(ch, variables, _visible) for ch in _element])

    # call recursive function on body, if it exists
    body = page.find('zofar:body', ns)
    if body is None:
        return []
    else:
        return _var_refs(body, variables, [])


def transitions(page: ElementTree.Element) -> List[Transition]:
    """
    Extract transitions from a given page

    :param page: page xml element
    :return: list of `Transition`s
    """
    trans = page.find('zofar:transitions', ns)

    if trans is None:
        return []
    else:
        return [Transition(tr.get('target'), tr.get('condition'))
                for tr in trans.findall('zofar:transition', ns)]


def questionnaire(root: ElementTree.Element) -> Questionnaire:
    """
    Extract questionnaire from xml root element

    :param root: xml root element
    :return: `Questionnaire`
    """
    variables = variable_declarations(root=root)

    pages = [Page(page.attrib['uid'], transitions(page), var_refs(page, variables), response_domains(page, variables))
             for page in root.findall("zofar:page", ns)]

    return Questionnaire(variables, pages)


def read_questionnaire(input_path: Union[Path, str]) -> Questionnaire:
    """
    Reads file from `input_path` and converts it into a `Questionnaire`

    :param input_path: path to input file as `str` or `Path`
    :return: `Questionnaire`
    """
    xml_root = ElementTree.parse(input_path)

    return questionnaire(xml_root.getroot())
