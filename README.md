# Bauzonen-Radar

**Analysewerkzeug für ungenutztes Bebauungspotenzial auf Schweizer Grundstücken.**

Ein Python-Tool, das für eine beliebige Adresse im Kanton Bern in Sekunden die aktuelle Nutzungsplanung, Überlagerungen, Naturgefahren und Baulinien ausliest — und aufzeigt, wo Verdichtungspotenzial brachliegt.

> Abschlussprojekt im Python-Kurs, Frühjahr 2026.
> Entwickelt von Christophe Jenzer und Fabienne Schmid.

---

## Inhaltsverzeichnis

1. [Motivation](#motivation)
2. [Funktionsumfang](#funktionsumfang)
3. [Schnellstart](#schnellstart)
4. [Projektstruktur](#projektstruktur)
5. [Technischer Ansatz](#technischer-ansatz)
6. [Datenquellen](#datenquellen)
7. [Beispielausgabe](#beispielausgabe)
8. [Minimalziel und Roadmap](#minimalziel-und-roadmap)
9. [Entwicklung](#entwicklung)
10. [Hinweise zu Daten und Recht](#hinweise-zu-daten-und-recht)
11. [Kontakt](#kontakt)

---

## Motivation

Die Schweizer Raumplanung fordert Siedlungsentwicklung nach innen. Neueinzonungen sind politisch weitgehend blockiert, der Wert eines Grundstücks entsteht heute durch **bessere Ausschöpfung bestehender Bauzonen**: Aufstockungen, Ersatzneubauten, Umnutzungen bei Zonenänderungen.

Die dafür relevanten Daten sind **öffentlich zugänglich**, aber über viele Portale verstreut und nur mit Fachwissen interpretierbar. Der Bauzonen-Radar führt diese Daten zu einer einheitlichen, maschinenlesbaren Gesamtsicht zusammen.

Zielgruppen sind **Architekturbüros** (für Akquise und Vorprüfung), **Gemeinden und Kantone** (für die gesetzlich vorgeschriebene Innenentwicklungs-Analyse) und **Immobilienentwickler** (für Deal-Identifikation).

---

## Funktionsumfang

### Heute verfügbar

- **Adresse → Parzelle in einem Aufruf:** Eingabe einer Adresse oder Parzellennummer im Kanton Bern, das Tool ruft Grundstückinformationen und alle ÖREB-Daten ab.
- **Strukturierte Ausgabe** aller Nutzungsplanungs-Kategorien gemäss OEREB-Schema V2.0:
  - Grundnutzung (Bauzone)
  - Nutzungszone und Bauklasse (Stadt-Bern-Dialekt)
  - Überlagerungen (Ortsbildschutz, Erhaltungszonen)
  - Sondernutzungen (Gestaltungspläne)
  - Gefahrengebiete (Hochwasser, Rutschung, Sturz)
  - Baulinien und weitere Flächen-Informationen
- **Zukunfts-Layer:** Erkennung projektierter Zonenänderungen via `Lawstatus` (rechtskräftig / Änderung mit Vorwirkung / Änderung ohne Vorwirkung / laufende Verfahren).
- **Robustheit gegenüber Gemeindedialekten:** Der Parser erkennt sowohl den Stadt-Bern-Stil (feine Unterscheidung in Nutzungszone und Bauklasse) als auch den im Berner Oberland verbreiteten Stil mit kombinierter Grundnutzung.
- **Übersichtsbericht** als strukturierte Textausgabe im Terminal.

### In Entwicklung

- Baureglement-JSON-Struktur für gemeindespezifische Ausnützungsziffern, Gebäudehöhen und Grenzabstände.
- Potenzialberechnung: theoretisch zulässige Geschossfläche vs. realisierte Bebauung.
- Rangliste über mehrere Parzellen.
- Einfache grafische Oberfläche und Kartenansicht.

---

## Schnellstart

### Voraussetzungen

- Python 3.11 oder neuer
- Git
- Internetverbindung (Tool arbeitet mit Online-Geodiensten)

### Installation

```bash
git clone https://github.com/christophejenzer-collab/bauzonen-radar.git
cd bauzonen-radar

# Virtuelle Umgebung anlegen
python -m venv .venv

# Umgebung aktivieren (Windows PowerShell)
.venv\Scripts\activate

# Umgebung aktivieren (macOS/Linux)
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Erste Abfrage

```bash
cd src/bauzonenradar
python bern.py "Kramgasse 49, 3011 Bern"
```

Nach 3–5 Sekunden erhält man ein strukturiertes Dossier der Parzelle im Terminal.

### Weitere Beispiele

```bash
python bern.py "Thunstrasse 40, 3005 Bern"
python bern.py "Dorfstrasse 10, 3095 Spiegel"
python bern.py "Rathausplatz 1, 3600 Thun"
```

---

## Projektstruktur

```
bauzonen-radar/
├── README.md                     Diese Anleitung
├── requirements.txt              Python-Abhängigkeiten
├── .gitignore                    Versionierungs-Ausschlüsse
├── docs/                         Konzept- und Architektur-Dokumentation
├── daten/
│   └── baureglemente/            Gemeindespezifische Reglement-Parameter (JSON)
├── src/
│   └── bauzonenradar/
│       ├── modelle.py            Datenmodell (Parzelle, Restriction, Lawstatus)
│       ├── bern.py               Datenquelle Kanton Bern (ÖREB-Webservice)
│       ├── xml_speichern.py      Hilfsskript zur Analyse neuer Gemeinden
│       ├── analyse/              Potenzialberechnung (in Entwicklung)
│       ├── ausgabe/              Report-Generierung (in Entwicklung)
│       ├── datenquellen/         Weitere Kantone (in Entwicklung)
│       └── gui/                  Benutzeroberfläche (in Entwicklung)
├── tests/                        Unit-Tests
└── beispiele/                    Beispielausgaben und Screenshots
```

---

## Technischer Ansatz

### Datenfluss

```
  Adresse
     │
     ▼
  ┌──────────────────────┐
  │ swisstopo SearchAPI  │  Geocoding
  └──────────┬───────────┘
             │ LV95-Koordinaten (E, N)
             ▼
  ┌──────────────────────┐
  │ ÖREB-Webservice      │  GetEGRID
  │ Kanton Bern          │  https://www.oereb2.apps.be.ch
  └──────────┬───────────┘
             │ EGRID
             ▼
  ┌──────────────────────┐
  │ ÖREB-Webservice      │  GetExtractById
  │ Kanton Bern          │
  └──────────┬───────────┘
             │ XML (ÖREB-Schema V2.0)
             ▼
  ┌──────────────────────┐
  │ Parser + Datenmodell │  Parzelle-Objekt
  └──────────┬───────────┘
             │
             ▼
  Strukturierte Ausgabe
```

### Entwurfsprinzipien

**Kantonale Abstraktion.** Die Datenquelle ist hinter einer Klasse `BernOerebQuelle` gekapselt. Eine spätere Erweiterung auf Zürich oder andere Kantone erfolgt durch analoge Klassen mit identischer Schnittstelle — der restliche Code bleibt unberührt.

**Dialekt-Robustheit.** Berner Gemeinden verwenden zwei unterschiedliche SubCode-Konventionen innerhalb des einheitlichen OEREB-Schemas. Der Parser erkennt beide Varianten über fallback-fähige Kategorisierung in der `Restriction`-Klasse.

**Typisierte Datenmodelle.** Parzellen und ihre Beschränkungen werden als Python-Dataclasses abgebildet. Filter- und Aggregations-Methoden sind direkt am Modell verankert (`parzelle.grundnutzungen()`, `parzelle.gefahrengebiete()`, `parzelle.laufende_aenderungen()`).

**Minimale externe Abhängigkeiten für die Kernlogik.** XML-Parsing erfolgt mit der Python-Standardbibliothek, um die Einstiegshürde niedrig zu halten. Geopandas und Folium werden nur für Kartenvisualisierung und Potenzialberechnung nachgezogen.

---

## Datenquellen

Alle verwendeten Daten sind **Open Government Data** und entsprechen den Vorgaben des Bundesgesetzes über Geoinformation (GeoIG).

| Datenquelle | Zweck | Anbieter |
|---|---|---|
| swisstopo SearchAPI | Adress-Geocoding nach LV95 | Bundesamt für Landestopografie |
| ÖREB-Webservice Kanton Bern | Grundstück- und Nutzungsplanung-Daten | Kanton Bern, Amt für Geoinformation |
| ÖREB-Schema V2.0 | Datenformat-Spezifikation | Bundesamt swisstopo |
| Baureglemente der Gemeinden | Ausnützungsziffern, Bauvorschriften | Manuell erfasst in `daten/baureglemente/` |

Die offiziellen Dienste werden zur Laufzeit abgerufen, es wird kein lokaler Datenbestand gepflegt.

---

## Beispielausgabe

### Rathausplatz 1, 3600 Thun

```
Parzelle 713 (Thun, BE)
EGRID:    CH600235884687
Flaeche:  3410 m^2
Adresse:  Rathausplatz 1, 3600 Thun

Grundnutzung (Bauzone):
  - Bestandeszone (76%, 2587 m^2)
  - Uferzone (24%, 823 m^2)

Ueberlagerungen:
  - SFG-Anerkennung Zonenplan 2022 Altstadt-Bälliz
  - Gefahrengebiet mit Grundwasseraufstoss

Naturgefahren:
  - ! Gefahrengebiet erhebliche Gefährdung
  - ! Gefahrengebiet mittlere Gefährdung
  - ! Gefahrengebiet geringe Gefährdung
  - ! Gefahrengebiet Restgefährdung

Baulinien:
  - bestehend
  - Altstadt
  - nationale Bedeutung

Weitere Flaechen:
  - Altstadtgebiet
  - Archäologisches Schutzgebiet

OEREB-Themen auf dieser Parzelle:
  - ch.BE.ArchaeologischesInventar (1 Eintrag)
  - ch.BE.Bauinventar (3 Einträge)
  - ch.BE.Denkmalschutzobjekte (1 Eintrag)
  - ch.BE.Gewaesserschutzbereiche (1 Eintrag)
  - ch.BE.Naturgefahren (4 Einträge)
  - ch.Gewaesserraum (1 Eintrag)
  - ch.Nutzungsplanung (13 Einträge)
```

Diese Übersicht fasst Informationen zusammen, die manuell aus mindestens sieben verschiedenen Datenquellen recherchiert werden müssten.

---

## Minimalziel und Roadmap

### Minimalziel (verbindlich bis Kursende)

- [x] Eingabe einer Adresse oder Parzellennummer im Kanton Bern
- [x] Abruf der Parzelle und aller ÖREB-Beschränkungen via offiziellem Webservice
- [x] Parser für alle sechs Kategorien des OEREB-Schemas V2.0
- [x] Robustheit gegenüber Gemeindedialekten (Stadt Bern, Berner Oberland)
- [x] Strukturierte Textausgabe
- [ ] Baureglement-Integration für mindestens zwei Gemeinden (Bern, Thun)
- [ ] Potenzialberechnung: theoretisch zulässige vs. realisierte Geschossfläche
- [ ] Einfache grafische Oberfläche (guizero oder Streamlit)
- [ ] Rangliste mehrerer Adressen nach ungenutztem Potenzial

### Geplante Erweiterungen nach Minimalziel

- Integration des schweizweit harmonisierten Bauzonen-Datensatzes des Bundesamts für Raumentwicklung für überschlägige Abdeckung der gesamten Schweiz
- Erweiterung auf Kanton Zürich (Validierung der Kanton-Abstraktion)
- PDF-Export des Parzellen-Dossiers für Kundengespräche
- Kartenvisualisierung mit folium (inkl. eingebundener WMS-Overlays)
- Filter für "Parzellen mit laufenden Änderungen" über ein ganzes Gemeindegebiet
- Berücksichtigung der Gebäudegrundflächen aus swissBUILDINGS3D für die Ist-Bebauung

---

## Entwicklung

### Hilfsskript zur Analyse neuer Gemeinden

Wenn eine neue Gemeinde unterstützt werden soll, hilft das mitgelieferte Diagnose-Skript, die verwendeten SubCodes zu identifizieren:

```bash
cd src/bauzonenradar
python xml_speichern.py "Eine Adresse, 1234 Ortsname" extract_test.xml
```

Anschliessend lassen sich die im XML verwendeten Kategorien untersuchen, um den Parser bei Bedarf zu erweitern.

### Git-Workflow

- Entwicklung erfolgt auf Feature-Branches, niemals direkt auf `main`.
- Pull Requests werden vor dem Merge von mindestens einem Teammitglied geprüft.
- Commit-Nachrichten auf Deutsch, im Imperativ, prägnant.

### Tests

Unit-Tests werden in `tests/` abgelegt und mit `pytest` ausgeführt:

```bash
pytest tests/
```

---

## Hinweise zu Daten und Recht

Die Analyse dient der **theoretischen Potenzialabschätzung** auf Basis offizieller öffentlicher Datenquellen. Sie ersetzt keine rechtsverbindliche baurechtliche Abklärung durch die zuständige Gemeinde oder ein Architekturbüro.

Alle verwendeten Daten sind unter den jeweiligen Open-Data-Lizenzen der Anbieter zugänglich. Der Bauzonen-Radar speichert keine Daten dauerhaft, sondern ruft die amtlichen Dienste zur Laufzeit ab. Grosse Geodaten-Dateien und XML-Auszüge aus Entwicklungsläufen werden per `.gitignore` aus der Versionierung ausgeschlossen.

---

## Kontakt

Bei Fragen zum Projekt oder für Feedback:

Fabienne Schmid
fabienneschmid@gmx.ch

Christophe Jenzer
christophejenzer@icloud.com

---

_Dieses Projekt entsteht im Rahmen des Python-Kurses und verfolgt einen realen Anwendungsfall in Zusammenarbeit mit einem Architekturbüro. Die Entwicklung ist öffentlich auf GitHub dokumentiert._
