# Projekt-Struktur

**Stand**: 11. Mai 2026 (vor Iter-4-Abschluss)
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
+-- historie/
|   +-- patches/                      6 alte Patch-Skripte aus Iter 2-4
|       +-- README.md                 Erklaerung der Patches
|       +-- patch_*.ps1               6 Skripte (siehe Tabelle unten)
|
+-- src/
|   `-- bauzonenradar/          Hauptpaket
|       +-- __init__.py
|       +-- analyse_adresse.py  Hauptprogramm mit AnalyseErgebnis-Datenklasse
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
|       +-- ausgabe/            (leer, Platzhalter fuer Output-Module Iter 5)
|       |   `-- __init__.py
|       |
|       +-- datenquellen/       Externe Datenquellen
|       |   +-- __init__.py     Exports: GwrQuelle, GwrGebaeude, Exception-Klassen
|       |   `-- gwr.py          GWR-API (Eidg. Geb.- u. Wohnungsregister)
|       |
|       `-- gui/                Streamlit-GUI (Iteration 4)
|           +-- __init__.py
|           `-- frontend.py     Streamlit-App von Fabienne
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
|   +-- anforderungen_backend.md         RE-Doku Backend (Fabienne)
|   +-- anforderungen_frontend.md        RE-Doku Frontend (Fabienne)
|   +-- requirements_backend.md          Requirements Backend (Fabienne)
|   +-- requirements_frontend.md         Requirements Frontend (Fabienne)
|   +-- glossar.md                       Fachbegriffe (Fabienne)
|   +-- releasenotes_backend.md          Releasenotes Backend
|   +-- releasenotes_frontend.md         Releasenotes Frontend (Fabienne)
|   +-- start_cheatsheet.md              Persoenliche Quick-Start-Befehle (lokal)
|   `-- archiv/                          LOKAL: PoC, alte Snapshots, Backups
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

## Lokale, nicht-getrackte Dateien

Folgende Dateien sind via `.gitignore` aus dem Repo ausgeschlossen,
aber lokal vorhanden zur Arbeitserleichterung:

- `src/bauzonenradar/gui/app_christophe_test.py` - Test-Kopie fuer
  parallele Frontend-Tests (vor Fabiennes Push). Kann geloescht werden,
  ist nicht mehr noetig seit das Repo gepushed wurde.
- `docs/archiv/output_baumgarten_thun.md` - Output-Snapshot interessanter
  Adressen mit Naturgefahren und Ortsbildschutz, historisches Material.
- `docs/archiv/backup_vor_aufraeumen_*.zip` - Sicherheits-Backups
  beim Aufraeumen.

## Module im Detail

### `analyse_adresse.py` (refactored 03.05., gefixt 11.05.)

Hauptprogramm und Eintrittspunkt fuer die ganze Pipeline. Seit
03.05. gilt eine klare **Trennung Berechnung/Ausgabe**:

```
analysiere(adresse) -> AnalyseErgebnis    # reine Logik, kein Print
drucke_bericht(ergebnis) -> None           # CLI-Output
main()                                     # ruft beide nacheinander
```

`AnalyseErgebnis` ist eine Datenklasse mit ~40 Feldern, die alle
Pipeline-Daten sammelt:
- Adresse, Status, Fehler, Warnungen
- Parzelle (gemeinde, parzellen_nummer, parzellen_flaeche_m2, egrid)
- Koordinaten (LV95 und WGS84)
- Reglement-Status
- BKP-Daten (Stadt Bern)
- GWR-Daten (Liste der Gebaeude, Summe Geschossflaeche)
- Potenzial (datenqualitaet, zulaessig_m2, ausschoepfung_prozent, ...)
- GUI-Aliase (theoretisch_zulaessig_m2, ausschoepfungsgrad_prozent,
  reserve_prozent, zonen_betrachtet, zone, arealbonus_anwendbar,
  bemerkungen) - direkt aus PotenzialErgebnis befuellt
- Original-Textbericht fuer Debug

So koennen GUI (Streamlit) und CLI dieselbe `analysiere()`-Funktion
nutzen, ohne Berechnungslogik zu duplizieren. **Separation of
Concerns**.

Pipeline-Aufruf (CLI):
```bash
python src\bauzonenradar\analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"
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

### `gui/frontend.py` (NEU 03.05.2026 - Fabienne)

Streamlit-GUI fuer Endanwender. Importiert `analysiere()` direkt
aus `analyse_adresse.py` und rendert das `AnalyseErgebnis` grafisch:

- Adress-Eingabefeld + "Analysieren"-Button
- Sektion **Lage**: Karte mit `st.map()` und WGS84-Koordinaten
- Sektion **Parzelle**: Gemeinde, Flaeche, Zone(n), Datenqualitaets-Badge
- Sektion **Bebauungspotenzial**: Zulaessig / Ausschoepfung / Reserve
  als Kennzahlen plus Progress-Bars und Lagebeurteilung
- Sektion **GWR**: Tabelle der Bestandsgebaeude plus
  Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz

Eigenes CSS mit Inter-Schrift, Schwarz/Rot-Akzent, ruhiger
professioneller Anmutung. Keine Streamlit-Default-Optik.

Aufruf (aus Projekt-Root):
```powershell
streamlit run src\bauzonenradar\gui\frontend.py
```

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

## Patch-Skripte (im Repo, dokumentarisch)

Patch-Skripte aus Iter 2-4 sind in `historie/patches/` erhalten als
**Beleg fuer iterative Entwicklung**:

| Skript | Zweck | Datum |
|---|---|---|
| `historie/patches/patch_potenzial.ps1` | Bug-Fixes Begrenzer-Logik | 29.04. |
| `historie/patches/patch_begrenzer_bugs.ps1` | Bug-Fixes max_gebaeudelaenge=None | 29.04. |
| `historie/patches/patch_thun_json.ps1` | thun.json-Erweiterung WA-Slash + ZPP | 29.04. |
| `historie/patches/patch_gwr_integration.ps1` | GWR-Modul-Anbindung | 01.05. |
| `historie/patches/patch_gwr_unvollstaendig.ps1` | GWR-Anzeige bei unvollstaendigen Daten | 01.05. |
| `historie/patches/patch_potenzial_ergebnis.ps1` | AnalyseErgebnis-Refactoring | 03.05. |

Siehe `historie/patches/README.md` fuer Details zur Methode.

Jedes Skript hat eingebauten Backup-Mechanismus, Syntax-Check und
Smoke-Test. Sie sind nicht reproduzierbar wiederholt ausfuehrbar (da
sie auf bestimmten Vorgaenger-Code bauen), zeigen aber den
nachvollziehbaren Entwicklungsweg.

## Lokales Archiv (`docs/archiv/`)

Dieser Ordner ist via `.gitignore` aus dem Repo ausgeschlossen,
aber lokal vorhanden:

- `proof_of_concept.py` (frueher POC)
- `Strukturbaum-bauzonen-radar.txt` (alte Baum-Datei)
- `extract_beispiel.xml` (Test-XML aus fruehen Tagen)
- `test_zwoelf_adressen.py` (alte Python-Version)
- `aufraeumen_30_04_2026.ps1` (Aufraeum-Skript)
- `output_baumgarten_thun.md` (interessante Outputs)
- `backup_vor_aufraeumen_*.zip` (ZIP-Sicherungen des Aufraeumens)

## Status Iteration 4 (Stand 11.05.2026)

**Iteration 4 ist im Wesentlichen ABGESCHLOSSEN:**

- [x] Streamlit-GUI mit eigenem CSS-Design (Fabienne)
- [x] AnalyseErgebnis-Datenklasse fuer GUI/CLI-Trennung
- [x] Alle drei Datenqualitaets-Pfade in GUI sichtbar
- [x] Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz
- [x] WGS84-Karte mit Marker (Karten-Sektion)
- [x] Tabellarische GWR-Anzeige mit Aggregation
- [x] Live-Test mit 4 Adressen erfolgreich (11.05.)

**Verbleibende kleinere Punkte (optional / Phase 3 Generalprobe)**:
- Negative Reserve bei >100% Ausschoepfung visuell sauberer
- Zonen-Suffix `[hoehen_und_gz]` ausblenden
- Karten-Marker eventuell kleiner

## Status Iteration 5 (Stand 12.05.2026)

**Iteration 5 ist ABGESCHLOSSEN** - alle 4 geplanten Module plus
3 Bonus-Module umgesetzt an einem Tag (~11h Session).

Detail siehe `docs/konzept_gemeinde_analyse.md`.

**Umgesetzt**:

- [x] `datenquellen/gwr.py` (30.04. vorgebaut, 12.05. EGRID-Fix)
  - `gebaeude_zu_adresse()` fuer Einzel-Analyse
  - `gebaeude_zu_egrid()` fuer Massen-Analyse (NEU 12.05.)
  - `_identify_features()` als gemeinsamer Helper
- [x] `datenquellen/parzellen_liste.py` (12.05.)
  - Praefix-Baum-Suche umgeht SearchAPI-Limit von 50 Treffern
  - Oberhofen: 1176 Parzellen via 161 API-Calls in 126 Sek
- [x] `datenquellen/tlm3d.py` (12.05., BONUS)
  - `TlmStrassenQuelle` (offizielle TLM3D-Strassen)
  - `ArealstatistikQuelle` (BFS-Bodenbedeckung 2023)
  - Gemeinsame `_MapServerIdentifyBasis`
- [x] `analyse_adresse.py` (12.05. erweitert)
  - `analysiere_per_egrid()` als Massen-Analyse-Eintrittspunkt
  - `AnalyseErgebnis` um 4 BB-Felder erweitert
- [x] `gemeinde_cache.py` (12.05.)
  - SQLite-Cache via Pickle-Serialisierung (Strategie A)
  - Wiederaufnahme nach Abbruch, idempotent
- [x] `klassifikation.py` (12.05.)
  - 7 Geschaeftslogik-Kategorien + 2 Bodenbedeckungs-Filter
  - Schwellen als Konstanten (am Schwager zu verifizieren)
- [x] `gemeinde_analyse.py` (12.05.)
  - Haupt-Pipeline mit Throttling, Retry, Progress-Logging mit ETA
  - CLI mit argparse, KeyboardInterrupt-sicher
- [x] `excel_export.py` (12.05.)
  - 6 Sheets, gestylte Header, Freeze-Panes, GRUDIS-Links

**Pilot-Lauf Oberhofen am Thunersee** (12.05.2026):
- 1176 Parzellen, 41 Min, 0 Fehler
- 170 hochwertige Kandidaten identifiziert
- 23 False-Positives durch Bodenbedeckungs-Filter eliminiert
- Verifikation 7 Stichproben gegen map.geo.admin.ch

**Bekannte Limitationen** (Iter 6 oder Folgeprojekt):
- Schmale Waldparzellen (Zentroid am Rand) nicht erwischt
- GWR-Polygon-Bug bei Hauptgebaeude weit vom Zentroid
- Loesung: Polygon-Intersection mit Parzellengeometrie
