# Projektplan: Bauzonen-Radar

Stand: 28. April 2026 (abends).
Abgabe: 17. Juni 2026.

## Iterationen im Ueberblick

```
Iteration 1: Pipeline               [ABGESCHLOSSEN] Marz/April 2026
Iteration 2: Potenzialberechnung    [ABGESCHLOSSEN] April 2026
Iteration 3: Verifikation           [ABGESCHLOSSEN] 28. April 2026
Iteration 4: Webseite               [GEPLANT]       Mai/Juni 2026
Iteration 5: Generalprobe           [GEPLANT]       Mitte Juni 2026
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
  (Gebaeudegrundflaeche x Vollgeschosse + 60% Dachgeschoss)
- Plausibilitaetscheck gegen altes AZ-Recht (vergleichswert_az_alt
  in JSON hinterlegt)
- Header-Banner und klare Status-Markierung bei Schaetzungen
- **Empfehlungs-Block mit ASCII-Balken** zur visuellen Lagebeurteilung
- Vier Lagebeurteilungs-Stufen anhand Bauland-Reserve in Prozent
- Erste echte GFZo-Berechnung: Thunstrasse 40 Bern, Status GERING
- Bug-Fix: Hoehen-System ohne GZ wird korrekt behandelt
- Bug-Fix: Sinnloser Reserve-Vergleich bei Schaetzungen entfernt
- Bug-Fix: Ausschoepfung bei Schaetzungen auf 100% gekappt

## Iteration 3: Verifikation und Vervollstaendigung (abgeschlossen)

**Zeitraum**: 28. April 2026 (in einem Tag durchgezogen)

**Ziel**: Stadt Bern mit parzellenscharfen Werten aus dem
Bauklassenplan vervollstaendigen.

**Erledigt**:
- Bauklassenplan Stadt Bern als ArcGIS REST-API entdeckt
- Modul `bern_bkp.py` mit pure Standard-Library implementiert
- Layer 88 (Bauweise) und Layer 95 (Grundzonen) live abgefragt
- `bern.json` komplett umgebaut: BK 2-6 als `hoehen_und_gz`
  statt `GFZo`, BKP-Code-Synonyme ergaenzt
- Neuer Pfad `NICHT_MOEGLICH` fuer Spezialregime (Altstadt,
  UeO/UeP, Schutzzonen)
- `Bauparameter.mit_bkp_daten()` Methode fuer parzellenscharfe
  Anreicherung
- Drei-Begrenzer-Logik in der Schaetz-Berechnung mit transparenter
  Anzeige (Gebaeudemasse / Parzelle / GZ - der kleinste gewinnt)
- `analyse_adresse.py` faengt Stadt-Bern-Adressen ab und ruft
  zusaetzlich BKP auf
- Sechs Adressen quer durch Bern verifiziert (alle drei
  Datenqualitaets-Pfade live durchgespielt)

**Verschoben in Iteration 4 oder spaeter**:
- Verifikation einzelner BKP-Werte durch Schwager (Stichproben)
- Subtypen FA-FD der ZoeN nachpflegen
- Vierte Gemeinde aufnehmen (z.B. Koeniz)
- Variable gGA aus Art. 46 BO Bern in Code umsetzen
  (aktuell: `grenzabstand_gross_m` als statischer Default)

### Christophe (offen)
- Erfassungs-Excel an Schwager senden (jetzt zur Verifikation
  statt zur Erst-Erfassung, weil API die Werte liefert)
- Antwort des Schwagers in `bern.json` als Stichprobe
  einarbeiten

### Fabienne (offen)
- GitHub-Username an Christophe senden fuer Collaborator-Einladung
- Repo durchklicken und erste Anforderungs-Liste erstellen
- `docs/anforderungen.md` als Skelett anlegen
- Implizite Annahmen im Code identifizieren

### Gemeinsam (offen)
- Mid-Iteration-Termin (Anfang Mai)
- Iteration 4 vorbereiten

## Iteration 4: Webseite (geplant)

**Zeitraum**: Mitte Mai 2026 - Anfang Juni 2026

**Ziel**: Streamlit-GUI fuer Endanwender.

**Verantwortlich**: Fabienne (mit Christophe als Backend-Support).

**Geplante Inhalte**:
- Eingabefeld fuer Adresse mit Autocomplete
- Live-Aufruf der Backend-Pipeline
- Visualisierung Parzelle auf Kartenausschnitt
- Strukturierte Ergebnisanzeige mit visueller Datenqualitaets-Ampel:
  - gruen = VERBINDLICH (echte AZ/GFZo-Berechnung)
  - orange = GROBSCHAETZUNG (Hoehen-System)
  - grau = NICHT_MOEGLICH (Daten fehlen)
- Empfehlungs-Block als grafische Progress-Bar (statt ASCII):
  - Bauland-Reserve in Prozent als zentrales visuelles Element
  - Farb-Skala fuer die vier Lagebeurteilungen
  - `_zeichne_balken`-Funktion aus dem Backend wird durch
    Streamlit-Progress-Bar ersetzt
- PDF-Export fuer Kundendossier
- Auch Anforderungs-Spezifikation `docs/anforderungen.md`
  vollenden

## Iteration 5: Generalprobe (geplant)

**Zeitraum**: Mitte Juni 2026

**Ziel**: Praesentation einueben und Edge-Cases abdecken.

**Inhalte**:
- Pitch-Text auf 5 Minuten trimmen
- Live-Demo-Adressen auswaehlen und proben
  (idealerweise eine pro Datenqualitaets-Stufe)
- Drei moegliche Code-Fragen vorbereiten
- Backup-Plan falls Internet/OEREB-Webservice down
- README finalisieren

## Risiken und Gegenmassnahmen

| Risiko | Gegenmassnahme |
|---|---|
| OEREB-Webservice down bei Demo | Cached-Output mitnehmen |
| Schwager liefert Daten zu spaet | Bauklassenplan eigenstaendig recherchieren |
| Streamlit-GUI nicht fertig | Fallback: CLI-Demo reicht fuer Bewertung |
| Bauklassenplan-Werte unklar | Direktanfrage Stadt Bern Stadtplanung |
| Schaetz-Werte werden falsch interpretiert | Klare Banner-Markierung im Output, "(geschaetzt)" in Empfehlung |

## Naechste Termine

- **Anfang Mai 2026**: Mid-Iteration-Sync mit Fabienne
- **Mitte Mai 2026**: Iteration 3 abgeschlossen, Bern komplett
- **Mitte Juni 2026**: Generalprobe
- **17. Juni 2026**: Abgabe und Praesentation
