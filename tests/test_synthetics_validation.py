# tests/tests_synthetics_validation.py

from seanox_ai_nlp.synthetics import synthetics, TemplateConditionException
from pathlib import Path

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")


def test_synthetics_validation_0x():
    for index in range(1, 7):
        synthetics(
            TESTS_PATH,
            f"synthetics_validation_0{index}.yaml"
        )
