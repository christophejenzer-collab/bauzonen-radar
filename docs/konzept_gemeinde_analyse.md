# Konzept: Gemeinde-Analyse mit Verdichtungs-Rangliste

**Status**: GENEHMIGT (29. April 2026)
**Geplant fuer**: Iteration 5 (nach Streamlit-GUI in Iteration 4)
**Primaerer Output**: CSV/Excel-Liste fuer Weiterverarbeitung
**Zielgruppe**: Architekten und Investoren (suchen Verdichtungs-Potenzial)
**Verfasser**: Christophe Jenzer mit Claude

## Zusammenfassung in einem Satz

Statt einzelne Adressen abzufragen, analysiert das Tool eine **ganze
Gemeinde** und liefert eine **priorisierte Rangliste** der Parzellen
mit dem groessten Verdichtungs-Potenzial - getrennt nach "frei" und
"bebaut mit Reserve".

## Motivation

Das aktuelle Tool beantwortet die Frage "Was kann ich an dieser
Adresse bauen?". Die naechste, viel wertvollere Frage ist:

> "In welcher Gemeinde gibt es ueberhaupt noch Verdichtungs-Potenzial,
> und wo genau?"

Diese Frage interessiert Architekten, Investoren und Stadtplaner
gleichermassen - aber niemand beantwortet sie heute systematisch fuer
den Berner Raum.

## Zwei-Phasen-Ansatz

Die Vision teilt sich in zwei Schritte mit unterschiedlicher
Datenqualitaet:

### Phase 1: Massen-Screening (alle Parzellen, grobe Werte)

Fuer **alle** Parzellen einer Gemeinde:
- Soll-Wert aus bestehender Pipeline (OEREB + Reglement)
- Ist-Wert aus GWR (Grundflaeche x Geschosse) oder 0 wenn frei
- Reserve = Soll - Ist
- Sortierung nach absoluter oder relativer Reserve

Output: Rangliste der Top-Kandidaten als Tabelle.

### Phase 2: Detail-Verifikation (Top-Treffer einzeln)

Fuer die Top 10-20 Kandidaten:
- Bestehender Detailbericht mit allen Bemerkungen
- Schwager-Verifikation
- Bei Bedarf Vor-Ort-Begehung

Phase 2 ist **bereits implementiert** (das ist unser heutiges Tool) -
neu ist nur Phase 1.

## Datengrundlage

Drei Datenquellen werden kombiniert. Zwei davon haben wir schon, die
dritte ist neu:

| Datenquelle | Was | Zugriff | Status |
|---|---|---|---|
| OEREB (BE) | Parzelle + Zone + Restriktionen | REST-API api3.geo.admin.ch | bereits implementiert |
| Baureglement (JSON) | Bauwerte pro Zone | lokale JSON-Dateien | bereits implementiert |
| GWR | Bestehende Gebaeude (Grundflaeche, Geschosse, EGID) | REST-API api3.geo.admin.ch | NEU - muss angebunden werden |

Plus eine vierte fuer die Listen-Generierung:

| Datenquelle | Was | Zugriff | Status |
|---|---|---|---|
| SearchServer | Liste aller Parzellen einer Gemeinde | REST-API api3.geo.admin.ch | NEU |

### Warum nicht swissBUILDINGS3D?

swissBUILDINGS3D 3.0 Beta liefert detaillierte 3D-Modelle. Wir
brauchen aber nur Grundflaeche und Geschosszahl. Beides liefert das
GWR direkt via API - ohne Mehrere-GB-Download.

Falls spaeter doch noetig (z.B. fuer Dachformen oder genaue
Volumenberechnung), kann swissBUILDINGS3D als Phase 3 dazukommen.
Heute waere es Overkill.

## GWR-API: was sie liefert

Endpoint: `https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/{egid}_0`

Beispielantwort fuer ein Lausanner Gebaeude (gekuerzt):
```json
{
  "egid": "880711",
  "egrid": "CH367583455638",
  "strname_deinr": "Chemin Isabelle-de-Montolieu 109",
  "ggdename": "Lausanne",
  "garea": 721,        // Grundflaeche m^2
  "gastw": 5,          // Anzahl Geschosse
  "ganzwhg": 8,        // Anzahl Wohnungen
  "gbauj": 1981,       // Baujahr
  "gkode": 2539319,    // LV95 Ost
  "gkodn": 1155036     // LV95 Nord
}
```

Ist-Geschossflaeche = `garea x gastw` = `721 x 5` = `3605 m^2`.

Das ist **kein Platzhalter**, sondern ein verbindlicher amtlicher
Wert.

## Architektur-Skizze

```
Eingabe: "Analysiere Gemeinde Oberhofen am Thunersee"
   |
   v
Schritt 1: Hole alle Parzellen-EGRIDs der Gemeinde
   - SearchServer mit type=locations, origin=parcel
   - Filter auf Gemeinde-Name
   - Ergebnis: ~500 EGRIDs
   |
   v
Schritt 2: Pro Parzelle (parallelisierbar)
   - OEREB-Auskunft (existiert)
   - Reglement-Lookup (existiert)
   - GWR-Lookup (NEU): garea + gastw -> Ist-Wert
     Falls kein Gebaeude: Ist-Wert = 0, Kategorie = FREI
   - Soll-Wert aus Reglement-Pipeline (existiert)
   - Reserve = Soll - Ist
   |
   v
Schritt 3: Rangliste erstellen
   - Sortieren nach absoluter Reserve in m^2
   - Filter: Mindestreserve, keine Schutzzone, etc.
   - Top 50 Kandidaten
   |
   v
Output: CSV/Excel/Streamlit-Tabelle
```

## Datenmodell (neu)

Eine zusaetzliche Datenklasse fuer die Massenanalyse:

```python
@dataclass
class ParzellenKandidat:
    egrid: str
    parzellennummer: str
    adresse: str | None
    flaeche_m2: float
    zone: str
    soll_geschossflaeche_m2: float
    ist_geschossflaeche_m2: float    # 0 wenn FREI
    kategorie: str                   # "FREI" oder "BEBAUT"
    reserve_m2: float                # soll - ist
    reserve_prozent: float
    datenqualitaet: str              # VERBINDLICH/GROBSCHAETZUNG/NICHT_MOEGLICH
    bemerkungen: list[str]


@dataclass
class GemeindeRangliste:
    gemeindename: str
    analyse_datum: str
    anzahl_parzellen_total: int
    anzahl_bebaut: int
    anzahl_frei: int
    anzahl_nicht_berechenbar: int
    kandidaten: list[ParzellenKandidat]   # sortiert
```

## Neue Module

Im Projekt `src/bauzonenradar/`:

| Modul | Aufgabe | Aufwand |
|---|---|---|
| `gwr.py` | GWR-API ansprechen, EGID -> Gebaeudedaten | 2-3 Std. |
| `parzellen_liste.py` | Liste aller EGRIDs einer Gemeinde holen | 2-3 Std. |
| `gemeinde_analyse.py` | Massen-Pipeline orchestrieren | 4-6 Std. |
| `rangliste_export.py` | CSV/Excel/Markdown ausgeben | 1-2 Std. |

Plus Anpassungen an existierenden Modulen:
- `analyse_adresse.py` bekommt eine zweite Eintrittspunkte fuer
  EGRID-basierte Abfragen (heute geht es nur ueber Adresse)

## Aufwandsschaetzung

Da diese Funktion in **Iteration 5** kommt (nach Streamlit-GUI),
fokussieren wir die Schaetzung auf die reine Backend-Implementierung.
Die GUI-Anbindung erfolgt spaeter optional.

| Schritt | Aufwand | Wer |
|---|---|---|
| Konzept-Dokument (dieses hier) | 30 Min | done |
| GWR-Anbindung mit Tests | 2-3 Std. | Entwickler |
| Parzellen-Liste pro Gemeinde | 2-3 Std. | Entwickler |
| Massen-Pipeline | 4-6 Std. | Entwickler |
| Excel/CSV-Export-Funktionen | 2-3 Std. | Entwickler |
| Test mit Oberhofen + Tuning | 2-3 Std. | Entwickler |
| **Gesamt** | **~13-19 Std.** | (ca. 2 Tage Entwickler-Zeit) |

Falls die Streamlit-GUI in Iteration 4 eine "Massen-Analyse"-Seite
bekommen soll, kommen ~4-6 Stunden zusaetzlich dazu - ist aber
optional und waere Iteration 6.

## Risiken und Annahmen

### Risiko 1: Rate-Limiting der OEREB-API

Bei 500 Parzellen sind 500 OEREB-Aufrufe noetig. Falls die API ein
Limit hat, brauchen wir:
- Throttling (z.B. 1 Aufruf/Sekunde)
- Lokales Caching (SQLite) der OEREB-Auskuenfte
- Wiederaufnahme bei Abbruch

**Mitigation**: Erst mit 50 Stichproben testen, dann Throttle-Wert
fixieren. Bei Bedarf SQLite-Cache fuer wiederholte Analysen.

### Risiko 2: Mapping EGRID <-> EGID

GWR liefert EGID (Gebaeude). OEREB arbeitet mit EGRID (Parzelle).
Eine Parzelle kann **mehrere Gebaeude** haben. Wir muessen alle
Gebaeude einer Parzelle aufsummieren.

**Mitigation**: GWR-Felder `egrid` und `lparz` (Liegenschaftsnummer)
nutzen, um pro Parzelle alle Gebaeude zu finden.

### Risiko 3: GWR-Datenqualitaet

GWR wird von Gemeinden gepflegt. In manchen Faellen fehlen `garea`
oder `gastw`. Dann faellt die Ist-Wert-Berechnung aus.

**Mitigation**: Fallback auf den 25%-Platzhalter mit klarer Markierung
"Ist-Wert geschaetzt mangels GWR-Daten".

### Risiko 4: Gemeinde-Filter im SearchServer

Es ist nicht ganz klar, ob der SearchServer eine "alle Parzellen
einer Gemeinde"-Abfrage erlaubt oder nur Volltext-Suche. Falls nur
Volltext: alternative Quelle ueber AV-Daten der amtlichen Vermessung.

**Mitigation**: Erst mit kleinem Test pruefen.

## Eingabewege fuer die Detail-Analyse

Bisheriger Eintrittspunkt war ausschliesslich die **Adresse** ueber das
Geocoding (swisstopo SearchAPI). Das funktioniert gut fuer bebaute
Parzellen mit Hausnummer.

**Problem**: Im Kanton Bern haben **unbebaute Parzellen meistens keine
Adresse**. Genau diese Parzellen sind aber fuer Architekten und
Investoren besonders interessant (komplettes Verdichtungs-Potenzial,
keine Eigentuemer-Verhandlung wegen Bestandsbau).

Iteration 5 erweitert deshalb die Eintrittspunkte:

| Eintritt | Beispiel | Use-Case |
|---|---|---|
| Adresse | "Hauptstrasse 30, 3653 Oberhofen" | bebaute Parzellen, Reserve-Berechnung |
| Parzellennummer + Gemeinde | "Oberhofen 309" | unbebaute Parzellen ohne Adresse |
| EGRID | "CH382046359635" | aus der Rangliste der Massen-Analyse |
| Koordinate (LV95) | "2614500, 1178500" | bei Karten-Klick (Streamlit-Iter4) |

Technisch funktionieren alle vier ueber das gleiche Backend - die
swisstopo SearchAPI unterstuetzt `origins=parcel` fuer Parzellen-
Suche, und die OEREB-Pipeline arbeitet ohnehin EGRID-basiert.

## Eigentuemer-Daten: bewusster Verzicht auf Automatisierung

Eine naheliegende Frage ist: kann das Tool nach Identifikation einer
interessanten Parzelle gleich auch die Eigentuemerin oder den
Eigentuemer rauslassen? Technisch existiert die kantonale
Datenbank GRUDIS public, die genau diese Daten liefert (Name,
Geburtsdatum, weitere Liegenschaften).

**Entscheidung: Tool greift NICHT automatisch auf Eigentuemerdaten zu.**

### Begruendung

1. **Captcha-Schutz**: GRUDIS verlangt vor jeder Abfrage eine
   fuenfstellige Captcha-Eingabe. Das ist die explizite technische
   Barriere des Datenherrn gegen Massenabfragen. Captcha-Umgehung
   waere als unbefugter Zugriff zu werten (Art. 143bis StGB).
2. **AGOV-Login seit 1. September 2025**: Die Eigentuemer-Auskunft
   erfordert seit Herbst 2025 ein authentifiziertes Login ueber
   AGOV. Das Tool weiterzugeben mit eingebetteten Credentials ist
   nicht moeglich.
3. **Datenschutzgesetz (revDSG seit 1.9.2023)**: Auch wenn
   Einzelteile oeffentlich abrufbar sind, ist das automatisierte
   **Profilieren** (Eigentuemer + Geburtsdatum + Bauland-Reserve)
   eine Personendatenbearbeitung mit hohem Risiko. Ohne
   Rechtsgrundlage problematisch.
4. **Reputationsrisiko**: Massenanschreiben an Eigentuemer auf
   Basis automatisch erhobener Daten ist gesellschaftlich heikel
   und wuerde dem Tool und den Nutzenden schaden.

### Was das Tool stattdessen macht

Im Output jeder Parzellen-Analyse erscheint ein **Direktlink** zur
manuellen GRUDIS-Abfrage:

```
PARZELLE 309, Oberhofen am Thunersee
====================================
Bauland-Reserve: 480 m^2 (33% Ausschoepfung)

Eigentuemer-Auskunft:
  Manuell ueber GRUDIS public (kantonale Datenbank, BE-Login):
  https://www.gba.dij.be.ch/de/start/dienstleistungen/online-abfragen/eigentumsauskunft.html
```

Damit ist die Funktion fuer Architekten und Investoren da - mit
einem zusaetzlichen Klick pro Parzelle.

### Die Rangliste skaliert die Funktion automatisch richtig

Genau hier kommt das Zwei-Phasen-Konzept zum Tragen. Die
Massen-Analyse liefert eine **priorisierte Rangliste**. Daraus
selektiert der User nur die Top-Treffer fuer die manuelle
GRUDIS-Abfrage:

```
500 Parzellen einer Gemeinde
       |
       | Massen-Screening (automatisch, Phase 1)
       v
ca. 50-100 Kandidaten mit signifikanter Reserve
       |
       | Filter (Top 25, Reserve > 200 m^2, Zone W2-W4)
       v
ca. 25 wirklich interessante Parzellen
       |
       | MANUELL: GRUDIS-Klick pro Parzelle (5-10 Minuten)
       v
25 Eigentuemer-Datensaetze
```

Ein typischer Investor-Workflow:
1. Massen-Analyse einer Gemeinde laufen lassen (1-2 Min)
2. Excel-Liste oeffnen, sortieren, Top 25 markieren
3. Pro Top-Parzelle: GRUDIS-Link klicken, einloggen, Eigentuemer
   notieren (~20 Sek pro Parzelle)
4. Nach 5-10 Minuten: 25 Adressen bereit fuer Akquisitions-Mail

Diese natuerliche Begrenzung durch Top-N ist **kein Workaround,
sondern gutes Design**: Wer nach 25 Klicks aufhoert, hat die besten
25 Parzellen sowieso schon. Wer 500 Eigentuemer braucht, sollte
ohnehin zum Grundbuchamt gehen - was rechtlich korrekt ist.

### Wenn jemand Eigentuemer-Massenabfragen braucht

Der korrekte Weg fuehrt ueber:
- Direktanfrage beim **kantonalen Grundbuchamt** mit nachgewiesenem
  berechtigtem Interesse
- **Datenkooperation** mit dem Kanton Bern (Geoinformation)
- **Bezahltes Datenprodukt** (z.B. von Privatdienstleistern, die
  eine Lizenz haben)

Diese Wege sind nicht Teil dieses Tools.

## Aufrufschnittstelle (geplant)

### Kommandozeile

```bash
# Massen-Analyse einer Gemeinde
python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee"
python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee" --top 20
python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee" --export csv

# Detail-Analyse via Adresse (existiert schon)
python -m bauzonenradar.analyse_adresse "Hauptstrasse 30, 3653 Oberhofen"

# NEU: Detail-Analyse via Parzellennummer (fuer unbebaute Parzellen)
python -m bauzonenradar.analyse_parzelle --gemeinde "Oberhofen" --nr 309

# NEU: Detail-Analyse via EGRID (z.B. aus Rangliste)
python -m bauzonenradar.analyse_parzelle --egrid CH382046359635

# NEU: Detail-Analyse via LV95-Koordinate (z.B. Karten-Klick)
python -m bauzonenradar.analyse_parzelle --lv95 2614500,1178500
```

### Output-Beispiel (CLI)

```
Verdichtungs-Radar Oberhofen am Thunersee
==========================================
Analyse-Datum: 2026-04-29
Gesamt: 487 Parzellen analysiert
Davon bebaut:           412 (84.6%)
Davon frei:              75 (15.4%)
Davon nicht berechenbar: 18  (3.7%)

TOP 20 KANDIDATEN (sortiert nach absoluter Reserve in m^2)
============================================================
 #  | Adresse              | Zone | Status  | Ist  | Soll | Reserve | %
----+----------------------+------+---------+------+------+---------+-----
 1. | Hauptstrasse 14      | M2   | bebaut  |  240 |  720 |     480 |  33%
 2. | Alpenstrasse 8       | W2   | frei    |    0 |  480 |     480 |   0%
 3. | Seestrasse 102       | W3   | bebaut  |  180 |  600 |     420 |  30%
 4. | Bahnhofstrasse 5     | M2   | bebaut  |  120 |  480 |     360 |  25%
 ...

Liste exportiert nach: oberhofen_rangliste_2026-04-29.xlsx
```

### Excel-Output-Spalten (Primaerformat)

Damit Architekten und Investoren direkt mit der Liste arbeiten
koennen, enthaelt das Excel folgende Spalten:

| Spalte | Inhalt | Beispiel |
|---|---|---|
| Rang | Position in der Rangliste | 1 |
| Adresse | Vollstaendige Adresse | Hauptstrasse 14, 3653 Oberhofen |
| EGRID | Eindeutige Parzellen-ID | CH382046359635 |
| Parzellennummer | Lokale Nummer | 309 |
| Gemeinde | Name der Gemeinde | Oberhofen am Thunersee |
| Zone | OEREB-Bezeichnung | Mischzone M2 |
| Bauklasse | Falls vorhanden | (leer fuer Thun) |
| Flaeche m^2 | Parzellenflaeche | 675 |
| Status | FREI / BEBAUT / NICHT_BERECHENBAR | bebaut |
| Anzahl Gebaeude | aus GWR | 1 |
| Baujahr | aelteste Baujahr aus GWR | 1962 |
| Ist Geschossflaeche m^2 | garea x gastw aus GWR | 240 |
| Soll Geschossflaeche m^2 | aus Pipeline | 720 |
| Reserve absolut m^2 | soll - ist | 480 |
| Reserve relativ % | reserve / soll | 67 |
| Datenqualitaet | VERBINDLICH/GROBSCHAETZUNG/NICHT_MOEGLICH | GROBSCHAETZUNG |
| Schutzzone | ja/nein | nein |
| Naturgefahren | ja/nein + Anzahl | nein |
| Bemerkungen | Kompakte Hinweise | Ortsbildschutz |
| OEREB-Link | Link zum offiziellen Auszug | https://... |

CSV ist als Alternative-Format ebenfalls verfuegbar (`--export csv`),
fuer Architekten/Investoren ist aber Excel der Standard.

## Beispiel-Use-Cases fuer die Verteidigung

Die Zielgruppe sind **Architekten und Investoren**, die in einer
Gemeinde gezielt Verdichtungs-Potenzial suchen. Die Rangliste ist
ihre Akquisitions-Grundlage.

### Use-Case 1: "Architekt sucht Verdichtungs-Auftrag"

Ein Architekt will in Thun ein Mehrfamilienhaus-Projekt akquirieren.
Statt selbst Adresse fuer Adresse anzuschauen, kriegt er die Top 50
Parzellen mit hohem Verdichtungs-Potenzial als Excel-Liste. Daraus
waehlt er die interessantesten aus und kontaktiert die Eigentuemer
direkt.

**Konkreter Workflow**:
1. `python -m bauzonenradar.gemeinde_analyse "Thun" --export xlsx`
2. Excel-Liste oeffnen, sortieren nach absoluter Reserve
3. Filter setzen: nur "bebaut mit Reserve > 200 m^2"
4. Top 20 Adressen kopieren -> Eigentuemer-Recherche

### Use-Case 2: "Investor sucht freie Bauland-Parzellen"

Ein Investor sucht freie Parzellen in Oberhofen fuer ein
Einfamilienhaus-Projekt. Filter: kein Gebaeude, mindestens 500 m^2,
Zone W2 oder W3.

**Konkreter Workflow**:
1. `python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee" --export csv`
2. CSV in Excel oeffnen, Filter "Status = FREI" + "Flaeche >= 500"
3. Ergebnis: 8 Parzellen mit Adresse und maximaler Bebauungsmoeglichkeit

### Use-Case 3: "Architekt vergleicht zwei Quartiere"

Architekt arbeitet an einem Stadtteilkonzept fuer Bern und Thun.
Er fragt beide Gemeinden ab und vergleicht die durchschnittliche
Reserve pro Parzelle, die Anzahl freier Parzellen und die Verteilung
der Zonen.

**Konkreter Workflow**: Zwei Excel-Files nebeneinander legen,
Pivot-Tabelle daraus.

## Was nicht zum Konzept gehoert

Bewusst ausgeklammert:

- Eigentuemer-Daten (sind aus Datenschutz-Gruenden nur via Login
  beim Grundbuchamt erhaeltlich, nicht via API)
- Echte 3D-Volumenberechnung mit swissBUILDINGS3D (zu aufwendig
  fuer den Mehrwert)
- Multi-Gemeinden-Vergleich in einer Abfrage (kommt spaeter, falls
  Use-Case sich bewaehrt)
- Marktdaten / Preise (nicht der Scope dieses Tools)

## Naechste Schritte

1. **Diese Konzept-Notiz reviewen** mit Schwager (Architekt-Sicht!)
2. **Konzept committen** - dient als Grundlage fuer Iteration 5
3. **Iteration 4 abwarten** (Fabienne baut die Streamlit-GUI)
4. **Vor Iteration 5**: GWR-API mit echter Adresse testen
   (Quick Win, 5 Min) - verifiziert die zentrale Annahme
5. **Iteration 5 starten**: Modul `gwr.py` als ersten Baustein
6. **Test mit Oberhofen** als erste Vollausbau-Gemeinde

Die Reihenfolge ist wichtig: Fabienne sollte ihre Streamlit-GUI nicht
fuer eine Funktion designen die noch nicht existiert. Wenn die
Massen-Analyse spaeter fertig ist, kann sie als zweiter Tab im
Streamlit dazukommen (Iteration 6 oder direkt im Backlog).
