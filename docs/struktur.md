# Projekt-Struktur

**Stand**: 30. April 2026 (abends)
**Erstellt mit**: `Get-ChildItem -Recurse -File` aus PowerShell

## Visualisierung

```
bauzonen-radar/
|
+-- README.md                   Projektbeschreibung
+-- requirements.txt            Python-Abhaengigkeiten
+-- .gitignore                  Git-Ausschluesse mit fixtures-Whitelist
+-- start.ps1                   PowerShell-Helper: venv + cd ins Modul
+-- demo.ps1                    Demo-Aufrufe fuer Test-Adressen
|
+-- patch_potenzial.ps1         Patch-Skript: Bug-Fixes Vormittag 29.04.
+-- patch_begrenzer_bugs.ps1    Patch-Skript: Bug-Fixes Mittag 29.04.
+-- patch_thun_json.ps1         Patch-Skript: thun.json-Erweiterung 29.04.
+-- patch_gwr_integration.ps1   Patch-Skript: GWR-Integration 30.04.
+-- patch_gwr_unvollstaendig.ps1 Patch-Skript: GWR-Anzeige verbessern 30.04.
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
|       +-- datenquellen/       Externe Datenquellen
|       |   +-- __init__.py     Exports: GwrQuelle, GwrGebaeude, Exception-Klassen
|       |   `-- gwr.py          GWR-API (Eidg. Geb.- u. Wohnungsregister) - NEU 30.04.
|       |
|       `-- gui/                (leer, Platzhalter fuer Iteration 4 Streamlit)
|           `-- __init__.py
|
+-- daten/
|   `-- baureglemente/
|       +-- bern.json
|       +-- oberhofen_am_thunersee.json
|       `-- thun.json
|
+-- docs/
|   +-- konzept.md                       Hauptkonzept
|   +-- konzept_gemeinde_analyse.md      Iteration-5-Konzept (verifiziert)
|   +-- projektplan.md                   Iteration-Roadmap
|   +-- fachliche_grundlagen.md          IVHB, Berner Systemwechsel
|   +-- journal.md                       Chronologisches Arbeitsjournal
|   +-- struktur.md                      Diese Datei
|   `-- archiv/                          LOKAL: PoC, alte Snapshots, Aufraeum-Skript
|
`-- tests/
    +-- __init__.py
    +-- test_zwoelf_adressen.ps1         Stichproben 12 Adressen
    +-- test_fuenfzig_adressen.ps1       Stresstest 50 Adressen
    +-- test_bern_batch.py               Stadt-Bern-spezifische Batch-Tests
    +-- test_output_nach_fix.txt         Verifikations-Snapshot vom 29.04.
    `-- fixtures/                        OEREB-XML-Snapshots (TRACKED via Whitelist)
        +-- README.md
        +-- extract_koeniz.xml
        +-- extract_pruefen.xml
        `-- extract_thun.xml
```

## Module im Detail

### `analyse_adresse.py`
Hauptprogramm. Eintrittspunkt fuer Einzelabfragen:
```bash
python src\bauzonenradar\analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"
```
Pipeline: OEREB -> Reglement -> [BKP fuer Bern] -> [GWR] -> Potenzialberechnung -> Bericht

### `bern.py`
Trotz des Namens ist dies der **generische OEREB-Adapter**. Holt
Parzellendaten via OEREB-Webservice fuer alle BE-Gemeinden, nicht
nur Bern. Refactoring-Kandidat fuer spaeter (z.B. nach `oereb.py`
verschieben).

### `bern_bkp.py`
Stadt-Bern-spezifischer Adapter fuer den parzellenscharfen
Bauklassenplan via ArcGIS-REST-API von `map.bern.ch`. Liefert
echte Bauweise (offen/geschlossen) und Gebaeudemasse pro Parzelle.

### `datenquellen/gwr.py` (NEU 30.04.2026)
Adapter fuer das Eidgenoessische Gebaeude- und Wohnungsregister
ueber api3.geo.admin.ch. Vollausbau ~330 Zeilen mit:
- `GwrGebaeude`-Datenklasse
- Zwei-Stufen-Workflow (SearchAPI -> MapServer)
- Caching, Retry-Logic, Throttling fuer Massen-Abfragen
- Aggregation `geschossflaeche_pro_parzelle()` fuer mehrere Gebaeude
- 3 Exception-Klassen

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
| `test_bern_batch.py` | Stadt-Bern-spezifische Batch-Tests | aktiv |
| `test_output_nach_fix.txt` | Snapshot-Verifikation Bug-Fix-Welle | Verifikations-Snapshot |
| `fixtures/extract_*.xml` | OEREB-XML-Snapshots fuer Offline-Demos | erhalten via Whitelist |

## Lokales Archiv (`docs/archiv/`)

Dieser Ordner ist via `.gitignore` aus dem Repo ausgeschlossen,
aber lokal vorhanden:

- `proof_of_concept.py` (frueher POC)
- `Strukturbaum-bauzonen-radar.txt` (alte Baum-Datei)
- `extract_beispiel.xml` (Test-XML aus fruehen Tagen)
- `test_zwoelf_adressen.py` (alte Python-Version)
- `aufraeumen_30_04_2026.ps1` (Aufraeum-Skript)
- `backup_vor_aufraeumen_*.zip` (ZIP-Sicherung des Aufraeumens)

## Geplante Erweiterungen

### Iteration 4 (Streamlit-GUI mit Fabienne, Sonntag-Coding-Tag)

Neu in `src/bauzonenradar/gui/`:
- `streamlit_app.py` - Hauptseite
- `komponenten.py` - wiederverwendbare Widgets

### Iteration 5 (Gemeinde-Analyse, Anfang Juni 2026)

**Bereits umgesetzt am 30.04.2026**:
- ✅ `datenquellen/gwr.py` - GWR-API integriert

**Noch zu tun**:
- `datenquellen/parzellen_liste.py` - alle Parzellen einer Gemeinde
- `analyse_parzelle.py` - Eintrittspunkt fuer Parzellennummer/EGRID
- `gemeinde_analyse.py` - Massen-Pipeline mit Throttling

Neu in `src/bauzonenradar/ausgabe/`:
- `excel_export.py` - Rangliste als XLSX
- `csv_export.py` - Rangliste als CSV
