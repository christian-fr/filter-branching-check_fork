from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Transition:
    target_uid: str
    condition: Optional[str] = None


@dataclass
class Variable:
    type: str
    is_preload: bool = False


@dataclass
class VarRef:
    variable: Variable
    condition: List[str] = field(default_factory=list)


@dataclass
class QmlPage:
    page_uid: str
    transitions: List[Transition]
    var_refs: List[VarRef]


@dataclass
class Questionnaire:
    variables: Dict[str, Variable]
    pages: List[QmlPage]
