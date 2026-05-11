# Projektplan: Bauzonen-Radar

Stand: 11. Mai 2026.
Abgabe: 17. Juni 2026.

## Iterationen im Ueberblick

```
Iteration 1: Pipeline               [ABGESCHLOSSEN] Maerz/April 2026
Iteration 2: Potenzialberechnung    [ABGESCHLOSSEN] April 2026
Iteration 3: Verifikation           [ABGESCHLOSSEN] 28.+29.04.2026
Iteration 4: Webseite (Streamlit)   [ABGESCHLOSSEN] 03.-11.05.2026
Iteration 5: Gemeinde-Analyse       [LAUFEND]       1 von 4 Modulen fertig (GWR)
Iteration 6: Generalprobe           [GEPLANT]       Mitte Juni 2026
```

## Iteration 1: Pipeline (abgeschlossen)

**Zeitraum**: Maerz 2026 - 27. April 2026

**Ziel**: Adresse rein, Parzellen-Daten und OEREB-Themen raus.

**Erledigt**:
- Geocoding via swisstopo SearchAPI
- OEREB GetEGRID + GetExtract
- XML-Parser fuer alle relevanten OEREB-Themen
- Datenklassen Parzelle, Restriction, Bauklasse, Naturgefahr usw.
- Hauptprogramm `analyse_adresse.py`
- Zehn Test-Adressen verifiziert

## Iteration 2: Potenzialberechnung (abgeschlossen)

**Zeitraum**: 25. April 2026 - 28. April 2026

**Ziel**: Mit Reglement-Daten konkrete Bauland-Reserven berechnen
und Datenqualitaet sauber kommunizieren. Visuelle Lagebeurteilung
fuer Endanwender.

**Erledigt**:
- `Baureglement`-Klasse mit JSON-Lade-Logik
- `BemessungsSystem`-Enum: AZ / GFZo / Hoehen+GZ
- `Datenqualitaet`-Enum: VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH
- `PotenzialBerechner` mit Drei-Pfad-Logik
- Stadt Bern komplett (Bauklassen 2-6, Bauklasse E, ZoeN, Altstadt)
- Stadt Thun komplett (BR 2022 mit Hoehen + GZ, Strukturgebiet,
  Arealbonus, alle Wohn-/Mischzonen)
- Oberhofen am Thunersee komplett (BR 2012/2024, Hoehen-System
  ohne GZ)
- Schaetz-Berechnung im Hoehen-System mit konservativen Annahmen
- Plausibilitaetscheck gegen altes AZ-Recht
- Header-Banner und klare Status-Markierung bei Schaetzungen
- Empfehlungs-Block mit ASCII-Balken zur visuellen Lagebeurteilung
- Vier Lagebeurteilungs-Stufen anhand Bauland-Reserve in Prozent
- Erste echte GFZo-Berechnung: Thunstrasse 40 Bern, Status GERING

## Iteration 3: Verifikation und Vervollstaendigung (abgeschlossen)

**Zeitraum**: 28. April 2026 - 29. April 2026

**Ziel**: Stadt Bern mit parzellenscharfen Werten aus dem
Bauklassenplan vervollstaendigen, Stresstest auf 50 Adressen,
Bug-Fixes der Begrenzer-Logik.

**Erledigt am 28.04.**:
- Bauklassenplan Stadt Bern als ArcGIS REST-API entdeckt
- Modul `bern_bkp.py` mit pure Standard-Library implementiert
- Layer 88 (Bauweise) und Layer 95 (Grundzonen) live abgefragt
- `bern.json` komplett umgebaut: BK 2-6 als `hoehen_und_gz`
- Neuer Pfad `NICHT_MOEGLICH` fuer Spezialregime
- `Bauparameter.mit_bkp_daten()` Methode
- Drei-Begrenzer-Logik (Gebaeudemasse / Parzelle / GZ)
- Sechs Adressen quer durch Bern verifiziert

**Erledigt am 29.04.**:
- Vier Bug-Fixes Begrenzer-Logik:
  - Ist-Platzhalter 40% -> 25% (realistischer Wohnzonen)
  - Ehrliche >100% Anzeige bei Schaetzungs-Versagen
  - `max_gebaeudelaenge_m=None` -> `float("inf")` statt Crash
  - Parzellen-Form 1:1.5 statt Quadrat (verhindert negative Seiten)
- 5 thun.json-Eintraege ergaenzt: WA3/4/5 Slash-Synonyme + ZPP
- Stresstest 12 Adressen: 12/12 Erfolg
- Stresstest 50 Adressen: 48/50 Erfolg (96%, 1.7 Min)
- 4 API-Spikes als Vorbereitung fuer Iteration 5 verifiziert
- Iteration-5-Konzept geschrieben (`docs/konzept_gemeinde_analyse.md`,
  708 Zeilen, empirisch verifiziert)

## Iteration 4: Webseite (abgeschlossen)

**Zeitraum**: 03. Mai 2026 - 11. Mai 2026

**Ziel**: Streamlit-GUI fuer Endanwender mit eigenstaendigem Design,
direkter Backend-Anbindung und Visualisierung der drei
Datenqualitaets-Pfade.

**Verantwortlich**: Fabienne (Frontend) und Christophe (Backend-API).

**Erledigt am 03.05. (Sonntag-Coding-Tag)**:
- Backend-Refactoring: `analyse_adresse.py` getrennt in `analysiere()`
  (reine Logik) und `drucke_bericht()` (CLI-Output)
- Neue Datenklasse `AnalyseErgebnis` mit ~30 Feldern fuer alle
  Pipeline-Daten - Separation of Concerns
- WGS84-Koordinaten direkt im Ergebnis fuer `st.map()`-Karten
- Streamlit-GUI von Fabienne (`gui/frontend.py`, ~370 Zeilen):
  - Eigenes CSS (Inter-Schrift, Schwarz/Rot-Akzent, ruhige Typografie)
  - Sektionen: Lage (Karte) / Parzelle / Bebauungspotenzial / GWR
  - Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz
- Fabienne: Doku-Architektur restrukturiert
  (Backend/Frontend-Trennung in anforderungen, glossar, releasenotes)
- Stresstest 12/12 Adressen mit refactoriertem Backend

**Erledigt am 05.05. (Frontend-Test)**:
- Lokaler Frontend-Test mit Layout-Bewertung
- Erste Crash-Diagnose: Backend-Mismatch bei Feldnamen entdeckt
- Mapping-Tabelle Backend/Frontend an Fabienne uebergeben
- Repo-Aufraeumen mit `.gitignore`-Erweiterung

**Erledigt am 11.05. (Iter-4-Abschluss)**:
- Fabiennes Frontend gepushed mit Anpassungen
- Backend-Bug entdeckt und gefixt: `AnalyseErgebnis`-Aliase
  (`zulaessig_m2` und `ausschoepfung_prozent` waren `None`)
- 7 neue GUI-Aliase ergaenzt (`theoretisch_zulaessig_m2`,
  `ausschoepfungsgrad_prozent`, `reserve_prozent`, `zonen_betrachtet`,
  `zone`, `arealbonus_anwendbar`, `bemerkungen`)
- Live-Test mit 4 Adressen erfolgreich:
  - Thunstrasse 40 (VERBINDLICH): 118.5 m^2 zulaessig, 50% Ausschoepfung
  - Frutigenstrasse 25 (GROBSCHAETZUNG): 1080 m^2 Soll vs. 1520 m^2 GWR
    -> Plausibilitaets-Konflikt-Box wird ausgeloest (Highlight!)
  - Kramgasse 49 (NICHT_MOEGLICH): keine Pseudo-Werte
  - Murifeldweg 8 (Edge-Case): 230% Ausschoepfung sichtbar gemacht
- Repo aufgeraeumt:
  - Temp-Dateien geloescht
  - `START JenzC.txt` -> `start_cheatsheet.md` (Markdown)
  - `## interessante Objekte.txt` ins lokale Archiv
- struktur.md auf aktuellen Stand
- Patch-Skripte bleiben im Repo als Beleg fuer iterative Entwicklung

**Pruefungs-Highlight aus Iter 4**: Die Plausibilitaets-Konflikt-Box
zeigt bei Frutigenstrasse 25 den 1.4-fachen Unterschied zwischen
Tool-Schaetzung (Soll: 1080 m^2) und GWR-Realitaet (Ist: 1520 m^2).
Genau das macht den Mehrwert des Tools sichtbar - nicht nur was
rechtlich moeglich waere, sondern auch der Gap zur Realitaet bei
Bestandsbauten.

**Optionale Verbesserungen (Phase 3 Generalprobe)**:
- Negative Reserve bei >100% Ausschoepfung visuell sauberer
- Zonen-Suffix `[hoehen_und_gz]` ausblenden fuer Endanwender
- Karten-Marker eventuell kleiner

## Iteration 5: Gemeinde-Analyse (laufend)

**Zeitraum**: Begonnen 30. April 2026, geplant Anfang Juni 2026

**Ziel**: Statt Einzeladressen abzufragen, eine ganze Gemeinde
analysieren und eine priorisierte Excel-Liste der Verdichtungs-
Kandidaten ausgeben.

**Detail-Konzept**: siehe `docs/konzept_gemeinde_analyse.md`
(708 Zeilen, empirisch verifiziert mit 4 API-Spikes)

**Status der vier geplanten Module**:

| Modul | Status | Stand |
|---|---|---|
| `gwr.py` | ✅ FERTIG | 30.04.2026, vorgebaut + integriert |
| `parzellen_liste.py` | offen | geplant Anfang Juni |
| `gemeinde_analyse.py` | offen | geplant Anfang Juni |
| Excel-Export | offen | geplant Anfang Juni |

**`gwr.py` (am 30.04.2026 erledigt)**:
- ~330 Zeilen, Vollausbau mit Caching, Retry, Throttling
- `GwrGebaeude`-Datenklasse mit allen API-Feldern
- `GwrQuelle` mit Zwei-Stufen-Workflow (SearchAPI -> MapServer)
- Aggregation `geschossflaeche_pro_parzelle()` fuer mehrere Gebaeude
- 3 Exception-Klassen (GwrFehler, GwrApiFehler, GwrParseFehler)
- Integration in `analyse_adresse.py` minimal/additiv
- Stresstest 50 Adressen: 96% Erfolg, 2.2 Min Laufzeit (+30 Sek vs. ohne GWR)
- Plausibilitaets-Konflikt zwischen Schaetzung und Realitaet sichtbar

**Noch zu tun in Iter 5**:
- Modul `parzellen_liste.py`: alle Parzellen einer Gemeinde holen
  (mit nummerischer Suchstrategie wegen 50-Treffer-Limit)
- Modul `gemeinde_analyse.py`: Massen-Pipeline mit Throttling +
  SQLite-Cache + Wiederaufnahme nach Abbruch
- Excel-Export mit den im Konzept definierten Spalten
- Test-Lauf mit Oberhofen am Thunersee als Pilot-Gemeinde
- Aufwand-Schaetzung Restarbeit: ca. 1.5 Tage Entwicklung

**Use-Case**: Architekten und Investoren bekommen eine Top-50-Liste
der Parzellen mit dem groessten Verdichtungs-Potenzial in einer
Gemeinde - sortierbar und filterbar in Excel, mit GRUDIS-Direktlinks
fuer manuelle Eigentuemer-Abfragen.

## Iteration 6: Generalprobe (geplant)

**Zeitraum**: Mitte Juni 2026

**Ziel**: Praesentation einueben und Edge-Cases abdecken.

**Inhalte**:
- Pitch-Text auf 5 Minuten trimmen
- Live-Demo-Adressen auswaehlen und proben
  (idealerweise eine pro Datenqualitaets-Stufe)
- Live-Demo Gemeinde-Analyse (z.B. Oberhofen)
- GWR-Plausibilitaets-Konflikt als Demo-Highlight
  (Frutigenstrasse 25: 1080 m^2 Soll vs. 1520 m^2 Ist in der GUI)
- Drei moegliche Code-Fragen vorbereiten
- Backup-Plan falls Internet/OEREB-Webservice down
- README finalisieren mit GUI-Screenshots

## Risiken und Gegenmassnahmen

| Risiko | Gegenmassnahme |
|---|---|
| OEREB-Webservice down bei Demo | tests/fixtures/ enthalten OEREB-XML-Snapshots fuer Offline-Demo |
| Streamlit-GUI nicht fertig | ABGESCHLOSSEN am 11.05.2026 |
| Bauklassenplan-Werte unklar | Direktanfrage Stadt Bern Stadtplanung |
| Schaetz-Werte werden falsch interpretiert | Klare Banner-Markierung, "(geschaetzt)" in Empfehlung, GWR-Vergleichswert sichtbar |
| Gemeinde-Analyse zu langsam (500 Parzellen) | Throttling 0.5-1 Sek + lokales SQLite-Caching |
| GWR-Daten luckenhaft | Klare Markierung "GWR-Daten unvollstaendig (fehlt: Feld)" |
| Massen-Suche limitiert auf 50 Treffer | Nummerische Suchstrategie (verifiziert in Iter-5-Konzept) |
| Iter 5 zu spaet fertig | GWR-Modul ist isoliert nutzbar, Massen-Analyse kann notfalls verschoben werden |

## Naechste Termine

- **Naechste Woche**: Termin mit Schwager (Reglement-Verifikation,
  Annahmen-Plausibilisierung, Iter-5-Strategie)
- **Anfang Juni 2026**: Iteration 5 abschliessen (parzellen_liste,
  gemeinde_analyse, Excel-Export)
- **Mitte Juni 2026**: Iteration 6 (Generalprobe)
- **17. Juni 2026**: Abgabe und Praesentation
