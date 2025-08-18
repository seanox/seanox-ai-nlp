# tests/test_synthetics_synthetics.py

from seanox_ai_nlp.synthetics import synthetics
from time import perf_counter

import pandas
import random
import copy
import json

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


LABEL_COLORS = {
    "planet": ("\033[38;5;0m", "\033[48;5;117m"),   # white on blue
    "term":   ("\033[38;5;0m", "\033[48;5;250m")    # black on light gray
}


def highlight_entities(text, entities):
    reset = '\033[0m'
    for start, end, label in sorted(entities, key=lambda x: -x[0]):
        if label not in LABEL_COLORS:
            label = "term"
        fg, bg = LABEL_COLORS[label]
        colored = f"{fg}{bg}{text[start:end]}{reset}"
        text = text[:start] + colored + text[end:]
    return text


def test_synthetics_usage_x02():
    with open("synthetics-planets_en.json", encoding="utf-8") as file:
        datas = json.load(file)
    for data in datas:
        synthetic = synthetics(".", "en_annotate", data)
        print(highlight_entities(synthetic.text, synthetic.entities))

        dataframe = pandas.DataFrame(synthetic.entities, columns=["start", "end", "label"])
        dataframe["text"] = dataframe.apply(lambda row: synthetic.text[row["start"]:row["end"]], axis=1)
        dataframe = dataframe[["start", "end", "label", "text"]]
        print(dataframe.to_string(index=False))
