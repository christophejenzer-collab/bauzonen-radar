# Bauzonen-Radar

Ein Python-Werkzeug zur Analyse von ungenutztem Bebauungspotenzial auf Schweizer Grundstücken – mit Fokus auf den Kanton Bern.

> Abschlussprojekt im OOP-Kurs Michael Pfeuti, Feusi Bildungszentrum, Frühjahr 2026.
> Entwickelt von Christophe Jenzer und Fabienne Schmid.

---

## Worum geht es?

In der Schweiz entsteht neuer Wohn- und Gewerberaum kaum noch durch Einzonung von Landwirtschaftsland, sondern durch **Verdichtung nach innen** – also durch bessere Ausschöpfung bestehender Bauzonen. Die nötigen Daten sind öffentlich, aber auf viele Portale verteilt und nur mit Fachwissen interpretierbar.

Der Bauzonen-Radar führt diese Daten zusammen. Für eine beliebige Adresse oder Parzelle im Kanton Bern zeigt das Tool:

- die aktuelle Nutzungszone und die zulässige Ausnützung gemäss Reglement
- die realisierte Bebauung anhand offizieller Gebäudedaten
- die **Differenz** – also das ungenutzte theoretische Bebauungspotenzial
- einen Hinweis, wenn die Parzelle in einer **laufenden oder projektierten Umzonung** liegt (ÖREB-Vorwirkungen)

Bei mehreren eingegebenen Adressen erstellt das Tool eine **Rangliste** nach ungenutztem Potenzial.

## Warum ist das sinnvoll?

Das Schweizer Raumplanungsgesetz verpflichtet Kantone und Gemeinden zur Siedlungsentwicklung nach innen. Tools, die Reserven sichtbar machen, unterstützen genau dieses Ziel – für Architekturbüros, Investoren, Gemeinden oder interessierte Grundeigentümer.

## Minimalziel (verbindlich bis Kursende)

- [ ] Eingabe einer Adresse oder Parzellennummer im Kanton Bern
- [ ] Abruf der Parzelle und aktuellen Zone via ÖREB-Kataster (WFS)
- [ ] Abruf der Gebäudegrundfläche via swisstopo
- [ ] Berechnung des theoretischen Potenzials (Ausnützungsziffer)
- [ ] Ausgabe als strukturierter Textbericht
- [ ] Einfache Kartenansicht der Parzelle
- [ ] Rangliste bei mehreren Adressen

## Geplante Erweiterungen

- Integration projektierter Zonenänderungen (ÖREB-Vorwirkungen) als Hinweis-Layer
- Berücksichtigung zusätzlicher Reglement-Parameter (Grenzabstände, Gebäudehöhe)
- Erweiterung auf Kanton Zürich (Validierung der Kanton-Abstraktion)
- Integration des schweizweit harmonisierten Bauzonen-Datensatzes für Basisabdeckung
- PDF-Export des Parzellen-Dossiers

## Technischer Stack

- **Python 3.11+**
- **geopandas** / **shapely** / **pyproj** für die Geodaten-Verarbeitung
- **owslib** / **requests** für den Zugriff auf WMS/WFS-Dienste
- **folium** für interaktive Karten
- **guizero** oder **Streamlit** für die Benutzeroberfläche
- **pytest** für Tests

## Datenquellen (alle Open Government Data)

- ÖREB-Kataster Kanton Bern (WFS) – Nutzungsplanung, rechtskräftig und projektiert
- Amtliche Vermessung Kanton Bern
- swissBUILDINGS3D (swisstopo) – Gebäudegrundflächen
- Baureglemente der Gemeinden (strukturiert von Hand erfasst in `daten/baureglemente/`)
- Bauzonen Schweiz (harmonisiert) des Bundesamts für Raumentwicklung

Vollständige Liste und URLs: siehe [`docs/datenquellen.md`](docs/datenquellen.md).

## Installation

```bash
git clone https://github.com/[user]/bauzonen-radar.git
cd bauzonen-radar
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Nutzung

```bash
python -m bauzonenradar.main --adresse "Musterstrasse 42, 3000 Bern"
```

Weitere Beispiele und GUI-Start siehe [`docs/konzept.md`](docs/konzept.md).

## Projektstruktur

```
src/bauzonenradar/   Quellcode (Datenquellen, Analyse, Ausgabe, GUI)
docs/                Konzept, Datenquellen, Architektur-Entscheidungen
daten/               Statische Konfigurationen (Baureglemente je Gemeinde)
tests/               Unit-Tests
beispiele/           Beispielausgaben und Screenshots
```

## Hinweise zu den Daten

Alle verwendeten Daten stammen aus offiziellen offenen Datenquellen des Bundes und des Kantons Bern. Grosse Geodaten-Dateien (Shapefiles, GeoPackages) sind **nicht** im Repository enthalten – sie werden zur Laufzeit über WMS/WFS abgerufen oder sind lokal einmalig herunterzuladen (Anleitung in `docs/datenquellen.md`).

Die Analyse dient der **theoretischen Potenzialabschätzung**. Sie ersetzt keine rechtsverbindliche baurechtliche Abklärung durch die zuständige Gemeinde oder ein Architekturbüro.

## Lizenz

[MIT] oder [keine Lizenz – privates Projekt] – bitte vor Veröffentlichung festlegen.

## Kontakt

Bei Fragen zum Projekt: christophejenzer@icloud.com oder fabienneschmid@gmx.ch
