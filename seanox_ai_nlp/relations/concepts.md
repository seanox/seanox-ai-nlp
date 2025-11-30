# Konzepte

## Inhalt
- [Theoretische Ansätze](#theoretische-ansätze)
  - [Allgemein](#allgemein)
    - [Grundsatz](#grundsatz)
    - [Syntaktische Konstituenten (Bausteine eines Satzes) als Cluster](
          #syntaktische-konstituenten-bausteine-eines-satzes-als-cluster)
    - [Satzgrenzen als Gültigkeitsbereiche](#satzgrenzen-als-gültigkeitsbereiche) 
    - [Negation und Kontrast](#negation-und-kontrast)
    - [Koreferenzauflösung / Coreference Resolution](
          #koreferenzauflösung--coreference-resolution)
    - [Maximales Minimum](#maximales-minimum)
  - [sprachspezifisch __`de`__](#sprachspezifisch-de)
  - [sprachspezifisch __`dk`__](#sprachspezifisch-dk)
  - [sprachspezifisch __`en`__](#sprachspezifisch-en)
  - [sprachspezifisch __`es`__](#sprachspezifisch-es)
  - [sprachspezifisch __`fr`__](#sprachspezifisch-fr)
  - [sprachspezifisch __`it`__](#sprachspezifisch-it)
  - [sprachspezifisch __`ru`__](#sprachspezifisch-ru)
- [Test](#test)
  - [Bekannte Probleme](#bekannte-probleme)
  - [Zielsetzung](#zielsetzung)
  - [Vorgehensweise](#vorgehensweise)
  - [Erweiterungen](#erweiterungen)

# Theoretische Ansätze

## Allgemein

### Grundsatz
Das Ziel ist es, von __vorgelagerten Prozessen identifizierte und kategorisierte
Entitäten__ innerhalb eines Satzes über ihre expliziten sowie oberflächlich
erschliessbaren logischen Beziehungen zu gruppieren, sodass sie als logische
Einheiten für einen __groben Vorfilter im Retrieval__ (z.B. für Embeddings)
dienen. Entitäten werden dabei weiterhin als __kategorisierte Meta-Information__
behandelt -- vergleichbar mit Keywords. Das Ergebnis ist ein __robuster
Kandidatensatz__, der die nachgelagerte Verarbeitung unterstützt, __ohne den
Anspruch, die vollständige Satzsemantik abzubilden__.

Der grundlegende Ansatz beruht auf der Einsicht, dass __natürliche Sprache__ zu
komplex ist, um sie vollständig und regelbasiert zu erfassen. Deshalb liegt der
Fokus konsequent auf den __Entitäten__ selbst. Ziel ist es, die __einfachste,
gröbste und zugleich flachste Form der logischen Abbildung__ zu finden: Statt
die gesamte sprachliche Komplexität nachzubilden, wird die __elementare logische
Grundaussage__ extrahiert, um nachgelagerten Prozessen als stabile Grundlage mit
bewusst reduzierter Komplexität zu dienen.

### Syntaktische Konstituenten (Bausteine eines Satzes) als Cluster
__Primär bilden alle Wörter eines Textes ein gemeinsames Cluster.__ Enthält der
Text mehrere Satzfragmente, können zusätzliche Cluster entstehen -- jedoch nur
dann, wenn eine __logische Trennung__ zwischen den Fragmenten erkennbar ist.  
Präpositionalphrasen (z.B. für X, zum Y) gelten als Indikatoren für den Beginn
eines neuen logischen Clusters. Konjunktionen (z.B. und, oder) sind lediglich
interne Verbindungen und bilden keine neuen Cluster.

### Satzgrenzen als Gültigkeitsbereiche
Satzgrenzen markieren den Scope, also den Bereich, in dem logische Relationen
gelten. Sie sind keine eigenen logischen Operatoren, sondern dienen als
natürliche linguistische Grenzen, innerhalb derer Cluster gebildet und
Relationen interpretiert werden.

### Negation und Kontrast
Negation und Kontraste sind besondere Formen der logischen Strukturierung, da
sie explizite oder implizite Ein- und Ausschlüsse innerhalb eines Satzes
markieren. Wörter und Phrasen wie __nicht__, __kein__, __ohne__, __aber__ oder
__sondern__ signalisieren, dass bestimmte Entitäten ausgeschlossen oder
kontrastiert werden. Diese Marker führen nicht zur Bildung eines neuen
Hauptclusters, sondern werden als synthetische Sub-Cluster innerhalb eines
bestehenden Clusters abgebildet. Auf diese Weise entsteht beispielsweise aus
__A und B, aber nicht C__ ein einzelnes Cluster, das die Einheiten __A__ und
__B__ enthält und zusätzlich ein Sub-Cluster __NOT(C)__ zur Abbildung des
Ausschlusses. Treten mehrere Negationen oder Kontraste auf, werden sie flach
innerhalb desselben Clusters gesammelt, etwa __SET(A,B,NOT(C),NOT(D))__, um
unnötig komplexe Verschachtelungen zu vermeiden und die logische Integrität auch
bei komplexeren Satzmustern zu erhalten.

### Koreferenzauflösung / Coreference Resolution
Die Koreferenzauflösung ist -- wie für natürliche Sprache typisch -- ein
komplexes Thema mit erheblicher Unsicherheit in der regelbasierten Abbildung.
Auch hier wird ein bewusst vereinfachter Ansatz verfolgt. Pronomen reflektieren
die im unmittelbar vorangehenden Satzfragment verwendeten Entitäten. Tritt ein
Pronomen innerhalb eines Nebensatzes auf, so werden alle im vorangehenden
Satzfragment genannten Entitäten als Referenz herangezogen. Befindet sich ein
Pronomen im Hauptsatz, werden die Entitäten aus dem Vorsatz reflektiert.

<details>
  <summary>
<strong>Ist die Koreferenzauflösung wirklich erforderlich?</strong>
  </summary>

Im Prinzip werden alle Entitäten vollständig als __SET__ organisiert, wobei
sowohl ganze Sätze als auch Teilsätze berücksichtigt sind. Da die finale
Struktur nur die Ebenen 0-3 nutzt -- mit Sätzen auf Ebene 0 und Teilsätzen auf
Ebene 1 -- sind die Entitäten, auf die ein Pronomen verweisen könnte, bereits in
den vorgelagerten Clustern enthalten und dort logisch eindeutig qualifiziert. Da
die Interpretation innerhalb der Struktur stets __in Verbindung mit__ erfolgt,
stellt sich die Frage, ob eine zusätzliche explizite Auflösung von Pronomen
überhaupt notwendig ist.

```
Hole Äpfel und Birnen für den Kuchen. Es können auch Konserven sein.

SET(SET(Äpfel, Birnen, Kuchen), Konserven)
```

__Antwort:__ Für den groben Vorfilter im Retrieval ist eine explizite
__Koreferenzauflösung nicht erforderlich__. Da alle Entitäten ohnehin als
__SET__ organisiert und logisch vollqualifiziert enthalten sind, werden Pronomen
automatisch __in Verbindung mit__ den vorherigen Clustern interpretiert. Eine
zusätzliche Auflösung würde nur unnötige Komplexität und Fehleranfälligkeit
einführen und widerspricht dem Prinzip der Minimalisierung und Robustheit. Falls
spätere, semantisch feinere Verarbeitung nötig ist, kann Koreferenzauflösung
dort erfolgen -- aber nicht im Vorfilter.
</details>

### Maximales Minimum
Abstrakt beschrieben geht es um die kleinste mögliche logische Repräsentation,
die stabil genug ist, um robustes Retrieval zu unterstützen, aber gleichzeitig
so minimal bleibt, dass sie die Komplexität natürlicher Sprache bewusst nicht
abzubilden versucht.

## sprachspezifisch __`de`__
TODO:

## sprachspezifisch __`dk`__
TODO:

## sprachspezifisch __`en`__
TODO:

## sprachspezifisch __`es`__
TODO:

## sprachspezifisch __`fr`__
TODO:

## sprachspezifisch __`it`__
TODO:

## sprachspezifisch __`ru`__
TODO:

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

TODO:
