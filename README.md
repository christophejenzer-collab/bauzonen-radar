# Bauzonen-Radar

> Schweizer Bauland-Analyse-Tool fuer den Kanton Bern.
> Adresse rein, Bauland-Potenzial raus.

Python-Abschlussprojekt im Rahmen der Weiterbildung.
Stand: 30. April 2026.

## Worum geht es

Architekten, Investoren und Eigentuemer wollen oft schnell wissen:
*Was darf ich auf dieser Parzelle bauen? Wie viel Reserve ist noch da?*

Bauzonen-Radar beantwortet das automatisiert:

1. Adresse eingeben (z.B. "Frutigenstrasse 25, 3604 Thun")
2. Tool holt sich Parzellen- und Zonen-Daten aus dem offiziellen
   OEREB-Webservice des Kantons Bern
3. Tool laedt das passende Gemeinde-Baureglement
4. Bei Stadt Bern: parzellenscharfe Werte aus dem Bauklassenplan (BKP)
5. Tool ruft GWR-API ab und zeigt die effektive Bestands-Bebauung
6. Tool rechnet das theoretische Bebauungspotenzial aus und
   markiert die Datenqualitaet klar
7. Ausgabe: Strukturierter Bericht mit Empfehlungs-Block,
   visuellem Balken und verbaler Lagebeurteilung

## Empfehlungs-Block (zentrale Ausgabe)

Jede Analyse mundet in einen klar markierten Empfehlungs-Block mit
ASCII-Fortschrittsbalken zur visuellen Lagebeurteilung:

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
- **>= 60%**: HOHES Verdichtungs-Potenzial (attraktive Reserve)
- **30-60%**: MITTLERES Verdichtungs-Potenzial (lohnt Detailpruefung)
- **10-30%**: GERINGES Verdichtungs-Potenzial (Bestandsoptimierung)
- **< 10%**: PRAKTISCH AUSGESCHOEPFT (kein nennenswertes Potenzial)

Bei Grobschaetzungen wird der Block deutlich gekennzeichnet
("(geschaetzt)").

## Datenqualitaet

Eine Besonderheit dieses Tools: Es unterscheidet drei klar getrennte
Qualitaetsstufen seiner Aussagen:

| Stufe | Wann | Beispiel |
|---|---|---|
| **VERBINDLICH** | AZ oder GFZo vorhanden | Stadt Bern Bauklasse E (GFZo 0.5) |
| **GROBSCHAETZUNG** | Hoehen-System | Stadt Thun BR 2022, Oberhofen |
| **NICHT_MOEGLICH** | Keine Werte verfuegbar | Zone noch nicht erfasst |

Bei einer Schaetzung wird das im Output **deutlich markiert** mit
Banner und einer Berechnungsbasis, die alle Annahmen offenlegt.
Architekten und Investoren sollen klar sehen, ob sie einer Zahl
trauen koennen.

## GWR-Integration: Soll vs. Ist

Seit dem 30. April 2026 zeigt das Tool zusaetzlich zum theoretischen
Soll-Wert auch die effektive Ist-Bebauung aus dem Eidgenoessischen
Gebaeude- und Wohnungsregister (GWR) an:

```
GWR-Daten (bestehende Bebauung):
  Frutigenstrasse 25 - EGID 1435137: 304 m^2 x 5 Geschosse = 1520 m^2 Geschossflaeche
    7 Wohnungen, Baujahr 8016
    Heizung saniert: 29.06.2021
```

Damit wird der Plausibilitaets-Konflikt zwischen unserer konservativen
Schaetzung und der gewachsenen Realitaet sichtbar - ein wichtiger
Mehrwert fuer Architekten, die einschaetzen wollen, ob eine
Verdichtung praktisch realistisch ist.

## Aktueller Funktionsumfang

- Geocoding ueber swisstopo SearchAPI
- OEREB-Datenabruf ueber Kanton Bern OEREB-Webservice
- XML-Parser fuer alle relevanten OEREB-Themen
- Drei Bemessungssysteme parallel unterstuetzt:
    - **AZ** (klassische Ausnuetzungsziffer)
    - **GFZo** (Geschossflaechenziffer oberirdisch, IVHB-konform)
    - **Hoehen + GZ** (mit oder ohne Gruenflaechenziffer)
- Schaetz-Berechnung im Hoehen-System mit konservativen Annahmen:
  Drei-Begrenzer-Logik (Geometrie / Parzelle / GZ - kleinster gewinnt)
- Bauklassenplan Stadt Bern parzellenscharf (ArcGIS REST-API)
- GWR-Integration: effektive Ist-Bebauung pro Parzelle
- Plausibilitaetscheck gegen altes AZ-Recht
- Empfehlungs-Block mit ASCII-Balken zur visuellen Lagebeurteilung
- Spezialfall-Erkennung: Strukturgebiet (Thun), Arealbonus,
  Naturgefahren, Baulinien, Ueberlagerungen
- Drei Gemeinden hinterlegt: Stadt Bern, Stadt Thun,
  Oberhofen am Thunersee
- Stresstest mit 50 realen Adressen via `tests\test_fuenfzig_adressen.ps1`
  (96% Erfolgsquote, 2.2 Min Laufzeit mit GWR)
- Regressionstest mit zwoelf Adressen via `tests\test_zwoelf_adressen.ps1`

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

- Python 3.13
- Windows mit PowerShell 7 (oder Linux/Mac mit angepassten Skripten)
- Internetverbindung (fuer swisstopo + OEREB + GWR)

### Installation

```powershell
git clone https://github.com/christophejenzer-collab/bauzonen-radar.git
cd bauzonen-radar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erste Abfrage

```powershell
.\start.ps1
python src\bauzonenradar\analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"
```

### Tests

```powershell
# Regressionstest mit zwoelf Adressen
.\tests\test_zwoelf_adressen.ps1

# Stresstest mit fuenfzig Adressen (~2-3 Minuten)
.\tests\test_fuenfzig_adressen.ps1
```

## Test-Adressen

Verifizierte Adressen, die das Tool zum Funktionieren bringen sollte:

**Stadt Bern (verbindliche GFZo-Berechnung):**
- Thunstrasse 40, 3005 Bern (Bauklasse E - GFZo 0.5, 118 m^2)
- Kramgasse 1, 3000 Bern (Untere Altstadt UNESCO)
- Marktgasse 1, 3011 Bern (Obere Altstadt mit Laubenfluchtlinie)
- Junkerngasse 47, 3011 Bern (zwei Bauklassen)
- Bundesgasse 26, 3011 Bern

**Stadt Thun (Grobschaetzung Hoehen+GZ):**
- Frutigenstrasse 25, 3604 Thun (Wohnen W3, GWR-Plausibilitaets-Konflikt)
- Hirschweg 7, 3604 Thun (Wohnen W2 mit Strukturgebiet)
- Florastrasse 5, 3600 Thun (Wohnen W3, 46% ausgeschoepft)
- Rathausplatz 1, 3600 Thun (Bestandeszone, vier Naturgefahren)

**Region Bern-Mittelland und Berner Oberland:**
- Untere Stadelstrasse 1, 3653 Oberhofen (W1, mehrere Gebaeude)
- Seestrasse 2, 3700 Spiez (kein Reglement, GWR liefert dennoch Mehrwert)

## Projektstruktur

```
bauzonen-radar/
|-- README.md                       Diese Datei
|-- requirements.txt                Python-Abhaengigkeiten
|-- start.ps1                       venv aktivieren, in Modul-Ordner wechseln
|-- demo.ps1                        Regressionstest fuer Test-Adressen
|-- patch_*.ps1                     Patch-Skripte fuer Iter 3 Bug-Fixes und Iter 5 GWR
|-- docs/
|   |-- konzept.md                          Hauptkonzept
|   |-- konzept_gemeinde_analyse.md         Iter 5 Konzept (empirisch verifiziert)
|   |-- projektplan.md                      Iterations-Roadmap
|   |-- journal.md                          Chronologisches Arbeitsjournal
|   |-- struktur.md                         Architektur-Karte
|   |-- fachliche_grundlagen.md             IVHB, Berner Systemwechsel
|   `-- archiv/                             Lokale Geschichts-Sammlung
|-- daten/baureglemente/
|   |-- bern.json
|   |-- thun.json
|   `-- oberhofen_am_thunersee.json
|-- tests/
|   |-- test_zwoelf_adressen.ps1            Regressionstest 12 Adressen
|   |-- test_fuenfzig_adressen.ps1          Stresstest 50 Adressen
|   |-- test_bern_batch.py                  Stadt-Bern-spezifische Batch-Tests
|   `-- fixtures/                           OEREB-XML-Snapshots
`-- src/bauzonenradar/
    |-- modelle.py                          Datenklassen
    |-- bern.py                             OEREB-Webservice-Anbindung
    |-- bern_bkp.py                         BKP-API Stadt Bern (parzellenscharf)
    |-- baureglement.py                     Reglement-Lade-Modul
    |-- analyse_adresse.py                  Hauptprogramm
    |-- analyse/
    |   `-- potenzial.py                    Potenzialberechnung mit Empfehlungs-Block
    |-- ausgabe/                            (Platzhalter fuer kuenftige Ausgabe-Module)
    |-- datenquellen/
    |   `-- gwr.py                          GWR-API (Eidg. Geb.- und Wohnungsregister)
    `-- gui/                                (Platzhalter fuer Streamlit Iter 4)
```

## Team

- **Christophe Jenzer** - Backend, OEREB-Pipeline, BKP-Integration,
  GWR-Modul, Reglement-Daten, Potenzialberechnung
- **Fabienne** - Dokumentation, Streamlit-Webseite (Iteration 4),
  Requirements-Engineering-Pruefung

## Datenquellen

- swisstopo SearchAPI:
  https://api3.geo.admin.ch/rest/services/api/SearchServer
- OEREB-Webservice Kanton Bern:
  https://www.oereb2.apps.be.ch/
- ArcGIS REST-API Stadt Bern Bauklassenplan:
  https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer
- GWR-API (Eidg. Gebaeude- und Wohnungsregister) ueber api3.geo.admin.ch:
  https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register
- Stadt Bern Bauordnung (BO 2006, Stand 2023):
  https://stadtrecht.bern.ch/lexoverview-home/lex-721_1
- Stadt Thun Ortsplanungsrevision:
  https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision
- Oberhofen Baureglement:
  https://www.oberhofen.ch/verwaltung/reglemente-verordnungen

## Hinweise zur Erstellung

Das Schweizer Baurecht ist hochkomplex: drei Bemessungssysteme parallel,
gemeindespezifische Reglemente, kantonale Uebergangsphasen, Spezialregimes
fuer Altstaedte und Schutzgebiete. Eine korrekte Umsetzung erfordert
exakte Werte aus offiziellen Reglementen.

Fuer die Erstellung dieses Projekts wurde Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Konkret unterstuetzte Claude bei
Architektur-Entscheidungen, Code-Generierung, Strukturierung der
Reglement-JSONs, Recherche gegen offizielle Quellen sowie der
Dokumentations-Erstellung.

Die fachlichen Entscheidungen, die Verifikation der Werte gegen die
offiziellen Reglemente und die finale Architektur lagen beim Projektteam.

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
