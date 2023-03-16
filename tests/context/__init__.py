from pathlib import Path

from fbc.data.xml import read_questionnaire
Q_A01_SOUNDNESS_FAIL = read_questionnaire(Path('.', 'tests', 'context', 'questionnaire_A01_soundness_fail.xml'))
Q_A01_SOUNDNESS_SUCC = read_questionnaire(Path('.', 'tests', 'context', 'questionnaire_A01_soundness_succ.xml'))
