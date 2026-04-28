# Konzept Bauzonen-Radar

**Pflichtdokument fuer die Kursabgabe**

---

## Projektname
**Bauzonen-Radar** - Schweizer Bauland-Analyse mit OEREB-Daten und gemeindespezifischen Baureglementen.

## Team
- **Christophe Jenzer** (christophejenzer@gmail.com, GitHub: christophejenzer-collab) - Projektleitung, Architektur, Backend
- **[Name Teampartner:in]** ([E-Mail-Adresse]) - GUI, UX, Iteration 4-5

**Externe Unterstuetzung:**
- **[Name Schwager]**, dipl. Architekt - Fachliche Verifikation der Reglement-Werte

## Projekt-URL
https://github.com/christophejenzer-collab/bauzonen-radar (privates Repo)

---

## Was das Tool macht

Fuer eine beliebige Adresse im Kanton Bern:

1. **Lokalisiert die Parzelle** ueber die swisstopo-Suchschnittstelle
2. **Holt die OEREB-Daten** (Bauzonen, Baulinien, Naturgefahren, Schutzgebiete) vom kantonalen Webservice
3. **Matcht die Zonen-Information** mit dem gemeindespezifischen Baureglement
4. **Berechnet das Bebauungspotenzial** unter Beruecksichtigung von Bauklasse, Hoehenvorgaben, Strukturgebieten und Arealbonus
5. **Erzeugt einen strukturierten Bericht** mit Status (HOCH/MITTEL/GERING/AUSGESCHOEPFT/NICHT_BERECHENBAR)

## Wie das Tool das macht

### Drei Bemessungssysteme
Das Tool kennt drei Regelwerke fuer die bauliche Dichte:
- **AZ** - Klassische Ausnuetzungsziffer (altes Recht)
- **GFZo** - Geschossflaechenziffer oberirdisch (neues Recht, IVHB-konform)
- **Hoehen + GZ** - Steuerung ueber Fassadenhoehen, Gebaeudelaenge und Gruenflaechenziffer (Thun BR 2022)

Diese Differenzierung ist fachlich entscheidend, weil verschiedene Gemeinden im Kanton Bern unterschiedliche Systeme verwenden.

### Spezialeffekte
- **Strukturgebiet (Thun):** Wenn auf einer Parzelle die Ueberlagerung "Strukturgebiet" liegt, kann der Beirat Stadtbild gestalterische Vorgaben machen. Das Tool warnt automatisch.
- **Arealbonus (Thun):** Bei Parzellen ueber 3000 m^2 oder bei Zusammenlegungen kann ein zusaetzliches Geschoss bewilligt werden. Das Tool weist automatisch darauf hin.

### Architektur
- **modelle.py:** Datenklassen Parzelle, Restriction, Lawstatus
- **bern.py:** OEREB-Webservice-Client (Geocoding, GetEGRID, GetExtract, XML-Parser)
- **baureglement.py:** Reglement-Lader und Bauparameter-Klasse
- **potenzial.py:** Potenzial-Berechnung mit allen Spezialeffekten
- **analyse_adresse.py:** CLI-Hauptschnittstelle

### Datenformate
- Reglemente als JSON-Dateien pro Gemeinde (`daten/baureglemente/`)
- Strukturierte OEREB-XML als Eingabe
- Lesbare Text-Berichte als Ausgabe

## Warum das Tool gebaut wird

Architekturbueros und Investoren stehen oft vor der Frage: Hat eine bestehende Parzelle noch Bebauungspotenzial? Diese Analyse erfordert heute manuelle Arbeit:

1. OEREB-Auszug pro Parzelle holen
2. Zonenvorschriften aus dem Reglement nachschlagen
3. Reserve berechnen
4. Hindernisse (Baulinien, Naturgefahren, Schutzgebiete) pruefen

Das Tool automatisiert diesen Prozess. Pro Adresse spart es **15-20 Minuten** Recherche-Aufwand bei einer Erstanalyse.

**Anwendungsbereiche:**
- Architekturbueros: Erstanalyse vor Kundengespraech
- Investoren: Screening von Liegenschaften
- Eigentuemer: Eigene Reserve-Einschaetzung

---

## Iterativer Plan (8 Wochen bis 17. Juni 2026)

### Iteration 1 (22.4. - 24.4.) ✅ ABGESCHLOSSEN
**Pipeline End-to-End**
- swisstopo-Geocoding integriert
- OEREB-Webservice angebunden
- XML-Parser fuer alle relevanten Subcodes
- Erste thun.json und bern.json
- Erste Adresse erfolgreich analysiert

### Iteration 2 (25.4. - 27.4.) ✅ ABGESCHLOSSEN
**Reglement-Daten und Spezialeffekte**
- Datenmodell erweitert (Fassadenhoehen, Gebaeudelaenge, Arealbonus)
- thun.json mit echten Werten aus Art. 42 BR 2022
- bern.json komplett gegen BO 2006/2023:
  - Bauklassen 2-6 statt A-E (Korrektur eines Fehlers)
  - Bauklasse E mit GFZo 0.5/0.6 aus Art. 57
  - ZoeN mit echten GFZo aus Art. 24
  - Altstadt-Spezialregimes
- Strukturgebiet-Erkennung
- Arealbonus-Pruefung
- **Erste echte GFZo-Berechnung gelungen** (Thunstrasse 40)
- 10 Test-Adressen erfolgreich verifiziert

### Iteration 3 (28.4. - 11.5.) - AKTUELL
**Vervollstaendigung der Reglement-Werte**
- Schwager-Termin: Excel zur Erfassung der konkreten Werte
- Bauklassenplan Stadt Bern: GFZo pro Zone-Bauklasse-Kombination
- Variable gGA aus Art. 46 BO Bern in Code umsetzen
- Weitere Subzonen ergaenzen (Innere/Aeussere Neustadt)
- Mitstudentin-Termin: Aufgabenverteilung fuer Iteration 4

### Iteration 4 (12.5. - 25.5.)
**GUI und Visualisierung (Mitstudentin uebernimmt)**
- Streamlit-GUI fuer einfache Bedienung
- Karten-Darstellung der Parzelle
- Tabellarische Uebersicht der OEREB-Daten

### Iteration 5 (26.5. - 8.6.)
**Erweiterung der Reichweite**
- swissBUILDINGS3D fuer echte Ist-Bebauung (statt 40%-Platzhalter)
- Weitere Gemeinden: Koeniz, Steffisburg, Muensingen
- Rangliste mehrerer Adressen nach Reserve-Potenzial

### Iteration 6 (9.6. - 15.6.)
**Demo-Vorbereitung und Code-Review**
- Code-Cleanup und Dokumentation
- 5-Minuten-Praesentation einueben
- Live-Demo mit kuratierten Test-Adressen vorbereiten
- 3 Code-Fragen vorbereiten

### Iteration 7 (16.6. - 17.6.)
**Abgabe und Praesentation**
- Letzter Test-Lauf
- Praesentation am 17. Juni 2026

---

## Minimalziel

**Die Pipeline funktioniert End-to-End fuer eine Stadt:**
- Adresse → Parzelle → OEREB-Daten → Reglement-Match → Potenzialbericht
- Mindestens eine Gemeinde mit konkreter Berechnung
- Lesbarer Textbericht
- Sauberes Verhalten bei nicht erfassten Gemeinden

**Status:** ✅ ERREICHT (Stand 27. April 2026)

## Erweiterte Ziele

**Erweiterung 1: Mehrere Gemeinden mit echter Berechnung**
- Stadt Bern: Bauklassenplan-Werte vom Schwager
- Stadt Thun: bereits aus Art. 42 verfuegbar
- Mindestens 2 Gemeinden mit reproduzierbarer Berechnung

**Erweiterung 2: GUI**
- Streamlit-Oberflaeche fuer einfache Bedienung
- Mitstudentin uebernimmt Iteration 4

**Erweiterung 3: Visualisierung**
- Parzelle auf Karte darstellen
- Theoretisches vs. realisiertes Potenzial visuell

**Erweiterung 4: Echte Ist-Bebauung**
- swissBUILDINGS3D-Anbindung statt 40%-Platzhalter
- Genauere Reserve-Berechnung

**Erweiterung 5: Erweiterte Adressliste**
- Rangliste-Funktion fuer Investoren-Screening
- 20+ Adressen in einem Lauf

**Erweiterung 6: Kanton Zuerich**
- OEREB-Webservice-Anbindung Zuerich
- Erste Zuercher Gemeinde modellieren

---

## Wer macht was

### Christophe Jenzer (Projektleitung)
- Architektur-Design
- Backend-Implementierung (OEREB, Reglement-Logik, Potenzial-Berechnung)
- Reglement-Daten-Modellierung
- Tests und Verifikation
- Dokumentation
- Recherche fachliche Grundlagen

### Mitstudentin (Iteration 4-5)
- Streamlit-GUI
- Visualisierung
- Karten-Darstellung
- UX-Tests
- Aufgabenverteilung wird im Termin am 28.4.2026 finalisiert

### Externer Input
- **Schwager (Architekt):** Fachliche Verifikation, Reglement-Werte fuer Stadt Bern
- **Investorin (Freundin):** Praxis-Feedback in spaeterer Phase

---

## Aktueller Stand (27. April 2026)

### Was funktioniert
- ✅ Pipeline End-to-End fuer Stadt Bern und Stadt Thun
- ✅ Erste echte Potenzialberechnung (Thunstrasse 40, GFZo 0.5)
- ✅ 10 Test-Adressen verifiziert
- ✅ Strukturgebiet- und Arealbonus-Erkennung
- ✅ Dokumentation auf Repo-Niveau

### Was offen ist
- ⏳ Schwager liefert Bauklassenplan-Werte fuer Stadt Bern
- ⏳ Mitstudentin-Termin und Aufgabenverteilung (28.4.2026)
- ⏳ Streamlit-GUI (Iteration 4)
- ⏳ swissBUILDINGS3D-Anbindung (Iteration 5)

### Was bisher nicht im Plan war, aber sich entwickelt hat
- Strukturgebiet-Erkennung als prominente Warnung im Bericht
- Arealbonus-Logik fuer grosse Parzellen
- Differenzierte Fassadenhoehen-Felder (traufseitig, giebelseitig, andere Dachform)
- Erfassungs-Excel als professionelles Schwager-Brief

Diese Erweiterungen sind aus den Praxistests entstanden - nicht aus theoretischer Vorausplanung. Sie zeigen, dass das Tool im Alltag mit Realdaten besteht.
