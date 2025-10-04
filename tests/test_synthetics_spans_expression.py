# tests/test_synthetics_spans_expression.py

from seanox_ai_nlp.synthetics import synthetics
from pathlib import Path

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")


def test_synthetics_spans_expression_01():
    for index in range(1, 4):
        synthetics(
            TESTS_PATH,
            "synthetics_spans_expression.yaml",
            {"template": index}
        )


def test_synthetics_spans_expression_04():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_spans_expression.yaml",
        {"template": 4}
    )
    assert synthetic.spans == [(7, 10, "X"), (18, 21, "X"), (29, 32, "X")]


def test_synthetics_spans_expression_05():
    synthetic = synthetics(
        TESTS_PATH,
        "synthetics_spans_expression.yaml",
        {"template": 5}
    )
    assert synthetic.spans == [(7, 21, "X"), (7, 32, "Y"), (18, 32, "Z")]
