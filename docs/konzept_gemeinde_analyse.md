# Konzept: Gemeinde-Analyse mit Verdichtungs-Rangliste

**Status**: GENEHMIGT, EMPIRISCH VERIFIZIERT, **UMGESETZT** (Iteration 5 + 6)
**Umgesetzt in**: Iteration 5 (Pilot Oberhofen, 12.05.2026) +
                  Iteration 6 (Grossstadt Thun + Konzept-Klaerung, 23.05.2026)
**Primaerer Output**: Excel-Liste fuer Weiterverarbeitung
**Zielgruppe**: Architekten und Investoren (suchen Verdichtungs-Potenzial)
**Verfasser**: Christophe Jenzer mit Claude

**Umsetzungs-Stand aller Module (23.05.2026)**:

| Modul | Status |
|---|---|
| `datenquellen/gwr.py` | ✅ FERTIG (30.04. vorgebaut, 12.05. EGRID-Fix, 20.05. Tolerance) |
| `datenquellen/parzellen_liste.py` | ✅ FERTIG (12.05., Gemeinde-Filter 22.05.) |
| `gemeinde_analyse.py` | ✅ FERTIG (12.05.) |
| `excel_export.py` | ✅ FERTIG (12.05., Karten-Link + Baujahr + Reserve-% 23.05.) |
| `klassifikation.py` (BONUS) | ✅ FERTIG (12.05., KLEINPARZELLE 23.05.) |
| `gemeinde_cache.py` (BONUS) | ✅ FERTIG (12.05.) |
| `datenquellen/tlm3d.py` (BONUS) | ✅ FERTIG (12.05., Bodenbedeckungs-Filter) |

**Pilot-Stand Iteration 5 (12.05.2026)**:
- Oberhofen am Thunersee, 1176 Parzellen, 41 Min, 0 Fehler
- 170 hochwertige Kandidaten identifiziert
- Verifikation gegen map.geo.admin.ch: 7 Stichproben (OEREB-Datenluecken
  bei Strassen/Wald entdeckt -> Bodenbedeckungs-Filter ergaenzt)

**Grossstadt-Stand Iteration 6 (23.05.2026)**:
- Stadt Thun, 8534 Parzellen, ~4h30, 0 Fehler
- VERDICHTUNG 890 / NEUGESCHAEFT 354 / ERSATZNEUBAU 1514 /
  AUSGEREIZT 1752 / KLEINPARZELLE neu eingefuehrt
- Vier Grossstadt-Bugs gefixt (EGRID-Fallback, Gemeinde-Filter,
  MAX_API_CALLS, GWR-tolerance)
- Karten-Link auf map.geo.admin.ch (Kanton BE hat geo.apps.be.ch
  zum 1.9.2025 abgeschafft)
- Konzeptionelle Klaerung: Tool als faktenbasierter Indikator
  (Konflikt-Visualisierung statt Pseudo-Praezision)

---

## HINWEIS ZUM URSPRUENGLICHEN KONZEPT

Der nachfolgende Text ist das urspruengliche Konzept-Dokument vom
29./30.04.2026. Es ist erhalten geblieben, weil es die Architektur-
Entscheidungen und die empirische Verifikation der API-Annahmen
dokumentiert. Der aktuelle Umsetzungs-Stand steht oben.

---

## Zusammenfassung in einem Satz

Statt einzelne Adressen abzufragen, soll das Tool eine ganze Gemeinde
analysieren und eine **priorisierte Excel-Liste der Verdichtungs-
Kandidaten** ausgeben, die ein Architekt oder Investor abarbeiten kann.

## Motivation

Heute: Anwender muss jede Parzelle einzeln ueber die Adresse abfragen.
Bei 1000 Parzellen einer Gemeinde -> mehrere Tage Arbeit.

Mit Massen-Analyse: Tool liefert in einer Stunde eine Excel-Liste mit
den interessantesten Parzellen - sortiert nach Reserve, Klassifikation
und Hinweis-Staerke. Daraus kann der Anwender 10-20 Parzellen fuer
die Detailpruefung waehlen.

Use-Cases siehe Abschnitt "Beispiel-Use-Cases" weiter unten.

## Zwei-Phasen-Ansatz

### Phase 1: Massen-Screening (alle Parzellen, grobe Werte)

- Alle Parzellen der Gemeinde sammeln (rekursiver Praefix-Baum ueber
  swisstopo SearchAPI)
- Pro Parzelle: Cache-Check, dann OEREB + Reglement + GWR
- Klassifikation (VERDICHTUNG, NEUGESCHAEFT, ERSATZNEUBAU, AUSGEREIZT,
  UNAUFFAELLIG, KLEINPARZELLE, AUSSCHLUSS_*)
- Throttling, Retry, SQLite-Cache
- Output: Excel mit 6 Sheets (Statistik + Klassifikations-Sheets +
  Gesamtliste)

### Phase 2: Detail-Verifikation (Top-Treffer einzeln)

- Anwender waehlt aus der Excel-Liste die interessanten Parzellen
- Detail-Analyse via Adresse, Parzellennummer, EGRID oder Koordinate
- Vollstaendiger Bericht mit Empfehlungs-Block und GWR-Plausibilitaets-
  Konflikt-Box

## Datengrundlage

- OEREB-Webservice Kanton Bern (Parzellen + Zonen)
- swisstopo SearchAPI (Adress-/Parzellen-/Koordinaten-Suche)
- GWR (Eidg. Geb.- und Wohnungsregister) ueber swisstopo MapServer
- Baureglement-JSON pro Gemeinde
- BKP-API Stadt Bern (parzellenscharfe Werte)
- swissTLM3D-Strassen (Bodenbedeckungs-Filter)
- BFS-Arealstatistik (Bodenbedeckung NOLC04)

### Warum nicht swissBUILDINGS3D?

Hatten wir am Anfang erwogen. Nachteile:
- mehrere GB Download pro Kanton
- aufwaendiges Aufsetzen einer lokalen Geodaten-Pipeline
- aktualisiert nur jaehrlich

Mit der GWR-API via REST-MapServer haben wir `garea` und `gastw` direkt
pro Gebaeude, ohne lokale Geodaten. Das skaliert sauber.

## GWR-API: was sie liefert

### Zwei-Stufen-Workflow

1. **SearchAPI** liefert pro Adresse die GWR-`featureId` (z.B.
   `1435137_0` fuer Frutigenstrasse 25, Thun)
2. **MapServer** liefert mit der featureId die vollen Gebaeudedaten:
   ```
   egid, egrid, lparz, ggdename
   garea (Grundflaeche m^2)
   gastw (Vollgeschosse)
   ganzwhg (Wohnungen)
   gbaup (Bauperiode-Code)
   warea (Wohnungs-Flaechen)
   ```

Fuer die Massen-Analyse (ohne Adresse) wurde ein direkter MapServer-
Identify-Aufruf entwickelt: `gebaeude_zu_egrid(egrid, koordinate_lv95)`.

### Beispielantwort (gekuerzt) Frutigenstrasse 25, Thun

```
egid:     1435137
egrid:    CH394601433582
lparz:    324
ggdename: Thun
garea:    304    (Grundflaeche m^2)
gastw:    5      (Vollgeschosse)
ganzwhg:  7      (Wohnungen)
gbaup:    8016   (Bauperiode-Code, ~1996-2000)
```

Daraus rechnen wir: 304 m^2 x 5 = 1520 m^2 Geschossflaeche.

### Wichtige empirische Befunde

1. **GWR-Felder alle da wie aus Doku erwartet.**
   `garea`, `gastw`, `egrid`, `lparz`, `ggdename` - alle vorhanden
   und sauber typisiert.

2. **Mehrere Adressen koennen auf VERSCHIEDENEN Parzellen sein.**
   Frutigenstrasse 25 liegt auf Parzelle 324, Frutigenstrasse 25a
   auf einer eigenen Parzelle 4029. Aggregation muss **pro EGRID**
   erfolgen, nicht pro Strasse.

3. **Plausibilitaets-Konflikt aufgedeckt.**
   Frutigenstrasse 25:
   - Ist mit Platzhalter 25%: 371 m^2
   - Ist aus GWR (304 x 5): 1520 m^2
   - Soll (Schaetzung): 1080 m^2

   Die Parzelle ist **bereits zu 141% ausgeschoepft** wenn man die
   echten GWR-Werte nimmt. Genau dieser Konflikt ist die
   Existenzberechtigung dieses Konzepts.

## Architektur-Skizze

```
parzellen_liste.py  (SearchAPI, rekursiver Praefix-Baum)
        |
        v
gemeinde_analyse.py  (Pipeline mit Throttling + Cache)
        |
        +--> analyse_adresse.analysiere_per_egrid()
        |    +--> bern.OerebQuelle (Reglement-Zone)
        |    +--> baureglement.lade()
        |    +--> bern_bkp.lade_parzelle()  (nur Stadt Bern)
        |    +--> gwr.gebaeude_zu_egrid()
        |    +--> tlm3d.ist_strasse() / ist_wald_verdacht()
        |    +--> potenzial.berechne()
        |    +--> klassifikation.klassifiziere()
        |
        +--> gemeinde_cache.speichere()
        |
        v
excel_export.exportiere()
        |
        v
ausgaben/bauzonen_radar_<gemeinde>_<datum>.xlsx
```

## Datenmodell (neu)

```python
@dataclass
class GemeindeKonfiguration:
    name: str
    bfs_nr: int
    kanton: str
    reglement_pfad: Path

@dataclass
class KantonsCache:
    db_pfad: Path
    eintraege: dict[str, AnalyseErgebnis]  # key: egrid

    def fuelle_aus_db(self): ...
    def speichere(self, ergebnis: AnalyseErgebnis): ...
    def ist_gecacht(self, egrid: str) -> bool: ...

@dataclass
class Klassifikation(Enum):
    VERDICHTUNG         # bebaut + Reserve
    NEUGESCHAEFT        # leer + Bauland
    ERSATZNEUBAU        # alt + Reserve
    AUSGEREIZT          # Bestandsschutz / >100%
    UNAUFFAELLIG        # bebaut, knapp ausgeschoepft
    KLEINPARZELLE       # 200-500 m2 (NEU Iter 6, neutral)
    AUSSCHLUSS_REGLEMENT
    AUSSCHLUSS_ZU_KLEIN
    AUSSCHLUSS_VERKEHR
    AUSSCHLUSS_WALD_VERDACHT
    AUSSCHLUSS_FEHLER
```

## Neue Module

- `datenquellen/parzellen_liste.py` (Praefix-Baum-Suche)
- `gemeinde_analyse.py` (Massen-Pipeline)
- `gemeinde_cache.py` (SQLite + Pickle)
- `klassifikation.py` (Geschaeftslogik)
- `excel_export.py` (XLSX mit 6 Sheets)
- `datenquellen/tlm3d.py` (BONUS, Bodenbedeckungs-Filter)

## Aufwandsschaetzung

Urspruengliche Schaetzung (29.04.): 13-19 Stunden.

Tatsaechlicher Aufwand:
- Iter 5 (12.05.): ~11 Stunden, alle Module fertig
- Iter 6 (20.-23.05.): ~10 Stunden, Grossstadt-Tauglichkeit + Konzept

## Risiken und Annahmen

### Risiko 1: Rate-Limiting der OEREB-API (EMPIRISCH BESTAETIGT)

Im 50-Adressen-Stresstest (29.04.) traten 2 transiente API-Fehler auf.
Hochgerechnet auf 500 Parzellen: ca. 20 Ausfaelle.

**Massnahmen umgesetzt**: Throttling 0.7 Sek, Retry 3x mit
exponentialem Backoff, SQLite-Caching (Wiederaufnahme nach Abbruch).

Im Pilot Oberhofen (1176) und Grossstadt-Lauf Thun (8534): jeweils
0 unbehobene Fehler.

### Risiko 2: Aggregation pro EGRID (EMPIRISCH GEKLAERT)

Mehrere Strassen-Adressen koennen auf derselben oder auf verschiedenen
Parzellen liegen.

**Loesung umgesetzt**: Aggregation erfolgt pro EGRID, nicht pro Adresse.

### Risiko 3: GWR-Datenqualitaet

GWR-Daten sind nicht immer vollstaendig - bei BK_E und Altstadt-
Adressen fehlt oft die Geschosszahl (`gastw`).

**Loesung umgesetzt**: Module faengt das mit "GWR-Daten unvollstaendig
(fehlt: Feld)"-Anzeige ab, statt zu crashen.

### Risiko 4: Massen-Suche limitiert auf 50 (EMPIRISCH BESTAETIGT)

swisstopo SearchAPI defaultet auf 50 Treffer.

**Loesung umgesetzt**: Rekursive Praefix-Baum-Suche
("Oberhofen" -> "Oberhofen 1" -> "Oberhofen 10" ...). Mit
Deduplizierung via EGRID-Set.

Im Pilot Oberhofen: 1176 Parzellen via 161 API-Calls in 126 Sek.
Im Grossstadt-Lauf Thun: 8534 Parzellen via 2940 API-Calls.

### Risiko 5: Grossstadt-Bugs (ENTDECKT IN ITER 6)

Vier Bugs, die im Dorf nie sichtbar waren:
- EGRID-Fallback (OEREB liefert in Thun teils kein egrid)
- Gemeinde-Filter (SearchAPI macht Praefix-Matching: "Thun" matcht
  Thundorf, Thunstetten etc.)
- MAX_API_CALLS Limit (500 reicht nicht fuer Thun)
- GWR-tolerance (Treffer-Cap-Ueberschreitung in dichten Quartieren)

Alle gefixt, dokumentiert in Journal (Iter 6).

## Eingabewege fuer die Detail-Analyse

Im Hinblick auf Phase 2: nicht alle Parzellen haben eine Adresse
(insb. unbebaute Bauland-Parzellen in BE). Vier Eintrittspunkte:

- **Adresse** (existiert schon): `analysiere(adresse_str)`
- **Parzellennummer + Gemeinde**: `analysiere_per_parzelle(nr, gem)`
- **EGRID direkt**: `analysiere_per_egrid(egrid)`
- **Koordinate LV95**: `analysiere_per_koordinate(e, n)`

Alle vier nutzen intern dieselbe `_analysiere_kernpipeline()`.

## Eigentuemer-Daten: bewusster Verzicht auf Automatisierung

Naheliegende Frage: kann das Tool nach Identifikation einer
interessanten Parzelle gleich auch den Eigentuemer rauslassen?

**Antwort: nein, bewusst nicht automatisiert.**

### Begruendung

1. **Captcha-Schutz** ist die explizite technische Barriere des
   Datenherrn. Umgehung waere unbefugter Zugriff (Art. 143bis StGB).
2. **AGOV-Login seit 1.9.2025**: GRUDIS public erfordert
   personalisierten Login. Tool-Weitergabe mit eingebetteten
   Credentials waere nicht zulaessig.
3. **revDSG seit 1.9.2023**: verbietet automatisches Profilieren
   personenbezogener Daten ohne Rechtsgrundlage.
4. **Reputationsrisiko** bei Massenanschreiben "Sehr geehrter Herr
   X geboren 15.3.1965, Ihre Parzelle hat 480 m^2 Reserve...".

### Was das Tool stattdessen macht

Brueckenansatz: Direktlink im Output zum eidg. Kartendienst
`map.geo.admin.ch/?swisssearch=<EGRID>`. Anwender loggt sich selber
ein und macht die Abfrage manuell.

Iter-6-Aktualisierung: Der urspruengliche GRUDIS-Direktlink
funktioniert nicht mehr (geo.apps.be.ch wurde vom Kanton BE zum
1.9.2025 abgeschafft). Wir nutzen jetzt den eidg. Kartendienst -
login-frei, immer verfuegbar.

### Die Rangliste skaliert die Funktion automatisch richtig

- Interessante 10-20 Parzellen aus der Excel-Liste? -> manuell mit
  GRUDIS abfragen (zumutbar)
- 500 Parzellen anschreiben? -> Direktanfrage beim Grundbuchamt ist
  der korrekte Weg

Das ist ehrliches Engineering: Komfort skaliert mit Datenschutz-
Verantwortung.

### Wenn jemand Eigentuemer-Massenabfragen braucht

Direktanfrage beim Grundbuchamt mit definiertem Berechtigungs-Pruefverfahren.
Das ist nicht Aufgabe dieses Tools.

## Aufrufschnittstelle (geplant)

### Kommandozeile

```
# Massen-Analyse einer Gemeinde
python -m bauzonenradar.gemeinde_analyse --gemeinde "Oberhofen am Thunersee"
python -m bauzonenradar.gemeinde_analyse --gemeinde "Thun" --throttling 1.0

# Detail-Analyse via Adresse (existiert schon)
python -m bauzonenradar.analyse_adresse "Frutigenstrasse 25, 3604 Thun"

# NEU: Detail-Analyse via Parzellennummer (fuer unbebaute Parzellen)
python -m bauzonenradar.analyse_adresse --parzelle "Oberhofen 309"

# NEU: Detail-Analyse via EGRID (z.B. aus Rangliste)
python -m bauzonenradar.analyse_adresse --egrid CH382046359635

# NEU: Detail-Analyse via LV95-Koordinate (z.B. Karten-Klick)
python -m bauzonenradar.analyse_adresse --koord "2614500,1178500"
```

### Output-Beispiel (CLI)

```
Bauzonen-Radar - Massen-Analyse Oberhofen am Thunersee
============================================================
Parzellen-Liste sammeln... 1176 Parzellen via 161 API-Calls (126s)
Analyse laeuft... [###################-] 95% (1117/1176)
ETA: 2 Min 14 Sek

Statistik:
  VERDICHTUNG:    55  ( 5%)
  NEUGESCHAEFT:  257  (22%)
  ERSATZNEUBAU:   38  ( 3%)
  AUSGEREIZT:     77  ( 7%)
  ...

Excel gespeichert: ausgaben/bauzonen_radar_oberhofen_2026-05-12.xlsx
```

### Excel-Output-Spalten (Primaerformat)

Pro Sheet (Verdichtung, Neugeschaeft, Ersatzneubau, Ausgereizt, Alle):

- Parzellen-Nr., Flaeche, Zone, Klassifikation
- Soll (m^2), Ist GWR (m^2), Reserve (m^2), Reserve (%)
- Geb. (Anzahl), Baujahr (NEU Iter 6, aeltestes), Datenqualitaet
- Karte (Direktlink auf map.geo.admin.ch, NEU Iter 6)

Sheet "Statistik": Klassifikations-Verteilung, Top-Parzellen pro
Kategorie, Hinweis auf Datenqualitaet.

## Beispiel-Use-Cases fuer die Verteidigung

### Use-Case 1: "Architekt sucht Verdichtungs-Auftrag"

Eingabe: "Oberhofen am Thunersee"
Ausgabe: Excel mit 55 VERDICHTUNG-Parzellen, sortiert nach Reserve.
Architekt kann gezielt 5-10 Eigentuemer kontaktieren mit konkreter
Schaetzung was machbar waere.

### Use-Case 2: "Investor sucht freie Bauland-Parzellen"

Eingabe: "Thun"
Ausgabe: Excel mit 354 NEUGESCHAEFT-Parzellen. Investor kann nach
Flaeche, Zone und Lage filtern und die interessantesten manuell
verifizieren (GRUDIS-Link fuer Eigentuemer-Abfrage).

### Use-Case 3: "Architekt vergleicht zwei Quartiere"

Zwei Massen-Analysen mit unterschiedlichen Gemeinden, Excel-Sheets
nebeneinander legen. Welche Gemeinde hat mehr ERSATZNEUBAU-Hebel?
Welche mehr leeres Bauland? Bei welcher ist das Durchschnitts-Baujahr
am ältesten? Datengetriebene Entscheidung statt Bauchgefuehl.

## Was nicht zum Konzept gehoert

- Automatische Eigentuemer-Massenabfragen (siehe oben, bewusst)
- Empfehlung an Eigentuemer (rechtlich heikel)
- 3D-Visualisierung (waere fuer Architekten relevant, aber out of
  scope)
- Live-Karten-View mit Klick-Interaktion (waere Phase 3 in Iter 6/7
  oder Folgeprojekt)
- Automatische Verifikation gegen Bauverwaltungs-Auskuenfte
  (manuell durch Anwender)

## Naechste Schritte

Iter 5 + 6 sind umgesetzt. Naechste Schritte siehe `projektplan.md`,
Iteration 7 (Indikator-Verfeinerung + Generalprobe, geplant Juni 2026).
