# Bauzonen-Radar

Ein Python-Tool zur automatisierten Analyse des Bebauungspotenzials von Schweizer Grundstuecken im Kanton Bern.

> **Status:** In aktiver Entwicklung. Erste echte Potenzialberechnung funktioniert. Pipeline End-to-End fuer Stadt Bern und Stadt Thun verifiziert.

## Inhalt

- [Was macht das Tool?](#was-macht-das-tool)
- [Datenfluss](#datenfluss)
- [Installation und Setup](#installation-und-setup)
- [Verwendung](#verwendung)
- [Aktueller Stand](#aktueller-stand)
- [Drei Bemessungssysteme](#drei-bemessungssysteme)
- [Datenquellen](#datenquellen)
- [Projektstruktur](#projektstruktur)
- [Roadmap](#roadmap)
- [Team](#team)

## Was macht das Tool?

Fuer eine beliebige Adresse im Kanton Bern liefert das Tool:

1. **Parzellen-Identifikation** via swisstopo-Geocoding
2. **OEREB-Daten** via offiziellen Webservice (Bauzonen, Naturgefahren, Baulinien, Schutzgebiete, etc.)
3. **Reglement-Match** mit gemeindespezifischen Baureglementen
4. **Potenzialberechnung** unter Beruecksichtigung von Bauklasse, Hoehenvorgaben, Strukturgebieten und Arealbonus

**Beispiel-Output (Thunstrasse 40, 3005 Bern):**
```
Parzellenflaeche:       237 m^2
Verwendetes System:     GFZo
Kennzahl:               GFZo = 0.5
Theoretisch zulaessig:  118 m^2
Realisiert (geschaetzt):95 m^2 (PLATZHALTER)
Reserve:                24 m^2
Ausschoepfungsgrad:     80%
Status:                 GERING
```

## Datenfluss

```
Adresse
   ↓
swisstopo Geocoding (LV95-Koordinaten)
   ↓
OEREB GetEGRID (Parzellen-ID)
   ↓
OEREB GetExtract (XML mit allen Bestimmungen)
   ↓
XML-Parser (modelle.py) → Parzelle-Objekt mit Restrictions
   ↓
Baureglement-Match (bern.json / thun.json)
   ↓
Potenzialberechnung (potenzial.py)
   ↓
Textbericht
```

## Installation und Setup

### Voraussetzungen
- Windows mit PowerShell 5.1+ oder Linux/macOS
- Python 3.13+
- Git

### Setup unter Windows

```powershell
git clone https://github.com/christophejenzer-collab/bauzonen-radar.git
cd bauzonen-radar
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erste Verwendung

```powershell
.\start.ps1
python analyse_adresse.py "Hirschweg 7, 3604 Thun"
```

`start.ps1` aktiviert die venv und wechselt in den Modul-Ordner.

### Vollstaendiger Demo-Lauf (10 Adressen)

```powershell
.\start.ps1
.\..\..\demo.ps1
```

## Verwendung

```powershell
python analyse_adresse.py "<Adresse>"
```

**Beispiele:**
```powershell
python analyse_adresse.py "Marktgasse 1, 3011 Bern"
python analyse_adresse.py "Rathausplatz 1, 3600 Thun"
python analyse_adresse.py "Kramgasse 49, 3011 Bern"
```

## Aktueller Stand

### Vollstaendig getestete Gemeinden
- **Stadt Bern** (BFS 351): 11 Bauklassen, 18 Nutzungszonen erfasst
- **Stadt Thun** (BFS 942): 12 Wohn-/Misch-/Spezialzonen erfasst

### Verifizierte Test-Adressen (10)

| Adresse | Besonderheit |
|---|---|
| Kramgasse 1, 3000 Bern | Untere Altstadt, UNESCO |
| Kramgasse 49, 3011 Bern | Untere Altstadt, UNESCO |
| Junkerngasse 47, 3011 Bern | Zwei Bauklassen (Altstadt + ZoeN) |
| Marktgasse 1, 3011 Bern | Obere Altstadt mit Laubenfluchtlinie |
| Bundesgasse 26, 3011 Bern | Obere Altstadt mit Planungspflicht |
| Thunstrasse 40, 3005 Bern | Bauklasse E - **berechnet** |
| Rathausplatz 1, 3600 Thun | Bestand + Ufer, 4 Naturgefahren |
| Hirschweg 7, 3604 Thun | Wohnen W2 mit Strukturgebiet |
| Dorfstrasse 10, 3095 Spiegel | Koeniz, kein Reglement (sauber) |
| Untere Sadelstrasse 1, 3653 Oberhofen | Naturgefahren-Hinweis |

## Drei Bemessungssysteme

Das Tool unterstuetzt drei Regelwerke fuer die bauliche Dichte:

### 1. AZ - Klassische Ausnuetzungsziffer
- Altes Recht (BauV Art. 93-98)
- Wenige Gemeinden im Kanton Bern verwenden noch dieses System

### 2. GFZo - Geschossflaechenziffer oberirdisch
- Neues Recht (IVHB-konform via BMBV)
- Stadt Bern: BO 2006/2023, Bauklasse E mit GFZo 0.5/0.6
- ZoeN gemaess Art. 24: FA=0.1, FB=0.6, FC=1.2

### 3. Hoehen + GZ - Hoehenbasiert mit Gruenflaechenziffer
- Stadt Thun BR 2022 ab Februar 2025
- AZ in Wohnzonen abgeschafft
- Steuerung ueber Fassadenhoehen (Fh tr/gi/Fh), Gebaeudelaenge (GL),
  Grenzabstaende (kA/gA), Gruenflaechenziffer (GZ)

## Spezialeffekte

### Strukturgebiet (Thun)
Wenn auf einer Parzelle ein "Strukturgebiet" liegt, kann der **Beirat Stadtbild
der Stadt Thun** gestalterische Vorgaben machen, die das Baureglement teilweise
aushebeln. Das Tool warnt automatisch.

### Arealbonus (Thun)
Bei Parzellen ueber 3000 m^2 oder bei Zusammenlegungen kann ein **zusaetzliches
Geschoss** bewilligt werden. Das Tool weist automatisch darauf hin.

## Datenquellen

### Webservices
- **swisstopo SearchAPI:** https://api3.geo.admin.ch/rest/services/api/SearchServer
- **OEREB-Webservice Kanton Bern:** https://www.oereb2.apps.be.ch/
- **OEREB-Schema V2.0** (Bundesstandard)

### Reglement-Quellen

**Stadt Bern:**
- Bauordnung (BO) vom 24.9.2006, Stand 28.9.2023
- Stadtrecht-Plattform: https://stadtrecht.bern.ch/lexoverview-home/lex-721_1
- PDF: https://oerebfiles.apps.be.ch/35101/5072/Bern_SSSB_721_1_Bauordnung_der_Stadt_Bern.pdf

**Stadt Thun:**
- Baureglement BR 2022/2025 (Ortsplanungsrevision OPR)
- URL: https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision

## Projektstruktur

```
C:\Tools\bauzonen-radar\
├── README.md                          (diese Datei)
├── requirements.txt                   (Python-Abhaengigkeiten)
├── .gitignore
├── start.ps1                          (venv aktivieren + Modul-Ordner)
├── demo.ps1                           (Regressionstest, 10 Adressen)
│
├── docs/
│   ├── konzept.md                     (Pflichtdokument fuer Kursabgabe)
│   ├── projektplan.md                 (8-Wochen-Plan bis 17. Juni)
│   ├── journal.md                     (Entwicklungs-Journal)
│   ├── fachliche_grundlagen.md        (Berner Baurecht-Recherche)
│   └── erfassung_baureglemente.xlsx   (Erfassungs-Excel fuer Schwager)
│
├── daten/
│   └── baureglemente/
│       ├── bern.json                  (Stadt Bern, Stand 2026-04-25)
│       └── thun.json                  (Stadt Thun, Stand 2026-04-27)
│
└── src/bauzonenradar/
    ├── __init__.py
    ├── modelle.py                     (Parzelle, Restriction, Lawstatus)
    ├── bern.py                        (BernOerebQuelle: OEREB-API)
    ├── baureglement.py                (Bauparameter, BemessungsSystem)
    ├── analyse_adresse.py             (CLI-Hauptschnittstelle)
    └── analyse/
        ├── __init__.py
        └── potenzial.py               (PotenzialBerechner)
```

## Roadmap

### Iteration 1: Pipeline End-to-End ✅
- swisstopo-Geocoding
- OEREB-Webservice
- XML-Parser
- Erste Reglement-Anbindung

### Iteration 2: Reglement-Daten ✅
- thun.json mit echten Werten aus Art. 42
- bern.json mit Bauklassen 2-6 + E
- Strukturgebiet- und Arealbonus-Erkennung
- Erste echte GFZo-Berechnung

### Iteration 3: Vervollstaendigung der Reglement-Werte (in Arbeit)
- Werte vom Schwager: Bauklassenplan Stadt Bern (GFZo pro Zone-Bauklasse)
- Variable gGA aus Art. 46 BO Bern in Code umsetzen
- Weitere Subzonen pruefen (Innere/Aeussere Neustadt)

### Iteration 4: GUI und UX
- Streamlit-GUI fuer einfache Bedienung (Mitstudentin)
- Karten-Darstellung der Parzelle
- PDF-Export fuer Kundendossiers

### Iteration 5: Erweiterung
- swissBUILDINGS3D fuer echte Ist-Bebauung (statt 40%-Platzhalter)
- Weitere Gemeinden: Koeniz, Steffisburg, Muensingen
- Rangliste mehrerer Adressen nach Reserve-Potenzial

### Iteration 6: Kanton Zuerich
- Zuerich OEREB-Webservice anbinden
- Erste Zuercher Gemeinden modellieren

## Team

- **Christophe Jenzer** ([christophejenzer-collab](https://github.com/christophejenzer-collab))
- **[Name Teampartner:in]** (Mitstudentin, Iteration 4-5)
- **[Name Schwager]** (Architekt, Reglement-Verifikation)

## Kontakt

Bei Fragen: christophejenzer@gmail.com

---

*Bauzonen-Radar - Schweizer Bauland-Analyse mit OEREB-Daten und gemeindespezifischen Baureglementen.*
