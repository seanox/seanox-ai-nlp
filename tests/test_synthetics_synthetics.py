# tests/test_synthetics_synthetics.py

from seanox_ai_nlp.synthetics import synthetics
from time import perf_counter

import pathlib
import random
import copy
import json
import pytest


def test_synthetics_benchmark_00():
    synthetics(
        ".",
        "de_annotate",
        {
            "planet": "",
            "type": "",
            "diameter": 0,
            "turnover": 0,
            "moons": 0,
            "atmosphere": [],
            "characteristics": []
        }
    )


def test_synthetics_benchmark_01():

    with open("synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)

    count_text = 0
    start = perf_counter()
    for data in datas:
        result = synthetics(".", "de_annotate", data)
        count_text += len(result.text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {count_text} characters")
    print(f"Benchmark iterations: {len(datas)} x")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_synthetics_benchmark_02():

    with open("synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)

    count_text = 0
    scaled_datas = []
    for data in datas:
        for _ in range(500):
            scaled_datas.append(copy.deepcopy(data))
    random.shuffle(scaled_datas)

    print(len(scaled_datas))
    start = perf_counter()
    for data in scaled_datas:
        result = synthetics(".", "de_annotate", data)
        count_text += len(result.text)
    end = perf_counter()

    print()
    print(f"Benchmark text: {count_text} characters")
    print(f"Benchmark iterations: {len(scaled_datas)} x")
    print(f"Benchmark duration: {(end - start) * 1000:.2f} ms")


def test_synthetics_usage_01():
    with open("synthetics-planets_en.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(".", "en_annotate", data)
        print(synthetic)


def test_synthetics_usage_02():
    with open("synthetics-planets_en.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(".", "en", data)
        print(synthetic)


def test_synthetics_usage_03():
    with open("synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(".", "de_annotate", data)
        print(synthetic)


def test_synthetics_usage_04():
    with open("synthetics-planets_de.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(".", "de", data)
        print(synthetic)


def test_synthetics_usage_05(monkeypatch):
    monkeypatch.chdir("../examples/synthetics")
    script_path = pathlib.Path("example-pandas.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")


def test_synthetics_usage_05(monkeypatch):
    monkeypatch.chdir("../examples/synthetics")
    script_path = pathlib.Path("example-spaCy-pipeline.py")
    try:
        exec(script_path.read_text(), {})
    except Exception as exception:
        pytest.fail(f"{script_path.name} failed with error: {exception}")
