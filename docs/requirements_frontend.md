# Requirements – Streamlit-GUI

---

## REQ-01 · Adresseingabe und Analysestart (→ F-01, NF-01, NF-02)

**Was:** Die App stellt ein Texteingabefeld und einen Button «Analysieren» bereit.

**Akzeptanzkriterien:**
- Eingabefeld mit Platzhaltertext: `z.B. Frutigenstrasse 25, 3604 Thun`
- Button löst den Backend-Aufruf aus
- Backend wird eingebunden via:
  ```python
  import sys
  sys.path.insert(0, "src/bauzonenradar")
  from analyse_adresse import analysiere
  resultat = analysiere(adresse)
  ```
- Kein zusätzlicher Framework ausser Streamlit (Python 3.13)
- App wird gestartet mit: `streamlit run src/bauzonenradar/gui/app.py`

---

## REQ-02 · Datenqualitäts-Badge (→ F-02)

**Was:** Nach der Analyse wird der Datenqualitäts-Status farbig als Badge angezeigt.

**Akzeptanzkriterien:**
- Quelle: `resultat.ergebnis.datenqualitaet` (Enum `Datenqualitaet`)
- Darstellung:

| Enum-Wert        | Farbe     | Hex-Code  | Label           |
|------------------|-----------|-----------|-----------------|
| `VERBINDLICH`    | Grün      | `#2E7D32` | ✓ Verbindlich   |
| `GROBSCHAETZUNG` | Orange    | `#E65100` | ~ Grobschätzung |
| `NICHT_MOEGLICH` | Grau      | `#757575` | – Nicht möglich |

- Bei `GROBSCHAETZUNG` zusätzlich sichtbarer Warnhinweis unter dem Badge

---

## REQ-03 · Progress-Bars Ausschöpfung & Reserve (→ F-03)

**Was:** Zwei grafische Balken zeigen Ausschöpfungsgrad und Bauland-Reserve.

**Akzeptanzkriterien:**
- Quelle: `resultat.ergebnis.ausschoepfungsgrad_prozent` und `resultat.ergebnis.reserve_prozent` (jeweils `float | None`)
- Balken Ausschöpfung: Farbe `#8B1A1A` (Bordeaux)
- Balken Reserve: Farbe `#2E7D32` (Grün)
- Prozentangabe rechtsbündig neben dem Label
- Bei `datenqualitaet == NICHT_MOEGLICH`: Balken weglassen, stattdessen Infotext

---

## REQ-04 · Kartenausschnitt mit Parzellen-Pin (→ F-04)

**Was:** Die analysierte Parzelle wird auf einer Karte verortet.

**Akzeptanzkriterien:**
- Komponente: `st.map()` mit zoom=15
- Koordinatenquelle: `resultat.parzelle.koordinate_lv95` (Tuple `(ost, nord)` in LV95)
- Konvertierung LV95 → WGS84 via swisstopo-Näherungsformel (±1m, ausreichend für Kartenanzeige)
- Falls keine Koordinate vorhanden: Kartenblock weglassen (kein Absturz)

---

## REQ-05 · GWR-Block Soll vs. Ist (→ F-05)

**Was:** Die bestehende Bebauung aus dem GWR wird tabellarisch angezeigt.

**Akzeptanzkriterien:**
- Quelle: `resultat.gwr_gebaeude` (Liste von `GwrGebaeude`-Objekten)
- Angezeigte Felder pro Gebäude: Bezeichnung, Grundfläche m², Geschosse, Geschossfläche m², Wohnungen, Baujahr
- Plausibilitäts-Konflikt: Wenn `Σ geschossflaeche_m2 > ergebnis.theoretisch_zulaessig_m2 × 1.05` → orangene Warnbox anzeigen mit Erklärung
- Bei leerem oder fehlendem `gwr_gebaeude`: Hinweis «Keine GWR-Daten – Parzelle möglicherweise unbebaut»

---

## REQ-06 · Fehlermeldung bei nicht gefundener Adresse (→ F-06)

**Was:** Gibt `analysiere()` `None` zurück oder tritt ein Fehler auf, sieht der Benutzer eine klare Meldung.

**Akzeptanzkriterien:**
- `if resultat is None` → `st.error(...)` mit Hinweis auf Schreibweise (z.B. «Adresse nicht gefunden. Bitte Format prüfen: Strasse Nr, PLZ Ort»)
- `try/except` um den gesamten `analysiere()`-Aufruf für Netzwerkfehler (OEREB/GWR-Timeout)
- Kein leeres oder abgestürztes UI – immer eine lesbare Fehlermeldung

---

## REQ-07 · Design & Layout (→ Abschnitt 4)

**Was:** Die GUI folgt den Design-Vorgaben aus `anforderungen_frontend.md`.

**Akzeptanzkriterien:**
- Schrift: Sans-Serif, leicht (Inter oder System-Font)
- Hintergrund: Weiss `#FFFFFF`, Primärtext: Dunkelgrau `#1A1A1A`
- Akzentfarbe: Bordeaux `#8B1A1A`
- Layout: Einspaltig, Sektionen durch horizontale Trennlinien klar abgegrenzt
- Sektions-Labels: Klein, in Grossbuchstaben, Grau (wie Abschnittstitel bei za-ag.ch)
- Keine überladenen UI-Elemente, keine Farb-Spielereien

---

## REQ-08 · Nicht-funktionale Anforderungen

**Akzeptanzkriterien:**
- Antwortzeit < 10 Sekunden pro Abfrage (inkl. OEREB + GWR)
- Spinner / Ladeindikator während der Abfrage sichtbar
- Keine Speicherung von Adress- oder GWR-Daten (kein File-Write, kein Session-Persist)
- Sprache der UI: Hochdeutsch / Schweizerdeutsch
- Lauffähig im Desktop-Browser via `streamlit run` (kein Deployment nötig)

---

## Ablageort & Startbefehl

```
Datei:        src/bauzonenradar/gui/app.py
Startbefehl:  streamlit run src/bauzonenradar/gui/app.py
Abhängigkeit: streamlit (in requirements.txt eintragen)
```

---

## Definition of Done

- [ ] REQ-01: Adresseingabe und Analysestart funktionieren
- [ ] REQ-02: Datenqualitäts-Badge korrekt für alle 3 Stufen
- [ ] REQ-03: Progress-Bars zeigen Ausschöpfung und Reserve korrekt
- [ ] REQ-04: Karte zeigt Parzellen-Pin am richtigen Ort
- [ ] REQ-05: GWR-Tabelle inkl. Plausibilitäts-Konflikt-Erkennung
- [ ] REQ-06: Fehlermeldung bei unbekannter Adresse und bei Netzwerkfehler
- [ ] REQ-07: Design entspricht Vorgaben (Farben, Schrift, Layout)
- [ ] REQ-08: Ladezeit < 10 Sek., kein Datenpersistenz, Sprache korrekt
- [ ] Getestet mit mind. je einer Adresse aus Bern, Thun und Oberhofen

---

*Requirements Engineering – Iteration 4, Bauzonen-Radar*
