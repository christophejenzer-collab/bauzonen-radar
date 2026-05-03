## 1. Einleitung

### 1.1 Zweck des Dokuments

Dieses Dokument spezifiziert die funktionalen und nicht-funktionalen
Anforderungen an das Bauzonen-Radar-Tool. Es dient als Grundlage fuer
Entwicklung, Verifikation und Validierung des Systems.

Das Dokument folgt den Prinzipien des Requirements Engineering nach
IEEE 830 und Volere. Anforderungen sind eindeutig identifiziert,
priorisiert (MoSCoW), testbar formuliert und mit Akzeptanzkriterien
versehen.

### 1.2 Geltungsbereich

Erfasst werden Anforderungen an:
- die Pipeline-Funktionalitaet (Adresse zu Bauland-Analyse)
- die Datenqualitaets-Trichotomie (VERBINDLICH/GROBSCHAETZUNG/NICHT_MOEGLICH)
- die Ausgabe-Logik (CLI-Bericht, geplant: Streamlit-GUI)
- die Reglement-Datenpflege fuer drei Pilot-Gemeinden
- die geplante Gemeinde-Analyse (Iteration 5)

Nicht erfasst werden:
- Anforderungen an die Hosting-Infrastruktur (Tool laeuft lokal)
- Internationalisierung (nur Deutsch, nur Schweiz, nur Kanton Bern)
- Haftungsfragen (siehe Datenqualitaets-Konzept und Disclaimers)

### 1.3 Methodisches Vorgehen

Die Anforderungen wurden in folgenden Schritten erhoben:

1. **Stakeholder-Identifikation**: Architekten, Investoren, Eigentuemer
   sowie sekundaere Stakeholder (Bauverwaltung, Datenanbieter)
2. **Domaenen-Analyse**: Schweizer Baurecht, OEREB-System, IVHB
3. **Code-Review**: Identifikation impliziter Annahmen im bestehenden Code
4. **Anforderungs-Extraktion**: Aus Use-Cases, Code-Verhalten und
   Stakeholder-Beduerfnissen
5. **Konflikt-Analyse**: Trade-offs zwischen Anforderungen explizit machen
6. **Verifikations-Mapping**: Jede Anforderung gegen einen Test mappen


---

## 2. Stakeholder-Analyse

### 2.1 Primaere Stakeholder

**Architekt**
- Bedarf: Schnelle Einschaetzung des Bebauungs-Potenzials einer Parzelle
  vor einem Erstgespraech mit Bauherrschaft
- Erwartet: Verbindliche Zahl, klare Datenqualitaet, fachliche Korrektheit
- Konflikt: Toleriert keine falschen Verbindlich-Aussagen, akzeptiert aber
  ehrliche "kann ich nicht"-Antworten

**Investor / Bautraeger**
- Bedarf: Massenanalyse einer Gemeinde, sortiert nach Verdichtungs-Potenzial
- Erwartet: Excel-Liste, sortier- und filterbar, mit ausreichenden Daten
  fuer Erstkontakt mit Eigentuemern
- Konflikt: Schnelligkeit vs. Datenqualitaet — eine Gemeinde mit 500
  Parzellen darf nicht 8 Stunden brauchen

**Eigentuemer**
- Bedarf: Verstehen ob auf eigenem Grundstueck noch Reserve besteht
- Erwartet: Allgemeinverstaendliche Sprache, kein Fachjargon
- Konflikt: Will keine Werbung von Investoren erhalten (Datenschutz)

### 2.2 Sekundaere Stakeholder

**Bauverwaltung / Stadtplanung**
- Indirekt betroffen, da das Tool ihre Reglemente interpretiert
- Erwartet: Klare Markierung "ersetzt keine rechtsverbindliche Auskunft"
- Konflikt: Falsche Aussagen koennten Mehrarbeit verursachen
  (Korrekturanfragen)

**Datenanbieter (swisstopo, Kanton Bern, Stadt Bern, BFS)**
- Liefern die Datengrundlage via APIs
- Erwartet: Faire Nutzung, Throttling, keine Massen-Scraping-Lasten
- Konflikt: Zu aggressive Massen-Abfragen koennten zu Rate-Limits oder
  Sperrungen fuehren

**Pruefungs-Kommission (Hochschule)**
- Bedarf: Bewertbare Lernleistung in den vier Bewertungsbereichen
  (Konzept/Code/Praesentation/Code-Fragen)
- Erwartet: Sauberes Konzept, lauffaehiges Programm, klare Abgrenzung
  der Eigenleistungen im Team

### 2.3 Anti-Stakeholder

**Eigentuemer von gefundenen Verdichtungs-Kandidaten**
- Werden durch Massenanalyse identifizierbar (Parzellennummer, Adresse)
- Datenschutz-Konflikt: Wir wollen sie nicht ungewollt zur Zielscheibe
  von Investoren machen
- Loesung: Tool zeigt nur oeffentliche Daten und einen GRUDIS-Direktlink
  ("Bruecken-Ansatz"), Eigentuemer-Recherche bleibt manuelle Arbeit
  des Users

---

 

## 3. Use-Case-Spezifikation

### UC-1: Architekt prueft Bebauungs-Potenzial einer Adresse

**Akteur**: Architekt
**Vorbedingung**: Adresse einer Schweizer Parzelle im Kanton Bern bekannt
**Hauptablauf**:
1. Architekt gibt Adresse in CLI ein
2. System erkennt Adresse via swisstopo SearchAPI
3. System ermittelt Parzelle und Zone via OEREB-Webservice
4. System laedt passendes Gemeinde-Baureglement
5. (Bei Stadt Bern) System ruft Bauklassenplan-API auf
6. System ruft GWR-API auf fuer effektive Bestands-Bebauung
7. System berechnet Bauland-Reserve mit angemessener Datenqualitaet
8. System erstellt Bericht mit Empfehlungs-Block

**Akzeptanzkriterium**: Bericht enthaelt Datenqualitaets-Banner,
Berechnungsgrundlage, Empfehlung mit visuellem Balken in unter 30 Sekunden.

**Alternativ-Ablauf 1**: OEREB-Webservice nicht erreichbar
- System gibt klare Fehlermeldung aus
- Optional: Hinweis auf Fixture-basierten Offline-Modus

**Alternativ-Ablauf 2**: Adresse in nicht hinterlegter Gemeinde
- System gibt OEREB-Daten aus, vermeidet aber Schein-Berechnung
- Datenqualitaet: NICHT_MOEGLICH mit Empfehlung "Reglement nicht hinterlegt"

### UC-2: Investor sucht Verdichtungs-Kandidaten in einer Gemeinde

**Akteur**: Investor / Bautraeger
**Vorbedingung**: BFS-Nummer oder Gemeindename bekannt
**Hauptablauf** (geplant fuer Iteration 5):
1. Investor startet Gemeinde-Analyse fuer eine Pilot-Gemeinde
2. System holt alle Parzellen via Massen-API mit Throttling
3. System fuehrt fuer jede Parzelle die Einzelanalyse durch
4. System schreibt Zwischenstaende in lokales SQLite-Cache
5. System erstellt Excel-Rangliste mit definierten Spalten
6. Investor kann Rangliste in Excel weiterverarbeiten

**Akzeptanzkriterium**: Excel-Datei mit allen Parzellen, sortierbar nach
Verdichtungs-Reserve, erfolgreich erstellt fuer Pilot-Gemeinde Oberhofen
(ca. 500 Parzellen) in unter 90 Minuten.

**Alternativ-Ablauf 1**: Lange Laufzeit, Abbruch durch User
- System schreibt jede Zwischenanalyse ins Cache
- Wiederaufnahme moeglich beim naechsten Start

**Alternativ-Ablauf 2**: Massen-API liefert nur 50 Treffer
- System nutzt nummerische Suchstrategie zum Umgehen des Limits
- (im Iter-5-Konzept empirisch verifiziert)

### UC-3: Eigentuemer prueft eigene Parzelle

**Akteur**: Eigentuemer (kein Fachwissen)
**Vorbedingung**: Eigene Adresse, Internet-Zugang
**Hauptablauf** (mit geplanter Streamlit-GUI):
1. Eigentuemer oeffnet Webseite
2. Gibt eigene Adresse ein
3. Sieht Resultat als grafische Datenqualitaets-Ampel
4. Sieht Empfehlungs-Block als Progress-Bar
5. Bei Bedarf: PDF-Export fuer eigene Unterlagen

**Akzeptanzkriterium**: Bedienung ohne baurechtliches Vorwissen moeglich,
Datenqualitaet visuell auf einen Blick erkennbar (Ampel-System).


---

## 4. Funktionale Anforderungen

Format: ID | Beschreibung | Prio | Status

Prioritaeten nach MoSCoW:
- **M** = Must have (Pflicht fuer Abgabe)
- **S** = Should have (wichtig, aber verzichtbar)
- **C** = Could have (nice to have)
- **W** = Won't have (bewusst ausgeschlossen)

Status:
- ✅ erfuellt und verifiziert
- ⚠️ teilweise erfuellt
- 🚧 in Arbeit
- ❌ offen

### 4.1 Eingabe und Geocoding

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-01 | Das System muss eine deutschsprachige Schweizer Adresse als Eingabe akzeptieren (Strasse, Hausnummer, PLZ, Ort) | M | ✅ |
| FA-02 | Das System muss eine Adresse via swisstopo SearchAPI in Geokoordinaten (LV95) uebersetzen | M | ✅ |
| FA-03 | Bei nicht eindeutigen Adressen muss das System einen aussagekraeftigen Fehler zurueckgeben | M | ✅ |
| FA-04 | Das System muss die Eingabe gegen Tippfehler robust sein (Toleranz fuer Sonderzeichen, Bindestriche) | S | ⚠️ |

**Akzeptanzkriterien**:
- 12 Test-Adressen quer durch den Kanton werden korrekt geokodiert
- Ungueltige Eingabe ergibt klare Fehlermeldung statt Stack-Trace

### 4.2 OEREB-Datenabruf

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-05 | Das System muss aus Geokoordinaten den EGRID via OEREB GetEGRID ermitteln | M | ✅ |
| FA-06 | Das System muss aus dem EGRID den vollen OEREB-Auszug via GetExtract abrufen | M | ✅ |
| FA-07 | Das System muss alle relevanten OEREB-Themen parsen: Nutzungsplanung, Naturgefahren, Baulinien, Grundwasser, ZoeN | M | ✅ |
| FA-08 | Das System muss die Parzellenflaeche, Bauklasse und Zonenbezeichnung als strukturierte Datenklassen ausgeben | M | ✅ |
| FA-09 | Bei OEREB-Webservice-Ausfall muss das System eine klare Fehlermeldung ausgeben | M | ✅ |

**Akzeptanzkriterien**:
- Alle drei OEREB-XML-Fixtures (Koeniz, Pruefen, Thun) lassen sich
  fehlerfrei parsen
- Stresstest 50 Adressen: mindestens 95% liefern strukturierte Daten

### 4.3 Reglement-Verarbeitung

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-10 | Das System muss Gemeinde-spezifische Baureglemente als JSON-Dateien laden | M | ✅ |
| FA-11 | Das System muss zwischen drei Bemessungssystemen unterscheiden: AZ, GFZo, Hoehen+GZ | M | ✅ |
| FA-12 | Das System muss Synonyme einer Zone erkennen (z.B. "W3", "Wohnen W3", "W 3") | M | ✅ |
| FA-13 | Das System muss bei nicht hinterlegter Gemeinde mit Datenqualitaet NICHT_MOEGLICH antworten | M | ✅ |
| FA-14 | Das System muss neue Gemeinden ohne Code-Aenderung unterstuetzen (nur durch JSON-Datei-Erfassung) | S | ✅ |

**Akzeptanzkriterien**:
- Drei Pilot-Gemeinden vollstaendig: Bern, Thun, Oberhofen am Thunersee
- Adresse in Spiegel/Koeniz (nicht hinterlegt) ergibt NICHT_MOEGLICH

### 4.4 Stadt-Bern-Spezialfall (BKP)

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-15 | Bei Stadt-Bern-Adressen muss das System den Bauklassenplan via ArcGIS REST-API abfragen | M | ✅ |
| FA-16 | Das System muss BKP-Layer 88 (Bauweise) und Layer 95 (Grundzonen) parzellenscharf abfragen | M | ✅ |
| FA-17 | Das System muss BKP-Werte (Gebaeudelaenge, Gebaeudetiefe) in die Schaetz-Berechnung einspeisen | M | ✅ |
| FA-18 | Das System muss klar anzeigen, welche Werte aus BKP stammen und welche aus Default-Annahmen | S | ✅ |

**Akzeptanzkriterien**:
- Sechs Stadt-Bern-Adressen (alle drei Datenqualitaets-Pfade) verifiziert
- BKP-Daten sind erkennbar als "aus BKP" markiert

### 4.5 GWR-Integration (Iteration 5, Teil 1)

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-19 | Das System muss pro Adresse die effektive Bestands-Bebauung via GWR-API abrufen | S | ✅ |
| FA-20 | Das System muss bei Parzellen mit mehreren Gebaeuden die Geschossflaechen aggregieren | S | ✅ |
| FA-21 | Das System muss unvollstaendige GWR-Datensaetze klar markieren (welche Felder fehlen) | S | ✅ |
| FA-22 | Bei GWR-API-Ausfall muss das System die Hauptanalyse trotzdem fertigstellen | M | ✅ |
| FA-23 | Das System soll Wohnungs-Anzahl, Baujahr, Heizungs-Sanierungsdatum anzeigen wenn verfuegbar | C | ✅ |

**Akzeptanzkriterien**:
- Frutigenstrasse 25 Thun: GWR-Daten korrekt (304 m^2 x 5 = 1520 m^2)
- Stresstest 50 Adressen: GWR-Anreicherung funktioniert ohne Erfolgsquoten-Verlust

### 4.6 Potenzialberechnung

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-24 | Bei AZ-System muss das System exakt rechnen: Parzelle x AZ = Geschossflaeche | M | ✅ |
| FA-25 | Bei GFZo-System muss das System exakt rechnen und Datenqualitaet VERBINDLICH setzen | M | ✅ |
| FA-26 | Bei Hoehen+GZ-System muss das System eine konservative Schaetzung mit Drei-Begrenzer-Logik durchfuehren | M | ✅ |
| FA-27 | Die Drei-Begrenzer-Logik muss aus Geometrie/Parzelle/GZ den kleinsten Wert verwenden | M | ✅ |
| FA-28 | Das System muss die Berechnungsbasis bei Schaetzungen vollstaendig offenlegen | M | ✅ |
| FA-29 | Das System muss einen Plausibilitaetscheck gegen altes AZ-Recht durchfuehren wenn hinterlegt | S | ✅ |
| FA-30 | Bei Strukturgebiet (Thun) muss das System Reduktionen anwenden | S | ✅ |
| FA-31 | Bei Arealbonus muss das System dies als Optionalwert anzeigen | C | ✅ |

**Akzeptanzkriterien**:
- Thunstrasse 40 Bern: 118 m^2 zulaessig (verifiziert gegen Bauordnung)
- Frutigenstrasse 25 Thun: 1080 m^2 Schaetzung mit transparenter Berechnungsbasis
- Strukturgebiet-Faelle in Thun korrekt erkannt

### 4.7 Datenqualitaets-Trichotomie

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-32 | Das System muss drei Datenqualitaeten unterscheiden: VERBINDLICH, GROBSCHAETZUNG, NICHT_MOEGLICH | M | ✅ |
| FA-33 | Bei VERBINDLICH muss das System exakte Zahlen ohne Schaetzungs-Banner ausgeben | M | ✅ |
| FA-34 | Bei GROBSCHAETZUNG muss das System ein deutliches Banner mit Warnung ausgeben | M | ✅ |
| FA-35 | Bei NICHT_MOEGLICH muss das System auf Schein-Berechnung verzichten und stattdessen eine Empfehlung geben | M | ✅ |
| FA-36 | Das System darf bei NICHT_MOEGLICH keinen Empfehlungs-Balken zeigen (keine Pseudo-Werte) | M | ✅ |

**Akzeptanzkriterien**:
- Stadtaltstadt Bern (Kramgasse) ergibt NICHT_MOEGLICH ohne Balken
- Thunstrasse 40 (BK_E) ergibt VERBINDLICH mit GFZo-Berechnung
- Hirschweg 7 Thun ergibt GROBSCHAETZUNG mit Banner

### 4.8 Empfehlungs-Block und Bericht

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-37 | Das System muss einen Empfehlungs-Block mit ASCII-Balken ausgeben | M | ✅ |
| FA-38 | Der Empfehlungs-Block muss vier Lagebeurteilungs-Stufen unterstuetzen (HOCH/MITTEL/GERING/AUSGESCHOEPFT) | M | ✅ |
| FA-39 | Bei Schaetzungen muss der Empfehlungs-Block mit "(geschaetzt)" markiert sein | M | ✅ |
| FA-40 | Das System muss alle relevanten OEREB-Themen im Bericht anzeigen (Naturgefahren, Baulinien, etc.) | S | ✅ |

**Akzeptanzkriterien**:
- Empfehlungs-Block in einer Sekunde visuell erfassbar
- Vier Lagebeurteilungs-Stufen klar getrennt (60%/30%/10%/0%)

### 4.9 Geplante Funktionen (Iteration 4 und 5)

| ID | Anforderung | Prio | Status |
|---|---|---|---|
| FA-41 | Das System soll eine Streamlit-GUI als Alternative zur CLI bereitstellen | S | 🚧 |
| FA-42 | Die GUI muss eine visuelle Datenqualitaets-Ampel anzeigen (gruen/orange/grau) | S | ❌ |
| FA-43 | Die GUI soll PDF-Export ermoeglichen | C | ❌ |
| FA-44 | Das System soll eine Massen-Analyse einer ganzen Gemeinde durchfuehren koennen | S | 🚧 |
| FA-45 | Die Massen-Analyse muss eine Excel-Rangliste der Verdichtungs-Kandidaten erzeugen | S | ❌ |
| FA-46 | Die Massen-Analyse muss durch SQLite-Cache wiederaufnahmefaehig sein | S | ❌ |
| FA-47 | Die Massen-Analyse muss bei jeder Parzelle einen GRUDIS-Direktlink ausgeben (kein Eigentuemer-Scraping) | M | ❌ |

**Akzeptanzkriterien fuer geplante Anforderungen**:
- FA-41 bis FA-43: Sonntag-Coding-Tag mit Fabienne als Ausgangspunkt
- FA-44 bis FA-47: Anfang Juni 2026 (Iteration 5)

---

## 5. Nicht-funktionale Anforderungen

### 5.1 Performance

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-01 | Eine Einzelabfrage muss bei intakten APIs in unter 30 Sekunden abgeschlossen sein | M | Stresstest 50 Adressen: 2.6 Sek/Adresse Mittel |
| NA-02 | Eine Massenanalyse von 500 Parzellen darf maximal 90 Minuten dauern | S | Pilottest Oberhofen geplant |
| NA-03 | Das System muss bei API-Latenzen >5 Sek mit Retry und Backoff reagieren | M | GWR-Modul implementiert exponentiellen Backoff |

### 5.2 Zuverlaessigkeit

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-04 | Stresstest mit 50 realen Adressen muss mindestens 95% Erfolgsquote erreichen | M | Aktuell 96% (48/50) |
| NA-05 | Das System muss bei einzelnen API-Ausfaellen die Pipeline nicht abbrechen | M | GWR-Ausfall ueberlebt durch try/except |
| NA-06 | Wiederholbarkeit: Gleiche Adresse muss bei wiederholten Aufrufen identisches Ergebnis liefern | M | Verifiziert durch Stresstest |

### 5.3 Datenqualitaet

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-07 | Das System darf keine VERBINDLICH-Aussage machen, wenn die Eingangsdaten unvollstaendig sind | M | Drei-Pfad-Logik in PotenzialBerechner |
| NA-08 | Das System muss bei Schaetzungen die Berechnungsbasis vollstaendig offenlegen | M | Berechnungsbasis-Block im Bericht |
| NA-09 | Reglement-JSONs muessen aus oeffentlichen Quellen verifizierbar sein | M | Quellenangabe in jedem JSON-Header |

### 5.4 Wartbarkeit

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-10 | Reglement-Daten muessen ohne Code-Aenderung pflegbar sein | S | JSON-basiert |
| NA-11 | Neue Gemeinden muessen ohne Eingriff in den Berechnungs-Code aufnehmbar sein | S | baureglement.py automatisch |
| NA-12 | Module muessen testbar in Isolation sein | S | Tests/Fixtures vorhanden |
| NA-13 | Code muss in Python 3.13 lauffaehig sein, ohne externe Abhaengigkeiten ausser explizit gelistet | M | requirements.txt |

### 5.5 Bedienbarkeit

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-14 | CLI-Bedienung muss ohne Programmierkenntnisse moeglich sein | S | Ein Aufruf, ein Adress-Argument |
| NA-15 | Tool-Ausgabe muss ohne baurechtliches Vorwissen verstaendlich sein | S | Verbale Lagebeurteilungen |
| NA-16 | Geplante GUI muss mit max. 3 Klicks zum Resultat fuehren | C | Iter 4 Akzeptanzkriterium |

### 5.6 Datenschutz und Rechtliches

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-17 | Das System darf keine personenbezogenen Eigentuemerdaten speichern oder weiterverarbeiten | M | "Bruecken-Ansatz": GRUDIS-Link statt Scraping |
| NA-18 | GWR-Daten duerfen nur zur Anzeige verwendet werden, nicht persistent gespeichert | M | Cache nur In-Memory |
| NA-19 | Das System muss bei jeder Verbindlich-Aussage einen Disclaimer ausgeben ("ersetzt keine rechtsverbindliche Auskunft") | M | Bericht-Footer |
| NA-20 | Schaetz-Werte muessen explizit als nicht-investitions-tauglich markiert sein | M | Banner bei GROBSCHAETZUNG |

### 5.7 Externe Abhaengigkeiten

| ID | Anforderung | Prio | Messbar |
|---|---|---|---|
| NA-21 | Das System soll bei OEREB-Ausfall mit Fixture-Daten arbeiten koennen (Demo-Modus) | C | tests/fixtures/ vorhanden |
| NA-22 | Das System muss API-Anfragen an externe Dienste rate-limit-freundlich gestalten (Throttling) | M | GWR-Modul mit Throttling |
| NA-23 | Das System muss zu API-Anbietern faire Nutzung sicherstellen (kein aggressives Scraping) | M | Massen-Analyse mit Caching geplant |

---

## 6. Implizite Annahmen — explizit gemacht

Diese Sektion ist Kernstueck der Anforderungs-Pruefung. Sie macht
Annahmen sichtbar, die der Code stillschweigend trifft, und bewertet
ihre Berechtigung.

### 6.1 Annahmen ueber Adressen

| ID | Annahme | Berechtigung | Risiko |
|---|---|---|---|
| AN-01 | Eine Adresse fuehrt zu genau einer Parzelle | Meistens, aber Eckhaeuser sitzen oft auf zwei Parzellen | Mittel — Tool nimmt erste Parzelle, ohne dies zu erwaehnen |
| AN-02 | Postleitzahl impliziert eindeutige Gemeinde | Stimmt fuer 95% der CH-Adressen, aber PLZ-Grenzen koennen Gemeindegrenzen kreuzen | Niedrig |
| AN-03 | Strassenname plus PLZ ist eindeutig | Es gibt Doppelungen ("Bahnhofstrasse" in vielen Orten) | Gering — swisstopo loest das |

### 6.2 Annahmen ueber Reglemente

| ID | Annahme | Berechtigung | Risiko |
|---|---|---|---|
| AN-04 | Manuell erfasste JSON-Werte stimmen mit Original-PDF ueberein | Nur durch externe Verifikation absicherbar | Hoch — Stichprobenpruefung durch Architekten geplant |
| AN-05 | Eine Zone hat genau ein Bemessungssystem | Stimmt im Kanton Bern; Mischzonen sind selten | Niedrig |
| AN-06 | Synonym-Erkennung deckt alle Schreibvarianten ab | Iter 3 hat 5 Varianten ergaenzt; weitere moeglich | Mittel — Stresstest deckt das ab |
| AN-07 | Reglemente aendern sich seltener als das Tool gepflegt wird | Ortsplanungen werden alle 10-15 Jahre revidiert | Niedrig fuer Pruefung, hoch fuer Langzeit-Betrieb |

### 6.3 Annahmen ueber Schaetzungen

| ID | Annahme | Berechtigung | Risiko |
|---|---|---|---|
| AN-08 | Ist-Bebauung 25% als Platzhalter | Reine Heuristik ohne Quelle | Hoch — durch GWR-Modul jetzt teilweise gemildert |
| AN-09 | Parzellen-Form 1:1.5 fuer Schaetz-Berechnung | Plausibel als Mittelwert, aber abweichend bei extrem schmalen Parzellen | Mittel — durch BKP-Daten in Bern teilweise korrigierbar |
| AN-10 | Dachgeschoss-Bonus 60% Geschossflaeche | Konservative Annahme, BR2022 Thun erlaubt mehr | Niedrig — Konservativitaet ist gewollt |
| AN-11 | Drei-Begrenzer-Logik: kleinster gewinnt | Rechtlich richtig (jede einzeln muss eingehalten werden) | Niedrig — explizit so dokumentiert |

### 6.4 Annahmen ueber externe APIs

| ID | Annahme | Berechtigung | Risiko |
|---|---|---|---|
| AN-12 | OEREB-Webservice ist verfuegbar | Stimmt im Normalbetrieb, kann bei Demo ausfallen | Mittel — Mitigation via Fixtures |
| AN-13 | swisstopo SearchAPI hat keine Rate-Limits fuer Einzelabfragen | Stimmt, aber dokumentiert sind 50 Treffer Limit fuer Massensuche | Hoch fuer Iter 5 — Nummerische Suchstrategie als Loesung |
| AN-14 | GWR-Daten sind aktuell | Stimmt grundsaetzlich, aber Sanierungsdaten haben Updates-Latenz | Niedrig — Tool zeigt Sanierungsdatum transparent |
| AN-15 | BKP-Daten der Stadt Bern sind vollstaendig | Manche Parzellen haben fehlende Felder (Spezialregime) | Mittel — durch NICHT_MOEGLICH abgefangen |

### 6.5 Annahmen ueber die Tool-Ausgabe

| ID | Annahme | Berechtigung | Risiko |
|---|---|---|---|
| AN-16 | "VERBINDLICH" wird vom User als rechtsverbindlich verstanden | Falsch! VERBINDLICH meint "berechnungs-verbindlich" | Mittel — durch Disclaimer mitigieren |
| AN-17 | ASCII-Balken sind in jedem Terminal lesbar | Stimmt fuer cmd.exe, PowerShell, Bash; Unicode-Probleme moeglich | Niedrig — UnicodeEncodeError nur bei Sonderzeichen wie ∞ aufgetreten |
| AN-18 | GROBSCHAETZUNG ist konservativ (eher zu wenig) | Durch GWR teilweise widerlegt: Frutigenstrasse 25 zeigt Realitaet > Schaetzung | Mittel — eroeffnet aber genau den interessanten Plausibilitaets-Konflikt |

---

## 7. Konflikt-Analyse

Anforderungen sind nicht widerspruchsfrei. Folgende Konflikte wurden
identifiziert und mit Loesungs-Strategien adressiert:

### KF-1: Genauigkeit vs. Geschwindigkeit
**Beteiligte Anforderungen**: NA-01 (Performance) vs. FA-15-18 (BKP-Anreicherung)
und FA-19-23 (GWR)
**Konflikt**: Mehr Datenquellen verbessern Genauigkeit, kosten aber Zeit.
**Loesung**: Caching im GWR-Modul (MAX_CACHE_SIZE=5000), parallele
API-Aufrufe wo moeglich, klare Performance-Budgets pro Komponente.
Aktueller Stand: 2.2 Sek pro Adresse mit allen drei Quellen.

### KF-2: Massenanalyse vs. Datenanbieter-Interessen
**Beteiligte Anforderungen**: FA-44 (Massen-Analyse Gemeinde) vs. NA-22-23
(faire Nutzung externer APIs)
**Konflikt**: 500 Parzellen abfragen kann als Scraping interpretiert werden.
**Loesung**: Throttling 0.5-1 Sek zwischen Anfragen, lokales SQLite-Cache,
einmalige Erfassung pro Lauf, Zwischenstaende speichern.
Empirisch verifiziert in Iter-5-Konzept (722 Zeilen).

### KF-3: Eigentuemer-Identifikation vs. Datenschutz
**Beteiligte Anforderungen**: UC-2 (Investor sucht Kandidaten) vs. NA-17-18
(kein Eigentuemer-Scraping)
**Konflikt**: Investor will Eigentuemer kontaktieren, aber wir wollen
keine Datenschutz-relevante Sammlung anlegen.
**Loesung**: "Bruecken-Ansatz" — Tool zeigt nur oeffentliche Parzellendaten
und einen GRUDIS-Direktlink. User loggt sich selber ein und macht die
Recherche manuell. Tool speichert nichts.

### KF-4: Schaetz-Konservativitaet vs. Realitaets-Naehe
**Beteiligte Anforderungen**: FA-26 (konservative Schaetzung) vs. AN-18
(Realitaet kann hoeher sein)
**Konflikt**: Konservativ ist sicher (rechtlich), aber unterschaetzt das
echte Potenzial bei Bestandsbauten mit historisch hoher Ausnuetzung.
**Loesung**: GWR-Daten zeigen die Diskrepanz transparent an. User sieht
Soll und Ist parallel und kann die Spannung selbst einschaetzen.
Beispiel Frutigenstrasse 25: 1080 m^2 Soll vs. 1520 m^2 Ist.

### KF-5: Verstaendlichkeit vs. Praezision
**Beteiligte Anforderungen**: NA-15 (ohne baurechtliches Vorwissen) vs.
FA-32 (Datenqualitaets-Trichotomie als Konzept)
**Konflikt**: Begriffe wie "GFZo", "VERBINDLICH" sind nicht selbsterklaerend.
**Loesung**: Verbale Lagebeurteilungen statt nur Zahlen, Glossar im Bericht-
Footer, geplante GUI mit Tooltips und Ampel-Symbolik.


