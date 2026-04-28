# Entwicklungs-Journal Bauzonen-Radar

Fortlaufendes Journal aller Entwicklungssitzungen.
Neueste Eintraege oben.

---

## 27. April 2026 (Vormittag bis Nachmittag, ca. 4 Stunden)

### Kontext
Tag vor dem Mitstudentin-Termin. Vorbereitung der Demo, Praxistests an realen Adressen, Ueberarbeitung der Reglement-Daten gegen die offiziellen Quellen.

### Geleistet

**Praxistests an Adressen:**
- Untere Sadelstrasse 1, 3653 Oberhofen → kein Reglement, aber Naturgefahren erkannt
- Hirschweg 7, 3604 Thun → Bug entdeckt (OEREB-Schreibweise vs. Reglement-Schreibweise)
- Kramgasse 1, 3000 Bern → Berner Altstadt-Spezialregime entdeckt
- Junkerngasse 47, 3011 Bern → "Zone im oeffentlichen Interesse" entdeckt
- Marktgasse 1 + Bundesgasse 26 → "Obere Altstadt, Zone mit Planungspflicht"
- Thunstrasse 40 → **erste echte GFZo-Berechnung** (Bauklasse E, GFZo 0.5)

**Datenmodell-Erweiterungen (`baureglement.py`):**
- Differenzierte Fassadenhoehen-Felder (traufseitig, giebelseitig, andere Dachform)
- Gebaeudelaenge als eigenes Feld
- Arealbonus-Felder (Schwellenwert, zusaetzliche Geschosse)
- Methode `hat_arealbonus()` zur parzellen-spezifischen Pruefung

**thun.json komplett ueberarbeitet:**
- Echte Werte aus Art. 42 BR 2022 (Tabelle vom Schwager)
- 7 Wohn-/Mischzonen mit allen kA, gA, GL, Fh tr, Fh gi, Fh, GZ
- Strukturgebiet-Konzept als Datenfeld
- Arealbonus mit Schwelle 3000 m^2 / +1 Geschoss

**bern.json komplett ueberarbeitet:**
- Quelle: Bauordnung der Stadt Bern (BO 2006, Stand 28.9.2023)
- Bauklassen 2-6 statt A-E (mein Fehler korrigiert)
- Bauklasse E mit GFZo 0.5/0.6 aus Art. 57
- Zonen FA/FB/FC/FD mit GFZo 0.1/0.6/1.2 aus Art. 24
- Berner Altstadt-Spezialregime mit Verweis auf Art. 76-86
- Variable Grenzabstaende aus Art. 46 als Datenstruktur (fuer spaeter)
- 11 Bauklassen + 18 Nutzungszonen erfasst

**potenzial.py erweitert:**
- Strukturgebiet-Erkennung mit prominenter Warnung
- Arealbonus-Pruefung pro Parzelle
- Hoehen+GZ-Ausgabe mit konkreter unversiegelter Flaeche in m^2
- Mehrere berechenbare Parameter werden alle ausgegeben

**Erfassungs-Excel fuer Schwager:**
- 4 Tabellenblaetter (Anleitung, Stadt Bern, Stadt Thun, Test-Adressen)
- 8 Tabellen mit gelben Eingabefeldern
- Lachsfarbene Markierung fuer Annahmen, die zu verifizieren sind

**Tooling:**
- `start.ps1` wechselt automatisch in Modul-Ordner
- `demo.ps1` fuer 10-Adressen-Regressionstest

### Erkenntnisse

**Fachlich:**
- OEREB- und Reglement-Schreibweisen koennen differieren ("Wohnen W2" vs. "Wohnzone W2")
- Stadt Bern verwendet Bauklassen 2-6, nicht A-E
- Stadt Bern: gGA haengt von Gebaeudelaenge ab (zweidimensionale Tabelle)
- Berner Altstadt: vier Spezialregime, davon zwei mit Planungspflicht
- "Zone im oeffentlichen Interesse" ist eigene Bauklasse-Kategorie
- Stadt Bern: GFZo wird parzellenscharf im Bauklassenplan (BKP) festgelegt, nicht in der BO
- Stadt Thun: Strukturgebiet-Ueberlagerung kann BR aushebeln (Beirat Stadtbild)
- Stadt Thun: Arealbonus ab 3000 m^2 gibt +1 Geschoss

**Architektonisch (Software):**
- Praxistests in verschiedenen Stadtteilen sind unverzichtbar
- Tool zeigt jetzt mehrere gefundene Bauklassen, nicht nur die erste
- Tool macht erste echte Potenzialberechnung (Thunstrasse 40)

### Getestete Adressen heute (10)
- Kramgasse 1 + 49, 3000/3011 Bern (beide Untere Altstadt)
- Junkerngasse 47, 3011 Bern (zwei Bauklassen!)
- Marktgasse 1, 3011 Bern (Obere Altstadt mit Laubenfluchtlinie)
- Bundesgasse 26, 3011 Bern (Obere Altstadt mit Planungspflicht)
- Thunstrasse 40, 3005 Bern (Bauklasse E - berechnet)
- Rathausplatz 1, 3600 Thun (Bestand+Ufer, 4 Gefahren)
- Hirschweg 7, 3604 Thun (Wohnen W2 mit Strukturgebiet)
- Dorfstrasse 10, 3095 Spiegel (Koeniz, kein Reglement)
- Untere Sadelstrasse 1, 3653 Oberhofen (Naturgefahren)

### Git
- thun.json: OEREB-Schreibweisen ergaenzt
- bern.json: Komplett neu gegen BO 2006/2023
- baureglement.py: Datenmodell erweitert
- potenzial.py: Strukturgebiet, Arealbonus, Hoehen-Ausgabe
- start.ps1, demo.ps1: Tooling
- erfassung_baureglemente.xlsx: Vorlage fuer Schwager

### Naechster Schritt
- Excel an Schwager senden mit Begleittext
- Mitstudentin-Termin morgen 28.4.2026 (30 Min):
  Konzept und Projektplan gemeinsam durchgehen, Aufgabenverteilung
- Sobald Werte vom Schwager kommen: in JSONs eintragen

---

## 25. April 2026 (Vormittag, ca. 1 Stunde)

### Kontext
Praxistest mit drei neuen Adressen vor dem Mitstudentin-Termin.

### Geleistet
- Test mit Untere Sadelstrasse 1, Oberhofen → kein Reglement, Naturgefahren
- Test mit Hirschweg 7, Thun → OEREB-Schreibweise "Wohnen W2" entdeckt
- Test mit Kramgasse 1, Bern → Berner Altstadt-Spezialregime entdeckt
- Fix thun.json: "Wohnen W2/W3" zusaetzlich zu "Wohnzone W2/W3"
- Fix bern.json: 4 Altstadt-Bereiche als Spezialbauklassen
- Fix start.ps1: Wechselt automatisch in Modul-Ordner

### Gelernt
- OEREB-Schreibweise und Baureglement-Schreibweise koennen differieren
- Berner Altstadt verwendet Spezialnamen statt numerischer Bauklassen
- Praxistests in verschiedenen Stadtteilen sind unverzichtbar

---

## 24. April 2026 (Abend, ca. 1 Stunde)

### Kontext
Erste komplette Pipeline funktioniert. Aufraeumen, Dokumentation, Repo-Setup.

### Geleistet
- README.md professionell gestaltet
- Konzept-Dokument fuer Kursabgabe erstellt
- Projektplan mit 8 Wochen bis 17. Juni
- Fachliche Grundlagen dokumentiert
- Repo aufgeraeumt (persoenliche Dateien entfernt, .gitignore erweitert)

### Naechster Schritt
- Praxistests an mehr Adressen
- Schwager kontaktieren fuer Reglement-Werte
- Mitstudentin terminieren

---

## 23. April 2026 (Tagsueber, ca. 4 Stunden)

### Kontext
Konzeption und Implementierung der ersten Pipeline-Iteration.

### Geleistet
- Modulstruktur entworfen: modelle.py, bern.py, baureglement.py, potenzial.py
- swisstopo-Geocoding integriert (Adresse → LV95-Koordinaten)
- OEREB-Webservice Kanton Bern angebunden (GetEGRID, GetExtract)
- XML-Parser fuer alle relevanten OEREB-Subcodes
- Erste thun.json mit historischen AZ-Werten (W2: 0.5, W3: 0.7)
- Erste bern.json mit Bauklassen-Struktur

### Gelernt
- OEREB-XML ist gut strukturiert, aber tief verschachtelt
- LV95-Koordinaten sind Pflicht fuer Schweizer Webservices
- Parzellen koennen mehrere Zonenausschnitte haben (Anteilsberechnung)

---

## 22. April 2026 (Abend)

### Kontext
Projekt-Idee: Bauzonen-Radar fuer den Kanton Bern als Abschlussprojekt fuer
den Python-Kurs. Abgabe 17. Juni 2026.

### Geleistet
- Projekt-Repository auf GitHub erstellt
- Python venv eingerichtet (requests, owslib, geopandas, shapely, pyproj, folium, guizero)
- Erstes geocode-Experiment mit swisstopo
- Erste OEREB-Anfrage an https://www.oereb2.apps.be.ch/

### Erste Pitch-Idee
"Schweizer Bauland-Analyse: Zeigt fuer jede Adresse das verbleibende
Bebauungspotenzial - ungenutzte Reserve unter Beruecksichtigung von OEREB-Daten,
Naturgefahren und Baulinien."

### Naechster Schritt
- Pipeline End-to-End bauen
- Ein Reglement (Thun) als Prototyp einbinden
