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
4. Tool rechnet das theoretische Bebauungspotenzial aus und vergleicht
   es mit der Ist-Bebauung
5. Ausgabe: Strukturierter Bericht mit Status (HOCH / MITTEL / GERING /
   AUSGESCHOEPFT)

## Aktueller Funktionsumfang

- Geocoding ueber swisstopo SearchAPI
- OEREB-Datenabruf ueber Kanton Bern OEREB-Webservice
- XML-Parser fuer alle relevanten OEREB-Themen
- Drei Bemessungssysteme parallel unterstuetzt:
    - **AZ** (klassische Ausnuetzungsziffer)
    - **GFZo** (Geschossflaechenziffer oberirdisch, IVHB-konform)
    - **Hoehen + GZ** (mit oder ohne Gruenflaechenziffer)
- Spezialfall-Erkennung: Strukturgebiet (Thun), Arealbonus,
  Naturgefahren, Baulinien, Ueberlagerungen
- Drei Gemeinden hinterlegt: Stadt Bern, Stadt Thun,
  Oberhofen am Thunersee
- Regressionstest mit zehn realen Adressen via `demo.ps1`

## Beispiel-Ausgabe

```
Bauzonen-Radar - Analyse fuer: Thunstrasse 40, 3005 Bern
======================================================================
Parzelle 337 (Bern, BE)
Flaeche:  237 m^2

Nutzungszone: Wohnzone (W)
Bauklasse:    Bauklasse E, Erhaltung der best. Bebauungsstruktur

Potenzialanalyse
----------------------------------------
Verwendetes System:     GFZo
Kennzahl:               GFZo = 0.5
Theoretisch zulaessig:  118 m^2
Realisiert (geschaetzt):95 m^2 (PLATZHALTER)
Reserve:                24 m^2
Ausschoepfungsgrad:     80%
Status:                 GERING
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

**Stadt Bern:**
- Thunstrasse 40, 3005 Bern (Bauklasse E - berechnet GFZo)
- Kramgasse 1, 3000 Bern (Untere Altstadt UNESCO)
- Marktgasse 1, 3011 Bern (Obere Altstadt mit Laubenfluchtlinie)
- Junkerngasse 47, 3011 Bern (zwei Bauklassen)
- Bundesgasse 26, 3011 Bern

**Stadt Thun:**
- Hirschweg 7, 3604 Thun (Wohnen W2 mit Strukturgebiet)
- Rathausplatz 1, 3600 Thun (Bestandeszone, Uferzone, vier Naturgefahren)

**Region Bern-Mittelland und Berner Oberland:**
- Untere Stadelstrasse 1, 3653 Oberhofen (Wohnzone W1, Hoehen-System)
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
        `-- potenzial.py            Potenzialberechnung
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
