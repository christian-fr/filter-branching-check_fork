from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Transition:
    target: str
    # condition as spring expression that has to be fulfilled on order to follow the transition
    condition: Optional[str] = None


@dataclass
class Variable:
    type: str
    is_preload: bool = False


@dataclass
class VarRef:
    variable: Variable
    # list of conditions (as spring expression) that have to be fulfilled in order to reach the variable reference
    condition: List[str] = field(default_factory=list)


@dataclass
class Page:
    page_uid: str
    transitions: List[Transition]
    var_refs: List[VarRef]


@dataclass
class Questionnaire:
    variables: Dict[str, Variable]
    pages: List[Page]
