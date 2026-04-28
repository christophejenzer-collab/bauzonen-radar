# Journal: Bauzonen-Radar

Chronologisches Arbeitsjournal zum Python-Abschlussprojekt.

## Hinweis zum KI-Einsatz

Fuer die Erstellung dieses Projekts wird Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Architektur, Code-Generierung,
Reglement-Strukturierung und Dokumentation entstehen in
Zusammenarbeit mit Claude. Fachliche Entscheidungen, Verifikation
der Werte und finale Architektur liegen beim Projektteam.

---

## 28. April 2026 (Dienstag) - Termin mit Fabienne, Oberhofen integriert

**Dauer**: ca. 2 Stunden

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

Vierter Schritt (nach Bern und Thun): Kleine Gemeinde abdecken.

**Recherche**:
- Offizielles Baureglement Oberhofen am Thunersee gefunden
- Quelle: BR vom 14. Mai 2012, Nachfuehrung bis 31. Dezember 2024,
  AGR-genehmigt
- PDF-URL:
  https://www.oberhofen.ch/images/files/Reglemente-und-Verordnungen/Bau/AGR-Gemeindebaureglement.pdf
- Art. 212 mit Tabelle: vier Wohn-/Mischzonen W1, W2, W3, M2
- Werte fuer kA, gA, GL, Fh tr, Fh gi, VG aus Reglement extrahiert
- Plus elf ZOEN, zehn ZPP, sechs Ortsbildschutzgebiete

**Erkenntnis**: Oberhofen verwendet Hoehen-System ohne
Gruenflaechenziffer (Unterschied zu Thun BR 2022). Das bricht
unsere bisherige `ist_berechenbar`-Logik.

### Bug-Fixes

**Problem**: Bei Oberhofen-Test schlug `_behandle_hoehen_und_gz`
nicht an, weil keine GZ in den Daten war.

**Fix 1 in baureglement.py**: `ist_berechenbar`-Property erweitert.
Schon eine Hoehenangabe genuegt jetzt fuer "berechenbar". GZ ist
optional.

**Fix 2 in potenzial.py**: `_behandle_hoehen_und_gz` arbeitet sich
durch alle vorhandenen Werte. Einleitungstext unterscheidet
zwischen "mit GZ" (Thun-Stil) und "ohne GZ" (Oberhofen-Stil).
Vollgeschosse werden ausgegeben.

### Verifikations-Tests (alle drei Gemeinden)

| Adresse | System | Ergebnis |
|---|---|---|
| Thunstrasse 40, Bern | GFZo | 118 m^2 zulaessig, 80%, Status GERING |
| Hirschweg 7, Thun | Hoehen+GZ | Komplette Werte, Strukturgebiet erkannt |
| U. Stadelstrasse 1, Oberhofen | Hoehen | Komplette Werte mit Vollgeschossen |

**Status**: Drei Bemessungssysteme im selben Tool funktional.

### Dokumentation aktualisiert

- README.md: Stand 28.04., Oberhofen-Test-Adresse, Fabienne-Eintrag,
  KI-Hinweis am Ende
- docs/konzept.md: Iteration 1+2 abgeschlossen markiert,
  Aufgabenverteilung mit Fabienne, KI-Werkzeuge-Sektion
- docs/projektplan.md: Iteration 3 als laufend markiert,
  Iteration 4 verfeinert, Risiken-Tabelle ergaenzt
- docs/journal.md: Dieser Eintrag
- docs/fachliche_grundlagen.md: Oberhofen-Sektion ergaenzt

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
