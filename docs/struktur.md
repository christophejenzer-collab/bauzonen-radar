# Projekt-Struktur

**Stand**: 23. Mai 2026 (nach Iteration 6)
**Erstellt mit**: `Get-ChildItem -Recurse -File` aus PowerShell

## Visualisierung

```
bauzonen-radar/
├── README.md                          # DAU-Schnellstart 5 Schritte
│                                       # + KI-Disclaimer
├── .gitignore                          # Schliesst aus:
│                                       # - **/*.xml (ausser tests/fixtures/)
│                                       # - docs/archiv/ (lokales Archiv)
│                                       # - docs/start_cheatsheet.md (privat)
│                                       # - .venv/, __pycache__/, *.pyc
│                                       # - cache/ (SQLite-Cache)
│                                       # - ausgaben/ (Excel-Outputs)
├── requirements.txt                    # Python-Abhaengigkeiten
│
├── daten/
│   └── baureglemente/                  # JSON-Reglemente pro Gemeinde
│       ├── bern.json                   # Stadt Bern + 25 Bauklassen
│       ├── thun.json                   # Stadt Thun + WA-Zonen + ZPP
│       └── oberhofen_am_thunersee.json # Oberhofen am Thunersee
│
├── docs/                               # Projekt-Dokumentation
│   ├── konzept.md                      # Projekt-Konzept (Iter 4-6)
│   ├── projektplan.md                  # Projektplan bis 17.06.
│   ├── journal.md                      # Arbeitsjournal chronologisch
│   ├── struktur.md                     # Dieses Dokument
│   ├── fachliche_grundlagen.md         # IVHB, BR-Vergleich, Indikator-
│   │                                   # Konzept (Iter-6-Erkenntnis)
│   ├── glossar.md                      # Fachbegriffe
│   ├── anforderungen_backend.md        # Backend-Anforderungen
│   ├── anforderungen_frontend.md       # Frontend-Anforderungen (Fabienne)
│   ├── requirements_backend.md         # Backend-Requirements
│   ├── requirements_frontend.md        # Frontend-Requirements (Fabienne)
│   ├── releasenotes_backend.md         # Backend-Releasenotes
│   ├── releasenotes_frontend.md        # Frontend-Releasenotes
│   ├── konzept_gemeinde_analyse.md     # Iter-5-Konzept (UMGESETZT)
│   ├── code_walkthrough_backend.md     # NEU 31.05.: Klartext-Erklaerung
│   │                                   # fuer Verteidigung
│   ├── code_walkthrough_frontend.md    # NEU 31.05.: Klartext-Erklaerung
│   │                                   # der Streamlit-GUI
│   └── 20260615_bauzonen_radar.pptx    # NEU 08.06.: Praesentation v4
│                                       # 14 Slides (3 versteckt fuer
│                                       # Backup-Szenarien)
│
├── src/
│   └── bauzonenradar/                  # Hauptpaket
│       ├── __init__.py
│       ├── analyse_adresse.py          # Hauptmodul - Einzelanalyse
│       │                               # AnalyseErgebnis (~40 Felder)
│       │                               # analysiere() / drucke_bericht()
│       │                               # analysiere_per_egrid() Iter 5
│       │                               # Separation of Concerns
│       ├── baureglement.py             # JSON-Reglement-Loader
│       ├── bern.py                     # OEREB-Webservice + XML-Parser
│       │                               # fuer Stadt Bern
│       ├── bern_bkp.py                 # Bauklassenplan-API Stadt Bern
│       │                               # ArcGIS REST map.bern.ch
│       ├── modelle.py                  # Datenklassen Parzelle, OEREB,
│       │                               # Restriction, Bauklasse
│       ├── klassifikation.py           # Iter 5: 7 Kategorien
│       │                               # + KLEINPARZELLE (Iter 6)
│       │                               # + AUSSCHLUSS_VERKEHR/WALD
│       ├── gemeinde_analyse.py         # Iter 5: Massen-Pipeline
│       │                               # SQLite-Cache integriert
│       │                               # Throttling, Retry, ETA
│       ├── excel_export.py             # Iter 5: 6-Sheets-Export
│       │                               # + Karten-Link (Iter 6:
│       │                               # map.geo.admin.ch)
│       │                               # + Baujahr-Spalte (Iter 6)
│       │                               # + Reserve-%-Fix (Iter 6)
│       ├── xml_speichern.py            # XML-Snapshot-Helper
│       │                               # fuer Test-Fixtures
│       │
│       ├── analyse/                    # Detail-Analyse-Module
│       │   ├── __init__.py
│       │   └── potenzial.py            # Potenzialberechnung
│       │                               # 3 Bemessungssysteme
│       │                               # 3 Datenqualitaets-Stufen
│       │                               # Drei-Begrenzer-Logik
│       │
│       ├── ausgabe/                    # Ausgabe-Formate
│       │   └── __init__.py             # Textbericht-Helper
│       │
│       ├── datenquellen/               # Externe APIs
│       │   ├── __init__.py
│       │   ├── gwr.py                  # GWR-API swisstopo
│       │   │                           # Iter 5: gebaeude_zu_egrid()
│       │   │                           # Iter 6: tolerance 500 -> 100
│       │   ├── tlm3d.py                # Iter 5 BONUS:
│       │   │                           # Bodenbedeckungs-Filter
│       │   │                           # TLM3D-Strassen + Arealstatistik
│       │   └── parzellen_liste.py      # Iter 5: Praefix-Baum-Suche
│       │                               # Iter 6: Gemeinde-Filter
│       │                               # MAX_API_CALLS 3000
│       │
│       └── gui/                        # Streamlit-Frontend (Fabienne)
│           ├── __init__.py
│           └── frontend.py             # Iter 4: ~370 Zeilen
│                                       # CSS-Design (Inter, schwarz/rot)
│                                       # 4 Sektionen (Lage/Parzelle/
│                                       # Potenzial/GWR)
│                                       # Plausibilitaets-Konflikt-Box
│
├── tests/                              # Tests und Fixtures
│   ├── __init__.py
│   ├── test_zwoelf_adressen.ps1        # Regression 12 Adressen
│   │                                   # (Bern + Thun + Oberhofen + Edge)
│   ├── test_fuenfzig_adressen.ps1      # Stresstest 50 Adressen (96%)
│   ├── test_bern_batch.py              # Stadt-Bern-Detailtests
│   ├── test_output_nach_fix.txt        # Test-Output-Snapshot vom
│   │                                   # Regressions-Lauf (Beleg)
│   └── fixtures/                       # OEREB-XML-Snapshots
│       ├── README.md                   # Erklaerung der XMLs
│       ├── extract_koeniz.xml          # Koeniz-Beispiel
│       ├── extract_pruefen.xml         # Test-Adresse Pruefen
│       └── extract_thun.xml            # Thun-Beispiel
│
└── (lokal, NICHT im Repo via .gitignore):
    ├── .venv/                          # Python venv
    ├── cache/                          # SQLite-Cache der Massen-Analysen
    ├── ausgaben/                       # Excel-Outputs (bauzonen_radar_*.xlsx)
    ├── docs/archiv/                    # Lokale Geschichts-Sammlung
    │   ├── proof_of_concept.py
    │   ├── Strukturbaum-bauzonen-radar.txt
    │   ├── extract_beispiel.xml
    │   ├── test_zwoelf_adressen.py
    │   └── output_baumgarten_thun.md
    ├── docs/start_cheatsheet.md        # Persoenlicher Spickzettel
    └── verteidigungs_quiz.md           # Internes Pruefungs-Quiz
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

## Status Iteration 7 (abgeschlossen, Juni 2026)

Pruefungs-Vorbereitung in mehreren Teilschritten:

**31.05.2026 - Doku-Konsolidierung**:
- 5 Dokumente neu/aktualisiert (konzept, struktur,
  fachliche_grundlagen, konzept_gemeinde_analyse, releasenotes_backend)
- 2 Code-Walkthroughs erstellt (backend + frontend) als Verteidigungs-
  Material in Klartext fuer IT-Fremde
- Repo-Aufraeumung gemaess Dozenten-Feedback: historie/patches/,
  start.ps1, demo.ps1 entfernt; start_cheatsheet.md ueber .gitignore
  lokal gehalten
- README.md neu mit DAU-Schnellstart, KI-Disclaimer und
  Doku-Verknuepfungen

**08.06.2026 - Demo-Konzept und Praesentation v4**:
- Konzept "Bauzonen-Radar AG" als Berater-Duo
- 3 Investoren-Stories aus Thun-Goldiwil:
  - VERDICHTUNG: Loetschenenweg 1 (Parz 2034, Reserve 68%)
  - NEUGESCHAEFT: Ruettiweg/Parz 4204 (Reserve 100%, leeres Bauland)
  - ERSATZNEUBAU: Frutigenstrasse 74 (Parz 3708, Baujahr 1900,
    Reserve 78%, 4 Restriktionen)
- Praesentation v4 mit 14 Slides committed: Slide 8 als Demo-Setup,
  Slides 8a/b/c versteckt als Backup-Screenshots, Slide 8d als
  Excel-Lookahead, Slide 9 erweitert um Iter-6-Erkenntnis und
  KI-Punkt
- Adressen lokal verifiziert, alle drei Tool-Outputs dokumentiert

**12.06.2026 (geplant) - Generalprobe**:
- Live-Probelauf mit Stoppuhr (strikt 10 Minuten)
- Fotos einbauen (Slide 8 + Backup-Slides)
- Edge-Case-Tests durchspielen
- Backup-Plaene durchspielen

**15.06.2026 12:00 - Push-Deadline**:
- Alle Dokumente, Code, Tests, Praesentation in GitHub
- Letzter Commit erlaubt

**17.06.2026 10:00 - Praesentation**:
- Raum o408, Praesenzpflicht
- 10 Minuten strikt
- Live-Demo mit Streamlit 

## Status Iteration 8 (Backlog nach der Pruefung)

Falls Projekt weitergefuehrt wird:
- Direkter EGRID-Input im Streamlit-Frontend
- pytest-Unit-Tests fuer Drei-Begrenzer-Logik
- Result-Pattern statt Optional[float] = None
- Polygon-Intersection statt 1:1.5-Rechteck-Annahme
- Architekt-Antwort zur Soll-Methodik einarbeiten
- Koeniz als 4. Gemeinde aufnehmen
- PDF-Export der Einzelanalyse (Kundendossier)
