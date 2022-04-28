from pathlib import Path
from typing import List, Dict, Union
from xml.etree import ElementTree
from fbc.util import flatten
from fbc.data import Variable, VarRef, Transition, QmlPage, Questionnaire

ns = {'zofar': 'http://www.his.de/zofar/xml/questionnaire'}


def variable_references(element: ElementTree.Element,
                        variables: Dict[str, Variable],
                        visible_conditions: List[str] = None) -> List[VarRef]:
    if visible_conditions is None:
        visible_conditions = []

    if element.get('visible') is not None:
        visible_conditions = visible_conditions + [element.get('visible').strip()]

    if element.get('variable') is not None:
        if element.get('variable') not in variables:
            raise ValueError(f"variable {element.get('variable')} was referenced but not declared")

        ref_list = [VarRef(variables[element.get('variable')], visible_conditions[:])]
    else:
        ref_list = []

    return ref_list + flatten([variable_references(c, variables, visible_conditions) for c in element])


def variable_declarations(root: ElementTree.Element) -> Dict[str, Variable]:
    variable_dict = {}

    preloads = root.find('zofar:preloads', ns)
    if preloads is not None:
        for preload in preloads.findall("zofar:preload", ns):
            for preload_item in preload.findall("zofar:preloadItem", ns):
                variable_name = preload_item.get('variable')
                if variable_name is not None:
                    variable_dict[f'PRELOAD{variable_name}'] = Variable(type='string', is_preload=True)

    variables = root.find('zofar:variables', ns)
    if variables is not None:
        for variable in variables.findall("zofar:variable", ns):
            if variable.get('name') is not None and variable.get('type') is not None:
                variable_dict[variable.get('name')] = Variable(type=variable.get('type'), is_preload=False)

    return variable_dict


def page_transitions(page: ElementTree.Element) -> List[Transition]:
    transitions = page.find('zofar:transitions', ns)

    if transitions is None:
        return []
    else:
        return [Transition(tr.get('target'), tr.get('condition'))
                for tr in transitions.findall('zofar:transition', ns)]


def questionnaire(root: ElementTree.Element) -> Questionnaire:
    variables = variable_declarations(root=root)

    pages = []
    for page in root.findall("zofar:page", ns):
        body = page.find('zofar:body', ns)
        pages.append(QmlPage(page_uid=page.attrib['uid'],
                             transitions=page_transitions(page),
                             var_refs=variable_references(body, variables) if body is not None else []))

    return Questionnaire(variables, pages)


def read_questionnaire(input_path: Union[Path, str]) -> Questionnaire:
    if isinstance(input_path, str):
        input_path = Path(input_path)

    xml_root = ElementTree.parse(input_path)

    return questionnaire(xml_root.getroot())
