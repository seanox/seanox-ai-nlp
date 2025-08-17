# tests/test_synthetics_synthetics.py

from seanox_ai_nlp.synthetics import synthetics

import itertools
import re

PATTERN_SYMBOLS = ['a', 'b', 'c', 'd']
PATTERN_COMBINATIONS = []
for index in range(1, len(PATTERN_SYMBOLS) + 1):
    perms = itertools.permutations(PATTERN_SYMBOLS, index)
    PATTERN_COMBINATIONS.extend(perms)

PATTERN_COMBINATIONS_2 = list(itertools.permutations(PATTERN_SYMBOLS, 2))
PATTERN_COMBINATIONS_2_STRINGS = [str(list(comb)) for comb in PATTERN_COMBINATIONS_2]

PATTERN_COMBINATIONS_4 = list(itertools.permutations(PATTERN_SYMBOLS, 4))
PATTERN_COMBINATIONS_4_STRINGS = [str(list(comb)) for comb in PATTERN_COMBINATIONS_4]

def test_synthetics_01():
    synthetic = synthetics(".", "test", {"case": "Template Functions"})
    lines = synthetic.text.splitlines()

    assert len(lines) == 14, f"Expected: 14 lines, found: {len(lines)}"

    print()
    print(lines[0])
    assert re.match(r"^[abcd]$", lines[1]), f"Expected: a|b|c|d, found: {lines[1]}"
    print(lines[2])
    print(lines[3])
    print(lines[4])
    assert re.match(r"^[abcd]$", lines[5]), f"Expected: a|b|c|d, found: {lines[5]}"
    print(lines[6])
    print(lines[7])
    assert lines[8] == "[]", f"Expected: [], found: {lines[8]}"
    assert lines[9] == "[]", f"Expected: [], found: {lines[9]}"
    assert lines[10] == "[]", f"Expected: [], found: {lines[10]}"
    assert re.match(r"^\['[abcd]'\]$", lines[11]), f"Expected: ['a|b|c|d'], found: {lines[11]}"
    assert lines[12] in PATTERN_COMBINATIONS_2_STRINGS, f"{lines[12]} not included in PATTERN_COMBINATIONS_2_STRINGS"
    assert lines[13] in PATTERN_COMBINATIONS_4_STRINGS, f"{lines[13]} not included in PATTERN_COMBINATIONS_4_STRINGS"
