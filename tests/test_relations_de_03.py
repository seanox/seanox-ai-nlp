# tests/test_relations_de_03.py

from tests.utilities import _create_entities
from seanox_ai_nlp.relations.relations import (
    relations,
    pretty_print_node,
    sentences,
    pretty_print_sentences
)


ASTRO_ENTITIES_PATTERN = [

    ("TYPE", r"(?i)\bGesteinsplanet[a-z]*\b"),
    ("TYPE", r"(?i)\bGasriese[a-z]*\b"),
    ("TYPE", r"(?i)\bEisriese[a-z]*\b"),
    ("TYPE", r"(?i)\bGasplanet[a-z]*\b"),

    ("TERM", r"(?i)\bPlanet[a-z]*\b"),
    ("TERM", r"(?i)\bAtmosphäre\b"),
    ("TERM", r"(?i)\bUmlaufzeit[a-z]*\b"),
    ("TERM", r"(?i)\bMond[a-z]*\b"),
    ("TERM", r"(?i)\bDurchmesser\b"),

    ("KEYWORD", r"(?i)\bSauerstoff\b"),
    ("KEYWORD", r"(?i)\bMagnetfeld\b"),
    ("KEYWORD", r"(?i)\bMethan\b"),
    ("KEYWORD", r"(?i)\bvulkanisch\b"),
    ("KEYWORD", r"(?i)\bWasser\b"),
    ("KEYWORD", r"(?i)\brückläufig[a-z]*\b"),
    ("KEYWORD", r"(?i)\bRotation\b"),
    ("KEYWORD", r"(?i)\bStürme\b"),
    ("KEYWORD", r"(?i)\bFleck[a-z]*\b"),
    ("KEYWORD", r"(?i)\bRingsystem[a-z]*\b"),
    ("KEYWORD", r"(?i)\bLeben\b"),
    ("KEYWORD", r"(?i)\bDichte\b"),
    ("KEYWORD", r"(?i)\bfest[a-z]*\b"),
    ("KEYWORD", r"(?i)\bOberfläche\b"),

    ("MOONS", r"(?i)\beinen\b"),
    ("MOONS", r"(?i)\bkeine\b"),
    ("MOONS", r"(?<!\d)\d{1,2}(?!\d)"),

    ("PLANET", r"(?i)\bErde\b"),
    ("PLANET", r"(?i)\bMars\b"),
    ("PLANET", r"(?i)\bVenus\b"),
    ("PLANET", r"(?i)\bJupiter\b"),
    ("PLANET", r"(?i)\bSaturn\b"),
    ("PLANET", r"(?i)\bMerkur\b"),
    ("PLANET", r"(?i)\bNeptun\b"),
    ("PLANET", r"(?i)\bUranus\b"),

    ("TURNOVER", r"(?<!\d)\d{3}(?!\d)"),

    ("DIAMETER", r"(?<!\d)\d{5,}(?!\d)"),

    ("DUMMY", r"^[A-Z](?!\w)|(?<!\w)[A-Z](?!\w)|(?<!\w)[A-Z](?!\w)")
]

EXAMPLES_TEXT_01 = [
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine Planeten mit vergleichbarer Atmosphäre wie die Erde.",
    "Zeige mir alle Gasriesen mit Ringsystem oder ohne Magnetfeld, aber keine mit einer der Erde vergleichbaren Atmosphäre.",
    "Zeige mir alle Gasriesen mit Ringsystem. Oder jene, die kein Magnetfeld haben.",
    "Nicht Mars, sondern Jupiter ist ein Gasriese und kein Gesteinsplanet, weil er kein feste Oberfläche hat.",
    "Im Text steht nicht Gesteinsplanet, sondern Planeten nicht ohne fester Oberfläche.",
    "Im Text steht nicht Gesteinsplanet oder Gasriese aber Eisriese.",
    "Zeige mir keine Gesteinsplanet oder Gasriese aber Eisriese."
]

EXAMPLES_TEXT_02 = [
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
    pass
