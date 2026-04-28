# Projektplan: Bauzonen-Radar

Stand: 28. April 2026.
Abgabe: 17. Juni 2026.

## Iterationen im Ueberblick

```
Iteration 1: Pipeline               [ABGESCHLOSSEN] Marz/April 2026
Iteration 2: Potenzialberechnung    [ABGESCHLOSSEN] April 2026
Iteration 3: Verifikation           [LAUFEND]       April/Mai 2026
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

**Ziel**: Mit Reglement-Daten konkrete Bauland-Reserven berechnen.

**Erledigt**:
- `Baureglement`-Klasse mit JSON-Lade-Logik
- `BemessungsSystem`-Enum: AZ / GFZo / Hoehen+GZ
- `PotenzialBerechner` mit Drei-Pfad-Logik
- Stadt Bern komplett (Bauklassen 2-6, Bauklasse E, ZoeN, Altstadt)
- Stadt Thun komplett (BR 2022 mit Hoehen + GZ, Strukturgebiet,
  Arealbonus)
- Oberhofen am Thunersee komplett (BR 2012/2024, Hoehen-System
  ohne GZ)
- Erste echte GFZo-Berechnung: Thunstrasse 40 Bern, Status GERING
- Bug-Fix: Hoehen-System ohne GZ wird korrekt behandelt

## Iteration 3: Verifikation und Vervollstaendigung (laufend)

**Zeitraum**: 28. April 2026 - Mitte Mai 2026

**Ziel**: Reglement-Daten durch Fachperson verifizieren lassen
und Stadt Bern Bauklassenplan vollstaendig einpflegen.

**Offene Aufgaben**:

### Christophe
- Erfassungs-Excel an Schwager senden mit Begleittext
- Antwort des Schwagers in `bern.json` einpflegen
- `fachliche_grundlagen.md` mit Bauklassenplan-Werten erweitern
- Falls noetig: vierte Gemeinde aufnehmen (z.B. Koeniz)

### Fabienne
- GitHub-Username an Christophe senden fuer Collaborator-Einladung
- Repo durchklicken und erste Anforderungs-Liste erstellen
- `docs/anforderungen.md` als Skelett anlegen
- Implizite Annahmen im Code identifizieren

### Gemeinsam
- Mid-Iteration-Termin (Anfang Mai)
- Fortschritt abgleichen
- Iteration 4 vorbereiten

## Iteration 4: Webseite (geplant)

**Zeitraum**: Mitte Mai 2026 - Anfang Juni 2026

**Ziel**: Streamlit-GUI fuer Endanwender.

**Verantwortlich**: Fabienne (mit Christophe als Backend-Support).

**Geplante Inhalte**:
- Eingabefeld fuer Adresse mit Autocomplete
- Live-Aufruf der Backend-Pipeline
- Visualisierung Parzelle auf Kartenausschnitt
- Strukturierte Ergebnisanzeige (Karten, Tabellen, Status-Ampel)
- PDF-Export fuer Kundendossier
- Auch Anforderungs-Spezifikation `docs/anforderungen.md`
  vollenden

## Iteration 5: Generalprobe (geplant)

**Zeitraum**: Mitte Juni 2026

**Ziel**: Praesentation einueben und Edge-Cases abdecken.

**Inhalte**:
- Pitch-Text auf 5 Minuten trimmen
- Live-Demo-Adressen auswaehlen und proben
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

## Naechste Termine

- **Anfang Mai 2026**: Mid-Iteration-Sync mit Fabienne
- **Mitte Mai 2026**: Iteration 3 abgeschlossen, Bern komplett
- **Mitte Juni 2026**: Generalprobe
- **17. Juni 2026**: Abgabe und Praesentation
