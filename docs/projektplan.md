# Projektplan Bauzonen-Radar

**Abgabedatum: 17. Juni 2026**
**Heute: 24. April 2026**
**Verbleibend: 7 Wochen, 6 Tage**

---

## Übersicht

| Woche | Zeitraum | Thema | Hauptverantwortlich |
|---|---|---|---|
| 1 | 25. April – 1. Mai | Team-Kickoff und Datengrundlage | Beide |
| 2 | 2. – 8. Mai | Baureglement-Daten verifizieren | Christophe |
| 3 | 9. – 15. Mai | GUI-Grundgerüst | [Mitstudentin] |
| 4 | 16. – 22. Mai | GUI-Feinschliff, Rangliste-Feature | Beide |
| 5 | 23. – 29. Mai | Tests und Code-Review | Beide |
| 6 | 30. Mai – 5. Juni | Präsentation vorbereiten | Beide |
| 7 | 6. – 12. Juni | Live-Demo üben, Puffer | Beide |
| 8 | 13. – 16. Juni | Finaler Feinschliff | Beide |
| **17. Juni** | **ABGABE** | | |

---

## Woche 1: Team-Kickoff und Datengrundlage
**25. April – 1. Mai**

### Ziele

- Beide Teammitglieder sind aufeinander eingespielt
- Konzept-Dokument gemeinsam abgestimmt und im Repo
- Erste Gespräche mit Schwager geführt
- Erste konkrete Baureglement-Werte erfasst

### Aufgaben

**Christophe:**
- [ ] Erstgespräch mit Schwager: reale AZ-Werte für Stadt Bern erheben (mindestens Bauklasse B und C, konkrete Wohnzonen)
- [ ] Schwager um Test-Adressen bitten: 3-5 reale Parzellen aus der Bürokartei
- [ ] Konzept-Dokument gemeinsam mit Mitstudentin finalisieren und committen

**[Mitstudentin]:**
- [ ] Projekt lokal aufsetzen (git clone, venv, Installation)
- [ ] Code und Dokumentation lesen, Verständnisfragen sammeln
- [ ] Streamlit-Tutorial durcharbeiten (2-3 Stunden)
- [ ] GitHub-Zugang zum Repo einrichten

**Gemeinsam:**
- [ ] Aufgabenverteilung im Konzept-Dokument präzisieren
- [ ] Kommunikations-Kanal festlegen
- [ ] Regelmässiger Treffpunkt definieren (z.B. jeden Sonntag 19:00 online)

### Resultat am Ende der Woche

- Konzept-Dokument vollständig im Repo
- Erste echte Baureglement-Werte in `bern.json`
- Mitstudentin ist im Code unterwegs und hat Streamlit-Grundlagen

---

## Woche 2: Baureglement-Daten verifizieren
**2. – 8. Mai**

### Ziele

- Stadt Bern: mindestens die drei häufigsten Zone-Bauklasse-Kombinationen haben konkrete AZ-Werte
- Stadt Thun: mindestens drei Zonen nach BR 2022 haben konkrete Gebäudehöhen und Grünflächenziffern
- GUI-Konzept skizziert

### Aufgaben

**Christophe:**
- [ ] Mit Schwager: AZ-Werte für Wohnzone W × Bauklasse B/C/D einpflegen
- [ ] Mit Schwager: Werte für Wohn- und Gewerbezone einpflegen
- [ ] Thun-Werte aus BR 2022 recherchieren (Grünflächenziffer-Merkblatt, Baubewilligungs-Leitfaden)
- [ ] Journal-Eintrag pro Session

**[Mitstudentin]:**
- [ ] GUI-Wireframe auf Papier oder digital skizzieren
- [ ] Entscheidung: Single-Page-App oder mit Navigation?
- [ ] Mock-Screens der gewünschten Benutzerführung
- [ ] Streamlit-Installation im venv

**Gemeinsam:**
- [ ] GUI-Konzept besprechen: was soll sichtbar sein, in welcher Reihenfolge?
- [ ] Mid-Week-Check: Was funktioniert, wo hakt es?

### Resultat am Ende der Woche

- Erste Potenzialanalysen mit echten Zahlen möglich
- GUI-Konzept steht auf Papier

---

## Woche 3: GUI-Grundgerüst
**9. – 15. Mai**

### Ziele

- Streamlit-App läuft lokal
- Eingabefeld für Adresse, Anzeige der Parzellen-Infos
- Erste Version der Ausgabe (Text-basiert, formatiert)

### Aufgaben

**[Mitstudentin] (Hauptverantwortung GUI):**
- [ ] `src/bauzonenradar/gui/app.py` als neue Streamlit-App
- [ ] Eingabe: Adress-Textfeld, Analyse-Button
- [ ] Aufruf der bestehenden `analyse_adresse.analysiere()`-Funktion
- [ ] Strukturierte Anzeige des Ergebnisses
- [ ] README ergänzen mit GUI-Start-Befehl

**Christophe:**
- [ ] `analyse_adresse.py` so refactoren, dass Ergebnis als strukturiertes Objekt zurückkommt, nicht nur print-Ausgabe (falls noch nicht geschehen)
- [ ] Mitstudentin bei Code-Verständnis unterstützen
- [ ] Weitere Baureglement-Werte einpflegen

**Gemeinsam:**
- [ ] Erste GUI-Demo bei Treffen am Wochenende
- [ ] Feedback einarbeiten

### Resultat am Ende der Woche

- Funktionsfähige GUI, die bestehende CLI-Funktionalität visualisiert

---

## Woche 4: GUI-Feinschliff, Rangliste-Feature
**16. – 22. Mai**

### Ziele

- GUI zeigt alle wichtigen Infos strukturiert und mit Farben/Icons
- Feature "mehrere Adressen vergleichen" ist implementiert
- Erste richtige Demo-fähigkeit

### Aufgaben

**[Mitstudentin]:**
- [ ] GUI-Verfeinerung: Icons für Warnhinweise, farbige Status-Anzeige
- [ ] Integration einer einfachen Karte (z.B. `st.map` mit der Parzellen-Koordinate)
- [ ] Export-Button für Report als Text

**Christophe:**
- [ ] Rangliste-Modul: `analyse/rangliste.py` mit Klasse `ParzellenRangliste`
- [ ] Nimmt Liste von Adressen, gibt sortierte Tabelle zurück
- [ ] Sortierung nach: Reserve-Potenzial, Parzellenfläche, Zonenvielfalt

**Gemeinsam:**
- [ ] Demo-Adressen-Liste vorbereiten: 5-10 reale Adressen aus Bern und Thun
- [ ] Test der Rangliste-Funktionalität

### Resultat am Ende der Woche

- Volltaugliche Demo-Version mit GUI und Rangliste

---

## Woche 5: Tests und Code-Review
**23. – 29. Mai**

### Ziele

- Kritische Module haben Unit-Tests
- Code-Qualität auf Abgabe-Niveau
- Dokumentation vollständig und konsistent

### Aufgaben

**Beide:**
- [ ] Pytest-Tests für `baureglement.py`: Matching-Logik, Systemerkennung
- [ ] Tests für `potenzial.py`: Berechnung bei AZ, GFZo, ohne Kennzahl
- [ ] Tests für `modelle.py`: Filter-Methoden, Lawstatus-Parsing
- [ ] Code-Review: Gegenseitiges Durchgehen von allen Modulen
- [ ] README final polieren
- [ ] Konzept-Dokument: alle Platzhalter ausfüllen

**Christophe:**
- [ ] Schwager um Feedback bitten: "Was fehlt noch, was ist falsch?"
- [ ] Journal komplett nachziehen, falls Einträge fehlen

### Resultat am Ende der Woche

- Repo ist im "Abgabe-Ready"-Zustand (technisch)

---

## Woche 6: Präsentation vorbereiten
**30. Mai – 5. Juni**

### Ziele

- Präsentation steht (5 Minuten)
- Demo-Ablauf ist geübt
- Fragen zum Code sind vorbereitet

### Aufgaben

**Beide:**
- [ ] Präsentations-Outline:
  - Pitch (1 Min): Was macht das Tool, warum relevant
  - Einblick Projektarbeit (2 Min): Teamwork, Architektur, Systemwechsel
  - Live-Demo (2 Min): Drei reale Adressen
  - 3 Fragen zum Code vorbereiten
- [ ] Slides erstellen (max. 5-7 Folien, klares Design)
- [ ] Rollen in der Präsentation definieren: Wer spricht wann?

**Christophe:**
- [ ] Code-Struktur visualisieren: Modul-Abhängigkeitsdiagramm für die Slides
- [ ] Mögliche Fachfragen antizipieren: Warum dieses Datenmodell? Warum drei Systeme?

**[Mitstudentin]:**
- [ ] Mögliche Python-Fragen antizipieren: Warum Dataclasses? Warum Enum? Warum type hints?

### Resultat am Ende der Woche

- Vollständige Präsentation inkl. Demo-Skript

---

## Woche 7: Live-Demo üben, Puffer
**6. – 12. Juni**

### Ziele

- Demo läuft zuverlässig in unter 2 Minuten
- Präsentation hält 5 Minuten ein
- Beide Teammitglieder kennen beide Rollen (Backup)

### Aufgaben

**Beide:**
- [ ] Mindestens dreimal komplett durchproben
- [ ] Stoppuhr verwenden
- [ ] Mit einer dritten Person als Publikum proben (Schwager?)
- [ ] Feedback einarbeiten

**Puffer für:**
- Bug-Fixes, die erst beim Üben auffallen
- Letzte Baureglement-Werte
- Notfall: Ausfall ÖREB-Dienst → Fallback-Variante mit gespeicherten Antworten

### Resultat am Ende der Woche

- Demo ist bühnenreif

---

## Woche 8: Finaler Feinschliff
**13. – 16. Juni**

### Ziele

- Alles ist committed und gepusht
- Repo ist sauber, keine lokalen uncommitted Changes
- Präsentationsmaterial liegt vor

### Aufgaben

**Montag 13. Juni:**
- [ ] Letzter Code-Check, letzte Commits
- [ ] README-Update mit finalem Stand

**Dienstag 14. Juni:**
- [ ] Generalprobe Präsentation

**Mittwoch 15. Juni:**
- [ ] Pause (bewusst)
- [ ] Präsentationsmaterial bereitmachen (USB-Stick, PDF-Export)

**Donnerstag 16. Juni:**
- [ ] Alles letztmalig prüfen
- [ ] Schlaf gehen

**Freitag 17. Juni:**
- [ ] **ABGABE und PRÄSENTATION**

---

## Risiken und Mitigation

### Risiko: Schwager hat keine Zeit für AZ-Werte
**Wahrscheinlichkeit: mittel**
**Impact: niedrig bis mittel**

**Mitigation:** Das Tool funktioniert auch ohne exakte Werte, der Status ist dann "NICHT_BERECHENBAR" mit klaren Hinweisen. Im Notfall arbeiten wir mit offiziellen Richtwerten aus der BauV (z.B. AZ 0.3 als ländlicher Durchschnitt). Präsentation kann trotzdem glänzen.

### Risiko: GUI wird komplizierter als gedacht
**Wahrscheinlichkeit: mittel**
**Impact: mittel**

**Mitigation:** Streamlit ist genau deshalb gewählt, weil es einfach ist. Fallback: Wenn bis Ende Woche 4 keine taugliche GUI steht, präsentieren wir die CLI mit Screenshots. Die Kernfunktionalität ist stark genug.

### Risiko: Krankheit oder anderer Ausfall einer Person
**Wahrscheinlichkeit: niedrig**
**Impact: hoch**

**Mitigation:** Beide Teammitglieder können beide Rollen in der Präsentation übernehmen. Dokumentation und Code-Kommentare sind so gut, dass der andere im Notfall einspringen kann.

### Risiko: Kursanforderungen ändern sich
**Wahrscheinlichkeit: niedrig**
**Impact: mittel**

**Mitigation:** Wöchentliche Prüfung der Folien und Kurs-Kommunikation. Dozent bei Unsicherheit direkt fragen.

---

## Kontinuierliche Aktivitäten

Diese laufen parallel zu allen Wochen:

- [ ] **Journal pflegen:** Nach jeder Session kurzer Eintrag in `docs/journal.md`
- [ ] **Regelmässige Commits:** Keine wochenlangen uncommitted Arbeiten
- [ ] **Zweiwöchentlich Schwager-Check:** Kurzer Status, neue Test-Adressen
- [ ] **Gemeinsames Wochen-Treffen:** Was gemacht, was kommt, wo haken
- [ ] **Dozent-Kontakt:** Bei Unklarheiten proaktiv fragen, nicht hoffen

---

## Wichtige Meilensteine im Blick

| Datum | Meilenstein |
|---|---|
| 1. Mai | Konzept-Dokument im Repo, Team aufgesetzt |
| 15. Mai | Erste GUI läuft |
| 29. Mai | Alles codetechnisch fertig |
| 5. Juni | Präsentation steht |
| 12. Juni | Dreifach geübt |
| **17. Juni** | **Abgabe** |

---

## Morgige Besprechung: 30-Minuten-Agenda

Als konkrete Vorlage für euer Teamgespräch:

**Minuten 1-5: Einführung**
- Projekt-Überblick: Christophe zeigt GitHub-Repo und laufende Demo
- Die drei wichtigsten Dokumente: README, fachliche_grundlagen.md, dieser Projektplan

**Minuten 6-15: Konzept-Dokument durchgehen**
- Was drin steht, was fehlt (Name, E-Mail, konkrete Aufgabenverteilung)
- Alle `[Platzhalter]` gemeinsam füllen

**Minuten 16-25: Projektplan besprechen**
- Ist der Zeitrahmen realistisch für euch beide?
- Wer übernimmt was in Woche 2?
- Kommunikations-Rhythmus festlegen

**Minuten 26-30: Nächste konkrete Schritte**
- Was macht jede/r diese Woche?
- Wann ist das nächste Treffen?
- Offene Fragen an Christophe

**Nach dem Termin:**
- Alle Platzhalter im Konzept-Dokument ausfüllen
- Konzept committen und pushen
- Erste Aufgaben starten
