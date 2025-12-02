# Test

Die Überprüfung der zu sprachlicher Eingaben erstellten logischen Strukturen
erfordert eine grosse Bandbreite an Testbeispielen. Aufgrund der hohen
sprachlichen Vielfalt -- unterschiedliche Wortwahl, Ausdrucksformen,
Satzstrukturen (inklusive Satzmodi), Negationsformen, Koreferenzmuster und
Sonderdarstellungen wie Listen oder Tabellen -- sind manuell erstellte Testfälle
nicht praktikabel. Regelbasierte Testansätze sind technisch begrenzt, da sie die
Variabilität natürlicher Sprache nicht ausreichend abbilden können.

Daher wird auf __neuronale Methoden__ gesetzt. Ein Sprachmodell kann im
Gegensatz zu klassischen Verfahren automatisch Testbeispiele generieren und
dabei sowohl die sprachliche Variation als auch die logische Konsistenz
berücksichtigen.

Die Tests sind nicht auf die vollständige Semantik ausgerichtet, sondern ein
pragmatischer Ansatz zur korrekten Abbildung vereinfachter logischer Strukturen.
Ziel ist eine breite sprachliche Abdeckung bei gleichzeitiger Vermeidung von
Redundanzen und automatisierter Validierung der Resultate.

- [Bekannte Probleme](#bekannte-probleme)
- [Zielsetzung](#zielsetzung)
- [Vorgehensweise](#vorgehensweise)
- [Erweiterungen](#erweiterungen)

## Bekannte Probleme

- __Sprachliche Vielfalt__  
  Natürliche Sprache hat eine hohe Variabilität in Wortwahl, Ausdrucksformen,
  Satzstrukturen (inklusive Satzmodi), Negationsformen und Koreferenzmuster.
  Manuelle Tests und regelbasierten Verfahren können diese Vielfalt nicht
  ausreichend abdecken.

- __LLM-Faulheit / Abnehmende Variantenvielfalt (Plateau-Effekt)__  
  Sprachmodelle zeigen bei der Generierung von Testbeispielen häufig ein
  Plateau: Nach einer gewissen Anzahl von Varianten nimmt die sprachliche
  Kreativität meist ab. Statt neue Strukturen zu erzeugen, wiederholen sich
  bekannte Muster in leicht veränderter Form. Das begrenzt die Diversität der
  Testfälle, wenn das Modell ohne zusätzliche Steuerung eingesetzt wird.

- __Redundanz und Oberflächenvariation__  
  Generierte Beispiele neigen zu rein stilistischen Unterschieden, während die
  zugrunde liegende logische Struktur identisch bleibt. Für eine robuste
  Testbasis ist jedoch eine echte Variation in logischen Mustern erforderlich.

- __Komplexe Phänomene__  
  Aspekte wie Negation, Kontrast oder Koreferenz sind sprachlich vielfältig und
  schwer regelbasiert zu erfassen. Ohne gezielte Testfälle werden diese
  Phänomene nicht ausreichend abdeckt.

- __Sonderformen__  
  Nicht-lineare Darstellungsweisen wie Listen, Tabellen oder elliptische Sätze
  werden von klassischen Testansätzen oft nicht berücksichtigt, obwohl sie in
  realen Texten häufig vorkommen.

- __Validierung__
  Die manuelle Überprüfung der generierten logischen Strukturen ist wegen der
  erforderlichen Testmenge nicht praktikabel und erfordert eine automatisierte
  Validierung. Wie bei den Testbeispielen muss auch hier wegen der hohen
  Variabilität auf __neuronale Methoden__ gesetzt werden.

## Zielsetzung
- Abdeckung breiter sprachliche Vielfalt
- Abdeckung echter Variation in logischen Mustern
- Abdeckung komplexer Phänomene wie Negation, Kontrast und Koreferenz
- Abdeckung Sonderformen (Listen, Tabellen, elliptische Sätze)
- Vermeidung von Redundanzen
- Automatisiert Validierung der Ergebnisse

## Vorgehensweise
TODO:

## Erweiterungen
TODO:
