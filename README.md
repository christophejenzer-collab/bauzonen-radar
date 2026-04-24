# Bauzonen-Radar

**Analysewerkzeug für ungenutztes Bebauungspotenzial auf Schweizer Grundstücken.**

Ein Python-Tool, das für eine beliebige Adresse im Kanton Bern in Sekunden die aktuelle Nutzungsplanung, Überlagerungen, Naturgefahren und Baulinien ausliest — und unter Berücksichtigung des jeweils geltenden Bemessungssystems (AZ, GFZo oder Höhen + Grünflächenziffer) aufzeigt, wo Verdichtungspotenzial brachliegt.

> Abschlussprojekt im Python-Kurs, Frühjahr 2026.
> Entwickelt von Christophe Jenzer und [Name Teampartner:in].

---

## Inhaltsverzeichnis

1. [Motivation](#motivation)
2. [Funktionsumfang](#funktionsumfang)
3. [Der Systemwechsel im Berner Baurecht](#der-systemwechsel-im-berner-baurecht)
4. [Schnellstart](#schnellstart)
5. [Projektstruktur](#projektstruktur)
6. [Technischer Ansatz](#technischer-ansatz)
7. [Datenquellen](#datenquellen)
8. [Beispielausgabe](#beispielausgabe)
9. [Minimalziel und Roadmap](#minimalziel-und-roadmap)
10. [Entwicklung](#entwicklung)
11. [Hinweise zu Daten und Recht](#hinweise-zu-daten-und-recht)
12. [Kontakt](#kontakt)

---

## Motivation

Die Schweizer Raumplanung fordert Siedlungsentwicklung nach innen. Neueinzonungen sind politisch weitgehend blockiert, der Wert eines Grundstücks entsteht heute durch **bessere Ausschöpfung bestehender Bauzonen**: Aufstockungen, Ersatzneubauten, Umnutzungen bei Zonenänderungen.

Die dafür relevanten Daten sind **öffentlich zugänglich**, aber über viele Portale verstreut und nur mit Fachwissen interpretierbar. Der Bauzonen-Radar führt diese Daten zu einer einheitlichen, maschinenlesbaren Gesamtsicht zusammen und berücksichtigt dabei den laufenden Systemwechsel im Berner Baurecht.

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
- **Zukunfts-Layer:** Erkennung projektierter Zonenänderungen via `Lawstatus` (rechtskräftig, Änderung mit Vorwirkung, Änderung ohne Vorwirkung, laufende Verfahren).
- **Mehrsystem-Modell:** Unterstützung für die drei Bemessungssysteme des Kantons Bern:
  - Klassische Ausnützungsziffer (AZ)
  - Geschossflächenziffer oberirdisch (GFZo, IVHB-konform)
  - Steuerung über Gebäudehöhen + Grünflächenziffer (z.B. Thun BR 2022)
- **Dualitäts-Behandlung:** In Übergangsphasen (z.B. Thun seit März 2022) werden altes und neues Recht parallel berücksichtigt.
- **Robustheit gegenüber Gemeindedialekten:** Der Parser erkennt sowohl den Stadt-Bern-Stil (feine Unterscheidung in Nutzungszone und Bauklasse) als auch den im Berner Oberland verbreiteten Stil mit kombinierter Grundnutzung.
- **Automatische Warnhinweise:** Überlagerungen, Naturgefahren, Baulinien und laufende Zonenplanänderungen werden als qualitative Risikohinweise ausgegeben, auch ohne berechenbare Kennzahl.
- **Übersichtsbericht** als strukturierte Textausgabe im Terminal.

### In Entwicklung

- Integration der Ist-Bebauung via swissBUILDINGS3D
- Rangliste über mehrere Parzellen nach ungenutztem Potenzial
- Einfache grafische Oberfläche und Kartenansicht
- PDF-Export des Parzellen-Dossiers für Kundengespräche

---

## Der Systemwechsel im Berner Baurecht

Das Tool unterstützt bewusst mehrere parallele Bemessungssysteme, weil der Kanton Bern mitten in einer Rechtsreform steht.

### Kantonaler Systemwechsel

Gemäss der kantonalen **Verordnung über die Begriffe und Messweisen im Bauwesen (BMBV)** — abgeleitet aus der interkantonalen Vereinbarung **IVHB** — wurde die klassische Ausnützungsziffer im Kanton Bern durch die **Geschossflächenziffer oberirdisch (GFZo)** ersetzt.

Der Unterschied: Während die alte AZ auch unterirdische Wohnräume mitzählte, bezieht sich die GFZo nur auf Flächen oberhalb des massgebenden Terrains. In der Praxis erlaubt dies oft eine leicht höhere Nutzbarkeit, weil Untergeschosse nicht mehr das Kontingent belasten.

### Gemeinden auf unterschiedlichem Stand

Jede Berner Gemeinde muss ihre baurechtliche Grundordnung (BNO) an die BMBV anpassen. Solange die Revision nicht erfolgt ist, gilt das alte AZ-Regime gemäss BauV Art. 93–98 weiter. Das heisst: Innerhalb des gleichen Kantons stehen Gemeinden gleichzeitig auf unterschiedlichen Rechtsständen.

### Stadt Thun: Drei-Schritte weiter

Thun hat mit der Ortsplanungsrevision (BR 2022, schrittweise in Kraft ab Februar 2025) einen weiteren Schritt gemacht und in den meisten Wohnzonen **auch auf die GFZo verzichtet**. Die bauliche Dichte wird dort primär über:

- Gebäude- und Fassadenhöhen
- Grenzabstände (z.B. 6 m grosser Grenzabstand in W2 und W3)
- Grünflächenziffer (unversiegelt zu haltender Anteil)

gesteuert. Seit März 2022 gilt in Thun **Dualität**: Baugesuche werden sowohl nach altem BR 2002 als auch nach neuem BR 2022 geprüft.

### Wie das Tool damit umgeht

Jede Zone in den Baureglement-JSON-Dateien trägt ein `system`-Feld mit einem der folgenden Werte:

| System | Bedeutung |
|---|---|
| `AZ` | Klassische Ausnützungsziffer (altes Recht) |
| `GFZo` | Geschossflächenziffer oberirdisch (IVHB-konform) |
| `hoehen_und_gz` | Steuerung über Gebäudehöhen und Grünflächenziffer |
| `dualitaet` | Übergangsphase, altes und neues Recht gelten parallel |

Der `PotenzialBerechner` wählt die passende Logik automatisch und gibt das verwendete System in der Ausgabe explizit aus. Historische AZ-Werte bleiben in den JSONs als `ausnuetzungsziffer_historisch` erhalten, damit der Vergleich zwischen altem und neuem Recht möglich ist.

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
python analyse_adresse.py "Kramgasse 49, 3011 Bern"
```

Nach 3–5 Sekunden erhält man ein strukturiertes Dossier der Parzelle im Terminal, inklusive Potenzialanalyse auf Basis des für diese Zone geltenden Bemessungssystems.

### Weitere Beispiele

```bash
python analyse_adresse.py "Thunstrasse 40, 3005 Bern"
python analyse_adresse.py "Dorfstrasse 10, 3095 Spiegel"
python analyse_adresse.py "Rathausplatz 1, 3600 Thun"
```

Alternativ nur die Bauparameter-Diagnose ohne Potenzialberechnung:

```bash
python baureglement.py "Rathausplatz 1, 3600 Thun"
```

---

## Projektstruktur

```
bauzonen-radar/
├── README.md                     Diese Anleitung
├── requirements.txt              Python-Abhängigkeiten
├── .gitignore                    Versionierungs-Ausschlüsse
├── docs/                         Konzept- und Fach-Dokumentation
├── daten/
│   └── baureglemente/            Gemeindespezifische Reglement-Parameter (JSON)
│       ├── bern.json
│       └── thun.json
├── src/
│   └── bauzonenradar/
│       ├── modelle.py            Datenmodell (Parzelle, Restriction, Lawstatus)
│       ├── bern.py               Datenquelle Kanton Bern (ÖREB-Webservice)
│       ├── baureglement.py       Reglement-Lader mit Bemessungssystem-Unterstützung
│       ├── analyse_adresse.py    CLI-Hauptschnittstelle (vollständige Analyse)
│       ├── xml_speichern.py      Hilfsskript zur Analyse neuer Gemeinden
│       ├── analyse/
│       │   └── potenzial.py      Potenzialberechnung (AZ, GFZo, Höhen+GZ)
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
  ┌──────────────────────┐
  │ Baureglement-Loader  │  Bauparameter (AZ / GFZo / Höhen+GZ)
  │ (JSON-basiert)       │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Potenzialberechner   │  Systemspezifische Analyse
  └──────────┬───────────┘
             │
             ▼
  Strukturierte Ausgabe
```

### Entwurfsprinzipien

**Kantonale Abstraktion.** Die Datenquelle ist hinter einer Klasse `BernOerebQuelle` gekapselt. Eine spätere Erweiterung auf Zürich oder andere Kantone erfolgt durch analoge Klassen mit identischer Schnittstelle — der restliche Code bleibt unberührt.

**Dialekt-Robustheit.** Berner Gemeinden verwenden zwei unterschiedliche SubCode-Konventionen innerhalb des einheitlichen OEREB-Schemas. Der Parser erkennt beide Varianten über fallback-fähige Kategorisierung in der `Restriction`-Klasse.

**Bemessungssystem als explizites Konzept.** Der Systemwechsel AZ → GFZo → Höhen+GZ wird im Datenmodell explizit über die Enum-Klasse `BemessungsSystem` abgebildet. Jede Zone trägt das für sie geltende System, der Berechner wählt automatisch den passenden Algorithmus.

**Typisierte Datenmodelle.** Parzellen, Beschränkungen und Bauparameter werden als Python-Dataclasses abgebildet. Filter- und Aggregations-Methoden sind direkt am Modell verankert.

**Minimale externe Abhängigkeiten für die Kernlogik.** XML-Parsing erfolgt mit der Python-Standardbibliothek, um die Einstiegshürde niedrig zu halten. Geopandas und Folium werden nur für Kartenvisualisierung und Potenzialberechnung nachgezogen.

---

## Datenquellen

Alle verwendeten Daten sind **Open Government Data** und entsprechen den Vorgaben des Bundesgesetzes über Geoinformation (GeoIG).

| Datenquelle | Zweck | Anbieter |
|---|---|---|
| swisstopo SearchAPI | Adress-Geocoding nach LV95 | Bundesamt für Landestopografie |
| ÖREB-Webservice Kanton Bern | Grundstück- und Nutzungsplanung-Daten | Kanton Bern, Amt für Geoinformation |
| ÖREB-Schema V2.0 | Datenformat-Spezifikation | Bundesamt swisstopo |
| BMBV des Kantons Bern | Rechtsgrundlage für IVHB-konforme Begriffe | Kanton Bern |
| Baureglemente der Gemeinden | Ausnützungsziffern, GFZo, Gebäudehöhen, Grünflächenziffern | Manuell erfasst in `daten/baureglemente/` |

Die offiziellen Dienste werden zur Laufzeit abgerufen, es wird kein lokaler Datenbestand gepflegt.

---

## Beispielausgabe

### Rathausplatz 1, 3600 Thun (BR 2022, Höhen+GZ-System)

```
Parzelle 713 (Thun, BE)
EGRID:    CH600235884687
Flaeche:  3410 m^2

Grundnutzung (Bauzone):
  - Bestandeszone (76%, 2587 m^2)
  - Uferzone (24%, 823 m^2)

Ueberlagerungen:
  - SFG-Anerkennung Zonenplan 2022 Altstadt-Bälliz
  - Gefahrengebiet mit Grundwasseraufstoss

Naturgefahren:
  ! Gefahrengebiet erhebliche Gefährdung
  ! Gefahrengebiet mittlere Gefährdung
  ! Gefahrengebiet geringe Gefährdung
  ! Gefahrengebiet Restgefährdung

Baulinien:
  - bestehend, Altstadt, nationale Bedeutung

Potenzialanalyse
----------------------------------------
Parzellenflaeche:  3410 m^2
Zone(n):           Bestandeszone [hoehen_und_gz], Uferzone [hoehen_und_gz]
Status:            NICHT_BERECHENBAR

Bemerkungen:
  - In keiner der Zonen ist eine Kennzahl (AZ oder GFZo) zur Potenzialberechnung hinterlegt.
  - Zone 'Bestandeszone' [hoehen_und_gz]: Erhaltungszone. Bestehende Volumetrie ist Richtgroesse.
  - Zone 'Uferzone' [hoehen_und_gz]: Uferbereich Aare/Thunersee. Bauverbot oder sehr eingeschraenkte Bebauung.
  - Parzelle hat Ueberlagerungen (z.B. Ortsbildschutz). Theoretisches Potenzial in der Praxis stark eingeschraenkt.
  - Parzelle liegt in 4 Naturgefahrengebiet(en). Bebaubarkeit im Detail zu pruefen.
  - Baulinien auf der Parzelle - effektive Bauflaeche ist kleiner als die Gesamtflaeche.
```

Die qualitativen Bemerkungen sind genauso wertvoll wie eine harte Zahl: Sie identifizieren die relevanten Risiken und Fachthemen für eine Parzelle.

---

## Minimalziel und Roadmap

### Minimalziel (verbindlich bis Kursende)

- [x] Eingabe einer Adresse oder Parzellennummer im Kanton Bern
- [x] Abruf der Parzelle und aller ÖREB-Beschränkungen via offiziellem Webservice
- [x] Parser für alle sechs Kategorien des OEREB-Schemas V2.0
- [x] Robustheit gegenüber Gemeindedialekten (Stadt Bern, Berner Oberland)
- [x] Strukturierte Textausgabe
- [x] Baureglement-Integration für Stadt Bern und Thun
- [x] Drei-System-Modell (AZ, GFZo, Höhen+GZ) gemäss Berner Rechtsstand
- [x] Potenzialberechnung mit systemspezifischer Logik
- [x] Automatische Warnhinweise zu OEREB-Einschränkungen
- [ ] Konkrete Kennzahlen (AZ, GFZo, Höhen, GZ) pro Zone einpflegen
- [ ] Einfache grafische Oberfläche
- [ ] Rangliste mehrerer Adressen nach ungenutztem Potenzial

### Geplante Erweiterungen nach Minimalziel

- Berücksichtigung der Gebäudegrundflächen aus swissBUILDINGS3D für die Ist-Bebauung
- Erweiterung auf Kanton Zürich (Validierung der Kanton-Abstraktion)
- PDF-Export des Parzellen-Dossiers für Kundengespräche
- Kartenvisualisierung mit folium (inkl. eingebundener WMS-Overlays)
- Filter für "Parzellen mit laufenden Änderungen" über ein ganzes Gemeindegebiet
- Integration weiterer Gemeinde-Baureglemente (Köniz, Steffisburg, Münsingen)

---

## Entwicklung

### Hilfsskript zur Analyse neuer Gemeinden

Wenn eine neue Gemeinde unterstützt werden soll, hilft das mitgelieferte Diagnose-Skript, die verwendeten SubCodes zu identifizieren:

```bash
cd src/bauzonenradar
python xml_speichern.py "Eine Adresse, 1234 Ortsname" extract_test.xml
```

Anschliessend lassen sich die im XML verwendeten Kategorien untersuchen, um den Parser bei Bedarf zu erweitern.

### Baureglement-JSON pflegen

Ein neues Gemeinde-Baureglement folgt dem Schema aus `daten/baureglemente/bern.json` oder `thun.json`. Pflichtfelder:

- `gemeinde`, `bfs_nr`, `kanton`, `stand`
- `struktur`: entweder `"bauklassen"` (Stadt-Stil) oder `"kombiniert"` (Land-Stil)
- `system_default`: das typische Bemessungssystem der Gemeinde

Pro Zone sind je nach System die passenden Kennzahlen einzutragen. Unbekannte Werte bleiben `null`, das Tool meldet dann präzise, was fehlt.

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

Die Analyse dient der **theoretischen Potenzialabschätzung** auf Basis offizieller öffentlicher Datenquellen. Sie ersetzt keine rechtsverbindliche baurechtliche Abklärung durch die zuständige Gemeinde oder ein Architekturbüro. Insbesondere in der Übergangsphase des Berner Rechtssystems (Stichwort Dualität) sind die Ergebnisse als Näherung zu verstehen.

Alle verwendeten Daten sind unter den jeweiligen Open-Data-Lizenzen der Anbieter zugänglich. Der Bauzonen-Radar speichert keine Daten dauerhaft, sondern ruft die amtlichen Dienste zur Laufzeit ab. Grosse Geodaten-Dateien und XML-Auszüge aus Entwicklungsläufen werden per `.gitignore` aus der Versionierung ausgeschlossen.

---

## Kontakt

Bei Fragen zum Projekt oder für Feedback:

Christophe Jenzer
[E-Mail-Adresse einfügen]

---

_Dieses Projekt entsteht im Rahmen des Python-Kurses und verfolgt einen realen Anwendungsfall in Zusammenarbeit mit einem Architekturbüro. Die Entwicklung ist öffentlich auf GitHub dokumentiert._
