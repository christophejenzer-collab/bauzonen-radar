# Bauzonen-Radar

> Schweizer Bauland-Analyse-Tool fuer den Kanton Bern.
> Adresse rein, Bauland-Potenzial raus.

Python-Abschlussprojekt im Rahmen der Weiterbildung.
Stand: 23. Mai 2026 (nach Iteration 6).
Abgabe: 12. Juni 2026 (vorzeitig, regulaer 17. Juni 2026).

📚 [Projektkonzept](docs/konzept.md) ·
[Projektplan](docs/projektplan.md) ·
[Journal](docs/journal.md) ·
[Fachliche Grundlagen](docs/fachliche_grundlagen.md) ·
[Struktur](docs/struktur.md)

---

## Worum geht es

Architekten, Investoren und Eigentuemer wollen oft schnell wissen:
*Was darf ich auf dieser Parzelle bauen? Wie viel Reserve ist noch da?*

Bauzonen-Radar beantwortet das automatisiert - in zwei Modi:

**Einzelfall-Analyse** (Adresse rein, Bericht raus):

1. Adresse eingeben (z.B. "Frutigenstrasse 25, 3604 Thun")
2. Tool holt sich Parzellen- und Zonen-Daten aus dem offiziellen
   OEREB-Webservice des Kantons Bern
3. Tool laedt das passende Gemeinde-Baureglement
4. Bei Stadt Bern: parzellenscharfe Werte aus dem Bauklassenplan (BKP)
5. Tool ruft GWR-API ab und zeigt die effektive Bestands-Bebauung
6. Tool rechnet das theoretische Bebauungspotenzial aus und
   markiert die Datenqualitaet klar
7. Ausgabe: Strukturierter Bericht mit Empfehlungs-Block,
   visuellem Balken und verbaler Lagebeurteilung (CLI oder GUI)

**Massen-Analyse** (Gemeinde rein, Excel raus):

1. Gemeinde-Name eingeben (z.B. "Thun")
2. Tool sammelt alle Parzellen ueber rekursive Praefix-Suche
3. Pro Parzelle: vollstaendige Pipeline mit Caching, Retry, Throttling
4. Klassifikation in 7+3 Kategorien (Verdichtung, Neugeschaeft,
   Ersatzneubau, Ausgereizt, Unauffaellig, Kleinparzelle, Ausschluss)
5. Excel-Export mit 6 Sheets + Karten-Direktlinks pro Parzelle

Detail-Konzept siehe [docs/konzept_gemeinde_analyse.md](docs/konzept_gemeinde_analyse.md).

## Empfehlungs-Block (zentrale Ausgabe)

Jede Einzelanalyse mundet in einen klar markierten Empfehlungs-Block
mit ASCII-Fortschrittsbalken zur visuellen Lagebeurteilung:

```
======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [################----]  80.0%
  Bauland-Reserve: [####----------------]  20.0%

  -> GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung
======================================================================
```

Vier Lagebeurteilungs-Stufen anhand der Bauland-Reserve:

* **>= 60%**: HOHES Verdichtungs-Potenzial (attraktive Reserve)
* **30-60%**: MITTLERES Verdichtungs-Potenzial (lohnt Detailpruefung)
* **10-30%**: GERINGES Verdichtungs-Potenzial (Bestandsoptimierung)
* **< 10%**: PRAKTISCH AUSGESCHOEPFT (kein nennenswertes Potenzial)

Bei Grobschaetzungen wird der Block deutlich gekennzeichnet
("(geschaetzt)").

## Datenqualitaet

Eine Besonderheit dieses Tools: Es unterscheidet drei klar getrennte
Qualitaetsstufen seiner Aussagen:

| Stufe | Wann | Beispiel |
| --- | --- | --- |
| **VERBINDLICH** | AZ oder GFZo vorhanden | Stadt Bern Bauklasse E (GFZo 0.5) |
| **GROBSCHAETZUNG** | Hoehen-System | Stadt Thun BR 2022, Oberhofen |
| **NICHT_MOEGLICH** | Keine Werte verfuegbar | Zone noch nicht erfasst |

Bei einer Schaetzung wird das im Output **deutlich markiert** mit
Banner und einer Berechnungsbasis, die alle Annahmen offenlegt.
Architekten und Investoren sollen klar sehen, ob sie einer Zahl
trauen koennen.

Fachlicher Hintergrund: siehe [docs/fachliche_grundlagen.md](docs/fachliche_grundlagen.md).

## GWR-Integration: Soll vs. Ist

Das Tool zeigt zusaetzlich zum theoretischen Soll-Wert auch die
effektive Ist-Bebauung aus dem Eidgenoessischen Gebaeude- und
Wohnungsregister (GWR) an:

```
GWR-Daten (bestehende Bebauung):
  Frutigenstrasse 25 - EGID 1435137: 304 m^2 x 5 Geschosse = 1520 m^2 Geschossflaeche
    7 Wohnungen, Baujahr 8016
    Heizung saniert: 29.06.2021
```

Damit wird der **Plausibilitaets-Konflikt** zwischen konservativer
Schaetzung und gewachsener Realitaet sichtbar - das ist der **zentrale
Indikator** des Tools (Iter-6-Erkenntnis): Architekten sehen sofort
wo Reglement und Bestand auseinanderlaufen, und genau dort lohnt
sich eine Detailpruefung.

## Aktueller Funktionsumfang

**Einzelfall-Analyse (Iter 1-4)**:

* Geocoding ueber swisstopo SearchAPI
* OEREB-Datenabruf ueber Kanton Bern OEREB-Webservice
* XML-Parser fuer alle relevanten OEREB-Themen
* Drei Bemessungssysteme parallel unterstuetzt:
  + **AZ** (klassische Ausnuetzungsziffer)
  + **GFZo** (Geschossflaechenziffer oberirdisch, IVHB-konform)
  + **Hoehen + GZ** (mit oder ohne Gruenflaechenziffer)
* Schaetz-Berechnung im Hoehen-System mit konservativen Annahmen:
  Drei-Begrenzer-Logik (Geometrie / Parzelle / GZ - kleinster gewinnt)
* Bauklassenplan Stadt Bern parzellenscharf (ArcGIS REST-API)
* GWR-Integration: effektive Ist-Bebauung pro Parzelle
* Plausibilitaets-Konflikt-Box als visuelles Highlight (Streamlit-GUI)
* Empfehlungs-Block mit ASCII-Balken zur visuellen Lagebeurteilung

**Massen-Analyse (Iter 5+6)**:

* Komplette Gemeinde in einem Durchgang analysieren
* Rekursive Praefix-Baum-Suche fuer alle Parzellen
* SQLite-Cache (Wiederaufnahme nach Abbruch moeglich)
* Throttling + Retry fuer robuste Massen-Pipeline
* Geschaeftslogische Klassifikation in 10 Kategorien:
  + **Fokus-Kategorien**: VERDICHTUNG, NEUGESCHAEFT, ERSATZNEUBAU
  + **Sekundaer**: UNAUFFAELLIG, AUSGEREIZT, KLEINPARZELLE
  + **Ausschluss**: REGLEMENT, ZU_KLEIN, VERKEHR, WALD_VERDACHT
* Bodenbedeckungs-Filter (TLM3D-Strassen + BFS-Arealstatistik)
* Excel-Export mit 6 Themen-Reitern (Statistik + Klassifikations-Sheets)
* Karten-Direktlinks pro Parzelle auf `map.geo.admin.ch`

**Erprobte Gemeinden**:

* Stadt Bern (Einzelfall - parzellenscharf via BKP)
* Stadt Thun (Einzelfall + Massen-Analyse 8534 Parzellen)
* Oberhofen am Thunersee (Einzelfall + Massen-Analyse 1176 Parzellen)

**Tests**:

* Regressionstest 12 Adressen (`tests\test_zwoelf_adressen.ps1`)
* Stresstest 50 Adressen (`tests\test_fuenfzig_adressen.ps1`) -
  96% Erfolg, 2.2 Min Laufzeit
* Pilot-Laeufe Oberhofen + Thun (jeweils 0 Fehler)

## Beispiel-Ausgabe (verbindliche Berechnung)

```
Bauzonen-Radar - Analyse fuer: Thunstrasse 40, 3005 Bern
======================================================================
Parzelle 337 (Bern, BE)
Flaeche:  237 m^2
Bauklasse: Bauklasse E

GWR-Daten (bestehende Bebauung):
  Thunstrasse 40 - EGID 1235915: 112 m^2 x 2 Geschosse = 224 m^2 Geschossflaeche
    2 Wohnungen, Baujahr 8013
    Heizung saniert: 10.12.2024

Potenzialanalyse - Datenqualitaet: VERBINDLICH
----------------------------------------------------------------------
Verwendetes System:     GFZo
Kennzahl:               GFZo = 0.5
Theoretisch zulaessig:  118 m^2
Realisiert (geschaetzt):59 m^2 (PLATZHALTER)
Reserve:                59 m^2
Ausschoepfungsgrad:     50%
Status:                 MITTEL

======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [##########----------]  50.0%
  Bauland-Reserve: [##########----------]  50.0%

  -> MITTLERES Verdichtungs-Potenzial - lohnt Detailpruefung
======================================================================
```

## Beispiel-Ausgabe (Grobschaetzung mit GWR-Plausibilitaets-Konflikt)

```
Bauzonen-Radar - Analyse fuer: Frutigenstrasse 25, 3604 Thun
======================================================================
Parzelle 324 (Thun, BE)
Flaeche:  1483 m^2
Zone:     Wohnen W3

GWR-Daten (bestehende Bebauung):
  Frutigenstrasse 25 - EGID 1435137: 304 m^2 x 5 Geschosse = 1520 m^2 Geschossflaeche
    7 Wohnungen, Baujahr 8016
    Heizung saniert: 29.06.2021

Potenzialanalyse - Datenqualitaet: GROBSCHAETZUNG
!!! Werte sind konservativ geschaetzt - keine Investitionsentscheidung darauf basieren !!!
----------------------------------------------------------------------
Verwendetes System:     hoehen_und_gz
GROBSCHAETZUNG zulaessig: ca. 1080 m^2
Status:                 SCHAETZWERT - keine Investitionsentscheidung darauf basieren

======================================================================
EMPFEHLUNG (Grobschaetzung - nur als Orientierung)
======================================================================
  Ausschoepfung:    [#######-------------]  34.3%
  Bauland-Reserve: [#############-------]  65.7%

  -> HOHES Verdichtungs-Potenzial - attraktive Bauland-Reserve (geschaetzt)
======================================================================
```

Bemerkenswert: GWR zeigt 1520 m^2 effektive Bebauung, die Schaetzung
gibt 1080 m^2 als Soll an. Das verdeutlicht den Plausibilitaets-Konflikt
und ist genau der Mehrwert, den die GWR-Integration bringt.

## Schnellstart

### Voraussetzungen

* Python 3.13
* Windows mit PowerShell 7 (oder Linux/Mac mit angepassten Skripten)
* Internetverbindung (fuer swisstopo + OEREB + GWR)

### Installation

```
git clone https://github.com/christophejenzer-collab/bauzonen-radar.git
cd bauzonen-radar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Einzelfall-Analyse

```
.\start.ps1
python src\bauzonenradar\analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"
```

### Streamlit-GUI (Einzelfall mit visueller Aufbereitung)

```
streamlit run src\bauzonenradar\gui\frontend.py
```

### Massen-Analyse (ganze Gemeinde)

```
python -m bauzonenradar.gemeinde_analyse --gemeinde "Oberhofen am Thunersee"
python -m bauzonenradar.gemeinde_analyse --gemeinde "Thun" --throttling 1.0
```

Ausgabe als Excel-Datei unter `ausgaben/bauzonen_radar_<gemeinde>_<datum>.xlsx`.

### Tests

```
# Regressionstest mit zwoelf Adressen
.\tests\test_zwoelf_adressen.ps1

# Stresstest mit fuenfzig Adressen (~2-3 Minuten)
.\tests\test_fuenfzig_adressen.ps1
```

## Test-Adressen

Verifizierte Adressen, die das Tool zum Funktionieren bringen sollte:

**Stadt Bern (verbindliche GFZo-Berechnung):**

* Thunstrasse 40, 3005 Bern (Bauklasse E - GFZo 0.5, 118 m^2)
* Kramgasse 1, 3000 Bern (Untere Altstadt UNESCO)
* Marktgasse 1, 3011 Bern (Obere Altstadt mit Laubenfluchtlinie)
* Junkerngasse 47, 3011 Bern (zwei Bauklassen)
* Bundesgasse 26, 3011 Bern

**Stadt Thun (Grobschaetzung Hoehen+GZ):**

* Frutigenstrasse 25, 3604 Thun (Wohnen W3, GWR-Plausibilitaets-Konflikt)
* Hirschweg 7, 3604 Thun (Wohnen W2 mit Strukturgebiet)
* Florastrasse 5, 3600 Thun (Wohnen W3, 46% ausgeschoepft)
* Rathausplatz 1, 3600 Thun (Bestandeszone, vier Naturgefahren)

**Region Bern-Mittelland und Berner Oberland:**

* Untere Stadelstrasse 1, 3653 Oberhofen (W1, mehrere Gebaeude)
* Seestrasse 2, 3700 Spiez (kein Reglement, GWR liefert dennoch Mehrwert)

## Projektstruktur

Vollstaendige Architektur-Karte: [docs/struktur.md](docs/struktur.md).

```
bauzonen-radar/
|-- README.md                       Diese Datei
|-- requirements.txt                Python-Abhaengigkeiten
|-- start.ps1                       venv aktivieren, in Modul-Ordner wechseln
|-- demo.ps1                        Regressionstest fuer Test-Adressen
|
|-- docs/                           Vollstaendige Projekt-Dokumentation
|   |-- konzept.md                          Hauptkonzept
|   |-- konzept_gemeinde_analyse.md         Massen-Analyse-Konzept
|   |-- projektplan.md                      Iterations-Roadmap
|   |-- journal.md                          Chronologisches Arbeitsjournal
|   |-- struktur.md                         Architektur-Karte
|   |-- fachliche_grundlagen.md             IVHB, Berner Systemwechsel, Indikator-Erkenntnis
|   |-- glossar.md                          Begriffsdefinitionen
|   |-- anforderungen_*.md                  Anforderungen Backend/Frontend
|   |-- requirements_*.md                   Technische Requirements Backend/Frontend
|   |-- releasenotes_*.md                   Releasenotes Backend/Frontend
|   |-- code_walkthrough_*.md               Code-Erklaerungen fuer Verteidigung
|   `-- archiv/                             Lokale Geschichts-Sammlung (gitignored)
|
|-- daten/baureglemente/
|   |-- bern.json
|   |-- thun.json
|   `-- oberhofen_am_thunersee.json
|
|-- tests/
|   |-- test_zwoelf_adressen.ps1            Regressionstest 12 Adressen
|   |-- test_fuenfzig_adressen.ps1          Stresstest 50 Adressen
|   |-- test_bern_batch.py                  Stadt-Bern-spezifische Batch-Tests
|   `-- fixtures/                           OEREB-XML-Snapshots fuer Offline-Demo
|
`-- src/bauzonenradar/
    |-- modelle.py                          Datenklassen
    |-- bern.py                             OEREB-Webservice-Anbindung
    |-- bern_bkp.py                         BKP-API Stadt Bern (parzellenscharf)
    |-- baureglement.py                     Reglement-Lade-Modul
    |-- analyse_adresse.py                  Einzelfall-Hauptprogramm + AnalyseErgebnis
    |-- gemeinde_analyse.py                 Massen-Analyse-Pipeline
    |-- gemeinde_cache.py                   SQLite-Cache fuer Massen-Analyse
    |-- klassifikation.py                   Klassifikations-Logik (10 Kategorien)
    |-- excel_export.py                     Excel-Export mit 6 Sheets
    |-- analyse/
    |   `-- potenzial.py                    Potenzialberechnung mit Empfehlungs-Block
    |-- datenquellen/
    |   |-- gwr.py                          GWR-API
    |   |-- parzellen_liste.py              Praefix-Baum-Suche
    |   `-- tlm3d.py                        TLM3D-Strassen + Arealstatistik
    `-- gui/
        `-- frontend.py                     Streamlit-GUI (Fabienne)
```

## Team

* **Christophe Jenzer** - Backend, OEREB-Pipeline, BKP-Integration,
  GWR-Modul, Reglement-Daten, Potenzialberechnung, Massen-Analyse-
  Pipeline (parzellen_liste, gemeinde_analyse, klassifikation,
  excel_export), Bodenbedeckungs-Filter
* **Fabienne** - Streamlit-GUI mit eigenstaendigem Design,
  Dokumentations-Architektur (Backend/Frontend-Trennung),
  Requirements-Engineering-Pruefung, Anforderungs- und
  Releasenotes-Dokumentation

## Datenquellen

* swisstopo SearchAPI:
  <https://api3.geo.admin.ch/rest/services/api/SearchServer>
* OEREB-Webservice Kanton Bern:
  <https://www.oereb2.apps.be.ch/>
* ArcGIS REST-API Stadt Bern Bauklassenplan:
  <https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer>
* GWR-API (Eidg. Gebaeude- und Wohnungsregister) ueber api3.geo.admin.ch:
  <https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register>
* swissTLM3D-Strassen + BFS-Arealstatistik (Bodenbedeckungs-Filter)
* Eidg. Kartendienst `map.geo.admin.ch` (Karten-Direktlinks)
* Stadt Bern Bauordnung (BO 2006, Stand 2023):
  <https://stadtrecht.bern.ch/lexoverview-home/lex-721_1>
* Stadt Thun Ortsplanungsrevision:
  <https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision>
* Oberhofen Baureglement:
  <https://www.oberhofen.ch/verwaltung/reglemente-verordnungen>

## Iterationen

Das Projekt wurde in sieben Iterationen entwickelt (Stand 23.05.2026):

| Iter | Thema | Stand |
|---|---|---|
| 1 | Pipeline | abgeschlossen (Maerz/April 2026) |
| 2 | Potenzialberechnung | abgeschlossen (April 2026) |
| 3 | Verifikation + Vervollstaendigung | abgeschlossen (29.04.2026) |
| 4 | Webseite (Streamlit-GUI) | abgeschlossen (11.05.2026) |
| 5 | Gemeinde-Analyse | abgeschlossen (12.05.2026) |
| 6 | Grossstadt + Konzept-Klaerung | abgeschlossen (23.05.2026) |
| 7 | Indikator-Verfeinerung + Generalprobe | geplant (Juni 2026) |

Detail siehe [docs/projektplan.md](docs/projektplan.md) und
[docs/journal.md](docs/journal.md).

## Iter-6-Konzept-Erkenntnis

Im Verlauf von Iteration 6 wurde klar: Die geometrische Soll-Berechnung
im Hoehensystem ist eine Heuristik mit bekannten Grenzen - das Reglement
gibt im Einzelfall keine eindeutige Zahl her (architekten-verifiziert:
"kein Generalrezept"). Das Tool ist daher als **faktenbasierter Indikator**
konzipiert: die GWR-Plausibilitaets-Konflikt-Box (Einzelfall) und die
Klassifikations-Kategorien (Massen-Analyse) zeigen ohne falsche Praezision,
welche Parzellen Aufmerksamkeit verdienen.

Details siehe [docs/fachliche_grundlagen.md](docs/fachliche_grundlagen.md)
(Abschnitt "Indikator-Erkenntnis aus Iteration 6").

## Hinweise zur Erstellung

Das Schweizer Baurecht ist hochkomplex: drei Bemessungssysteme parallel,
gemeindespezifische Reglemente, kantonale Uebergangsphasen, Spezialregimes
fuer Altstaedte und Schutzgebiete. Eine korrekte Umsetzung erfordert
exakte Werte aus offiziellen Reglementen.

### Hinweis zum KI-Einsatz

Fuer die Erstellung dieses Projekts wurde **Claude.AI (Anthropic)**
als Programmier-Assistent eingesetzt. Konkret unterstuetzte Claude bei:

- Architektur-Entscheidungen und Code-Generierung
- Strukturierung der Reglement-JSONs
- Recherche gegen offizielle Quellen (OEREB, GWR, swisstopo)
- Dokumentations-Erstellung (Konzept, Journal, Releasenotes)

Die **fachlichen Entscheidungen**, die **Verifikation der Werte gegen
offizielle Reglemente** und die **finale Code-Verantwortung** liegen
beim Projektteam (Christophe Jenzer, Fabienne). Eine zusaetzliche
fachliche Verifikation durch einen Architekten (Schwager von Christophe)
hat zentrale Konzept-Entscheidungen bestaetigt (siehe
[docs/fachliche_grundlagen.md](docs/fachliche_grundlagen.md)).

Dieses Vorgehen ist im Projektkonzept ([docs/konzept.md](docs/konzept.md))
und im Arbeitsjournal ([docs/journal.md](docs/journal.md)) transparent
dokumentiert.

## Lizenz und Rechtliches

Hochschul-Projekt, nicht zur kommerziellen Nutzung freigegeben. Die
Reglement-Daten sind Eigeninterpretation der oeffentlichen Reglemente
und ersetzen keine rechtsverbindliche Auskunft der zustaendigen
Bauverwaltung.

Insbesondere die Schaetz-Berechnungen im Hoehen-System sind explizit
als Grobschaetzungen markiert und duerfen nicht als Grundlage fuer
Investitions-Entscheidungen verwendet werden.

GWR-Daten sind oeffentlich, enthalten aber Bestandsangaben zu real
existierenden Gebaeuden. Sie werden nur zur Anzeige verwendet, nicht
gespeichert oder weiterverarbeitet.
