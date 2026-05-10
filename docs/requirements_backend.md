# Requirements – Backend-Schnittstelle für Streamlit-GUI


Grundlage: `docs/anforderungen_backend.md` 

---

## REQ-B-01 · Rückgabe-Objekt `analysiere()` (→ FA-41, UC-3)

**Was:** `analysiere()` gibt heute `None` zurück und schreibt via `print()` auf stdout.
Die GUI benötigt ein strukturiertes Rückgabe-Objekt.

**Akzeptanzkriterien:**
- `analysiere(adresse: str)` gibt ein `AnalyseResultat`-Objekt zurück
- Dataclass-Definition (neu in `modelle.py` oder `analyse_adresse.py`):

  ```python
  @dataclass
  class AnalyseResultat:
      parzelle:     Parzelle            # bestehend
      ergebnis:     PotenzialErgebnis   # bestehend
      gwr_gebaeude: list | None         # bestehend aus GWR-Lookup
  ```

- `print()`-Aufrufe bleiben erhalten (CLI-Betrieb darf nicht brechen)
- Bei nicht gefundener Adresse: Rückgabe `None` (bestehend, kein Change)
- Importierbar via:

  ```python
  import sys
  sys.path.insert(0, "src/bauzonenradar")
  from analyse_adresse import analysiere
  resultat = analysiere("Frutigenstrasse 25, 3604 Thun")
  ```

---

## REQ-B-02 · Koordinaten auf `Parzelle`-Objekt (→ FA-02, FA-08, UC-3)

**Was:** Die GUI braucht LV95-Koordinaten für die Kartenanzeige (`st.map()`).
Der Code dazu ist in `analysiere()` bereits vorhanden (Geocoding-Lookup), das Feld
wird aber nicht persistent auf das Parzellen-Objekt geschrieben.

**Akzeptanzkriterien:**
- `resultat.parzelle.koordinate_lv95` ist gesetzt als `tuple(ost, nord)` in LV95
- Fallback: Falls das Parzellen-Objekt kein `koordinate_lv95`-Attribut hat →
  `AnalyseResultat` enthält ein zusätzliches Feld `koordinate_lv95: tuple | None`
- Bei Geocoding-Fehler: Feld auf `None` setzen (kein Absturz)

---

## REQ-B-03 · `PotenzialErgebnis` – Pflicht-Felder für GUI (→ FA-32–36, FA-37–39, FA-42)

**Was:** Die GUI greift direkt auf Felder der bestehenden `PotenzialErgebnis`-Dataclass zu.
Sicherstellen, dass folgende Felder befüllt und zugänglich sind:

| Feld | Typ | Verwendung GUI |
|---|---|---|
| `datenqualitaet` | `Datenqualitaet` (Enum) | Ampel-Badge |
| `ausschoepfungsgrad_prozent` | `float \| None` | Progress-Bar |
| `reserve_prozent` | `float \| None` | Progress-Bar |
| `theoretisch_zulaessig_m2` | `float \| None` | Kennzahl + Plausibilitätsprüfung |
| `zonen_betrachtet` | `list[str]` | Zonenanzeige |
| `bemerkungen` | `list[str]` | Spezialfälle (Naturgefahren, Baulinien etc.) |
| `arealbonus_anwendbar` | `bool` | Optionaler Hinweis |
| `status` | `PotenzialStatus` (Enum) | Lagebeurteilung |

**Akzeptanzkriterium:** Alle Felder vorhanden und nicht `AttributeError`-auslösend
bei den drei Pilot-Adressen (Bern VERBINDLICH, Thun GROBSCHAETZUNG, Koeniz NICHT_MOEGLICH).

---

## REQ-B-04 · Fehler-Robustheit der Pipeline (→ NA-05, FA-09, FA-22)

**Was:** Einzelne API-Ausfälle dürfen die Hauptanalyse nicht abbrechen.
Dies ist gemäss `anforderungen_backend.md` bereits implementiert, muss aber
im Kontext des neuen Rückgabe-Objekts weiterhin gelten.

**Akzeptanzkriterien:**
- OEREB-Ausfall → `None`-Rückgabe mit klarer Exception (kein Stack-Trace)
- GWR-Ausfall → `gwr_gebaeude = None` im `AnalyseResultat`, Hauptanalyse läuft durch
- BKP-Ausfall → `bkp_quelle = None`, Analyse läuft mit Default-Annahmen weiter
- Kein unkontrolliertes Abbrechen bei Netzwerk-Timeout (NA-03: Retry + Backoff bereits implementiert im GWR-Modul)

---

## REQ-B-05 · Datenqualitäts-Logik bleibt unverändert (→ FA-32–36, NA-07)

**Was:** Die Datenqualitäts-Trichotomie (VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH)
ist das Kernkonzept des Systems und darf durch die GUI-Anbindung nicht verändert werden.

**Akzeptanzkriterien:**
- Bei `NICHT_MOEGLICH`: `ausschoepfungsgrad_prozent` und `reserve_prozent` bleiben `None`
  (kein Pseudo-Wert, gemäss FA-36)
- Bei `VERBINDLICH`: kein Schätzungs-Banner (FA-33)
- Bei `GROBSCHAETZUNG`: Banner-Flag im Ergebnis vorhanden (FA-34)
- Bestehende Verifikations-Adressen liefern weiterhin identische Ergebnisse (NA-06)

---

## REQ-B-06 · Disclaimer im Rückgabe-Objekt (→ NA-19, NA-20)

**Was:** Die GUI muss den gesetzlich/fachlich notwendigen Disclaimer anzeigen können,
ohne diesen selbst zu formulieren.

**Akzeptanzkriterien:**
- `AnalyseResultat` oder `PotenzialErgebnis` enthält ein Feld `disclaimer: str`
  mit dem bestehenden Standardtext:
  *«Ersetzt keine rechtsverbindliche Auskunft der Bauverwaltung.
  Grobschätzungen sind keine Grundlage für Investitionsentscheide.»*
- Alternativ: Disclaimer als Konstante in `modelle.py` exportiert

---

## REQ-B-07 · Keine Datenpersistenz (→ NA-17, NA-18)

**Was:** Das Backend darf keine Adress- oder GWR-Daten persistent speichern.

**Akzeptanzkriterien:**
- GWR-Cache bleibt In-Memory (bestehend, kein Change)
- Kein File-Write von Analysedaten durch `analysiere()`
- Kein Logging von Adressen in Dateien

---

## REQ-B-08 · Performance-Budget (→ NA-01, NA-03)

**Was:** Die GUI hat ein Ladezeit-Limit von 10 Sekunden (NF-03 `anforderungen_frontend.md`),
das Backend muss dies einhalten.

**Akzeptanzkriterien:**
- Einzelabfrage mit allen drei Quellen (OEREB + BKP + GWR) < 10 Sek.
  (Basis: aktuell 2.2 Sek/Adresse gemäss Stresstest, Puffer vorhanden)
- Bei Überschreitung: kein Absturz, sondern Timeout-Fehlermeldung zurück

---

## Definition of Done 

- [ ] REQ-B-01: `analysiere()` gibt `AnalyseResultat` zurück, CLI-Betrieb intakt
- [ ] REQ-B-02: `koordinate_lv95` im Resultat gesetzt (Thun-Adresse verifiziert)
- [ ] REQ-B-03: Alle GUI-Pflicht-Felder in `PotenzialErgebnis` zugänglich
- [ ] REQ-B-04: Pipeline überlebt OEREB-, GWR- und BKP-Ausfall ohne Absturz
- [ ] REQ-B-05: Datenqualitäts-Trichotomie unverändert (Regressions-Test mit 3 Adressen)
- [ ] REQ-B-06: Disclaimer-Text verfügbar im Rückgabe-Objekt oder als Konstante
- [ ] REQ-B-07: Kein File-Write, kein persistentes Adress-Logging
- [ ] REQ-B-08: Einzelabfrage < 10 Sek. mit allen drei Datenquellen
