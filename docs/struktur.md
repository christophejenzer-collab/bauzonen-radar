# Projekt-Struktur

**Stand**: 05. Mai 2026
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
+-- patch_potenzial.ps1                Patch: Bug-Fixes Vormittag 29.04.
+-- patch_begrenzer_bugs.ps1           Patch: Bug-Fixes Mittag 29.04.
+-- patch_thun_json.ps1                Patch: thun.json-Erweiterung 29.04.
+-- patch_gwr_integration.ps1          Patch: GWR-Integration 30.04.
+-- patch_gwr_unvollstaendig.ps1       Patch: GWR-Anzeige verbessern 30.04.
+-- patch_potenzial_ergebnis.ps1       Patch: AnalyseErgebnis-Refactoring 03.05.
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
|       +-- ausgabe/            (leer, Platzhalter fuer Output-Module)
|       |   `-- __init__.py
|       |
|       +-- datenquellen/       Externe Datenquellen
|       |   +-- __init__.py     Exports: GwrQuelle, GwrGebaeude, Exception-Klassen
|       |   `-- gwr.py          GWR-API (Eidg. Geb.- u. Wohnungsregister)
|       |
|       `-- gui/                Streamlit-GUI (Iteration 4 - LAUFEND)
|           +-- __init__.py
|           `-- app.py          Streamlit-App von Fabienne (LAUFEND, in Arbeit)
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
|   +-- glossar.md                       Fachbegriffe (Fabienne)
|   +-- releasenotes_backend.md          Releasenotes Backend
|   +-- releasenotes_frontend.md         Releasenotes Frontend (Fabienne)
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

## Lokale, nicht-getrackte Dateien

Folgende Dateien sind via `.gitignore` aus dem Repo ausgeschlossen,
aber lokal vorhanden zur Arbeitserleichterung:

- `src/bauzonenradar/gui/app_christophe_test.py` - lokale Test-Kopie
  von Fabiennes Frontend, fuer Layout-Tests durch Christophe.
  Wird geloescht sobald Fabienne ihre eigene Version pushed.

## Module im Detail

### `analyse_adresse.py` (refactored 03.05.2026)

Hauptprogramm und Eintrittspunkt fuer die ganze Pipeline. Seit
03.05. gilt eine klare **Trennung Berechnung/Ausgabe**:

```
analysiere(adresse) -> AnalyseErgebnis    # reine Logik, kein Print
drucke_bericht(ergebnis) -> None           # CLI-Output
main()                                     # ruft beide nacheinander
```

`AnalyseErgebnis` ist eine Datenklasse mit ~30 Feldern, die alle
Pipeline-Daten sammelt:
- Adresse, Status, Fehler, Warnungen
- Parzelle (gemeinde, parzellen_nummer, parzellen_flaeche_m2, egrid)
- Koordinaten (LV95 und WGS84)
- Reglement-Status
- BKP-Daten (Stadt Bern)
- GWR-Daten (Liste der Gebaeude, Summe Geschossflaeche)
- Potenzial (datenqualitaet, zulaessig_m2, ausschoepfung_prozent, ...)
- Original-Textbericht fuer Debug

So koennen GUI (Streamlit) und CLI dieselbe `analysiere()`-Funktion
nutzen, ohne Berechnungslogik zu duplizieren. **Separation of
Concerns**.

Pipeline-Aufruf:
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

### `gui/app.py` (NEU 03.05.2026 - LAUFEND, von Fabienne)

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

Aufruf:
```powershell
streamlit run src\bauzonenradar\gui\app.py
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

### Iteration 4 (Streamlit-GUI - LAUFEND seit 03.05.2026)

**Bereits umgesetzt**:
- `gui/app.py` - Streamlit-Hauptseite mit eigenem CSS-Design (Fabienne)
- `analysiere() -> AnalyseErgebnis` als Backend-API (Christophe)
- Layout: Adress-Eingabe, Karte, Parzelle, Bebauungspotenzial, GWR-Tabelle
- Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz

**Noch zu tun**:
- Frontend-Felder an Backend-API anpassen (Fabienne, in Arbeit)
- Live-Test mit echten Daten
- Visuelle Datenqualitaets-Ampel finalisieren
- PDF-Export (Could have, nicht Pflicht)

### Iteration 5 (Gemeinde-Analyse, Anfang Juni 2026)

**Bereits umgesetzt am 30.04.2026**:
- `datenquellen/gwr.py` - GWR-API integriert (1 von 4 Modulen)

**Noch zu tun**:
- `datenquellen/parzellen_liste.py` - alle Parzellen einer Gemeinde
- `analyse_parzelle.py` - Eintrittspunkt fuer Parzellennummer/EGRID
- `gemeinde_analyse.py` - Massen-Pipeline mit Throttling

Neu in `src/bauzonenradar/ausgabe/`:
- `excel_export.py` - Rangliste als XLSX
- `csv_export.py` - Rangliste als CSV
