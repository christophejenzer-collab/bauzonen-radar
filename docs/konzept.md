# Konzept-Dokument: Bauzonen-Radar

**Abschlussprojekt Python-Kurs, Frühjahr 2026**
**Abgabe: 17. Juni 2026**

---

## 1. Projektname und Team

**Projektname:** Bauzonen-Radar

**Team:**
- Christophe Jenzer (christophejenzer@gmail.com)
- [Name Mitstudentin] ([E-Mail Mitstudentin])

**Externer Fachpate:** [Name Schwager], Architekt, [Name Architekturbüro]
*Unterstützt das Projekt mit Fachwissen zu Schweizer Baurecht und stellt reale Testfälle zur Verfügung. Bewertet die fachliche Korrektheit der Tool-Ausgaben.*

**Repository:** https://github.com/christophejenzer-collab/bauzonen-radar

---

## 2. Projektbeschreibung

### Was

Der Bauzonen-Radar ist ein Python-Tool zur Analyse ungenutzten Bebauungspotenzials auf Schweizer Grundstücken. Für eine beliebige Adresse im Kanton Bern liefert es in Sekunden:

- Die aktuelle Zonierung und Baureglement-Parameter
- Alle relevanten baurechtlichen Einschränkungen (Überlagerungen, Naturgefahren, Baulinien, Denkmalschutz)
- Eine systemspezifische Potenzialabschätzung (AZ, GFZo oder Höhen + Grünflächenziffer)
- Automatische Warnhinweise zu einschränkenden Faktoren

### Wie

Die Kernpipeline verbindet drei öffentliche Datenquellen der Schweizer Behörden:

1. **swisstopo SearchAPI** zur Umwandlung einer Adresse in LV95-Koordinaten
2. **ÖREB-Webservice des Kantons Bern** (`oereb2.apps.be.ch`) zur Abfrage von Grundstück-ID und allen raumrelevanten Beschränkungen gemäss OEREB-Schema V2.0
3. **Gemeindespezifische Baureglemente** (manuell erfasst als JSON), die die Ausnützungsziffern, Gebäudehöhen und weitere Parameter pro Zone enthalten

Das Tool kombiniert diese Daten zu einem strukturierten Fach-Dossier pro Parzelle.

### Warum

Die Schweizer Raumplanung fordert Siedlungsentwicklung nach innen. Architekturbüros, Gemeindeplaner und Immobilienentwickler müssen heute systematisch prüfen, wo Grundstücke ihr zulässiges Bebauungspotenzial nicht ausschöpfen. Die dafür notwendigen Daten sind öffentlich zugänglich, aber über viele Portale verstreut und nur mit Fachwissen interpretierbar. Jede Vorprüfung einer Parzelle kostet einen Architekten heute zwischen 30 Minuten und mehreren Stunden Recherchearbeit.

Der Bauzonen-Radar komprimiert diese Vorprüfung auf wenige Sekunden und stellt die relevanten Fachthemen in einer für Architekten direkt nutzbaren Form dar.

### Persönliche Relevanz

Christophe arbeitet 10% als freier Mitarbeiter im Architekturbüro seines Schwagers und erhält dort direkten Zugang zu realen Anwendungsfällen. Das Tool wird im Büro als Arbeitsmittel zur Deal-Identifikation getestet. Die fachliche Tiefe des Projekts (Systemwechsel im Berner Baurecht, OEREB-Schema) entsteht aus diesem Austausch.

---

## 3. Iterativer Projektplan

Das Projekt folgt einem iterativen Ansatz in klar abgegrenzten Sprints. Jede Iteration schliesst mit einem funktionsfähigen Teilresultat ab, das getestet und dokumentiert wird.

### Abgeschlossene Iterationen

**Iteration 1: Datenzugang (abgeschlossen)**
- ÖREB-Webservice-Client für den Kanton Bern
- XML-Parser für das OEREB-Schema V2.0
- Datenmodell für Parzellen und Beschränkungen
- Getestet in vier Gemeinden

**Iteration 2: Fachdomäne abbilden (abgeschlossen)**
- Baureglement-Lade-Modul mit drei Matching-Strategien
- Mehrsystem-Modell (AZ, GFZo, Höhen + Grünflächenziffer)
- Dualitäts-Behandlung für Übergangsphasen
- Umfassende Fachdokumentation

**Iteration 3: Potenzialberechnung (abgeschlossen)**
- Kombinierte Analyse: OEREB-Daten + Baureglement + Risikohinweise
- CLI-Hauptschnittstelle
- Automatische Warnhinweise zu einschränkenden Faktoren

### Geplante Iterationen

**Iteration 4: Daten vervollständigen (geplant bis [Datum])**
- Einpflegen konkreter Kennzahlen für Stadt Bern (AZ/GFZo pro Bauklasse)
- Einpflegen konkreter Kennzahlen für Thun (Gebäudehöhen, Grünflächenziffer)
- Verifikation mit Architekturbüro
- **Verantwortlich:** Christophe (Recherche mit Schwager)

**Iteration 5: Benutzeroberfläche (geplant bis [Datum])**
- Einfache grafische Oberfläche mit Streamlit
- Eingabeformular und strukturierte Ausgabe
- Kartenvisualisierung der Parzelle
- **Verantwortlich:** [Mitstudentin] mit Unterstützung Christophe

**Iteration 6: Rangliste (geplant bis [Datum])**
- Analyse mehrerer Adressen nacheinander
- Sortierung nach Reserve-Potenzial
- Export als Tabelle (CSV/Excel)
- **Verantwortlich:** [noch zu klären]

**Iteration 7: Abgabe-Vorbereitung (geplant bis [Datum])**
- Präsentation erstellen (5 Min + Demo)
- Code-Review und letzter Feinschliff
- Live-Demo mit drei realen Adressen einüben
- Mögliche Fragen zum Code vorbereiten
- **Verantwortlich:** Beide**

### Minimalziel

Das Minimalziel ist **erreicht** und besteht aus den Iterationen 1–3. Das Tool kann:

- [x] Eine Adresse im Kanton Bern entgegennehmen
- [x] Die Parzelle via offiziellen ÖREB-Webservice abrufen
- [x] Alle OEREB-Kategorien parsen (6 Typen)
- [x] Strukturierte Textausgabe liefern
- [x] Baureglement einer Gemeinde laden
- [x] Systemspezifische Potenzialanalyse durchführen
- [x] Qualitative Warnhinweise ausgeben

Die Iterationen 4–7 setzen auf diesem Fundament auf und erhöhen die Reife und Präsentierbarkeit des Projekts.

### Erweiterte Ziele (ausserhalb des Minimalziels)

*Ideen für spätere Iterationen, sollten Zeit und Interesse bleiben:*

- Integration der Gebäude-Grundflächen aus swissBUILDINGS3D für eine echte Ist-Bebauungs-Berechnung
- Erweiterung auf den Kanton Zürich (Validierung der Kantons-Abstraktion)
- PDF-Export für Kundendossiers
- Filter für "alle Parzellen mit laufenden Zonenänderungen" über ein Gemeindegebiet
- Integration weiterer Gemeinden (Köniz, Steffisburg, Münsingen)

---

## 4. Teamarbeit: Wer macht was

### Aufgabenverteilung

**Christophe Jenzer:**
- Core-Architektur und Datenmodell
- ÖREB-Pipeline (Datenbeschaffung und Parser)
- Baureglement-Modul und JSON-Daten
- Koordination mit Architekturbüro
- Fachliche Dokumentation

**[Name Mitstudentin]:**
- [Noch mit Mitstudentin abzusprechen]
- [Beispiele: GUI-Entwicklung mit Streamlit, Kartenvisualisierung, Tests, Rangliste-Feature]

### Kollaborations-Werkzeuge

- **Git/GitHub:** Version Control und Code-Review
- **Dokumentation:** Markdown-Dateien im Repo (`docs/`)
- **Kommunikation:** [noch festzulegen — z.B. WhatsApp, Signal, E-Mail]
- **Treffen:** [noch festzulegen — z.B. wöchentlich online, zweiwöchentlich persönlich]

### Git-Workflow

- Neue Features entstehen auf Feature-Branches
- Pull Requests werden vom Partner gereviewed, bevor sie in `main` gemerged werden
- Commit-Nachrichten auf Deutsch, im Imperativ, prägnant
- Regelmässige Synchronisation mindestens alle paar Tage

### Code-Standards

- Python 3.11+
- Typisierung (type hints) wo sinnvoll
- Docstrings für öffentliche Module, Klassen und Methoden
- Keine externen Abhängigkeiten ohne Absprache
- Code auf Deutsch kommentiert (das Projekt ist in deutscher Sprache)

---

## 5. Risiken und Unklarheiten

*Transparente Benennung der offenen Punkte, die das Projekt beeinflussen können:*

### Fachliche Risiken

- **Baureglement-Werte:** Die konkreten AZ-/GFZo-Werte sind mit dem Architekturbüro zu verifizieren. Solange diese Werte fehlen, gibt das Tool nur qualitative Einschätzungen. Plan: Verifikation bis spätestens [Datum].

- **Systemwechsel-Stand:** Der Umstellungsstand der Stadt Bern auf GFZo ist unklar. Das Datenmodell ist auf Dualität vorbereitet, aber die konkrete Zuordnung muss aus offiziellen Quellen erfolgen.

### Technische Risiken

- **ÖREB-API-Verfügbarkeit:** Das Tool ist von der Verfügbarkeit der kantonalen ÖREB-Dienste abhängig. Bei Ausfall ist keine Abfrage möglich. Mitigation: Das Tool meldet klar, wenn ein Dienst nicht erreichbar ist.

- **Format-Änderungen:** Die SubCode-Konventionen der Gemeinden können sich ändern. Der Parser ist robust, aber nicht unverwundbar. Mitigation: Diagnose-Skript `xml_speichern.py` erlaubt schnelle Anpassung.

### Organisatorische Risiken

- **Abstimmung im Team:** Zwei Personen mit eigenem Alltag – verlässliche Kommunikation ist entscheidend. Plan: Regelmässige Treffen und klare Aufgabenverteilung.

---

## 6. Referenzen

- **README.md** – Einstieg und Anleitung
- **docs/fachliche_grundlagen.md** – Detaildokumentation zum Berner Baurecht
- **docs/journal.md** – Entwicklungstagebuch pro Session
- **OEREB-Webservice Kanton Bern:** https://www.oereb2.apps.be.ch/
- **IVHB (Interkantonale Vereinbarung):** BSG 721.2-1
- **BauG / BauV Kanton Bern:** BSG 721.0 / 721.1

---

*Dieses Konzept-Dokument ist Teil der Projektabgabe und wird parallel zur Entwicklung aktualisiert. Änderungen werden via Git-Commits mit klaren Nachrichten dokumentiert.*
