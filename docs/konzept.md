# Konzept: Bauzonen-Radar

Pflichtdokument zum Python-Abschlussprojekt.
Stand: 28. April 2026.

## Projektidee

Ein Tool, das fuer eine Schweizer Adresse automatisch das
baurechtliche Potenzial einer Parzelle ermittelt. Architekten,
Investoren und Eigentuemer sollen schnell sehen, was auf einem
Grundstueck rechtlich moeglich ist und wie viel Reserve gegenueber
der Ist-Bebauung besteht.

## Problem

Wer heute in der Schweiz wissen will, was auf einer Parzelle
gebaut werden darf, muss:

- die Parzellen-Nummer aus dem kantonalen Geoportal heraussuchen
- den OEREB-Auszug (oeffentlich-rechtliche Eigentumsbeschraenkungen)
  studieren
- das Gemeinde-Baureglement lesen
- die richtige Bauklasse oder Zone zuordnen
- die Kennzahlen (AZ, GFZo, Hoehen, Grenzabstaende) in eine
  Berechnung umsetzen

Das ist Spezialwissen. Bauzonen-Radar buendelt diese Schritte in
einer Adress-Abfrage und liefert eine sofort lesbare visuelle
Lagebeurteilung.

## Loesung

Eine Python-Pipeline, die folgendes leistet:

1. **Geocoding**: Adresse zu Koordinaten via swisstopo SearchAPI
2. **OEREB-Abfrage**: Parzellen- und Zonen-Daten via Kanton Bern
   OEREB-Webservice
3. **XML-Parsing**: Strukturierte Datenklassen fuer Parzelle,
   Restrictions, Bauklassen, Naturgefahren etc.
4. **Reglement-Matching**: Passendes Gemeinde-JSON laden, Zone
   und Bauklasse zuordnen
5. **Potenzialberechnung**: Theoretisch zulaessig vs. geschaetzt
   realisiert. Vier Lagebeurteilungen mit ASCII-Balken
6. **Bericht**: Strukturierter Textbericht mit klarer Markierung
   der Datenqualitaet, visueller Empfehlung und allen relevanten
   Hinweisen

## Drei Bemessungssysteme

Eine Besonderheit des Schweizer Baurechts: Es gibt nicht ein
einheitliches Mass, sondern mehrere parallele Systeme, die je
nach Gemeinde und Reglement-Stand greifen. Das Tool unterstuetzt
alle drei:

| System | Beschreibung | Beispiel-Gemeinde |
|---|---|---|
| **AZ** | Klassische Ausnuetzungsziffer | altes Recht, viele Gemeinden |
| **GFZo** | Geschossflaechenziffer oberirdisch | Stadt Bern, IVHB-konform |
| **Hoehen + GZ** | Steuerung ueber Gebaeudemasse + Gruenflaeche | Stadt Thun BR 2022 |
| **Hoehen** | Nur Vollgeschosse + Hoehen | Oberhofen BR 2012 |

## Datenqualitaet als zentrales Konzept

Eine wichtige Design-Entscheidung: Das Tool unterscheidet drei
Qualitaetsstufen seiner eigenen Aussagen:

### VERBINDLICH

Wenn eine direkte Kennzahl wie AZ oder GFZo vorhanden ist, wird
exakt gerechnet: `Parzellenflaeche x Kennzahl = Geschossflaeche`.
Das Ergebnis ist verbindlich und kann fuer eine erste Investitions-
Plausibilisierung verwendet werden.

### GROBSCHAETZUNG

Im Hoehen-System gibt es keine flaechen-bezogene Kennzahl. Das Tool
macht eine konservative Schaetzung anhand der Gebaeudemasse:
`Grundflaeche x Vollgeschosse + Dachgeschoss-Anteil`. Das Ergebnis
wird im Output mit einem **Banner** und der **Berechnungsbasis**
transparent ausgewiesen. Ein Plausibilitaetscheck gegen das alte
AZ-Recht (falls hinterlegt) zeigt, ob die Schaetzung im erwartbaren
Bereich liegt.

### NICHT_MOEGLICH

Wenn die Zone einem Spezialregime unterliegt (UNESCO-Altstadt,
UeO/UeP mit projektspezifischen Vorschriften, Schutzzonen) oder
weder Kennzahlen noch Hoehenwerte verfuegbar sind, verzichtet das
Tool **bewusst** auf eine Schein-Berechnung und gibt stattdessen
eine klare Empfehlung zum weiteren Vorgehen aus (z.B. "Direkter
Kontakt mit Bauverwaltung und Denkmalpflege"). Der visuelle
Empfehlungs-Block (Balken) wird in diesem Fall konsequent
weggelassen, statt Pseudo-Werte anzuzeigen.

Diese saubere Trennung der Datenqualitaet ist **rechtlich und
ethisch wichtig**: Architekten und Investoren sollen sofort sehen,
ob sie einer Zahl trauen koennen oder nur eine Orientierung
bekommen. Falsche Werte sind viel schlimmer als ein ehrliches
"kann ich nicht".

## Bauklassenplan Stadt Bern (BKP-API)

Eine Besonderheit der Stadt Bern: Die konkreten Bau-Vorschriften
pro Parzelle stehen nicht in der Bauordnung selbst, sondern
parzellenscharf im Bauklassenplan (BKP). Die Stadt Bern stellt
diesen ueber einen oeffentlichen ArcGIS REST-Service zur Verfuegung:

```
https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer
```

Das Modul `bern_bkp.py` fragt zwei Layer ab:
- **Layer 88 (BKP_Bauweise)**: Bauweise (offen/geschlossen),
  Gebaeudelaenge, Gebaeudetiefe pro Parzelle
- **Layer 95 (BKP_Grundzonen_Flaechen)**: Nutzungszone (W, WG,
  K, K(s), K(l), D, IG) und Bauklasse (BK_2 bis BK_6, BK_E,
  BK_SPEZ, OA, UA)

Die parzellenscharfen Werte (z.B. Gebaeudelaenge 70 m,
Gebaeudetiefe 13 m fuer eine konkrete Parzelle in BK_4) werden in
die Schaetz-Berechnung eingespeist und ersetzen damit die
pauschalen Default-Annahmen. Das Tool zeigt im Bericht klar an,
welcher Wert aus dem BKP stammt ("aus BKP") und welcher aus dem
Default ("aus Default").

Drei Faelle in der Stadt Bern:

| Fall | Beispiel | BKP-Bauweise | Pfad |
|---|---|---|---|
| BK 1-6 mit Bauweise | Eigerstrasse 60 (BK_4) | ja | GROBSCHAETZUNG |
| BK_E (Erhaltung) | Thunstrasse 40 | nein | VERBINDLICH (GFZo aus BO) |
| Spezialregime | Altstadt OA, BK_SPEZ (UeO) | nein | NICHT_MOEGLICH |

## Empfehlungs-Block mit visueller Lagebeurteilung

Jede Analyse mundet in einen klar markierten Empfehlungs-Block.
Dieser fasst die Auswertung in drei Ebenen zusammen:

### Drei Ebenen der Empfehlung

1. **Datenqualitaets-Banner** (oben): Sagt was die Zahlen wert sind
2. **ASCII-Fortschrittsbalken** (Mitte): Visuelle Lagebeurteilung
   in einer Sekunde erfassbar
3. **Verbale Lagebeurteilung** (unten): Was bedeutet die Zahl konkret

### Beispiel verbindliche Berechnung

```
======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [################----]  80.0%
  Bauland-Reserve: [####----------------]  20.0%

  -> GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung
======================================================================
```

### Beispiel Grobschaetzung

```
======================================================================
EMPFEHLUNG (Grobschaetzung - nur als Orientierung)
======================================================================
  Ausschoepfung:    [#########-----------]  45.8%
  Bauland-Reserve: [###########---------]  54.2%

  -> MITTLERES Verdichtungs-Potenzial - lohnt Detailpruefung (geschaetzt)
======================================================================
```

### Vier Lagebeurteilungen

Anhand der Bauland-Reserve in Prozent:

| Reserve | Lagebeurteilung |
|---|---|
| >= 60% | HOHES Verdichtungs-Potenzial - attraktive Bauland-Reserve |
| 30-60% | MITTLERES Verdichtungs-Potenzial - lohnt Detailpruefung |
| 10-30% | GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung |
| < 10% | PRAKTISCH AUSGESCHOEPFT - kein nennenswertes Verdichtungs-Potenzial |

Bei Schaetzungen wird die Lagebeurteilung mit "(geschaetzt)" markiert.

## Aufgabenverteilung

Das Projekt wird im Zweier-Team bearbeitet:

### Christophe "Matis" Jenzer
- Backend-Entwicklung (Python-Pipeline)
- OEREB-Webservice-Anbindung
- XML-Parser
- Reglement-Daten-Erfassung (Stadt Bern, Stadt Thun, Oberhofen)
- Potenzialberechnung mit Drei-System-Modell und Schaetz-Logik
- Empfehlungs-Block mit visueller Lagebeurteilung
- Spezialfall-Behandlung (Strukturgebiet, Arealbonus, Naturgefahren)

### Fabienne
- Dokumentation des gesamten Projekts
- Streamlit-Webseite fuer komfortable Adress-Abfrage (Iteration 4)
- Requirements-Engineering-Pruefung: systematische Pruefung der
  Anforderungen auf Vollstaendigkeit, Eindeutigkeit, Testbarkeit
- Identifikation impliziter Annahmen im Code
- Erstellung einer formalen Anforderungs-Spezifikation in
  `docs/anforderungen.md` (geplant)

## Werkzeuge und Hilfsmittel

### Datenkomplexitaet als Herausforderung

Das Schweizer Baurecht ist hochkomplex: drei Bemessungssysteme
parallel (AZ/GFZo/Hoehen+GZ), gemeindespezifische Reglemente,
kantonale Uebergangsphasen, Spezialregimes fuer Altstaedte und
Schutzgebiete. Eine korrekte Umsetzung erfordert exakte Werte
aus offiziellen Reglementen. Schaetzungen oder Annahmen wuerden
zu falschen Ergebnissen fuehren, die einem Architekten oder
Investor schaden wuerden.

### Einsatz von KI-Assistenten

Fuer die Erstellung dieses Projekts wurde Claude.AI (Anthropic)
als Programmier-Assistent eingesetzt. Konkret unterstuetzte Claude:

- Architektur-Entscheidungen (Drei-Systeme-Modell, Datenqualitaets-
  Stufen, Schaetz-Logik im Hoehen-System, Empfehlungs-Block)
- Code-Generierung fuer Datenklassen, Parser, Berechnungslogik
- Strukturierung der Reglement-JSONs
- Recherche und Verifikation gegen offizielle Quellen (Bauordnung
  Stadt Bern, Baureglement Stadt Thun, Baureglement Oberhofen)
- Dokumentations-Erstellung
- Bug-Diagnose und iterative Verbesserung

Die fachlichen Entscheidungen, die Verifikation der Werte gegen
die echten Reglemente und die finale Architektur lagen beim
Projektteam. Eine externe Verifikation der eingepflegten Werte
durch einen Architekten (Schwager des Projektleiters, Fachperson
in Thun) ist Teil der laufenden Iteration 3.

## Iterationen

### Iteration 1: Pipeline (abgeschlossen)
**Ziel**: Adresse rein, Parzelle und Zonen-Daten raus.

**Ergebnis**:
- swisstopo Geocoding funktioniert
- OEREB-Webservice abgerufen
- XML in strukturierte Datenklassen geparst
- 10 Test-Adressen liefern korrekte Parzellen-Daten

### Iteration 2: Potenzialberechnung (abgeschlossen)
**Ziel**: Mit Reglement-Daten echte Berechnung durchfuehren und
Datenqualitaet sauber kommunizieren.

**Ergebnis**:
- Drei Bemessungssysteme im Datenmodell verankert
- Drei Gemeinden vollstaendig hinterlegt: Bern, Thun, Oberhofen
- Erste echte GFZo-Berechnung erfolgreich (Thunstrasse 40 Bern:
  118 m^2 zulaessig, 80% Ausschoepfung, Status GERING)
- Hoehen-System mit und ohne Gruenflaechenziffer funktional
- Strukturgebiet- und Arealbonus-Erkennung implementiert
- Schaetz-Berechnung im Hoehen-System mit Datenqualitaets-Stufen
- Plausibilitaetscheck gegen altes AZ-Recht
- Klare Banner-Markierung von Schaetzungen
- Empfehlungs-Block mit ASCII-Balken zur visuellen Lagebeurteilung
- Vier Lagebeurteilungs-Stufen anhand Bauland-Reserve

### Iteration 3: Verifikation und Vervollstaendigung (laufend)
**Ziel**: Echte Werte aus dem Bauklassenplan Bern einpflegen,
Tool-Output durch Architekt-Schwager validieren lassen.

**Aufgaben**:
- Schwager liefert GFZo-Werte fuer Stadt Bern Bauklassenplan
- Erfassungs-Excel `docs/erfassung_baureglemente.xlsx` mit acht
  Tabellen ist vorbereitet
- Mit echten Werten in `bern.json` vollstaendig rechnen koennen
- Fabienne: erste Anforderungs-Liste erstellen

### Iteration 4: Webseite (geplant)
**Ziel**: Streamlit-GUI fuer Endanwender.

**Verantwortlich**: Fabienne.

**Vorgesehen**:
- Eingabefeld fuer Adresse
- Visualisierung der Parzelle (Kartenausschnitt)
- Strukturierte Ergebnisanzeige mit visueller Datenqualitaets-Ampel
  (gruen = verbindlich, orange = Schaetzung, grau = nicht moeglich)
- Empfehlungs-Block als grafische Progress-Bar (statt ASCII)
- PDF-Export fuer Kundendossier

## Bewertungskriterien (laut Kursvorgabe)

| Bereich | Punkte |
|---|---|
| Konzept-Dokument und Dokumentation | 20 |
| Python-Programm | 50 |
| Praesentation und Live-Demo | 10 |
| Fragen zum Code | 20 |
| **Total** | **100** |

## Zeitplan

- 28.04.2026 - Aufgabenverteilung mit Fabienne abgestimmt
- 28.04.2026 - Schaetz-Berechnung im Hoehen-System mit
  Datenqualitaets-Markierung implementiert
- 28.04.2026 - Empfehlungs-Block mit ASCII-Balken implementiert
- bis Mai - Iteration 3 abgeschlossen, Bern-Bauklassenplan komplett
- Mai-Juni - Iteration 4 (Webseite) durch Fabienne
- Mitte Juni - Generalprobe Live-Demo
- 17.06.2026 - Abgabe und Praesentation (5 Min Pitch + Demo +
  Code-Fragen)

## Aktueller Stand (28.04.2026)

- Pipeline End-to-End funktional
- Drei Gemeinden mit drei verschiedenen Bemessungssystemen
  abgedeckt
- Schaetz-Berechnung im Hoehen-System mit klarer Datenqualitaets-
  Markierung implementiert
- Plausibilitaetscheck gegen altes AZ-Recht funktional
- Empfehlungs-Block mit visueller Lagebeurteilung in 1 Sekunde
  erfassbar
- Code in privates GitHub-Repo eingecheckt
- Fuenf Dokumente im Repo gepflegt (README + 4 docs/)
- Zehn Test-Adressen verifiziert
- Mitstudentin Fabienne fest an Bord
