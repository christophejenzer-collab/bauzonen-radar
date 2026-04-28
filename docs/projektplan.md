# Projektplan Bauzonen-Radar

**Zeitraum:** 22. April 2026 - 17. Juni 2026 (Abgabe)
**Stand:** 27. April 2026

---

## Ueberblick

| Iteration | Zeitraum | Fokus | Status |
|---|---|---|---|
| 1 | 22.4. - 24.4. | Pipeline End-to-End | ✅ Abgeschlossen |
| 2 | 25.4. - 27.4. | Reglement-Daten und Spezialeffekte | ✅ Abgeschlossen |
| **3** | **28.4. - 11.5.** | **Vervollstaendigung Reglement-Werte** | **🔄 Aktuell** |
| 4 | 12.5. - 25.5. | GUI und Visualisierung | ⏳ Geplant |
| 5 | 26.5. - 8.6. | Erweiterung der Reichweite | ⏳ Geplant |
| 6 | 9.6. - 15.6. | Demo-Vorbereitung | ⏳ Geplant |
| 7 | 16.6. - 17.6. | Abgabe und Praesentation | ⏳ Geplant |

---

## Iteration 1: Pipeline End-to-End (22.4. - 24.4.) ✅

### Ziele
- swisstopo-Geocoding integrieren
- OEREB-Webservice anbinden
- XML-Parser fuer alle relevanten Subcodes
- Erste Reglement-Anbindung
- Erste Adresse erfolgreich analysieren

### Erreicht
- swisstopo SearchAPI integriert (Adresse → LV95-Koordinaten)
- OEREB-Webservice Kanton Bern angebunden (GetEGRID, GetExtract)
- XML-Parser fuer 6 OEREB-Subcodes
- Erste thun.json mit historischen AZ-Werten
- Erste bern.json mit Bauklassen-Struktur
- Pipeline fuer Hirschweg 7, Thun erfolgreich

---

## Iteration 2: Reglement-Daten und Spezialeffekte (25.4. - 27.4.) ✅

### Ziele
- Datenmodell um Hoehen-Werte erweitern
- Echte Reglement-Werte aus offiziellen Quellen
- Strukturgebiet- und Arealbonus-Erkennung
- Mehrere Test-Adressen verifizieren

### Erreicht
- Datenmodell baureglement.py erweitert (differenzierte Fassadenhoehen, Gebaeudelaenge, Arealbonus)
- thun.json mit Art. 42 BR 2022 (vom Schwager bestaetigt)
- bern.json komplett gegen BO 2006/2023:
  - Bauklassen 2-6 (Korrektur des Fehlers A-E)
  - Bauklasse E mit GFZo 0.5/0.6 aus Art. 57
  - ZoeN mit echten GFZo aus Art. 24
  - Berner Altstadt-Spezialregimes
- potenzial.py: Strukturgebiet, Arealbonus, Hoehen-Ausgabe
- **Erste echte GFZo-Berechnung gelungen** (Thunstrasse 40)
- 10 Test-Adressen erfolgreich verifiziert
- Erfassungs-Excel fuer Schwager erstellt

---

## Iteration 3: Vervollstaendigung Reglement-Werte (28.4. - 11.5.) 🔄

### Ziele
- Werte vom Schwager einarbeiten (Bauklassenplan Stadt Bern)
- Variable gGA aus Art. 46 BO Bern in Code umsetzen
- Mitstudentin-Termin und Aufgabenverteilung
- Konzept und Projektplan im Repo aktuell halten

### Aufgaben

**28. April (Mitstudentin-Termin, 30 Min):**
- Konzept und Projektplan gemeinsam durchgehen
- Aufgabenverteilung fuer Iteration 4 (GUI)
- Kommunikations-Kanal vereinbaren
- Mitstudentin als GitHub-Collaborator hinzufuegen
- Streamlit-GUI grob besprechen

**29. April - 5. Mai (Schwager-Erfassung):**
- Excel an Schwager senden
- Begleittext mit Priorisierung (Tabelle 1 + 6)
- Antworten abwarten
- Werte in JSONs eintragen

**6. Mai - 11. Mai (Code-Erweiterungen):**
- Variable gGA aus Art. 46 in baureglement.py
- Weitere Subzonen ergaenzen (Innere/Aeussere Neustadt mit echten Werten)
- Bei Bedarf weitere Praxistests

### Definition of Done
- Stadt Bern hat fuer alle Bauklassen 2-6 echte GFZo-Werte aus dem BKP
- Variable gGA wird im Tool korrekt verwendet
- Mitstudentin hat Zugriff aufs Repo
- Aufgabenverteilung Iteration 4 ist klar

---

## Iteration 4: GUI und Visualisierung (12.5. - 25.5.) ⏳

### Ziele
- Streamlit-GUI fuer einfache Bedienung
- Karten-Darstellung der Parzelle
- Tabellarische Uebersicht der OEREB-Daten

### Verantwortlich
- **Mitstudentin** (federfuehrend)
- Christophe als Backend-Support

### Aufgaben
- Streamlit-Skelett aufsetzen
- Adress-Eingabefeld mit Autovervollstaendigung
- Anzeige der Potenzialanalyse als Webseite
- Karten-Integration (folium oder pydeck)
- Farbige Statusanzeige (HOCH=gruen, GERING=rot, etc.)
- Mobile-Tauglichkeit pruefen

### Definition of Done
- Tool laeuft im Browser ohne Code-Kenntnisse
- Adresse eingeben → Bericht erscheint
- Karten-Darstellung der Parzelle
- 3-5 Adressen erfolgreich getestet

---

## Iteration 5: Erweiterung der Reichweite (26.5. - 8.6.) ⏳

### Ziele
- Echte Ist-Bebauung statt 40%-Platzhalter
- Weitere Gemeinden
- Rangliste-Funktion

### Aufgaben
- swissBUILDINGS3D-Anbindung untersuchen
- Datenformat und Lizenz pruefen
- Implementierung in modelle.py oder neuem Modul
- Weitere Gemeinden: Koeniz, Steffisburg, Muensingen
- Rangliste mehrerer Adressen nach Reserve-Potenzial

### Definition of Done
- Mindestens eine Adresse mit echter Ist-Bebauung
- 4 Gemeinden vollstaendig erfasst (Bern, Thun, Koeniz, Steffisburg)
- Rangliste-Funktion mit 5+ Adressen

---

## Iteration 6: Demo-Vorbereitung (9.6. - 15.6.) ⏳

### Ziele
- Code-Cleanup und Dokumentation finalisieren
- 5-Minuten-Praesentation einueben
- Live-Demo vorbereiten
- 3 Code-Fragen vorbereiten

### Aufgaben

**Code-Cleanup:**
- Unbenutzte Imports entfernen
- Konsistente Docstrings
- Type-Hints wo sinnvoll
- README final pruefen

**Praesentation (5 Minuten):**
- Pitch (1 Min): Problem, Loesung, Zielgruppe
- Live-Demo (2 Min): 3 kuratierte Adressen
- Code-Einblick (1 Min): Eine interessante Architektur-Entscheidung
- Ausblick (1 Min): Naechste Schritte, Iteration 6

**3 Code-Fragen vorbereiten:**
- Frage 1 (Detail): "Wie funktioniert das XML-Parsing in modelle.py?"
- Frage 2 (Architektur): "Warum ist Bauparameter ein dataclass und nicht ein dict?"
- Frage 3 (Erweiterung): "Wie wuerdest du Kanton Zuerich integrieren?"

### Definition of Done
- Praesentation in 5 Minuten durchgespielt
- Demo laeuft fluessig auf 3 Adressen
- 3 Fragen mit Antworten vorbereitet
- Code-Doku abgeschlossen

---

## Iteration 7: Abgabe und Praesentation (16.6. - 17.6.) ⏳

### Aufgaben
- 16. Juni: Letzter Regressionstest (demo.ps1, 10 Adressen)
- 16. Juni: Final-Commit, Tag "v1.0" setzen
- 17. Juni: Praesentation

---

## Risiken und Mitigationen

### Risiko 1: Schwager liefert keine Werte
**Mitigation:** Tool funktioniert auch ohne. Es zeigt klar an, was fehlt. Stadt Thun liefert bereits eine vollstaendige Berechnungsgrundlage ueber Hoehen+GZ.

### Risiko 2: Mitstudentin steigt aus
**Mitigation:** Streamlit-GUI ist nicht zwingend fuer Minimalziel. Backend funktioniert eigenstaendig. Falls noetig, simpler GUI in Iteration 6 selbst.

### Risiko 3: swissBUILDINGS3D zu komplex
**Mitigation:** 40%-Platzhalter ist transparent dokumentiert. Falls Iteration 5 nicht klappt, bleibt es beim Platzhalter mit klarem Hinweis.

### Risiko 4: Code-Komplexitaet erschlaegt mich vor 17.6.
**Mitigation:** Iteratives Vorgehen mit klaren Definition-of-Done pro Iteration. Lieber weniger Features, dafuer sauber.

---

## Wochen-Routine

**Jeden Werktag (5-15 Min):**
- Journal-Eintrag pflegen (`docs/journal.md`)
- Mindestens einen Commit pro Tag

**Jeden Sonntag (30 Min):**
- Wochenruckblick: Was ist erreicht? Was fehlt?
- Naechste Woche planen
- Projektplan aktualisieren falls noetig

---

## Zwischenstaende (Soll/Ist)

| Datum | Soll | Ist |
|---|---|---|
| 24.4. | Pipeline End-to-End | ✅ Erreicht |
| 27.4. | Reglement-Daten + erste Berechnung | ✅ Erreicht (uebertroffen) |
| 11.5. | Bauklassenplan-Werte vollstaendig | (offen) |
| 25.5. | GUI funktioniert | (offen) |
| 8.6. | swissBUILDINGS3D + 4 Gemeinden | (offen) |
| 15.6. | Praesentation eingeuebt | (offen) |
| 17.6. | Abgabe | (offen) |
