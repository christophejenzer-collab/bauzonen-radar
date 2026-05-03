## 1. Kontext & Ziel

**Zielgruppe:** Architekten, Bau-Investoren, private Grundstückeigentümer.

Die GUI importiert die bestehende Funktion `analysiere()` aus `analyse_adresse.py` direkt
und stellt deren strukturierten Output (`PotenzialErgebnis`-Dataclass) visuell dar.
Der Platzhalter `src/bauzonenradar/gui/` ist bereits angelegt.

**Design-Referenz:** [za-ag.ch](https://www.za-ag.ch) – Klares, reduziertes Schweizer
Architekturbüro-Styling: viel Weissraum, dezente Typografie, keine Spielereien.

---

## 2. Funktionale Anforderungen (User Stories)

| ID   | Als…          | möchte ich…                                                                 | damit…                                                        |
|------|---------------|-----------------------------------------------------------------------------|---------------------------------------------------------------|
| F-01 | Benutzer      | eine Adresse eingeben und eine Analyse starten                              | ich das Baulandpotenzial sofort sehe                          |
| F-02 | Benutzer      | den Datenqualitäts-Status farbig angezeigt bekommen                         | ich die Verlässlichkeit des Resultats einschätzen kann        |
| F-03 | Benutzer      | eine grafische Progress-Bar für Ausschöpfung und Reserve sehen              | der Empfehlungs-Block visuell lesbar ist                      |
| F-04 | Benutzer      | die Parzelle auf einem Kartenausschnitt sehen                               | ich weiss, welches Grundstück analysiert wird                 |
| F-05 | Benutzer      | die GWR-Ist-Daten (Soll vs. Ist, inkl. Plausibilitätskonflikt) sehen       | ich die reale Bebauung mit dem Potenzial vergleichen kann     |
| F-06 | Benutzer      | eine Fehlermeldung erhalten, wenn die Adresse nicht gefunden wird           | ich nicht vor einem leeren Ergebnis stehe                     |

---

## 3. Nicht-funktionale Anforderungen

| ID    | Anforderung                                                                                              |
|-------|----------------------------------------------------------------------------------------------------------|
| NF-01 | **Technologie:** Python 3.13 / Streamlit – kein zusätzlicher Framework-Stack                            |
| NF-02 | **Backend-Import:** `analysiere()` wird via `sys.path.insert` eingebunden (kein Refactoring nötig)     |
| NF-03 | **Performance:** Ladezeit < 10 Sek. pro Abfrage (inkl. OEREB + GWR)                                    |
| NF-04 | **Plattform:** Desktop-Browser (lokal via `streamlit run`), kein Deployment für Abgabe nötig            |
| NF-05 | **Sprache:** Schweizerdeutsch / Hochdeutsch als UI-Sprache                                              |
| NF-06 | **Datenschutz:** Keine Speicherung von Adress- oder GWR-Daten                                           |

---

## 4. Design-Vorgaben

| Element                  | Vorgabe                                                                                   |
|--------------------------|-------------------------------------------------------------------------------------------|
| Schrift                  | Sans-Serif, leicht (Inter oder System-Font)                                               |
| Hintergrund              | Weiss `#FFFFFF`                                                                           |
| Primärtext               | Dunkelgrau `#1A1A1A`                                                                      |
| Akzentfarbe              | Anthrazit / Bordeaux `#8B1A1A`                                                            |
| Datenqualität VERBINDLICH | Grün `#2E7D32`                                                                           |
| Datenqualität GROBSCHÄTZUNG | Orange `#E65100`                                                                       |
| Datenqualität NICHT_MÖGLICH | Grau `#757575`                                                                         |
| Layout                   | Einspaltig, klare Sektionsabgrenzung mit Trennlinien                                      |
| Karte                    | `st.map()` mit Parzellen-Pin (LV95 → WGS84-Konvertierung)                                |

---
