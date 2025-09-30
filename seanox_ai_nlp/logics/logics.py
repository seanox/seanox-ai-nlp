# seanox_ai_npl/logics/logics.py
from dataclasses import dataclass

# TODO:
# 1. Break down the sentence into parts (clauses/span groups CLAUSE(s))
# 2. Identify logical indicators in clauses (span groups LOGIC(s))
# 3. Normalize the logical fragments (set of rules)
# 4. Build/compose the logical structure (list with objects including entities)

@dataclass
class Logic:
    pass


def logics() -> Logic:
    pass
