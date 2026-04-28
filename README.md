# Bauzonen-Radar

> Schweizer Bauland-Analyse-Tool fuer den Kanton Bern.
> Adresse rein, Bauland-Potenzial raus.

Python-Abschlussprojekt im Rahmen der Weiterbildung.
Stand: 28. April 2026.

## Worum geht es

Architekten, Investoren und Eigentuemer wollen oft schnell wissen:
*Was darf ich auf dieser Parzelle bauen? Wie viel Reserve ist noch da?*

Bauzonen-Radar beantwortet das automatisiert:

1. Adresse eingeben (z.B. "Hirschweg 7, 3604 Thun")
2. Tool holt sich Parzellen- und Zonen-Daten aus dem offiziellen
   OEREB-Webservice des Kantons Bern
3. Tool laedt das passende Gemeinde-Baureglement
4. Tool rechnet das theoretische Bebauungspotenzial aus und
   markiert die Datenqualitaet klar
5. Ausgabe: Strukturierter Bericht mit Empfehlungs-Block,
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

## Aktueller Funktionsumfang

- Geocoding ueber swisstopo SearchAPI
- OEREB-Datenabruf ueber Kanton Bern OEREB-Webservice
- XML-Parser fuer alle relevanten OEREB-Themen
- Drei Bemessungssysteme parallel unterstuetzt:
    - **AZ** (klassische Ausnuetzungsziffer)
    - **GFZo** (Geschossflaechenziffer oberirdisch, IVHB-konform)
    - **Hoehen + GZ** (mit oder ohne Gruenflaechenziffer)
- Schaetz-Berechnung im Hoehen-System mit konservativen Annahmen:
  Gebaeudegrundflaeche x Vollgeschosse + anteiliges Dachgeschoss
- Plausibilitaetscheck gegen altes AZ-Recht
- Empfehlungs-Block mit ASCII-Balken zur visuellen Lagebeurteilung
- Spezialfall-Erkennung: Strukturgebiet (Thun), Arealbonus,
  Naturgefahren, Baulinien, Ueberlagerungen
- Drei Gemeinden hinterlegt: Stadt Bern, Stadt Thun,
  Oberhofen am Thunersee
- Regressionstest mit zehn realen Adressen via `demo.ps1`

## Beispiel-Ausgabe (verbindliche Berechnung)

```
Bauzonen-Radar - Analyse fuer: Thunstrasse 40, 3005 Bern
======================================================================
Parzelle 337 (Bern, BE)
Flaeche:  237 m^2
Bauklasse: Bauklasse E

Potenzialanalyse - Datenqualitaet: VERBINDLICH
----------------------------------------------------------------------
Verwendetes System:     GFZo
Kennzahl:               GFZo = 0.5
Theoretisch zulaessig:  118 m^2
Realisiert (Platzhalter):95 m^2
Reserve:                24 m^2
Ausschoepfungsgrad:     80%
Status:                 GERING

======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [################----]  80.0%
  Bauland-Reserve: [####----------------]  20.0%

  -> GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung
======================================================================
```

## Beispiel-Ausgabe (Grobschaetzung)

```
Bauzonen-Radar - Analyse fuer: Florastrasse 5, 3600 Thun
======================================================================
Parzelle 248 (Thun, BE)
Flaeche:  894 m^2
Zone:     Wohnen W3

Potenzialanalyse - Datenqualitaet: GROBSCHAETZUNG
!!! Werte sind konservativ geschaetzt - keine Investitionsentscheidung darauf basieren !!!
----------------------------------------------------------------------
Verwendetes System:     hoehen_und_gz
GROBSCHAETZUNG zulaessig: ca. 780 m^2
Status:                 SCHAETZWERT - keine Investitionsentscheidung darauf basieren

======================================================================
EMPFEHLUNG (Grobschaetzung - nur als Orientierung)
======================================================================
  Ausschoepfung:    [#########-----------]  45.8%
  Bauland-Reserve: [###########---------]  54.2%

  -> MITTLERES Verdichtungs-Potenzial - lohnt Detailpruefung (geschaetzt)
======================================================================

BERECHNUNGSBASIS DER SCHAETZUNG:
  Grundflaeche-Annahme:  217 m^2 (GL 25 m x angenommene Breite 12 m)
  Vollgeschosse:         3
  Dachgeschoss-Bonus:    +60% (Schraegdach moeglich)
  = GROBSCHAETZUNG zulaessig: 780 m^2

PLAUSIBILITAETSCHECK gegen altes Recht:
  Altes BR: AZ=0.7 -> 626 m^2 erlaubt
  Schaetzung: 780 m^2 (Faktor 1.25x gegenueber altem AZ-Recht)
  Plausibel: Faktor 1.25x liegt im erwartbaren Bereich der Verdichtungs-Reform.
```

## Schnellstart

### Voraussetzungen

- Python 3.13
- Windows mit PowerShell 7 (oder Linux/Mac mit angepassten Skripten)
- Internetverbindung (fuer swisstopo + OEREB)

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
python analyse_adresse.py "Hirschweg 7, 3604 Thun"
```

### Regressionstest mit zehn Adressen

```powershell
.\demo.ps1
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
- Hirschweg 7, 3604 Thun (Wohnen W2 mit Strukturgebiet, 93% ausgeschoepft)
- Florastrasse 5, 3600 Thun (Wohnen W3, 46% ausgeschoepft)
- Rathausplatz 1, 3600 Thun (Bestandeszone, Uferzone, vier Naturgefahren)

**Region Bern-Mittelland und Berner Oberland:**
- Untere Stadelstrasse 1, 3653 Oberhofen (Wohnzone W1, Hoehen-System ohne GZ)
- Dorfstrasse 10, 3095 Spiegel (Koeniz - Reglement noch nicht hinterlegt)

## Projektstruktur

```
bauzonen-radar/
|-- README.md                       Diese Datei
|-- requirements.txt                Python-Abhaengigkeiten
|-- start.ps1                       venv aktivieren, in Modul-Ordner wechseln
|-- demo.ps1                        Regressionstest fuer alle Test-Adressen
|-- docs/                           Konzept, Plan, Journal, Recherche
|   |-- konzept.md
|   |-- projektplan.md
|   |-- journal.md
|   |-- fachliche_grundlagen.md
|   `-- erfassung_baureglemente.xlsx
|-- daten/baureglemente/            Gemeinde-spezifische Reglement-Daten
|   |-- bern.json
|   |-- thun.json
|   `-- oberhofen_am_thunersee.json
`-- src/bauzonenradar/              Python-Module
    |-- modelle.py                  Datenklassen Parzelle/Restriction/...
    |-- bern.py                     OEREB-Webservice-Anbindung Kanton Bern
    |-- baureglement.py             Reglement-Lade-Modul
    |-- analyse_adresse.py          Hauptprogramm
    `-- analyse/
        `-- potenzial.py            Potenzialberechnung mit Empfehlungs-Block
```

## Team

- **Christophe "Matis" Jenzer** - Backend, OEREB-Pipeline, Reglement-Daten,
  Potenzialberechnung
- **Fabienne** - Dokumentation, Streamlit-Webseite (Iteration 4),
  Requirements-Engineering-Pruefung

## Datenquellen

- swisstopo SearchAPI:
  https://api3.geo.admin.ch/rest/services/api/SearchServer
- OEREB-Webservice Kanton Bern:
  https://www.oereb2.apps.be.ch/
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
Externe Verifikation der Werte durch einen Architekten ist Teil der
laufenden Iteration 3.

## Lizenz und Rechtliches

Hochschul-Projekt, nicht zur kommerziellen Nutzung freigegeben. Die
Reglement-Daten sind Eigeninterpretation der oeffentlichen Reglemente
und ersetzen keine rechtsverbindliche Auskunft der zustaendigen
Bauverwaltung.

Insbesondere die Schaetz-Berechnungen im Hoehen-System sind explizit
als Grobschaetzungen markiert und duerfen nicht als Grundlage fuer
Investitions-Entscheidungen verwendet werden.
