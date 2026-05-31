# Code-Walkthrough Backend — fuer die Verteidigung

Dieses Dokument erklaert jede Code-Sektion in Klartext, so dass auch
ein IT-Fremder versteht was passiert. Ziel: bei jeder Code-Frage
strukturiert antworten koennen.

---

## TEIL 1: Datenfluss durch das ganze System

```
Adresse                      "Frutigenstrasse 25, 3604 Thun"
   |
   v
[1] analyse_adresse.py       Schaltzentrale
   |                         "Hole Daten von ueberall, baue Bericht"
   |
   +--> [2] Geocoding         Adresse -> Koordinaten (LV95 + WGS84)
   |        swisstopo SearchAPI
   |
   +--> [3] OEREB-Webservice  Welche Parzelle? Welche Zone?
   |        Kanton Bern
   |
   +--> [4] baureglement.py   Was sagt das Gemeinde-Reglement?
   |        Lokales JSON
   |
   +--> [5] bern_bkp.py       Nur Stadt Bern: parzellenscharfe Werte
   |        ArcGIS REST-API
   |
   +--> [6] gwr.py            Was steht heute auf der Parzelle?
   |        Gebaeuderegister GWR
   |
   +--> [7] potenzial.py      RECHENKERN
   |        Zulaessig vs. Bestand vs. Reserve
   |
   v
AnalyseErgebnis (Datencontainer mit ~40 Feldern)
   |
   v
GUI (Streamlit) oder CLI (Konsole)
```

---

## TEIL 2: Die wichtigsten Dateien

| Datei | Was sie tut | Zeilen |
|---|---|---|
| analyse_adresse.py | Schaltzentrale - ruft alle Module auf | ~552 |
| potenzial.py | Rechenkern - drei Berechnungspfade | ~934 |
| baureglement.py | Laedt Reglement aus JSON, erkennt Synonyme | ~495 |
| klassifikation.py | Ordnet Parzelle einer Kategorie zu | ~287 |
| gemeinde_analyse.py | Massen-Pipeline fuer ganze Gemeinde | ~404 |
| excel_export.py | Erstellt Excel mit 6 Reitern | ~467 |
| datenquellen/gwr.py | GWR-API-Anbindung | ~330 |

---

## TEIL 3: analyse_adresse.py - Sektion fuer Sektion

### Sektion 1: AnalyseErgebnis (Zeile 66-150)

**Was es ist:** Ein "Behaelter" fuer alle Daten, die das Tool zu einer
Adresse sammelt. Wie ein Formular mit ~40 Feldern.

**Warum als Dataclass:** Python erlaubt mit `@dataclass` einen sauberen,
typsicheren Container ohne viel Boilerplate-Code. Der Behaelter
transportiert Daten zwischen den Schritten - das ist sein einziger
Zweck. Dataclass ist hier richtig, weil das Objekt kaum Logik hat
(nur zwei Hilfsmethoden `hat_potenzial` und `koordinaten_fuer_karte`).

**Klartext-Vergleich:** Stell dir vor, ein Anwalt sammelt fuer einen
Fall: Personalien (Name, Adresse), Sachverhalt (Datum, Ort),
Beweise (Dokumente), Gutachten (Expertenmeinung). Alles in einer
Akte. AnalyseErgebnis ist die Akte.

**Was drin steht:**
- Adresse, Status, Fehler, Warnungen
- Parzellen-Infos (Gemeinde, Nummer, Flaeche, EGRID)
- Koordinaten (LV95 fuer Schweiz, WGS84 fuer Karten)
- Reglement-Status, Bauklasse, Zone
- GWR-Daten (Liste der Gebaeude + Geschossflaeche)
- Potenzial (datenqualitaet, zulaessig_m2, ausschoepfung etc.)

---

### Sektion 2: Geocoding-Hilfsfunktionen (Zeile 161-220)

**Was es ist:** Zwei kleine Funktionen, die Adressen in Koordinaten
umwandeln.

`_hole_lv95_koordinaten`: Schickt die Adresse an die swisstopo
SearchAPI und bekommt Schweizer Koordinaten zurueck (LV95-System).

`_lv95_zu_wgs84`: Wandelt Schweizer Koordinaten (LV95) in Welt-
Koordinaten (WGS84, was Google Maps & Co. nutzen) um. Brauchen wir
fuer die Karten-Anzeige in der GUI.

**Klartext-Vergleich:** Wie wenn ein GPS einen Strassennamen in 
"Breitengrad/Laengengrad" uebersetzt - mit zwei verschiedenen 
Koordinatensystemen (Schweiz vs. Welt).

---

### Sektion 3: analysiere() - die Schaltzentrale (Zeile 222-407)

**Was es ist:** Die Hauptfunktion. Bekommt eine Adresse rein,
ruft alle Module der Reihe nach auf, gibt ein vollstaendig befuelltes
AnalyseErgebnis zurueck.

**Warum getrennt von der Ausgabe:** Bewusste Architektur-Entscheidung
aus Iteration 4. Die GUI und die Konsole brauchen DIESELBE Logik, 
aber unterschiedliche Ausgaben. `analysiere()` rechnet, 
`drucke_bericht()` zeigt an. So koennen beide Oberflaechen 
denselben Rechenkern nutzen, ohne Code zu duplizieren.

**Ablauf in analysiere():**

```
1. Geocoding         Adresse -> LV95 + WGS84
2. OEREB-Anfrage     LV95 -> Parzelle + Zonen
3. Reglement laden   Gemeinde -> JSON-Reglement
4. BKP (nur Bern)    Parzelle -> Bauweise + Geometrie
5. GWR-Anfrage       Parzelle/Adresse -> Bestehende Gebaeude
6. Potenzial rechnen Alles -> Zulaessig + Reserve
7. Bericht bauen     Alles -> Textbericht (fuer CLI)
```

**Defensive Programmierung:** Wenn eine Anfrage fehlschlaegt 
(z.B. GWR down), faengt der Code das ab und fuegt eine Warnung 
ein, statt komplett zu crashen. Das macht das Tool robust gegen 
transiente API-Fehler (wir hatten 2 von 50 Adressen im Stresstest 
mit solchen Ausfaellen).

---

### Sektion 4: Helper-Funktionen (Zeile 409-441)

**Was sie tun:** `_attr_zu_string()` und `_zahlenfeld()` sind kleine
defensive Helfer, um Werte aus dem PotenzialErgebnis robust 
auszulesen. Falls ein Feld nicht existiert (z.B. weil das Modell 
in einem aelteren Iterations-Stand erstellt wurde), liefert die 
Funktion None statt einen Crash.

**Lessons-Learned (Iter 4):** Diese Helfer waren urspruenglich zu 
defensiv - sie suchten nach mehreren moeglichen Feldnamen. Das 
fuehrte beim Sonntag-Refactoring (03.05.) zu einem Bug, weil nie 
einer der Namen matchte. In Iter 4 (11.05.) haben wir das gefixt, 
indem wir die echten Feldnamen direkt verwenden und die Aliase 
explizit als zusaetzliche Felder in AnalyseErgebnis aufgenommen 
haben.

---

### Sektion 5: drucke_bericht() (Zeile 443-534)

**Was es tut:** Formatiert das AnalyseErgebnis fuer die Konsole.
Das ist die CLI-Ausgabe ("Bauzonen-Radar - Analyse fuer: Adresse").

**Wichtig:** Die Logik (rechnen) ist getrennt von der Praesentation 
(formatieren). Die GUI nutzt die Daten direkt ohne diesen 
Konsolen-Text - sie macht ihre eigene visuelle Darstellung.

---

### Sektion 6: main() (Zeile 536-552)

**Was es tut:** Der CLI-Einstiegspunkt. Liest die Adresse als 
Kommandozeilen-Argument, ruft `analysiere()` und `drucke_bericht()`, 
gibt einen Exit-Code zurueck.

```
python -m bauzonenradar.analyse_adresse "Frutigenstrasse 25, 3604 Thun"
```

---

## TEIL 4: potenzial.py - der Rechenkern

### Sektion 1: PotenzialStatus + Datenqualitaet (Zeile 45-58)

**Was sie sind:** Zwei Enums (Aufzaehlungstypen) fuer klare Zustaende:

```python
class PotenzialStatus(Enum):
    HOCH      = "HOCH"        # >= 60% Reserve
    MITTEL    = "MITTEL"      # 30-60% Reserve
    GERING    = "GERING"      # 10-30% Reserve
    AUSGESCHOEPFT = "AUSGESCHOEPFT"  # < 10% Reserve

class Datenqualitaet(Enum):
    VERBINDLICH     = "VERBINDLICH"   # AZ/GFZo - exakt
    GROBSCHAETZUNG  = "GROBSCHAETZUNG"  # Hoehensystem - Heuristik
    NICHT_MOEGLICH  = "NICHT_MOEGLICH"  # Spezialregime
```

**Warum Enum:** Statt magischen Strings ("HOCH", "MITTEL") haben wir 
typsichere Konstanten. Der Compiler/IDE warnt bei Tippfehlern, der 
Code ist selbstdokumentierend.

**Klartext-Vergleich:** Wie ein Ampelsystem. Drei feste Farben 
(rot/gelb/gruen) statt frei waehlbarer Farbtoene. Eindeutig und 
nachvollziehbar.

---

### Sektion 2: PotenzialErgebnis (Zeile 61-220)

**Was es ist:** Container fuer das Ergebnis der Potenzialberechnung. 
Enthaelt alle Zwischenwerte (Soll, Ist, Reserve), den Status, die 
Datenqualitaet und den ASCII-Empfehlungsblock.

**Methoden:**
- `textbericht()`: Erstellt den lesbaren Block fuer die Konsole
- `_formatiere_empfehlung()`: Baut den Empfehlungs-Block mit Balken
- `_zeichne_balken()`: Erstellt den ASCII-Balken `[####------]`
- `_lagebeurteilung()`: Mappt Reserve-% auf einen der 4 Status

---

### Sektion 3: PotenzialBerechner.berechne() (Zeile 225+)

**Was es tut:** Die Hauptmethode des Rechenkerns. Entscheidet, 
welche Berechnungsmethode anzuwenden ist, basierend auf dem 
Reglement:

```
Wenn Reglement = VERBINDLICH (AZ oder GFZo):
    -> _behandle_verbindliche_berechnung()
    -> Flaeche x Kennzahl, exakt

Wenn Reglement = Hoehen+GZ (Schaetzung noetig):
    -> _behandle_hoehen_und_gz()
    -> _schaetze_geschossflaeche_hoehen()
    -> Drei-Begrenzer-Logik

Wenn Reglement = NICHT_MOEGLICH (z.B. ZPP):
    -> _behandle_nicht_moeglich()
    -> Keine Zahl, Verweis auf Bauverwaltung
```

**Klartext-Vergleich:** Wie ein Bahnhofs-Vorsteher der entscheidet 
welcher Zug auf welches Gleis kommt - je nach Zugtyp (ICE, 
Regio, Gueterzug). Drei verschiedene Pfade fuer drei 
verschiedene Datenlagen.

---

### Sektion 4: Drei-Begrenzer-Logik (Zeile 798+)

**Das ist die wichtigste Sektion fuer die Mathematik-Verteidigung.**

`_schaetze_geschossflaeche_hoehen()` berechnet bei Hoehen-System 
die maximale Geschossflaeche ueber drei mathematische Begrenzer 
und nimmt den kleinsten:

```python
# Begrenzer 1: Geometrie
nutzbare_lang = lange_seite - 2 * grosser_grenzabstand
nutzbare_kurz = kurze_seite - 2 * kleiner_grenzabstand
grundflaeche_geometrie = nutzbare_lang * nutzbare_kurz

# Begrenzer 2: Parzelle minus Gruenflaeche
grundflaeche_parzelle = parzellenflaeche * (1 - GZ)

# Begrenzer 3: Parzelle geteilt durch Geschosszahl
# (Wenn 3 Geschosse, kann die Grundflaeche max. 1/3 sein, 
# damit das Total der Geschossflaeche im Rahmen bleibt)
grundflaeche_gz = grundflaeche_parzelle / geschosszahl

# Der kleinste der drei gewinnt:
grundflaeche_zulaessig = min(
    grundflaeche_geometrie,
    grundflaeche_parzelle,
    grundflaeche_gz
)

geschossflaeche = grundflaeche_zulaessig * geschosszahl
```

**Klartext-Vergleich:** Wie wenn drei Personen einen Schrank tragen 
muessen, der durch drei Tueren passt. Die kleinste Tuer bestimmt, 
wie gross der Schrank maximal sein darf. Die anderen zwei Tueren 
sind groesser, also nicht das Problem.

**Edge-Cases (wichtig zu erklaeren):**
- Wenn `max_gebaeudelaenge=None` (unbeschraenkt): wir setzen 
  `float("inf")`. `min()` ignoriert das automatisch, dann werden 
  die anderen zwei Begrenzer relevant.
- Wenn die Parzelle so klein ist, dass `nutzbare_lang < 0`: 
  Geometrie-Begrenzer wird negativ, was unrealistisch ist. 
  Iter-6-Erkenntnis: bei sehr kleinen Parzellen kollabiert das 
  Soll - das ist eine Eigenschaft der geometrischen Annahme, 
  keine Schwaeche des Codes.

**Annahmen:**
- Parzellen-Form: Rechteck 1:1.5 (statt Quadrat - verhindert dass 
  bei langen, schmalen Parzellen die kurze Seite negativ wird)
- Grenzabstaende werden auf allen vier Seiten voll abgezogen
- 1:1.5 ist eine pragmatische Vereinfachung, weil wir die echte 
  Parzellengeometrie nicht abfragen (das waere ein Folgeprojekt)

---

### Sektion 5: _schaetze_ist_bebauung() (Zeile 887)

**Was es tut:** Wenn keine GWR-Daten vorliegen, schaetzt diese 
Funktion die aktuelle Bebauung als 25% der Parzellenflaeche.

```python
def _schaetze_ist_bebauung(parzelle):
    return parzelle.flaeche_m2 * 0.25
```

**Warum 25%:** Empirisch begruendet - typische Schweizer Wohnzonen 
liegen bei 20-30% Grundflaechenanteil. Wir starteten in Iter 2 mit 
40%, korrigierten in Iter 3 auf 25% weil 40% bei vielen Parzellen 
unrealistische Werte ueber 100% Ausschoepfung produzierte. 25% ist 
konservativ am unteren Rand des Bandes - wir wollen lieber Reserve 
unterschaetzen als ueberschaetzen.

**Wichtig - wann kommt dieser Platzhalter zum Einsatz:** NUR wenn 
GWR keine echten Daten liefert. Bei bebauten Parzellen mit 
GWR-Treffer haben wir den echten Wert. Der Platzhalter ist eine 
Notloesung fuer:
- Unbebaute Parzellen (Gebaeude existiert nicht im GWR)
- GWR-Datenluecken (Gebaeude existiert, aber Geschosszahl fehlt)

**Bekannte Schwaeche:** Bei unbebauten Parzellen (Kategorie 
NEUGESCHAEFT) ist 25% konzeptionell falsch - real sind sie 0%. 
Das ist ein Punkt fuer Iter 7.

---

## TEIL 5: baureglement.py - Reglement-Lader

### Was es tut

Liest die JSON-Datei der Gemeinde (bern.json, thun.json, 
oberhofen_am_thunersee.json) und macht die Werte fuer das Tool 
verfuegbar.

### Wichtigste Logik

**Synonym-Erkennung:** OEREB liefert Zonen-Namen in einer 
Schreibweise ("Wohnen/Arbeiten WA4" mit Slash). Das Reglement 
kann sie anders aufzeichnen ("Wohnen + Arbeiten WA4" mit Plus). 
Der Lader erkennt beide als dieselbe Zone.

**Mehrere Bemessungssysteme:** Pro Reglement koennen Zonen in 
unterschiedlichen Systemen sein. Stadt Bern z.B. hat:
- BK_E mit GFZo (verbindlich)
- BK 2-6 mit Hoehen+GZ (Grobschaetzung)
- ZoeN ohne Werte (NICHT_MOEGLICH)

**Klartext-Vergleich:** Wie ein mehrsprachiges Woerterbuch - 
schlaegt einen Begriff nach, der in verschiedenen Sprachen 
unterschiedlich heisst, und liefert die einheitliche Definition.

---

## TEIL 6: klassifikation.py - Geschaeftslogik fuer Massen-Analyse

### Sektion 1: Hilfsfunktionen (Zeile 63-156)

`echte_ausschoepfung_prozent()`: Berechnet die Ausschoepfung aus 
GWR-Ist und Reglement-Soll. Nutzt die ECHTEN Daten, nicht den 
Platzhalter.

`echte_reserve_m2()`: Reserve in Quadratmetern (Soll - Ist).

`_aeltestes_baujahr()`: Sucht das aelteste Gebaeude in den 
GWR-Daten der Parzelle (Iter 6 ergaenzt).

`_bauperiode_code_zu_jahr()`: Mappt GWR-Bauperiode-Codes 
(8011=1900, 8012=1910 etc.) auf das Anfangsjahr der Periode. 
Wird verwendet wenn das echte Baujahr in den GWR-Daten fehlt.

### Sektion 2: klassifiziere() (Zeile 159+)

**Was es tut:** Ordnet eine Parzelle einer der 10 Kategorien zu, 
basierend auf festen Schwellenwerten.

```
Reglement nicht erfasst        -> AUSSCHLUSS_REGLEMENT
Parzelle < 200 m²              -> AUSSCHLUSS_ZU_KLEIN
Parzelle 200-500 m² (NEU Iter 6) -> KLEINPARZELLE
Strasse (TLM + Areal)          -> AUSSCHLUSS_VERKEHR
Wald-Verdacht (Arealstat)      -> AUSSCHLUSS_WALD_VERDACHT
Berechnungsfehler              -> AUSSCHLUSS_FEHLER

Wenn Soll bekannt:
  Ausschoepfung > 95%          -> AUSGEREIZT (Bestandsschutz)
  Ausschoepfung 70-95%         -> UNAUFFAELLIG
  Ausschoepfung < 70% UND
    keine Bebauung             -> NEUGESCHAEFT
  Ausschoepfung < 70% UND
    bebaut, alt (vor 1980)     -> ERSATZNEUBAU
  Ausschoepfung < 70% UND
    bebaut, neuer              -> VERDICHTUNG
```

**Warum Schwellen als Konstanten:** Anpassbar ohne Code-Eingriff. 
Architekt kann sagen "70% ist zu tief, mach 65%" und es ist EIN 
Zeilen-Change am Anfang der Datei.

---

## TEIL 7: gemeinde_analyse.py - Massen-Pipeline

### Sektion 1: AnalyseOptionen + GemeindeStatistik (Zeile 52-122)

Container fuer die CLI-Optionen (welche Gemeinde, Throttling, 
Limit etc.) und das Endergebnis (Statistik aller Klassifikationen).

### Sektion 2: _analysiere_eine_parzelle() (Zeile 125-203)

**Was es tut:** Verarbeitet eine einzelne Parzelle in der 
Massen-Pipeline:

```
1. Cache pruefen          - Schon analysiert? -> aus DB laden
2. Wenn nicht im Cache:
   - analysiere_per_egrid() aufrufen
   - Throttling: 0.7 Sek warten (API-Schonung)
   - Bei Fehler: 3x Retry mit exponentialem Backoff
3. Bodenbedeckung pruefen - Strasse? Wald?
4. Klassifizieren
5. In Cache speichern
```

**Warum so robust:** Eine Massen-Analyse mit 8534 Parzellen (Thun) 
darf nicht nach 4 Stunden Laufzeit abbrechen, weil eine API einmal 
einen Fehler liefert. Cache + Retry + Throttling sichern den 
Erfolg.

### Sektion 3: analysiere_gemeinde() (Zeile 205-311)

Die Haupt-Schleife. Holt die Parzellen-Liste, iteriert ueber alle, 
zeigt Progress, behandelt Strg+C. Am Ende: Statistik und Cache 
fertig fuer den Excel-Export.

**ETA-Berechnung:** Aus der bisherigen Laufzeit hochrechnen, 
wieviele Minuten noch bleiben. Bei langen Laeufen (4h30 fuer Thun) 
wichtig fuer den Anwender.

---

## TEIL 8: Hauptantworten auf die wahrscheinlichen Dozenten-Fragen

### Frage: "Warum Dataclass fuer AnalyseErgebnis, aber Klasse fuer PotenzialBerechner?"

**Antwort:** "AnalyseErgebnis hat fast keine Logik - es ist ein 
Datencontainer. Dataclass ist perfekt fuer 'value objects' ohne 
Verhalten. PotenzialBerechner hat dagegen viel Verhalten (drei 
Berechnungspfade, Hilfsmethoden, Zustandshalter). Da macht eine 
echte Klasse Sinn, weil das Verhalten zur Identitaet gehoert. 
Generelle Regel: Dataclass fuer Daten, Klasse fuer Verhalten."

### Frage: "Wo kommt die 25%-Annahme her?"

**Antwort:** "Empirisch - typische Schweizer Wohnzonen liegen bei 
20-30% Grundflaechenanteil. Wir starteten konservativ bei 40%, 
korrigierten in Iter 3 auf 25% weil 40% zu hohe Ausschoepfungen 
ueber 100% produzierte. 25% ist am unteren Rand des Bandes, 
konservativ. Wichtig: der Platzhalter greift NUR wenn GWR keine 
echten Daten liefert. Bei den meisten Parzellen haben wir den 
echten Ist-Wert."

### Frage: "Was bedeutet None bei zulaessig_m2?"

**Antwort:** "Heute drei moegliche Bedeutungen: NICHT_MOEGLICH-Pfad 
(Spezialregime), Berechnungsfehler, oder GWR-Datenluecke. Die 
Datenqualitaets-Enum trennt den ersten Fall sauber ab - die GUI 
fragt 'if datenqualitaet == NICHT_MOEGLICH' statt 'if zulaessig 
is None'. Das macht den None-Zustand semantisch klar. Fuer 
Iter 7 waere ein Result-Pattern wie in Rust sauberer."

### Frage: "Erklaer die Drei-Begrenzer-Logik mathematisch."

**Antwort:** Siehe TEIL 4, Sektion 4. Formel zeigen, alle drei 
Begrenzer erklaeren, `min()` als kleinster Sieger, `float("inf")` 
Edge-Case erwaehnen, ehrliche Limitation: bei sehr kleinen 
Parzellen kollabiert das Soll - das ist Iter-6-Erkenntnis.

### Frage: "Warum ist der Reserve-%-Bug in Iter 6 passiert?"

**Antwort:** "Single Source of Truth verletzt. Wir hatten zwei 
Quellen fuer dieselbe Information: reserve_prozent im Backend 
basierte auf einer Modell-Schaetzung (25%-Platzhalter), 
Reserve(m²) im Excel auf echten GWR-Daten. Beide drifteten 
auseinander. Klassisches OOP-Antipattern - in einem Commit gefixt: 
Reserve-% wird jetzt direkt aus Reserve(m²)/Soll berechnet, eine 
Quelle. Im Journal als Lessons-Learned dokumentiert."

---

## TEIL 9: Stichwoerter zum Auswendiglernen

```
Architektur:        Separation of Concerns - analysiere() vs. drucke_bericht()
Datenmodell:        Dataclass fuer Container, Klasse fuer Verhalten
Datenqualitaet:     Drei Stufen statt zwei (NICHT_MOEGLICH separat)
                    Ehrlichkeit ueber Pseudopraezision
Robustheit:         Throttling, Retry, Cache, KeyboardInterrupt-sicher
Klassifikation:     7+3 Kategorien, Schwellen als Konstanten
Bug-Reflexion:      Single Source of Truth, Reserve-%-Bug Iter 6
Iter-6-Erkenntnis:  Tool als faktenbasierter Indikator
                    Konflikt-Box statt Pseudo-Soll
                    Architekt-verifiziert: "kein Generalrezept"
```
