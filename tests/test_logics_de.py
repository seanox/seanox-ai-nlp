# tests/test_logics_de.py

from pathlib import Path
from seanox_ai_nlp.synthetics.synthetics import _extract_entities
from seanox_ai_nlp.logics.logics import logics

import re

TESTS_PATH = Path("./tests") if Path("./tests").is_dir() else Path(".")
EXAMPLES_PATH = Path("./examples") if Path("./examples").is_dir() else Path("../examples")

_ANNOTATION_PATTERN = {
    "TYPE": [
        r"\bGesteinsplanet[a-z]*\b", r"\bGasriese[a-z]*\b",
        r"\bEisriese[a-z]*\b", r"\bGasplanet[a-z]*\b"
    ],
    "TERM": [
        r"\bPlanet[a-z]*\b", r"\bAtmosphäre\b", r"\bUmlaufzeit[a-z]*\b",
        r"\bMond[a-z]*\b", r"\bDurchmesser\b"
    ],
    "KEYWORD": [
        r"\bSauerstoff\b", r"\bMagnetfeld\b", r"\bMethan\b", r"\bvulkanisch\b",
        r"\bWasser\b", r"\brückläufig[a-z]*\b", r"\bRotation\b", r"\bStürme\b",
        r"\bFleck[a-z]*\b", r"\bRingsystem[a-z]*\b", r"\bLeben\b", r"\bDichte\b",
        r"\bfest[a-z]*\b", r"\bOberfläche\b"
    ],
    "MOONS": [r"\beinen\b", r"\bxkeine\b", r"(?<!\d)\d{1,2}(?!\d)"],
    "PLANET": [
        r"\bErde\b", r"\bMars\b", r"\bVenus\b", r"\bJupiter\b", r"\bSaturn\b",
        r"\bMerkur\b", r"\bNeptun\b", r"\bUranus\b"
    ],
    "TURNOVER": [r"(?<!\d)\d{3}(?!\d)"],
    "DIAMETER": [r"(?<!\d)\d{5,}(?!\d)"],
    "DUMMY": [r"^[A-Z](?!\w)|(?<!\w)[A-Z](?!\w)|(?<!\w)[A-Z](?!\w)"]
}


def _annotate_text(text: str) -> str:
    matches = []
    for key, patterns in _ANNOTATION_PATTERN.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                matches.append({
                    "start": match.start(),
                    "end": match.end(),
                    "key": key,
                    "text": match.group()
                })
    matches.sort(key=lambda m: m["start"])
    annotated_text = text
    offset = 0
    for match in matches:
        start = match["start"] + offset
        end = match["end"] + offset
        annotated = f"[[[{match['key']}]]]{match['text']}[[[-]]]"
        annotated_text = annotated_text[:start] + annotated + annotated_text[end:]
        offset += len(annotated) - (end - start)
    return annotated_text

# TODO: Examples for Multi-Word/Multi-Token Entities are missing.

# Prompt:
# Erstelle einfache logische Sätze.
# Nutze dazu primär die Worte:
#     finde, vergleiche, sortiere, A, B, C, D, E, F, G, H, und, oder, nicht,
#     nichts, kein, keines, nie, niemals, ohne, weder, noch.
# ---
EXAMPLES_TEXT_01 = [
    "A und B",
    "A, B und C",

    "Nicht A, aber B",
    "Finde A statt B.",

    "Finde A sonst B.",

    "Finde A und B.",
    "Vergleiche C, D und E.",
    "Sortiere F oder G.",
    "Finde A, B, C und D.",

    "Finde A, aber nicht B.",
    "Vergleiche C und D, nicht E.",
    "Sortiere F, G, H, aber kein A.",
    "Finde B oder C, aber nichts von D.",

    "Finde A und B ohne C.",
    "Vergleiche D, E und F ohne G.",
    "Sortiere H ohne A und ohne B.",

    "Finde A, aber niemals B.",
    "Vergleiche C und D, nie E.",
    "Sortiere F, G, H, aber niemals A.",

    "Finde weder A noch B.",
    "Vergleiche weder C noch D, aber E.",
    "Sortiere weder F noch G, sondern H.",

    "Vergleiche A, B und C, aber nicht D und E oder F.",
    "Finde A und B, ohne C, aber mit D oder E.",
    "Sortiere A, B, C, aber weder D noch E, und niemals F.",
    "Vergleiche A, B, C, aber nicht D, und ohne E oder F."
]

# Prompt:
# Erstelle logische Sätze mit Haupt und Nebensatz.
# Nutze dazu primär die Worte:
#     finde, vergleiche, sortiere, A, B, C, D, E, F, G, H, und, oder, nicht,
#     nichts, kein, keines, nie, niemals, ohne, weder, noch.
# ---
EXAMPLES_TEXT_02 = [
    "Finde A und B, wobei du C nicht berücksichtigst.",
    "Vergleiche D und E, dass F niemals erscheint.",
    "Sortiere G, dass kein H enthalten ist.",

    "Finde A, das nicht B ist.",
    "Vergleiche C, die weder D noch E enthalten.",
    "Sortiere F, der ohne G auskommt.",

    "Finde A, wenn B nicht vorkommt.",
    "Vergleiche C und D, falls E niemals erscheint.",
    "Sortiere F, sofern weder G noch H berücksichtigt werden.",

    "Finde A, obwohl B ausgeschlossen ist.",
    "Vergleiche C, auch wenn D und E nicht vorkommen.",
    "Sortiere F, selbst wenn G niemals berücksichtigt wird."
]

EXAMPLES_TEXT_03 = [
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine Planeten mit vergleichbarer Atmosphäre wie die Erde.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine mit einer der Erde vergleichbaren Atmosphäre.",
    "Zeige mir alle Gasriesen mit Ringsystem. Oder jene, die kein Magnetfeld haben.",
    "Nicht Mars, sondern Jupiter ist ein Gasriese und kein Gesteinsplanet, weil er kein feste Oberfläche hat.",
    "Im Text steht nicht Gesteinsplanet, sondern Planeten nicht ohne fester Oberfläche.",
    "Im Text steht nicht Gesteinsplanet oder Gasriese aber Eisriese.",
    "Zeige mir keine Gesteinsplanet oder Gasriese aber Eisriese."
]

EXAMPLES_TEXT_04 = [
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine Planeten mit vergleichbarer Atmosphäre wie die Erde.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine mit einer der Erde vergleichbaren Atmosphäre.",
    "Zeige mir alle Gasriesen mit Ringsystem. Oder jene, die kein Magnetfeld haben.",
    "Nicht Mars, sondern Jupiter ist ein Gasriese und kein Gesteinsplanet, weil er kein feste Oberfläche hat.",
    "Im Text steht nicht Gesteinsplanet, sondern Planeten nicht ohne fester Oberfläche.",

    "Zeige mir alle Gasriesen mit Ringsystem, aber ohne Magnetfeld.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld.",
    "Welche Planeten haben einen Mond und Atmosphäre, aber kein Leben?",
    "Finde alle Eisriesen oder Gasplaneten, die eine rückläufige Rotation haben und keine Monde besitzen.",
    "Welche Gesteinsplaneten enthalten Wasser oder Sauerstoff, und haben eine Umlaufzeit von 300 Tagen?",
    "Liste alle Planeten mit Durchmesser grösser als 10000 km, die Stürme haben, aber kein Ringsystem und nicht vulkanisch sind.",
    "Welche Gasriesen besitzen mehr als 10 Monde und gleichzeitig einen grossen Fleck, aber keine Atmosphäre mit Methan?",
    "Nenne mir alle Planeten ausser Mars und Venus, die Atmosphäre haben, aber kein Wasser und keine Monde.",
    "Welche Gesteinsplaneten sind nicht Erde und haben keine Atmosphäre, aber eine Dichte grösser als die von Saturn?",
    "Hat der Jupiter ein Magnetfeld und Ringsystem, aber kein Leben?",
    "Vergleiche Merkur und Mars: welcher hat keine Atmosphäre, aber einen Mond?",

    "Zeige mir alle Gesteinsplaneten, die mindestens einen Mond besitzen, aber ignoriere solche ohne Sauerstoff in der Atmosphäre.",
    "Welche Planeten haben eine Umlaufzeit länger als ein Erdjahr, und welche davon besitzen mehr als 10 Monde? Bitte nenne nur die Gas- oder Eisriesen.",
    "Nenne mir den grössten Planeten, aber nur wenn er ein Magnetfeld hat. ausserdem möchte ich wissen, ob er schneller rotiert als die Erde.",
    "Welche Planeten haben eine Atmosphäre mit Methan, und welche davon besitzen ein Ringsystem? Bitte trenne Eisriesen und Gasplaneten in deiner Antwort.",
    "Zeige mir alle Planeten, die vulkanisch aktiv sind oder Hinweise auf früheres Wasser haben. Aber nenne keine, die keine Monde besitzen.",
    "Welche Planeten haben eine Umlaufzeit kürzer als 100 Tage, und welche davon haben eine extrem dünne oder gar keine Atmosphäre?",
    "Liste alle Planeten mit mehr als 50 Monden auf. Ergänze, ob sie ein auffälliges Ringsystem besitzen oder nicht.",
    "Welche Planeten haben Temperaturen, die unter -150 °C fallen können, und welche davon sind Eisriesen? Bitte nenne auch ihre Umlaufzeit.",
    "Zeige mir alle Gesteinsplaneten, die keine rückläufige Rotation haben. Vergleiche ausserdem ihre Durchmesser mit dem der Erde.",
    "Welche Planeten haben Stürme in der Atmosphäre, und welche besitzen zusätzlich ein markantes Fleck -Phänomen wie den Grossen Roten Fleck  oder den Dunklen Fleck ?",

    "Zeige mir alle Planeten mit einem Durchmesser kleiner als 10000 km, aber nur wenn sie mindestens einen Mond besitzen.",
    "Welche Gesteinsplaneten sind grösser als 6000 km im Durchmesser und haben gleichzeitig eine Atmosphäre, die nicht leer ist?",
    "Nenne die Gasplaneten, deren Durchmesser mehr als 100000 km beträgt. Ergänze bitte, wie viele Monde sie haben.",
    "Welche Planeten sind kleiner als die Erde, aber haben eine längere Umlaufzeit als 365 Tage?",
    "Liste alle Planeten mit einem Durchmesser zwischen 40000 und 60000 km auf. Unterscheide dabei, ob es sich um Eisriesen oder Gasplaneten handelt.",
    "Welche Planeten sind grösser als 12000 km, aber keine Gasriesen? Bitte nenne auch ihre Atmosphäre.",
    "Zeige mir alle Planeten, die kleiner als 5000 km sind oder keine Atmosphäre besitzen. Aber nenne keine, die mehr als 1 Mond haben.",
    "Welche Planeten haben einen Durchmesser grösser als 100000 km und gleichzeitig ein auffälliges Ringsystem?",
    "Nenne die Planeten, die kleiner als der Mars sind, aber eine Umlaufzeit kürzer als 100 Tage haben.",
    "Welche Planeten sind grösser als 50000 km, besitzen Methan in der Atmosphäre und haben mehr als 10 Monde?",
    "Liste alle Planeten auf, die kleiner als 13000 km sind, aber trotzdem mindestens einen Hinweis auf Wasser oder Leben haben.",
    "Welche Planeten sind grösser als 120000 km und haben eine geringere Dichte als Wasser?",

    "Vergleiche Mars und Venus: Welcher hat eine längere Umlaufzeit, und welcher ist grösser im Durchmesser?",
    "Zeige mir Informationen zu Jupiter und Saturn, aber nur wenn sie mehr als 50 Monde haben. Ergänze bitte, ob beide ein Ringsystem besitzen.",
    "Welche Unterschiede gibt es zwischen Merkur, Erde und Neptun in Bezug auf ihre Atmosphäre? Nenne nur die Bestandteile, die nicht bei allen vorkommen.",
    "Nenne die Gemeinsamkeiten von Uranus und Neptun, aber erwähne auch, was sie von Jupiter unterscheidet.",
    "Vergleiche Erde und Mars: Welcher hat mehr Monde, und welcher weist Hinweise auf Wasser auf?",
    "Zeige mir die Planeten Venus, Erde und Mars, aber sortiere sie nach Durchmesser. Ergänze, welcher davon eine rückläufige Rotation hat.",
    "Welche Planeten sind grösser als die Erde, aber kleiner als Jupiter? Bitte nenne nur Venus, Mars, Uranus und Neptun, falls sie in diese Kategorie fallen.",
    "Vergleiche Saturn und Jupiter: Welcher rotiert schneller, und welcher hat die geringere Dichte?",
    "Zeige mir Merkur, Venus und Mars, aber nur die, die eine Atmosphäre besitzen. Ergänze, ob sie Monde haben oder nicht.",
    "Welche Planeten - Erde, Jupiter und Saturn - haben ein Magnetfeld, und welcher davon hat das stärkste?",
]


def test_logics_01():
    examples = [
        {"text": synthetic.text, "entities": synthetic.entities}
        for text in EXAMPLES_TEXT_01
        for synthetic in [_extract_entities(_annotate_text(text))]
    ]

    # TODO:
    for example in examples:
        print(logics("de", example["text"], example["entities"]))
