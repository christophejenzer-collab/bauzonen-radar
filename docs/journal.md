# Journal: Bauzonen-Radar

Chronologisches Arbeitsjournal zum Python-Abschlussprojekt.

## Hinweis zum KI-Einsatz

Fuer die Erstellung dieses Projekts wird Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Architektur, Code-Generierung,
Reglement-Strukturierung und Dokumentation entstehen in
Zusammenarbeit mit Claude. Fachliche Entscheidungen, Verifikation
der Werte und finale Architektur liegen beim Projektteam.

---

## 28. April 2026 (Dienstag) - Schaetz-Berechnung und Datenqualitaet

**Dauer**: ca. 4 Stunden

### Termin mit Fabienne (Mitstudentin)

Aufgabenverteilung fixiert:
- **Fabienne**: Dokumentation, Streamlit-Webseite (Iteration 4),
  Requirements-Engineering-Pruefung
- **Christophe**: Backend, OEREB-Pipeline, Reglement-Daten

Naechste Schritte fuer Fabienne:
- GitHub-Username an Christophe senden
- Repo durchklicken
- Erste Anforderungs-Liste erstellen
- Implizite Annahmen im Code identifizieren

### Oberhofen integriert

Vierter Schritt nach Bern und Thun: kleine Gemeinde abdecken.

**Recherche**:
- Offizielles Baureglement Oberhofen am Thunersee gefunden
- Quelle: BR vom 14. Mai 2012, Nachfuehrung bis 31. Dezember 2024,
  AGR-genehmigt
- Art. 212 mit Tabelle: vier Wohn-/Mischzonen W1, W2, W3, M2
- Werte fuer kA, gA, GL, Fh tr, Fh gi, VG aus Reglement extrahiert
- Plus elf ZOEN, zehn ZPP, sechs Ortsbildschutzgebiete

**Erkenntnis**: Oberhofen verwendet Hoehen-System ohne
Gruenflaechenziffer. Das bricht unsere bisherige
`ist_berechenbar`-Logik.

### Bug-Fixes (erste Runde)

**Problem**: Bei Oberhofen-Test schlug `_behandle_hoehen_und_gz`
nicht an, weil keine GZ in den Daten war.

**Fix 1 in baureglement.py**: `ist_berechenbar`-Property erweitert.
Schon eine Hoehenangabe genuegt jetzt fuer "berechenbar". GZ ist
optional.

**Fix 2 in potenzial.py**: `_behandle_hoehen_und_gz` arbeitet sich
durch alle vorhandenen Werte. Einleitungstext unterscheidet
zwischen "mit GZ" (Thun-Stil) und "ohne GZ" (Oberhofen-Stil).
Vollgeschosse werden ausgegeben.

### Erweiterung: Schaetz-Berechnung im Hoehen-System

Real-Test mit "Florastrasse 5, 3600 Thun" (Wohnen W3) brachte die
Frage: "Warum berechnet das Tool nichts? Es ist ja nur W3."

**Erkenntnis**: Im Hoehen-System ist eine direkte m^2-Berechnung
nicht moeglich, aber eine konservative Schaetzung sehr wohl. Wir
brauchen:
- Annahme Gebaeudebreite (default 12 m, gekappt durch GL)
- Multiplikation mit Vollgeschossen
- Anteiliger Dachgeschoss-Bonus bei Schraegdach (60%)
- Beruecksichtigung von Grenzabstaenden und GZ als Begrenzung

### Datenqualitaets-Konzept

Wichtige Design-Entscheidung: Schaetzungen muessen sich klar von
verbindlichen Berechnungen unterscheiden.

Drei Stufen eingefuehrt:
- **VERBINDLICH** (AZ/GFZo)
- **GROBSCHAETZUNG** (Hoehen-System)
- **NICHT_MOEGLICH** (keine Werte)

Bei Schaetzungen erscheint:
- Header-Banner mit Warnung
- "GROBSCHAETZUNG zulaessig" statt "Theoretisch zulaessig"
- "Status: SCHAETZWERT - keine Investitionsentscheidung darauf basieren"
- Vollstaendige Berechnungsbasis transparent
- Annahmen-Sektion ("Annahme Gebaeudebreite kann zu hoch oder zu
  niedrig sein...")
- Plausibilitaetscheck gegen altes AZ-Recht (falls in JSON
  hinterlegt)
- KEINE Reserve und KEIN Ausschoepfungsgrad (Vergleich zweier
  Schaetzungen waere irrefuehrend)

### Plausibilitaetscheck

Neues Feld `vergleichswert_az_alt` in `Bauparameter`. Bei jeder
Thun-Zone hinterlegt der alte AZ-Wert aus BR 2002.

Aussage:
- Faktor < 0.7: "auffaellig niedrig"
- Faktor 0.7-1.8: "plausibel"
- Faktor > 1.8: "auffaellig hoch"

### thun.json komplett ueberarbeitet

Sieben Zonen mit allen Werten plus `vergleichswert_az_alt`:
- W2, W3, W4
- WA3, WA4, WA5
- Arbeiten A
- Arealbonus bei WA5 ab 3000 m^2

### Verifikations-Tests (alle vier Adressen)

| Adresse | System | Datenqualitaet | Ergebnis |
|---|---|---|---|
| Thunstrasse 40, Bern | GFZo | VERBINDLICH | 118 m^2, 80%, GERING |
| Florastrasse 5, Thun W3 | Hoehen+GZ | GROBSCHAETZUNG | ~780 m^2 (Faktor 1.25x) |
| Hirschweg 7, Thun W2 | Hoehen+GZ | GROBSCHAETZUNG | ~201 m^2 (Faktor 0.86x) |
| U. Stadelstrasse 1, Oberhofen | Hoehen | GROBSCHAETZUNG | ~384 m^2 (kein AZ-Vergleich) |

**Status**: Drei Bemessungssysteme im selben Tool funktional, mit
sauberer Datenqualitaets-Markierung.

### Dokumentation aktualisiert

- README.md: Beispiel-Outputs fuer beide Datenqualitaeten,
  Test-Adressen mit Datenqualitaets-Hinweis, Schaetz-Disclaimer
- docs/konzept.md: Neue Sektion "Datenqualitaet als zentrales
  Konzept", aktualisierte Iteration 2
- docs/projektplan.md: Iteration 2 mit allen Schaetz-Features
  dokumentiert, Iteration 4 mit Datenqualitaets-Ampel
- docs/journal.md: Dieser Eintrag
- docs/fachliche_grundlagen.md: Neue Sektion "Schaetz-Berechnung
  im Hoehen-System"

---

## 27. April 2026 (Montag) - Mehrsystem-Modell und Reglement-Daten

**Dauer**: ca. 4 Stunden

### Erkenntnis des Tages: Drei Bemessungssysteme parallel

Der Kanton Bern hat den Systemwechsel von AZ zu GFZo
(IVHB-konform) eingelaeutet, aber Gemeinden setzen ihn
unterschiedlich schnell um. Stadt Thun BR 2022 verzichtet sogar
ganz auf eine flaechen-bezogene Kennzahl und steuert ueber Hoehen
und Gruenflaechenziffer.

Datenmodell entsprechend erweitert:
- `BemessungsSystem`-Enum
- Felder fuer Hoehen, Grenzabstaende, Gebaeudelaenge, GZ
- `Bauparameter.ist_berechenbar` und `hauptkennzahl()`

### Stadt Bern komplett

Recherche gegen offizielle Bauordnung BO 2006 (Stand 28.09.2023):
- Bauklassen 2-6 mit FH/FHA/kGA/gGA (Art. 46)
- Bauklasse E mit GFZo 0.5 / 0.6 (Art. 57)
- ZoeN FA-FD mit GFZo (Art. 24)
- Arbeitszonen mit FH/FHA pro Bauklasse 1-6 (Art. 58)
- Altstadt-Spezialregimes Untere/Obere Altstadt (Art. 76-86)

`bern.json` mit 30+ Eintraegen vollstaendig erfasst. Hinweis: Die
GFZo-Werte pro Bauklasse-Zone-Kombination liegen aber im
Bauklassenplan (BKP), nicht in der BO. Schwager wird die liefern.

### Stadt Thun komplett

Schwager-Tabelle mit Art.-42-Werten BR 2022 eingepflegt:
- W2/W3/W4/WA3-WA5/Arbeiten A
- Strukturgebiet als Spezialfall
- Arealbonus ab 3000 m^2

`thun.json` mit allen Werten erfasst.

### Erste echte GFZo-Berechnung

Thunstrasse 40, 3005 Bern (Bauklasse E):
- Parzellenflaeche: 237 m^2
- GFZo = 0.5
- Theoretisch zulaessig: 118 m^2
- Status: GERING (80% Ausschoepfung)

Tool funktioniert technisch und fachlich.

### Erfassungs-Excel fuer Schwager

`docs/erfassung_baureglemente.xlsx` mit vier Tabs und acht
Tabellen erstellt. Soll dem Schwager helfen, die fehlenden
Bauklassenplan-Werte effizient nachzuliefern.

### Test-Adressen-Suite

Zehn realweltliche Adressen verifiziert. `demo.ps1` als
Regressionstest erstellt.

---

## (frueheres) - Iteration 1 abgeschlossen

Pipeline End-to-End funktional. Geocoding, OEREB-Abfrage,
XML-Parsing, Datenmodell. Erste Test-Adressen liefern korrekte
Daten.

---

## Verschiedene Beobachtungen

- Windows-PowerShell mit `start.ps1` automatisiert venv-Aktivierung
  und Wechsel ins Modul-Verzeichnis. Spart bei jedem Start drei
  Befehle.
- `demo.ps1` verwendet `$PSScriptRoot`, also ortsunabhaengig
  aufrufbar.
- OEREB-Webservice antwortet meist in unter 5 Sekunden, ab und zu
  laengere Wartezeiten.
- swisstopo SearchAPI ist sehr schnell und tolerant gegenueber
  Tippfehlern in Adressen.
- Iteratives Vorgehen mit Real-Tests deckt Schwachstellen auf, die
  in der Theorie nicht sichtbar sind. Beispiel: Florastrasse-Test
  fuehrte direkt zur Schaetz-Berechnung.
