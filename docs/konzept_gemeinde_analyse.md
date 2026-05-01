# Konzept: Gemeinde-Analyse mit Verdichtungs-Rangliste

**Status**: GENEHMIGT, EMPIRISCH VERIFIZIERT, **TEILWEISE UMGESETZT** (30. April 2026)
**Geplant fuer**: Iteration 5 (parallel zu Streamlit-GUI in Iteration 4)
**Primaerer Output**: CSV/Excel-Liste fuer Weiterverarbeitung
**Zielgruppe**: Architekten und Investoren (suchen Verdichtungs-Potenzial)
**Verfasser**: Christophe Jenzer mit Claude

**Umsetzungs-Stand der vier geplanten Module**:

| Modul | Status |
|---|---|
| `datenquellen/gwr.py` | ✅ FERTIG (30.04.2026) |
| `datenquellen/parzellen_liste.py` | offen, Anfang Juni |
| `gemeinde_analyse.py` | offen, Anfang Juni |
| Excel-Export | offen, Anfang Juni |

**Verifikations-Stand am 29.04.2026**:
- 50-Adressen-Stresstest: 96% Erfolg, 1.7 Min Laufzeit
- API-Spike: SearchServer (Parzelle/Massen/Adresse) + GWR-MapServer alle bestaetigt
- Echtes Beispiel Frutigenstrasse 25 zeigt: garea=304 m^2, gastw=5,
  Ist-Geschossflaeche=1520 m^2 (vs. unsere Schaetzung 1080 m^2)

**Live-Stand am 30.04.2026 (mit GWR integriert)**:
- 50-Adressen-Stresstest mit GWR: 96% Erfolg, 2.2 Min Laufzeit
- Plausibilitaets-Konflikt jetzt sichtbar bei vielen Adressen
- Aggregation mehrerer Gebaeude pro Parzelle funktioniert

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

**Empirisch verifiziert am 29.04.2026 mit Frutigenstrasse 25, Thun.**

### Zwei-Stufen-Workflow

```
Stufe 1: SearchAPI mit type=address liefert featureId
  https://api3.geo.admin.ch/rest/services/api/SearchServer
    ?type=locations&origins=address&searchText=Frutigenstrasse+25+Thun
  -> featureId: "1435137_0"

Stufe 2: MapServer mit featureId liefert Gebaeudedaten
  https://api3.geo.admin.ch/rest/services/ech/MapServer/
    ch.bfs.gebaeude_wohnungs_register/1435137_0
```

Die SearchAPI liefert sogar einen **direkten Link** zum GWR-Datensatz
im `links`-Feld der Response - wir muessen die URL nicht selber
basteln.

### Beispielantwort (gekuerzt) Frutigenstrasse 25, Thun

```json
{
  "egid": "1435137",
  "egrid": "CH394601433582",
  "strname_deinr": "Frutigenstrasse 25",
  "ggdename": "Thun",
  "ggdenr": 942,
  "lparz": "324",                  // Parzellennummer
  "garea": 304,                    // Grundflaeche m^2 ⭐
  "gastw": 5,                      // Anzahl Vollgeschosse ⭐
  "ganzwhg": 7,                    // Anzahl Wohnungen
  "gbauj": null,                   // Baujahr fehlt manchmal
  "gbaup": 8016,                   // Bauperiode-Code (Fallback)
  "gkode": 2614427,                // LV95 Ost
  "gkodn": 1177937,                // LV95 Nord
  "gschutzr": null,                // Denkmalschutz
  "gwaerzh1": 7432,                // Heizungs-Code (Waermepumpe)
  "gwaerdath1": "29.06.2021",      // Heizung saniert
  "warea": [85, 105, 45, 75, 95, 105, 75],  // Wohnungs-Flaechen
  "wazim": [2, 4, 2, 3, 4, 4, 3]            // Zimmer pro Wohnung
}
```

**Ist-Geschossflaeche** = `garea x gastw` = `304 x 5` = **1520 m^2**.

Das ist **kein Platzhalter**, sondern ein verbindlicher amtlicher
Wert vom Bundesamt fuer Statistik.

### Wichtige empirische Befunde

**Befund 1: Mehrere Adressen koennen auf verschiedenen Parzellen sein.**
Frutigenstrasse 25 (Hauptgebaeude) liegt auf Parzelle 324, Frutigen-
strasse 25a (Nebengebaeude, 5 m^2) liegt auf einer eigenen Parzelle
4029. Die Aggregation erfolgt also **pro EGRID**, nicht pro Adresse.

**Befund 2: Plausibilitaetskonflikt mit der Schaetzung.** Auf
Frutigenstrasse 25 zeigt der Vergleich:

| Wert | Quelle | m^2 |
|---|---|---|
| Ist (Platzhalter 25%) | unser bisheriges Tool | 371 |
| Ist (GWR echt) | garea x gastw | **1520** |
| Soll (Schaetzung) | Reglement-Pipeline | 1080 |

Die Parzelle ist mit GWR-Werten bereits **141% ausgeschoepft**.
Unser Tool sagte 34% Ausschoepfung. Das ist **kein Tool-Bug** -
es ist die Konsequenz daraus, dass die Schaetzung im Hoehen-System
konservativ ist (sie nimmt 12 m Defaultbreite, real wurde aber
breiter gebaut). Genau diese Diskrepanz wird Iteration 5 mit echten
Ist-Werten aufdecken.

**Befund 3: Reichhaltige Bonus-Daten.** Pro Gebaeude liefert GWR
nicht nur garea/gastw, sondern auch:
- Wohnungs-Aufstellung (Anzahl, Flaechen, Zimmer)
- Heizungs-System mit Sanierungsdatum
- Energietraeger Heiz- und Warmwasser
- Geometrie-Koordinaten (LV95)
- Denkmalschutz-Flag

Diese Daten koennen optional in den Excel-Export der Massen-Analyse
einfliessen - fuer Investoren ist das Sanierungs-Datum besonders
relevant ("vor 1990 gebaut, ungesanierte Heizung -> Wertsteigerungs-
Potenzial").

## Architektur-Skizze

Mit den am 29.04.2026 empirisch verifizierten API-Endpoints sieht
der Datenfluss konkret so aus:

```
Eingabe: "Analysiere Gemeinde Oberhofen am Thunersee"
   |
   v
Schritt 1: Parzellen-Liste der Gemeinde holen
   - GET .../SearchServer?type=locations&origins=parcel
                          &searchText=Oberhofen
   - Achtung: API limitiert auf 50 Treffer
   - Strategie: alphabetische oder nummerische Suchstrategie
     (z.B. "Oberhofen 1-50", "Oberhofen 51-100", ...)
   - Throttling: 0.5-1 Sek Pause zwischen Calls
   - Cache: SQLite zur Wiederaufnahme bei Abbruch
   - Ergebnis: ~500 EGRIDs mit Koordinaten und Bounding Box
   |
   v
Schritt 2: Pro Parzelle (sequenziell, mit Throttling)
   |
   +-- 2a: OEREB-Auskunft (existiert)
   |       GET .../oereb/extract/json?EGRID=...
   |       -> Zone, Restriktionen
   |
   +-- 2b: Reglement-Lookup (existiert)
   |       Lokale JSON pro Gemeinde
   |       -> Soll-Wert via Pipeline
   |
   +-- 2c: GWR-Lookup (NEU) - Zwei-Stufen-Prozess
   |       Stufe 1: Adresse(n) der Parzelle finden
   |          GET .../SearchServer?type=locations
   |              &origins=address&searchText=<Adresse-aus-OEREB>
   |          -> Liste von featureIds
   |       Stufe 2: Pro featureId das Gebaeude abfragen
   |          GET .../MapServer/.../gebaeude_wohnungs_register
   |              /<featureId>
   |          -> garea, gastw, ganzwhg, etc.
   |       Aggregation: Gebaeude mit gleichem EGRID
   |                    aufsummieren
   |       -> Ist-Wert oder 0 falls keine Gebaeude (FREI)
   |
   +-- 2d: Reserve berechnen
           Reserve = Soll - Ist
   |
   v
Schritt 3: Rangliste erstellen
   - Sortieren nach absoluter Reserve in m^2
   - Filter: Mindestreserve, Schutzzone-Ausschluss
   - Top 50 Kandidaten als Excel
   |
   v
Output: Excel-Liste mit GRUDIS-Direktlinks pro Parzelle
        (manuelle Eigentuemer-Abfrage durch User)
```

## Datenmodell (neu)

Drei Datenklassen werden gebraucht, basierend auf den am 29.04.
verifizierten GWR-Feldern. Die Felder spiegeln **direkt die echte
GWR-API-Antwort** wider.

```python
@dataclass
class GwrGebaeude:
    """Ein einzelnes Gebaeude aus dem GWR.
    Felder spiegeln die echte API-Response.
    """
    egid: str                # eindeutige Gebaeude-ID
    egrid: str               # Parzelle (zur Aggregation)
    parzellennummer: str     # lparz aus GWR
    gemeinde: str            # ggdename
    bfs_gemeinde: int        # ggdenr (z.B. 942 fuer Thun)
    grundflaeche_m2: int     # garea
    geschosse: int           # gastw
    anzahl_wohnungen: int | None      # ganzwhg
    baujahr: int | None              # gbauj
    bauperiode_code: int | None       # gbaup (Fallback wenn baujahr fehlt)
    heizung_saniert_datum: str | None # gwaerdath1
    denkmalschutz: bool              # gschutzr is not None
    koord_lv95: tuple[float, float]   # gkode, gkodn

    @property
    def geschossflaeche_m2(self) -> int:
        """Ist-Geschossflaeche = Grundflaeche * Geschosse"""
        return self.grundflaeche_m2 * self.geschosse


@dataclass
class ParzellenKandidat:
    """Eine Parzelle in der Rangliste.
    Aggregiert ggf. mehrere Gebaeude.
    """
    egrid: str
    parzellennummer: str
    adresse: str | None              # Hauptadresse falls vorhanden
    gemeinde: str
    flaeche_m2: float
    zone: str

    # Soll aus Pipeline (bestehende Logik)
    soll_geschossflaeche_m2: float
    datenqualitaet_soll: str         # VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH

    # Ist aus GWR (NEU in Iter 5)
    gebaeude: list[GwrGebaeude]      # leer wenn FREI
    ist_geschossflaeche_m2: float    # sum(g.geschossflaeche_m2 for g in gebaeude)

    # Abgeleitet
    kategorie: str                   # "FREI", "BEBAUT", "NICHT_BERECHENBAR"
    reserve_m2: float                # soll - ist
    reserve_prozent: float           # reserve / soll * 100

    # GRUDIS-Link fuer manuelle Eigentuemer-Abfrage
    grudis_link: str

    bemerkungen: list[str]


@dataclass
class GemeindeRangliste:
    gemeindename: str
    bfs_nummer: int
    analyse_datum: str
    laufzeit_sekunden: float

    anzahl_parzellen_total: int
    anzahl_bebaut: int
    anzahl_frei: int
    anzahl_nicht_berechenbar: int
    anzahl_api_fehler: int           # transiente Ausfaelle aus Stresstest

    kandidaten: list[ParzellenKandidat]   # sortiert nach reserve_m2 desc
```

**Begruendung der Aufteilung in `GwrGebaeude` und `ParzellenKandidat`**:
Der Stichproben-Test mit Frutigenstrasse 25 hat empirisch gezeigt,
dass eine Parzelle mehrere Gebaeude haben kann (Hauptbau + Schopf),
und dass diese unterschiedliche EGRIDs haben koennen. Die saubere
Trennung erlaubt:
- pro Parzelle alle zugehoerigen Gebaeude aufsummieren
- pro Gebaeude die Bonus-Daten (Heizung, Sanierungsdatum)
  optional in den Excel-Export uebernehmen
- spaeter (Iteration 6+) auch pro-Gebaeude-Filter
  ("nur unsanierte vor 1990")

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

Die Risiken wurden am 29.04. mit dem 50-Adressen-Stresstest und dem
API-Spike empirisch konkretisiert.

### Risiko 1: Rate-Limiting der OEREB-API (EMPIRISCH BESTAETIGT)

**Empirischer Befund vom 50-Adressen-Stresstest**:
- 50 Adressen, 1.7 Min Laufzeit, 96% Erfolgsquote
- 2 transiente Ausfaelle (4%)
- Beide Adressen einzeln nochmal durchgelaufen -> erfolgreich

Hochrechnung auf 500 Parzellen: ca. 20 Ausfaelle ohne
Fehlerhandling. Das ist zu viel fuer eine produktive Massen-Analyse.

**Mitigation (Implementierungs-Plan)**:
- **Throttling**: 0.5-1 Sek Pause zwischen Calls. Bei 500 Parzellen
  -> 5-10 Min Laufzeit, akzeptabel.
- **Retry-Logic**: 1-2 Wiederholungen bei `Returncode 1` mit
  exponentialem Backoff (z.B. 2, 4, 8 Sek)
- **SQLite-Cache** der OEREB-Auskuenfte: bei Wiederholungslauf einer
  Gemeinde keine erneuten API-Calls noetig
- **Wiederaufnahme nach Abbruch**: idempotenter Pipeline-Start, der
  Cache pruefen, fortsetzen statt neu beginnen

### Risiko 2: Aggregation pro EGRID (EMPIRISCH GEKLAERT)

**Empirischer Befund vom GWR-Spike**:
Frutigenstrasse 25 hat zwei featureIds:
- `1435137_0` -> Hauptgebaeude auf Parzelle 324 (EGRID CH394601433582)
- `502105207_0` -> Nebengebaeude (5 m^2) auf eigener Parzelle 4029
                   (EGRID CH200135654628)

Die zwei Adressen liegen also auf **verschiedenen Parzellen**. Die
Aggregation erfolgt per **EGRID-Gleichheit**, nicht per
Adress-Aehnlichkeit.

**Mitigation (Implementierungs-Plan)**:
- Pro Adresse alle featureIds vom SearchServer holen
- Pro featureId via GWR-MapServer das Gebaeude laden
- Gebaeude nach EGRID gruppieren, pro EGRID `geschossflaeche_m2`
  aufsummieren

### Risiko 3: GWR-Datenqualitaet

GWR wird von Gemeinden gepflegt. In den Tests sahen wir bereits:
- `gbauj` war null fuer Frutigenstrasse 25 (`gbaup` Bauperiode-Code
  als Fallback vorhanden)
- `gastw` und `garea` waren bei Hauptgebaeude voll vorhanden
- Bei Nebengebaeuden (gkat=1060) fehlten viele Felder

**Mitigation**:
- Wenn `garea` und `gastw` beide vorhanden -> Ist-Wert verbindlich
- Wenn nur `garea` vorhanden -> Schaetzung mit Annahme 2 Geschossen,
  klare Markierung "geschaetzt"
- Wenn weder noch -> Fallback auf 25%-Platzhalter wie heute,
  Datenqualitaet GROBSCHAETZUNG

### Risiko 4: Massen-Suche limitiert auf 50 (EMPIRISCH BESTAETIGT)

**Empirischer Befund vom Massen-Suche-Spike**:
```
GET .../SearchServer?type=locations&origins=parcel&searchText=Oberhofen
```
liefert genau **50 Treffer**, sortiert nach Parzellennummer
aufsteigend. Die offizielle Doku erwaehnt keinen `offset`- oder
`limit`-Parameter.

**Mitigation - drei Strategien zur Auswahl**:

1. **Nummerische Suchstrategie** (einfach, robust):
   ```
   GET .../?searchText=Oberhofen+1     -> Parzelle 1, 10, 100, ...
   GET .../?searchText=Oberhofen+2     -> Parzelle 2, 20, 200, ...
   GET .../?searchText=Oberhofen+50    -> Parzelle 50, 500, ...
   ```
   Mehrere Aufrufe pro Gemeinde, dafuer alle Parzellen erreichbar.

2. **Bbox-Strategie** (geometrisch):
   ```
   GET .../?bbox=617000,175000,618000,176000&type=locations
   ```
   Gemeindegebiet in Quadranten teilen, pro Quadrant max. 50 Treffer.

3. **AV-Daten-Direktbezug** (alternative Quelle):
   Kanton Bern stellt amtliche Vermessungsdaten zur Verfuegung,
   diese enthalten alle Parzellen einer Gemeinde komplett.

**Empfehlung**: Strategie 1 (nummerisch) ist am einfachsten und
funktioniert ohne lokale Datenhaltung. Bei Pilotgemeinde Oberhofen
mit ~500 Parzellen reichen 10-20 Aufrufe von je max. 50 Treffern.

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
