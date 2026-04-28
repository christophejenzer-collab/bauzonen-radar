# Konzept: Bauzonen-Radar

Pflichtdokument zum Python-Abschlussprojekt.
Stand: 28. April 2026.

## Projektidee

Ein Tool, das fuer eine Schweizer Adresse automatisch das
baurechtliche Potenzial einer Parzelle ermittelt. Architekten,
Investoren und Eigentuemer sollen schnell sehen, was auf einem
Grundstueck rechtlich moeglich ist und wie viel Reserve gegenueber
der Ist-Bebauung besteht.

## Problem

Wer heute in der Schweiz wissen will, was auf einer Parzelle
gebaut werden darf, muss:

- die Parzellen-Nummer aus dem kantonalen Geoportal heraussuchen
- den OEREB-Auszug (oeffentlich-rechtliche Eigentumsbeschraenkungen)
  studieren
- das Gemeinde-Baureglement lesen
- die richtige Bauklasse oder Zone zuordnen
- die Kennzahlen (AZ, GFZo, Hoehen, Grenzabstaende) in eine
  Berechnung umsetzen

Das ist Spezialwissen. Bauzonen-Radar buendelt diese Schritte in
einer Adress-Abfrage.

## Loesung

Eine Python-Pipeline, die folgendes leistet:

1. **Geocoding**: Adresse zu Koordinaten via swisstopo SearchAPI
2. **OEREB-Abfrage**: Parzellen- und Zonen-Daten via Kanton Bern
   OEREB-Webservice
3. **XML-Parsing**: Strukturierte Datenklassen fuer Parzelle,
   Restrictions, Bauklassen, Naturgefahren etc.
4. **Reglement-Matching**: Passendes Gemeinde-JSON laden, Zone
   und Bauklasse zuordnen
5. **Potenzialberechnung**: Theoretisch zulaessig vs. geschaetzt
   realisiert. Status HOCH / MITTEL / GERING / AUSGESCHOEPFT
6. **Bericht**: Strukturierter Textbericht mit allen relevanten
   Hinweisen (Naturgefahren, Strukturgebiet, Arealbonus, ...)

## Drei Bemessungssysteme

Eine Besonderheit des Schweizer Baurechts: Es gibt nicht ein
einheitliches Mass, sondern mehrere parallele Systeme, die je
nach Gemeinde und Reglement-Stand greifen. Das Tool unterstuetzt
alle drei:

| System | Beschreibung | Beispiel |
|---|---|---|
| **AZ** | Klassische Ausnuetzungsziffer | altes Recht, viele Gemeinden |
| **GFZo** | Geschossflaechenziffer oberirdisch | Stadt Bern, IVHB-konform |
| **Hoehen + GZ** | Steuerung ueber Gebaeudemasse | Stadt Thun BR 2022 |
| **Hoehen** | Nur Vollgeschosse + Hoehen | Oberhofen BR 2012 |

## Aufgabenverteilung

Das Projekt wird im Zweier-Team bearbeitet:

### Christophe "Matis" Jenzer
- Backend-Entwicklung (Python-Pipeline)
- OEREB-Webservice-Anbindung
- XML-Parser
- Reglement-Daten-Erfassung (Stadt Bern, Stadt Thun, Oberhofen)
- Potenzialberechnung mit Drei-System-Modell
- Spezialfall-Behandlung (Strukturgebiet, Arealbonus, Naturgefahren)

### Fabienne
- Dokumentation des gesamten Projekts
- Streamlit-Webseite fuer komfortable Adress-Abfrage (Iteration 4)
- Requirements-Engineering-Pruefung: systematische Pruefung der
  Anforderungen auf Vollstaendigkeit, Eindeutigkeit, Testbarkeit
- Identifikation impliziter Annahmen im Code
- Erstellung einer formalen Anforderungs-Spezifikation in
  `docs/anforderungen.md` (geplant)

## Werkzeuge und Hilfsmittel

### Datenkomplexitaet als Herausforderung

Das Schweizer Baurecht ist hochkomplex: drei Bemessungssysteme
parallel (AZ/GFZo/Hoehen+GZ), gemeindespezifische Reglemente,
kantonale Uebergangsphasen, Spezialregimes fuer Altstaedte und
Schutzgebiete. Eine korrekte Umsetzung erfordert exakte Werte
aus offiziellen Reglementen. Schaetzungen oder Annahmen wuerden
zu falschen Ergebnissen fuehren, die einem Architekten oder
Investor schaden wuerden.

### Einsatz von KI-Assistenten

Fuer die Erstellung dieses Projekts wurde Claude.AI (Anthropic)
als Programmier-Assistent eingesetzt. Konkret unterstuetzte Claude:

- Architektur-Entscheidungen (z.B. Drei-Systeme-Modell)
- Code-Generierung fuer Datenklassen, Parser, Berechnungslogik
- Strukturierung der Reglement-JSONs
- Recherche und Verifikation gegen offizielle Quellen (Bauordnung
  Stadt Bern, Baureglement Stadt Thun, Baureglement Oberhofen)
- Dokumentations-Erstellung
- Bug-Diagnose und iterative Verbesserung

Die fachlichen Entscheidungen, die Verifikation der Werte gegen
die echten Reglemente und die finale Architektur lagen beim
Projektteam. Eine externe Verifikation der eingepflegten Werte
durch einen Architekten (Schwager des Projektleiters, Fachperson
in Thun) ist Teil der laufenden Iteration 3.

## Iterationen

### Iteration 1: Pipeline (abgeschlossen)
**Ziel**: Adresse rein, Parzelle und Zonen-Daten raus.

**Ergebnis**:
- swisstopo Geocoding funktioniert
- OEREB-Webservice abgerufen
- XML in strukturierte Datenklassen geparst
- 10 Test-Adressen liefern korrekte Parzellen-Daten

### Iteration 2: Potenzialberechnung (abgeschlossen)
**Ziel**: Mit Reglement-Daten echte Berechnung durchfuehren.

**Ergebnis**:
- Drei Bemessungssysteme im Datenmodell verankert
- Drei Gemeinden vollstaendig hinterlegt: Bern, Thun, Oberhofen
- Erste echte GFZo-Berechnung erfolgreich (Thunstrasse 40 Bern:
  118 m^2 zulaessig, 80% Ausschoepfung, Status GERING)
- Hoehen-System mit und ohne Gruenflaechenziffer funktional
- Strukturgebiet- und Arealbonus-Erkennung implementiert

### Iteration 3: Verifikation und Vervollstaendigung (laufend)
**Ziel**: Echte Werte aus dem Bauklassenplan Bern einpflegen,
Tool-Output durch Architekt-Schwager validieren lassen.

**Aufgaben**:
- Schwager liefert GFZo-Werte fuer Stadt Bern Bauklassenplan
- Erfassungs-Excel `docs/erfassung_baureglemente.xlsx` mit acht
  Tabellen ist vorbereitet
- Mit echten Werten in `bern.json` vollstaendig rechnen koennen
- Fabienne: erste Anforderungs-Liste erstellen

### Iteration 4: Webseite (geplant)
**Ziel**: Streamlit-GUI fuer Endanwender.

**Verantwortlich**: Fabienne.

**Vorgesehen**:
- Eingabefeld fuer Adresse
- Visualisierung der Parzelle (Kartenausschnitt)
- Strukturierte Ergebnisanzeige
- PDF-Export fuer Kundendossier

## Bewertungskriterien (laut Kursvorgabe)

| Bereich | Punkte |
|---|---|
| Konzept-Dokument und Dokumentation | 20 |
| Python-Programm | 50 |
| Praesentation und Live-Demo | 10 |
| Fragen zum Code | 20 |
| **Total** | **100** |

## Zeitplan

- 28.04.2026 - Aufgabenverteilung mit Fabienne abgestimmt
- bis Mai - Iteration 3 abgeschlossen, Bern-Bauklassenplan komplett
- Mai-Juni - Iteration 4 (Webseite) durch Fabienne
- Mitte Juni - Generalprobe Live-Demo
- 17.06.2026 - Abgabe und Praesentation (5 Min Pitch + Demo +
  Code-Fragen)

## Aktueller Stand (28.04.2026)

- Pipeline End-to-End funktional
- Drei Gemeinden mit drei verschiedenen Bemessungssystemen
  abgedeckt
- Code in privates GitHub-Repo eingecheckt
- Vier Dokumente im `docs/`-Ordner gepflegt
- Zehn Test-Adressen verifiziert
- Mitstudentin Fabienne fest an Bord
