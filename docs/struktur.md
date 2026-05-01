# Projekt-Struktur

**Stand**: 30. April 2026
**Erstellt mit**: `Get-ChildItem -Recurse -File` aus PowerShell

## Visualisierung

```
bauzonen-radar/
|
+-- README.md                   Projektbeschreibung
+-- requirements.txt            Python-Abhaengigkeiten
+-- .gitignore                  Git-Ausschluesse
+-- start.ps1                   PowerShell-Helper: venv + cd ins Modul
+-- demo.ps1                    Demo-Aufrufe fuer Test-Adressen
|
+-- patch_potenzial.ps1         Patch-Skript: Bug-Fixes Vormittag 29.04.
+-- patch_begrenzer_bugs.ps1    Patch-Skript: Bug-Fixes Mittag 29.04.
+-- patch_thun_json.ps1         Patch-Skript: thun.json-Erweiterung 29.04.
|
+-- src/
|   `-- bauzonenradar/          Hauptpaket
|       +-- __init__.py
|       +-- analyse_adresse.py  Hauptprogramm: Adresse -> Bericht
|       +-- baureglement.py     Reglement-Loader (JSON pro Gemeinde)
|       +-- bern.py             OEREB-Adapter (auch fuer andere Gemeinden)
|       +-- bern_bkp.py         BKP-API Stadt Bern (parzellenscharfe Werte)
|       +-- modelle.py          Datenklassen (Parzelle, Restriction, etc.)
|       +-- xml_speichern.py    XML-Helper
|       |
|       +-- analyse/
|       |   +-- __init__.py
|       |   `-- potenzial.py    Potenzialberechnung mit drei Bemessungssystemen
|       |
|       +-- ausgabe/            (leer, Platzhalter fuer Output-Module)
|       |   `-- __init__.py
|       |
|       +-- datenquellen/       (leer, Platzhalter fuer Iteration 5)
|       |   `-- __init__.py     Hier kommt: gwr.py, parzellen_liste.py
|       |
|       `-- gui/                (leer, Platzhalter fuer Iteration 4)
|           `-- __init__.py     Hier kommt: streamlit_app.py (Fabienne)
|
+-- daten/
|   `-- baureglemente/
|       +-- bern.json
|       +-- oberhofen_am_thunersee.json
|       `-- thun.json
|
+-- docs/
|   +-- README.md (per Symlink oder im Root)
|   +-- konzept.md                       Projektkonzept
|   +-- konzept_gemeinde_analyse.md      Iteration-5-Konzept (verifiziert)
|   +-- projektplan.md                   Iteration-Roadmap
|   +-- fachliche_grundlagen.md          IVHB, Berner Systemwechsel
|   +-- journal.md                       Chronologisches Arbeitsjournal
|   `-- struktur.md                      Diese Datei
|
`-- tests/
    +-- __init__.py
    +-- test_zwoelf_adressen.ps1         Stichproben 12 Adressen
    +-- test_fuenfzig_adressen.ps1       Stresstest 50 Adressen
    `-- test_output_nach_fix.txt         Verifikations-Snapshot vom 29.04.
```

## Module im Detail

### `analyse_adresse.py`
Hauptprogramm. Eintrittspunkt fuer Einzelabfragen:
```bash
python analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"
```

### `bern.py`
Trotz des Namens ist dies der **generische OEREB-Adapter**. Holt
Parzellendaten via OEREB-Webservice fuer alle BE-Gemeinden, nicht
nur Bern. Refactoring-Kandidat fuer spaeter (z.B. nach `oereb.py`
verschieben).

### `bern_bkp.py`
Stadt-Bern-spezifischer Adapter fuer den parzellenscharfen
Bauklassenplan via ArcGIS-REST-API von `map.bern.ch`. Liefert
echte Bauweise (offen/geschlossen) und Gebaeudemasse pro Parzelle.

### `analyse/potenzial.py`
Drei-System-Berechnungslogik (AZ, GFZo, hoehen_und_gz). Drei
Datenqualitaeten (VERBINDLICH, GROBSCHAETZUNG, NICHT_MOEGLICH).
Empfehlungs-Block mit ASCII-Balken. Drei-Begrenzer-Logik
(Geometrie/Parzelle/GZ).

### `baureglement.py`
Laedt Reglement-JSON pro Gemeinde, erkennt Synonyme automatisch,
liefert Parameter fuer die Potenzialberechnung.

## Reglement-Daten

| Gemeinde | Datei | Stand | Struktur |
|---|---|---|---|
| Bern | `bern.json` | 2026-04-28 | bauklassen + nutzungszonen |
| Thun | `thun.json` | 2026-04-29 | kombiniert (kein BK) |
| Oberhofen am Thunersee | `oberhofen_am_thunersee.json` | 2026-04-27 | kombiniert |

## Test-Suiten

| Datei | Zweck | Stand |
|---|---|---|
| `test_zwoelf_adressen.ps1` | Regressions-Test mit 12 fixen Adressen | aktiv |
| `test_fuenfzig_adressen.ps1` | Stresstest mit 50 Adressen | aktiv |
| `test_output_nach_fix.txt` | Snapshot-Verifikation Bug-Fix-Welle | Verifikations-Snapshot |
| `test_zwoelf_adressen.py` | aelterer Python-Test | obsolet, durch ps1 ersetzt |

## Aufraeum-Kandidaten

Diese Dateien sind in einer fortgeschrittenen Phase weniger
relevant und koennten beim naechsten Cleanup verschwinden:

- `proof_of_concept.py` (Root) - frueher POC, Code ist in Module gewandert
- `extract_beispiel.xml` (Root) - Test-XML, ist in `.gitignore`
- `extract_koeniz.xml`, `extract_pruefen.xml`, `extract_thun.xml`
  (im Modul-Ordner) - Test-XMLs, sollten in `tests/fixtures/`
  oder ganz weg
- `test_bern_batch.py` (im Modul-Ordner) - Test-Skript, sollte in `tests/`
- `Strukturbaum-bauzonen-radar.txt` (Root) - alte Baum-Datei,
  ersetzt durch dieses Dokument

## Geplante Erweiterungen

### Iteration 4 (Streamlit-GUI mit Fabienne, Mai 2026)

Neu in `src/bauzonenradar/gui/`:
- `streamlit_app.py` - Hauptseite
- `komponenten.py` - wiederverwendbare Widgets

### Iteration 5 (Gemeinde-Analyse, Anfang Juni 2026)

Neu in `src/bauzonenradar/datenquellen/`:
- `gwr.py` - GWR-API (Ist-Werte aus garea x gastw)
- `parzellen_liste.py` - alle Parzellen einer Gemeinde

Neu auf Modul-Ebene:
- `analyse_parzelle.py` - Eintrittspunkt fuer Parzellennummer/EGRID
- `gemeinde_analyse.py` - Massen-Pipeline mit Throttling

Neu in `src/bauzonenradar/ausgabe/`:
- `excel_export.py` - Rangliste als XLSX
- `csv_export.py` - Rangliste als CSV
