# Projekt-Struktur

**Stand**: 23. Mai 2026 (nach Iteration 6)
**Erstellt mit**: `Get-ChildItem -Recurse -File` aus PowerShell

## Visualisierung

```
bauzonen-radar/
|-- README.md                       Einstiegs-Doku, Test-Adressen, Beispiele
|-- requirements.txt                Python-Abhaengigkeiten
|-- .gitignore                      Repo-Ausschluesse
|
|-- docs/
|   |-- konzept.md                          Pflicht-Konzeptdokument
|   |-- konzept_gemeinde_analyse.md         Iter-5/6-Konzept (empirisch verifiziert)
|   |-- projektplan.md                      Iterations-Roadmap
|   |-- journal.md                          Chronologisches Arbeitsjournal
|   |-- struktur.md                         Diese Datei
|   |-- fachliche_grundlagen.md             IVHB, Berner Systemwechsel, Indikator-Erkenntnis
|   |-- glossar.md                          Begriffsdefinitionen
|   |-- start_cheatsheet.md                 Persoenliche Befehls-Sammlung
|   |-- anforderungen_backend.md            Funktionale + nicht-funktionale Anforderungen (Backend)
|   |-- anforderungen_frontend.md           Anforderungen Streamlit-GUI (Fabienne)
|   |-- requirements_backend.md             Backend-Schnittstelle fuer GUI
|   |-- requirements_frontend.md            Streamlit-GUI-Requirements (Fabienne)
|   |-- releasenotes_backend.md             Backend-Versionierung
|   |-- releasenotes_frontend.md            Frontend-Versionierung (Fabienne)
|   `-- archiv/                             LOKAL (gitignored): PoC, alte Strukturbaeume
|
|-- daten/baureglemente/
|   |-- bern.json                           Stadt Bern (BK 2-6, BK E, ZoeN, Altstadt)
|   |-- thun.json                           Stadt Thun (BR 2022, Hoehen+GZ)
|   `-- oberhofen_am_thunersee.json         Oberhofen (BR 2012/2024, Hoehen-System)
|
|-- tests/
|   |-- test_zwoelf_adressen.ps1            Regressionstest 12 Adressen
|   |-- test_fuenfzig_adressen.ps1          Stresstest 50 Adressen
|   |-- test_bern_batch.py                  Stadt-Bern-spezifische Batch-Tests
|   |-- __init__.py
|   `-- fixtures/                           OEREB-XML-Snapshots (getrackt via Whitelist)
|       |-- README.md
|       |-- extract_koeniz.xml
|       |-- pruefen.xml
|       `-- thun.xml
|
`-- src/bauzonenradar/
    |-- __init__.py
    |-- modelle.py                          Datenklassen (Parzelle, Restriction, ...)
    |-- bern.py                             OEREB-Webservice-Anbindung
    |-- bern_bkp.py                         BKP-API Stadt Bern (parzellenscharf)
    |-- baureglement.py                     Reglement-Lade-Modul
    |-- analyse_adresse.py                  Einzelfall-Hauptprogramm + AnalyseErgebnis
    |-- gemeinde_analyse.py                 Massen-Analyse-Pipeline (Iter 5)
    |-- gemeinde_cache.py                   SQLite-Cache fuer AnalyseErgebnisse (Iter 5)
    |-- klassifikation.py                   Klassifikations-Logik (Iter 5+6)
    |-- excel_export.py                     Excel-Output mit Karten-Links + Baujahr (Iter 5+6)
    |-- analyse/
    |   `-- potenzial.py                    Potenzialberechnung mit Empfehlungs-Block
    |-- datenquellen/
    |   |-- gwr.py                          GWR-API (Eidg. Geb.- und Wohnungsregister)
    |   |-- parzellen_liste.py              Praefix-Baum-Suche (Iter 5)
    |   `-- tlm3d.py                        TLM3D-Strassen + Arealstatistik (Iter 5)
    |-- ausgabe/
    |   `-- (Platzhalter fuer kuenftige Ausgabe-Module)
    `-- gui/
        `-- frontend.py                     Streamlit-GUI (Fabienne, Iter 4)
```

## Lokale, nicht-getrackte Dateien

Folgende Dateien existieren lokal, sind aber via `.gitignore` aus
dem Repo ausgeschlossen:

- `app_christophe_test.py` (lokale Frontend-Test-Datei)
- `analyse_adresse.py.bak_*` (vereinzelte Code-Backups)
- `ausgaben/` (Excel-Outputs der Massen-Analyse, gross + flutet das Repo)
- `cache/cache_*.db` (SQLite-Caches der Gemeinde-Analyse)
- `docs/archiv/` (PoC, alte Strukturbaeume, interessante Output-Snapshots)

## Module im Detail

### `analyse_adresse.py` (refactored 03.05., gefixt 11.05.)

Hauptprogramm fuer den Einzelfall-Modus. Liefert ein `AnalyseErgebnis`-
Objekt mit allen Daten der Pipeline (~40 Felder inkl. GUI-Aliase) und
trennt klar zwischen `analysiere()` (reine Logik) und
`drucke_bericht()` (CLI-Output). Damit nutzt die GUI dieselbe Logik
wie die CLI - Separation of Concerns als zentrale Architektur-
Entscheidung.

Wichtige Felder im `AnalyseErgebnis`:
- Adresse, Status, Fehler, Warnungen
- Parzelle (gemeinde, parzellen_nummer, parzellen_flaeche_m2, egrid)
- Koordinaten (LV95 und WGS84 fuer Karten)
- Reglement, BKP-, GWR-Daten
- Potenzial (datenqualitaet, zulaessig_m2, ausschoepfung_prozent, ...)
- 7 GUI-Aliase ergaenzt am 11.05. (theoretisch_zulaessig_m2 etc.)

Iter-6-Erweiterung (20.05.): `analysiere_per_egrid()` mit egrid-
Fallback fuer Massen-Analyse, wenn OEREB selber kein egrid liefert.

### `bern.py`

OEREB-Webservice-Anbindung (`oereb2.apps.be.ch`). XML-Parser fuer
GetEGRID + GetExtract. Erkennt Gefahrengebiete, Baulinien, Flaechen,
vereinfachte Grundnutzungs-Form, Spezialregimes.

### `bern_bkp.py`

ArcGIS REST-API Anbindung an `map.bern.ch/Bauklassenplan`. Liefert
parzellenscharfe Werte fuer Bauweise (Layer 88) und Grundzonen
(Layer 95) der Stadt Bern. Pure Standard-Library, keine Zusatz-
Abhaengigkeit. `Bauparameter.mit_bkp_daten()` integriert das.

### `datenquellen/gwr.py` (vorgebaut 30.04.2026)

Eidg. Gebaeude- und Wohnungsregister via swisstopo MapServer.
~330 Zeilen mit Caching, Retry, Throttling. Zwei Stufen:
- `GwrQuelle.gebaeude_zu_adresse()`: SearchAPI -> MapServer (Einzelfall)
- `gebaeude_zu_egrid()` (NEU 12.05.): MapServer-identify mit
  Punkt-Geometrie (fuer Massen-Analyse)

Iter-6-Fix (20.05.): tolerance 500 -> 100, damit in dichten Stadt-
quartieren die eigene Parzelle nicht aus dem 201-Treffer-Cap der
API herausfaellt.

### `analyse/potenzial.py`

Potenzialberechnung mit Drei-Pfad-Logik (VERBINDLICH / GROBSCHAETZUNG
/ NICHT_MOEGLICH). Drei-Begrenzer-Logik bei Schaetzungen (Geometrie /
Parzelle / GZ - kleinster gewinnt). Empfehlungs-Block mit ASCII-
Balken und vier Lagebeurteilungs-Stufen.

### `baureglement.py`

Lade-Logik fuer die Reglement-JSONs. Erkennt Synonyme von Zonen-
Namen (OEREB-Schreibweisen vs. Reglement-Schreibweisen), unterstuetzt
mehrere Bemessungssysteme pro Reglement.

### `gui/frontend.py` (Fabienne, 03.05.2026)

Streamlit-GUI ~370 Zeilen mit eigenstaendigem Design:
- Inter-Schrift, Schwarz/Rot-Akzent, ruhige Typografie
- Drei Sektionen: Lage (Karte) / Parzelle / Bebauungspotenzial / GWR
- Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz (Iter-4-Highlight)
- Defensive Programmierung mit Variant-Detection

### `gemeinde_analyse.py` (NEU 12.05.2026, Iter 5)

Massen-Analyse-Pipeline. Liest die Parzellen-Liste, ruft pro
Parzelle Cache-Check -> analysiere_per_egrid -> klassifiziere ->
Cache-Schreiben. Throttling 0.7s zwischen Live-Calls (nicht bei
Cache-Hits), Retry 3x bei API-Fehler, Progress-Logging mit ETA,
KeyboardInterrupt-sicher.

CLI-Flags: `--kanton`, `--no-cache`, `--refresh-aelter-als TAGE`,
`--limit N`, `--throttling SEK`.

### `gemeinde_cache.py` (NEU 12.05.2026, Iter 5)

SQLite-Cache fuer komplette `AnalyseErgebnisse`. Flache Felder fuer
schnelle Queries + `daten_json`-Spalte mit Pickle-Serialisierung
des vollen Objekts. Wiederaufnahme nach Abbruch klappt, Cache
ueberlebt Strg+C.

### `klassifikation.py` (NEU 12.05.2026, erweitert 23.05.)

Geschaeftslogik-Kategorien:
- VERDICHTUNG (bebaut + Reserve)
- NEUGESCHAEFT (leer + Bauland)
- ERSATZNEUBAU (alt + Reserve)
- AUSGEREIZT (Bestandsschutz)
- UNAUFFAELLIG
- **KLEINPARZELLE** (200-500 m2, neutral - NEU Iter 6)
- AUSSCHLUSS_REGLEMENT, AUSSCHLUSS_ZU_KLEIN, AUSSCHLUSS_FEHLER,
  AUSSCHLUSS_VERKEHR, AUSSCHLUSS_WALD_VERDACHT

Nutzt die ECHTE Ausschoepfung aus GWR (Ist/Soll * 100), nicht das
Backend-Platzhalter-Feld.

### `excel_export.py` (NEU 12.05.2026, erweitert 23.05.)

XLSX-Export aus dem `KantonsCache` mit 6 Sheets: Statistik,
Verdichtung, Neugeschaeft, Ersatzneubau, Ausgereizt, Alle.

Iter-6-Erweiterungen:
- Karten-Link auf `map.geo.admin.ch/?swisssearch=<EGRID>`
  (`geo.apps.be.ch` wurde vom Kanton BE zum 1.9.2025 abgeschafft)
- Reserve-% GWR-konsistent (negative Werte ehrlich gezeigt)
- Baujahr-Spalte aus `daten_json` (aeltestes Gebaeude pro Parzelle)

### `datenquellen/parzellen_liste.py` (NEU 12.05.2026, gefixt 22.05.)

Praefix-Baum-Suche ueber die swisstopo SearchAPI. Sammelt rekursiv
alle Parzellen einer Gemeinde via Praefix-Anfragen (`Oberhofen`,
dann `Oberhofen 1`, `Oberhofen 10`, ...). Deduplizierung via EGRID-
Set.

Iter-6-Fixes (20.-22.05.):
- Gemeindename-Filter (verwirft Fremdtreffer wie Thundorf bei "Thun")
- `MAX_API_CALLS` 500 -> 3000 fuer Grossstadt-Tauglichkeit

### `datenquellen/tlm3d.py` (NEU 12.05.2026, Iter 5 Bonus)

Bodenbedeckungs-Filter:
- `TlmStrassenQuelle`: Layer `ch.swisstopo.swisstlm3d-strassen`,
  offizielle TLM3D-Strassen
- `ArealstatistikQuelle`: Layer `ch.bfs.arealstatistik-bodenbedeckung`,
  NOLC04-Codes

Erkennt Strassen (4 Indikatoren noetig, konservativ) und Wald-
Verdacht ('VERDACHT' weil Arealstatistik nicht 100% verlaesslich).

## Reglement-Daten

| Gemeinde | Datei | System | Status |
|---|---|---|---|
| Stadt Bern | `bern.json` | hoehen_und_gz + GFZo + BK_E | komplett |
| Stadt Thun | `thun.json` | hoehen_und_gz + AZ-Vergleich | komplett |
| Oberhofen | `oberhofen_am_thunersee.json` | hoehen_und_gz ohne GZ | komplett |

## Test-Suiten

| Test | Datei | Zweck |
|---|---|---|
| Regression 12 Adressen | `tests/test_zwoelf_adressen.ps1` | Sicherstellen dass die bekannten Adressen weiter durchlaufen |
| Stresstest 50 Adressen | `tests/test_fuenfzig_adressen.ps1` | Massentest gegen die API (96% Erfolg) |
| Bern-Batch | `tests/test_bern_batch.py` | Stadt-Bern-spezifische Detailtests |
| Pilot Oberhofen | (Massen-Lauf) | 1176 Parzellen, 41 Min, 0 Fehler |
| Pilot Thun | (Massen-Lauf) | 8534 Parzellen, 4h30, 0 Fehler |
| OEREB-XML-Snapshots | `tests/fixtures/*.xml` | Offline-Demo-Faehigkeit |

## Lokales Archiv (`docs/archiv/`)

Per `.gitignore` ausgeschlossen, lokal vorhanden:

- `proof_of_concept.py`
- `Strukturbaum-bauzonen-radar.txt`
- `extract_beispiel.xml`
- `test_zwoelf_adressen.py` (Python-Version, ersetzt durch PowerShell)
- `output_baumgarten_thun.md` (interessante Output-Snapshots)

## Status Iteration 4 (abgeschlossen 11.05.2026)

Streamlit-GUI live, Backend-API stabil, drei Datenqualitaets-Pfade
in der GUI verifiziert, Plausibilitaets-Konflikt-Box als Pruefungs-
Highlight.

## Status Iteration 5 (abgeschlossen 12.05.2026)

Massen-Analyse-Pipeline komplett (parzellen_liste, gemeinde_analyse,
gemeinde_cache, klassifikation, excel_export). Bonus: Bodenbedeckungs-
Filter (tlm3d) + GWR-Fix per EGRID. Pilot Oberhofen erfolgreich
(1176 Parzellen, 170 hochwertige Kandidaten).

## Status Iteration 6 (abgeschlossen 23.05.2026)

Grossstadt-Tauglichkeit nachgewiesen (Thun 8534 Parzellen, 0 Fehler).
Vier Bugs gefixt (GWR-tolerance, EGRID-Fallback, Gemeinde-Filter,
MAX_API_CALLS), Reserve-% GWR-konsistent, Baujahr-Spalte, neuer
Karten-Link (`map.geo.admin.ch`), KLEINPARZELLE als faktischer
Fokus-Indikator (200-500 m2 neutral).

Konzeptionelle Klaerung: Die Konflikt-Visualisierung zwischen
Schaetzung (Soll) und Realitaet (GWR-Ist) ist der zentrale Indikator
des Tools - keine Pseudo-Praezision bei der Soll-Berechnung im
Hoehensystem (Architekten-verifiziert: "kein Generalrezept").

## Status Iteration 7 (geplant, Juni 2026)

Generalprobe vorbereiten, Pitch trimmen, Demo-Adressen waehlen,
README finalisieren. Optional Architekt-Antwort zur Soll-Methodik
einarbeiten.
