# Journal: Bauzonen-Radar

Chronologisches Arbeitsjournal zum Python-Abschlussprojekt.

## Hinweis zum KI-Einsatz

Fuer die Erstellung dieses Projekts wird Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Architektur, Code-Generierung,
Reglement-Strukturierung und Dokumentation entstehen in
Zusammenarbeit mit Claude. Fachliche Entscheidungen, Verifikation
der Werte und finale Architektur liegen beim Projektteam.

---

## 28. April 2026 (Dienstag, sehr spaeter Abend) - Stichproben-Test mit 12 Adressen

**Dauer**: ca. 30 Minuten (10 Minuten Skript + Live-Test)

### Was getestet wurde

Robustheits-Test des gesamten Tools mit 12 Adressen verteilt ueber
drei Gemeinden plus Edge-Cases. Skript: `tests/test_zwoelf_adressen.ps1`
(folgt dem `demo.ps1`-Pattern: cd in Modul-Ordner, dann pro Adresse
`python analyse_adresse.py`).

Resultat: **12/12 erfolgreich** - keine Crashes, alle Adressen
durchgelaufen, alle drei Datenqualitaets-Pfade in Aktion gesehen.

### Erkenntnisse aus den Stichproben

**Erkenntnis 1: Bug bei kleinen Parzellen mit BK_3 (Bern)**

Murifeldweg 8 (336 m^2 Parzelle, BK_3, BKP-Werte 40 m x 12 m):

```
Drei Begrenzer:
  1. Gebaeudemasse: 480 m^2  (40 x 12 aus BKP)
  2. Parzelle minus Grenzabstaende: 0 m^2 <- aktiv
  3. GFZ: nicht definiert
  -> 0 m^2
```

Die quadratische Approximation `(sqrt(336) - 5 - 10)^2` produziert
einen negativen Wert, der auf 0 abgeschnitten wird. Bei kleinen
Parzellen mit grossen Grenzabstaenden ist die Naeherung unbrauchbar.

**Loesungsansatz**: Statt quadratischer Naeherung ein realistischeres
Modell - z.B. Annahme einer rechteckigen Parzelle mit Verhaeltnis 1:2
oder Mindestbreite gA + 1 m. Oder warnen wenn der Ansatz versagt.

**Erkenntnis 2: BK_5 in Bern produziert keinen Schaetzwert**

Effingerstrasse 35 (BK_5, geschlossene Bauweise, Gebaeudelaenge
unbeschraenkt):

```
Status: SCHAETZWERT
(aber: keine Zeile "GROBSCHAETZUNG zulaessig: ca. X m^2")
GROBSCHAETZUNG nicht moeglich: Es fehlen Vollgeschosse oder
Geometrie-Werte (kA, gA, GL).
```

Wenn `Gebaeudelaenge unbeschraenkt` gesetzt ist, bricht die
Begrenzer-Logik ab. **Loesungsansatz**: Bei geschlossener Bauweise mit
unbegrenzter Laenge nur die anderen zwei Begrenzer auswerten
(Parzellen-Grenzabstaende, GFZ).

**Erkenntnis 3: thun.json fehlen Zonen**

Allmendstrasse 4 (ZPP) und Seestrasse 72a (WA4) liefern beide
"Zone im Reglement nicht erfasst". Die OEREB-Auskunft hat diese
Zonen, aber `thun.json` kennt sie nicht.

**Loesungsansatz**: WA4 (Wohnen/Arbeiten) plus ZPP-Hinweis (Spezialregime)
als Synonyme/Zonen in `thun.json` ergaenzen.

**Erkenntnis 4: Bauklassen-Erkennung bei Mehrfacheintraegen**

Murifeldweg 8 (BK_E erwartet wegen Bauweise offen 40 x 12) wird als
BK_3 eingeordnet. Die OEREB-Auskunft listet zwei Eintraege:
- "Bauweise Offen, max. Gebaeudelaenge/-tiefe = 40 / 12"
- "Bauklasse 3"

Die Auswertung waehlt den Bauklassen-Eintrag, ignoriert die Bauweisen-
Information bei der Klassen-Bestimmung. Das ist nicht zwingend falsch,
aber die Logik braucht klare Doku.

**Loesungsansatz**: Pruefen, ob die zwei Eintraege wirklich BK_3 oder
BK_E meinen. Im BKP-Output steht `Bauklasse: BK_3 (BK_3 - Bauklasse 3)`
- also stimmt BK_3. Damit ist Erkenntnis 4 keine Bug, sondern eine
falsche Erwartung meinerseits. **Murifeld ist tatsaechlich BK_3.**

### Was wirklich gut funktioniert

- **Unbekannte Gemeinden** werden sauber abgefangen (Sigriswil/Gunten:
  "Kein Baureglement fuer Sigriswil verfuegbar.")
- **Stadtteile** werden korrekt der Mutter-Gemeinde zugeordnet
  (Gwatt -> Thun)
- **Schutzzonen** triggern korrekt den NICHT_MOEGLICH-Pfad mit klarer
  UNESCO/Denkmalpflege-Empfehlung
- **ZPP/UeO** triggert den NICHT_MOEGLICH-Pfad statt einen unsinnigen
  Schaetzwert zu produzieren
- **Naturgefahren-Ueberlagerungen** werden in den Bemerkungen
  aufgefuehrt
- **Baulinien-Warnung** erscheint zuverlaessig

### Backlog fuer Iteration 4 oder spaeter

- [ ] **Bug**: Begrenzer-Logik bei kleinen Parzellen + grossen
  Grenzabstaenden (Murifeld-Pattern)
- [ ] **Bug**: Begrenzer-Logik bei `Gebaeudelaenge unbeschraenkt`
  (Effingerstrasse-Pattern)
- [ ] **Daten**: WA4 und ZPP in `thun.json` ergaenzen
- [ ] Stichproben als Regressions-Test mit erwarteten Werten ausbauen
  (Snapshot-Tests)

---

## 28. April 2026 (Dienstag, spaeter Abend) - Datenquellen-Evaluation Thun + geodienste.ch

**Dauer**: ca. 30 Minuten

### Frage des Tages

Nachdem die Stadt Bern dank BKP-API parzellenscharfe Werte liefert: Geht
das fuer Thun und andere Gemeinden auch? Konkret evaluiert wurden zwei
weitere Datenquellen.

### Quelle 1: geodienste.ch

Schweizweite, einheitliche WFS-API. Endpoint:
`https://geodienste.ch/db/npl_nutzungsplanung_v1_2_0/deu`

WFS-Capabilities geben vier Layer:
- `ms:grundnutzung`
- `ms:ueberlagernde_nutzungsplaninhalte_flaechenbezogene_festlegungen`
- `ms:ueberlagernde_nutzungsplaninhalte_linienbezogene_festlegungen`
- `ms:ueberlagernde_nutzungsplaninhalte_punktbezogene_festlegungen`

Live-Test mit BBox um Thun-Zentrum lieferte Features mit Properties
wie `typ_kommunal_code`, `typ_kantonal_code`, `hauptnutzung_bezeichnung`
und PDF-Links zum Baureglement. **Aber keine Bauwerte** (keine
Geschossigkeit, keine Ausnuetzungsziffer, keine Hoehen).

### Quelle 2: ThunGIS (thun.regiogis-beo.ch)

Stadt-spezifisches GIS-Portal mit Geokatalog "Bauzonenplan" -
parzellenscharfes Click-Popup zeigt fuer Seestrasse 72a:
- Kant.Art: WA4
- Abkuerzung Zonenname: WA4
- Bezeichnung: Wohnen/Arbeiten WA4
- Beschrieb: (leer)
- Planbeschriftung: (leer)

**Auch hier keine Bauwerte** - nur Zonen-Bezeichnung.

### Erkenntnis: Bern ist der Sonderfall

Im Kanton Bern haben die Geoinformations-Stellen entschieden, im
Datenmodell nur die rechtlich verbindliche Zonenzuteilung zu fuehren.
Die konkreten Bauwerte (Geschosse, Hoehen, Grenzabstaende, GFZo) sind
**ausschliesslich in den Baureglement-PDFs** der Gemeinden verfuegbar.

Stadt Bern hat als einzige BE-Gemeinde eine eigene ArcGIS REST-API
(`map.bern.ch`) mit dem Bauklassenplan, der parzellenscharfe
Gebaeudemasse (Bauweise, Gebaeudelaenge, Gebaeudetiefe) liefert.

### Architektur-Konsequenz

Drei Tier von Datenquellen sind moeglich:

| Tier | Beispiel | Detailgrad | Aufwand |
|---|---|---|---|
| OEREB | alle BE-Gemeinden | Zonen-Code + Rechtsstatus | bereits implementiert |
| Spezialisierte Stadt-API | map.bern.ch BKP | + Gebaeudelaenge, Bauweise | implementiert fuer Bern |
| geodienste.ch | schweizweit | nur Zonen-Code (gleiche Info wie OEREB) | KEIN MEHRWERT |

### Schlussfolgerung fuer die Architektur

Die Tool-Architektur **bleibt wie sie ist**. Pro Gemeinde erfassen wir
das Baureglement in einer JSON-Datei (kommt aus der Recherche im PDF),
und nur fuer Stadt Bern reichern wir parzellenscharf via BKP-API an.

Das ist keine Schwaeche, sondern eine **fundierte Datenquellen-
Entscheidung mit Begruendung**. Wertvoll fuer die Verteidigung am 17.6.
und fuer Diskussionen mit Fachleuten.

### Koeniz: getestet - kein Mehrwert ueber OEREB hinaus

Gemeinde Koeniz (4-groesste BE-Gemeinde, 43'000 Einwohner, grenzt an
Stadt Bern) hat ein eigenes Geoportal `geoportal.koeniz.ch` mit
ArcGIS-Backend. Live-Test mit Parzelle 1274 (im Layer "Nutzungsplan"):

Popup zeigt:
```
Wohnzone (Art. 29 BauR), Bauklasse IIa (Art. 53 BauR)
+ Link auf das Baureglement-PDF
+ Link auf das Nutzungsplan-Dokument
```

**Das gleiche Muster wie Thun**: Zone und Bauklasse sind
parzellenscharf verfuegbar, aber **die konkreten Bauwerte (Geschosse,
Hoehen, Grenzabstaende) fehlen**. Sie stehen nur im
PDF-Baureglement (Art. 53).

Interessante architektonische Erkenntnis: **Koeniz hat ein
Bauklassen-System wie Bern** (statt Hoehen-System wie Thun). Das heisst,
wenn wir die Werte aus Art. 53 BauR Koeniz einmalig erfassen und in eine
`koeniz.json` packen, koennten wir Koeniz mit der gleichen Pipeline wie
Bern abdecken - nur eben ohne Live-API, sondern mit statischen JSON-
Werten.

Baureglement direkt zugreifbar:
`https://gisdoc.koeniz.ch/public/plak/npl/Baureglement/721.0_Baureglement.pdf`

**TODO fuer Iteration 4 oder spaeter**:
- Art. 53 BauR Koeniz auswerten und Bauklassen-Tabelle in `koeniz.json`
  uebernehmen
- Das ist die gleiche Erfassungs-Arbeit wie fuer Thun/Oberhofen, nur
  fuer eine vierte Gemeinde

### Endergebnis der Datenquellen-Evaluation

| Gemeinde | Bauwerte aus Live-API verfuegbar? |
|---|---|
| Stadt Bern | JA (parzellenscharf via map.bern.ch BKP) |
| Stadt Thun | nein - nur PDF |
| Oberhofen | nein - nur PDF |
| Koeniz | nein - nur PDF |
| Alle anderen BE-Gemeinden (vermutlich) | nein - nur PDF |

**Stadt Bern bleibt die Ausnahme.** Fuer alle anderen Gemeinden ist die
JSON-Erfassung pro Gemeinde der einzige Weg zu den Bauwerten.

---

## 28. April 2026 (Dienstag, abends) - Bauklassenplan via ArcGIS-API live

**Dauer**: ca. 3 Stunden

### Ausgangsproblem: parzellenscharfe Werte fehlten

Bauklassen 2-6 in `bern.json` standen als `system: GFZo` mit
`geschossflaechenziffer_oberirdisch: null`. Der Hintergrund: Die
konkreten GFZo-Werte stehen nicht in der Bauordnung selbst, sondern
parzellenscharf im Bauklassenplan (BKP) der Stadt Bern. Solange
diese Daten fehlten, lieferte das Tool fuer 80% der Bern-Adressen
"NICHT_BERECHENBAR" zurueck.

### Durchbruch: ArcGIS REST-API map.bern.ch

Recherche im Geoportal der Stadt Bern: Der Bauklassenplan ist als
ArcGIS REST-Service oeffentlich abfragbar.

```
https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer
```

Zwei relevante Layer:
- **Layer 88 (BKP_Bauweise)**: Bauweise (offen/geschlossen),
  Gebaeudelaenge, Gebaeudetiefe pro Parzelle
- **Layer 95 (BKP_Grundzonen_Flaechen)**: Nutzungszone (W/WG/K/D/IG)
  und Bauklasse (BK_2 bis BK_6, BK_E, BK_SPEZ, OA, UA)

Ueberraschende Erkenntnis: Der BKP liefert **keine GFZo-Werte**.
Bauklassen 2-6 sind reine Hoehen-Systeme - definiert ueber
Vollgeschosse + Fassadenhoehe + Geometrie. Nur Bauklasse E hat
ueber Art. 57 BO einen GFZo-Wert (0.5 bzw. 0.6).

Das aendert die Architektur grundlegend: Die `bern.json` musste von
`GFZo` auf `hoehen_und_gz` umgestellt werden.

### Neues Modul: bern_bkp.py

ArcGIS-Anbindung mit pure Standard-Library (urllib, json), Cache
pro Session, robust gegen Fehler. Drei Datenklassen:
- `BkpBauweise` (Layer 88)
- `BkpGrundzone` (Layer 95)
- `BkpAuskunft` (kombiniert)

Live-getestet mit sechs Adressen quer durch Bern - alle Pfade
funktionieren.

### Drei Faelle in der Stadt Bern

Die Live-Tests deckten drei klar unterscheidbare Faelle auf:

| Fall | Beispiel | Bauweise-Daten | Pfad |
|---|---|---|---|
| BK 1-6 mit Bauweise | Eigerstrasse 60 (BK_4) | ja | GROBSCHAETZUNG mit echten Werten |
| BK_E (Erhaltung) | Thunstrasse 40, Optingenstrasse 30 | nein | VERBINDLICH (GFZo aus BO) |
| Altstadt OA/UA | Marktgasse 25 (OA) | nein | NICHT_MOEGLICH |
| BK_SPEZ (UeO) | Bumplitzstrasse 100, Sulgenrain 12 | nein | NICHT_MOEGLICH |

### Architektur-Entscheidung: pragmatisch ehrlich

Bei BK_E gibt es Spezialregelung (Erhaltung der Volumetrie ist
verbindlich, GFZo nur als Obergrenze). Bei Altstadt und BK_SPEZ
gibt es keine quantitative Berechnung sinnvoll, weil das Spezial-
regime das Standard-Reglement aushebelt.

**Entscheidung**: Falsche Werte sind viel schlimmer als ein
ehrliches "kann ich nicht". Entsprechend wurde das Datenmodell um
das System `NICHT_MOEGLICH` erweitert - Zonen mit diesem System
liefern eine klare Meldung statt einer Schein-Berechnung.

### NICHT_MOEGLICH-Pfad in potenzial.py

Neuer Behandlungspfad `_behandle_nicht_moeglich`:
- Datenqualitaet: NICHT_MOEGLICH
- Status: NICHT_BERECHENBAR
- Verwendetes System: "Spezialregime (keine Standard-Berechnung)"
- Klare Erklaerung warum nicht gerechnet wird
- Empfehlung: Direkter Kontakt mit Bauverwaltung / Denkmalpflege
- Empfehlungs-Block (Balken) wird konsequent weggelassen statt
  Pseudo-Werte zu zeigen

### Bauparameter.mit_bkp_daten() Methode

Neue Methode auf der `Bauparameter`-Klasse. Reichert die im
JSON definierten Werte mit parzellenscharfen BKP-Daten an:
- `max_gebaeudelaenge_m` aus BKP (z.B. 70 m fuer Eigerstrasse 60)
- Neues Feld `bkp_gebaeudetiefe_m` (z.B. 13 m statt Default 12 m)
- Neues Feld `bkp_bauweise` ("offen" / "geschlossen")
- Hinweis-Text wird automatisch um BKP-Info ergaenzt

Die Anreicherung passiert im PotenzialBerechner, bevor die
Schaetzung gerechnet wird.

### Drei-Begrenzer-Logik mit transparenter Anzeige

Im Hoehen-System wird die Grundflaeche durch drei Faktoren
begrenzt:
1. Gebaeudemasse (Laenge x Tiefe aus BKP)
2. Parzelle minus Grenzabstaende (quadratische Naeherung)
3. Gruenflaechenziffer (falls definiert)

Der kleinste Wert gewinnt. Vorher zeigte der Bericht nur den
Endwert mit irrefuehrender Begruendung. Jetzt werden alle drei
Kandidaten ausgewiesen, der aktive Begrenzer ist mit `<- aktiv`
markiert.

```
Drei Begrenzer der Grundflaeche werden geprueft:
  1. Gebaeudemasse: 910 m^2 (70.0 m x 13.0 m aus BKP)
  2. Parzelle minus Grenzabstaende: 743 m^2 <- aktiv
  3. Gruenflaechenziffer: nicht definiert (entfaellt)
-> Massgebende Grundflaeche: 743 m^2
```

Damit ist sofort sichtbar, ob das Reglement oder die Parzelle der
Engpass ist.

### bern.json komplett umgebaut

Alle Bauklassen-Eintraege ueberarbeitet:
- BK 2-6: System auf `hoehen_und_gz`, Vollgeschosse, FH/FHA, kA/gA
- BKP-Code-Synonyme `BK_2`, `BK_3`, ..., `BK_E`, `BK_SPEZ`
- Altstadt-Zonen + ZPP + Schutzzonen + ZoeN FD: System
  `nicht_moeglich`
- Nutzungszonen-Code-Synonyme `W`, `WG`, `K`, `K (s)`, `K (l)`,
  `D`, `IG`, `OA`, `UA`

### bessere Meldung bei "Zone nicht im Reglement erfasst"

Neue Hilfsmethode `_bkp_zone_hinweis`. Wenn eine Adresse eine
Bauklasse oder Zone hat, die noch nicht im Reglement-JSON erfasst
ist, gibt das Tool jetzt aus:
- Welche BKP-Codes konkret gefunden wurden
- Den Hinweis, dass eine Sonderzone (UeO/UeP) der Grund sein kann
- Eine Empfehlung zum weiteren Vorgehen

### Verifikations-Tests (neue Adressen-Suite)

Sechs Bern-Adressen quer durchs Stadtgebiet getestet:

| Adresse | Bauklasse | Datenqualitaet | Output |
|---|---|---|---|
| Thunstrasse 40 | BK_E | VERBINDLICH | GFZo 0.5, 80% Ausschoepfung |
| Optingenstrasse 30 | BK_E | VERBINDLICH | GFZo 0.5, 80% Ausschoepfung |
| Eigerstrasse 60 | BK_4 | GROBSCHAETZUNG | mit echten BKP-Werten |
| Marktgasse 25 | OA | NICHT_MOEGLICH | klare Empfehlung |
| Bumplitzstrasse 100 | BK_SPEZ | NICHT_MOEGLICH | UeO-Hinweis |
| Sulgenrain 12 | BK_SPEZ | NICHT_MOEGLICH | UeO-Hinweis |

Alle drei Pfade (VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH)
funktionieren mit Live-API-Daten.

### Bug-Fix-Sequenz

Drei kleinere Bugs mit jeweils gezieltem Fix:
1. `koordinate_lv95` wurde nicht auf das Parzellen-Objekt
   zurueckgeschrieben - der Berechner fand die Koordinate nicht
   und konnte die BKP-Anreicherung nicht ausfuehren.
2. `bkp_gebaeudetiefe_m` wurde von der Schaetz-Berechnung ignoriert
   (Default 12 m statt echte 13 m aus BKP).
3. Begruendungstext im Bericht zeigte multiplikative Formel
   (70 m x 13 m = 743 m^2), die mathematisch nicht stimmt -
   tatsaechlich war die Parzelle der Begrenzer, nicht die
   Geometrie.

### Status

Stadt Bern ist mit dieser Iteration **vollstaendig abgedeckt**:
- VERBINDLICH-Pfad fuer BK_E (~10% der Stadt)
- GROBSCHAETZUNG-Pfad fuer BK 2-6 mit parzellenscharfen Werten
  (~70% der Stadt)
- NICHT_MOEGLICH-Pfad fuer Altstadt, UeO, Schutzzonen, ZoeN ohne
  konkretem Subtyp (~20% der Stadt)

Die Schwager-Erfassungs-Excel ist fuer die Bauklassenplan-Werte
nicht mehr zwingend noetig - die API liefert die Werte direkt. Sie
bleibt aber relevant fuer:
- Verifikation der BKP-Werte (Stichproben)
- Subtypen FA-FD der ZoeN (nicht in API)
- Anhang II der BO (Zonen-spezifische Sondervorschriften)

### Dokumentation aktualisiert

- `docs/journal.md`: Dieser Eintrag
- `docs/konzept.md`: Sektion ueber BKP-API-Anbindung
- `docs/projektplan.md`: Iteration 3 als abgeschlossen markiert,
  Iteration 4 vorbereitet
- `docs/fachliche_grundlagen.md`: Neue Sektion "Bauklassenplan
  Stadt Bern (BKP-API)"

---

## 28. April 2026 (Dienstag) - Schaetz-Berechnung, Datenqualitaet, Empfehlungs-Block

**Dauer**: ca. 5 Stunden

### Termin mit Fabienne (Mitstudentin)

Aufgabenverteilung fixiert:
- **Fabienne**: Dokumentation, Streamlit-Webseite (Iteration 4),
  Requirements-Engineering-Pruefung
- **Christophe**: Backend, OEREB-Pipeline, Reglement-Daten

Naechste Schritte fuer Fabienne:
- GitHub-Username an Christophe senden
- Repo durchklicken
- Erste Anforderungs-Liste erstellen
- Implizite Annahmen im Code identifizieren

### Oberhofen integriert

Vierter Schritt nach Bern und Thun: kleine Gemeinde abdecken.

**Recherche**:
- Offizielles Baureglement Oberhofen am Thunersee gefunden
- Quelle: BR vom 14. Mai 2012, Nachfuehrung bis 31. Dezember 2024,
  AGR-genehmigt
- Art. 212 mit Tabelle: vier Wohn-/Mischzonen W1, W2, W3, M2
- Werte fuer kA, gA, GL, Fh tr, Fh gi, VG aus Reglement extrahiert
- Plus elf ZOEN, zehn ZPP, sechs Ortsbildschutzgebiete

**Erkenntnis**: Oberhofen verwendet Hoehen-System ohne
Gruenflaechenziffer. Das bricht unsere bisherige
`ist_berechenbar`-Logik.

### Bug-Fixes (erste Runde)

**Problem**: Bei Oberhofen-Test schlug `_behandle_hoehen_und_gz`
nicht an, weil keine GZ in den Daten war.

**Fix 1 in baureglement.py**: `ist_berechenbar`-Property erweitert.
Schon eine Hoehenangabe genuegt jetzt fuer "berechenbar". GZ ist
optional.

**Fix 2 in potenzial.py**: `_behandle_hoehen_und_gz` arbeitet sich
durch alle vorhandenen Werte. Einleitungstext unterscheidet
zwischen "mit GZ" (Thun-Stil) und "ohne GZ" (Oberhofen-Stil).
Vollgeschosse werden ausgegeben.

### Erweiterung: Schaetz-Berechnung im Hoehen-System

Real-Test mit "Florastrasse 5, 3600 Thun" (Wohnen W3) brachte die
Frage: "Warum berechnet das Tool nichts? Es ist ja nur W3."

**Erkenntnis**: Im Hoehen-System ist eine direkte m^2-Berechnung
nicht moeglich, aber eine konservative Schaetzung sehr wohl. Wir
brauchen:
- Annahme Gebaeudebreite (default 12 m, gekappt durch GL)
- Multiplikation mit Vollgeschossen
- Anteiliger Dachgeschoss-Bonus bei Schraegdach (60%)
- Beruecksichtigung von Grenzabstaenden und GZ als Begrenzung

### Datenqualitaets-Konzept

Wichtige Design-Entscheidung: Schaetzungen muessen sich klar von
verbindlichen Berechnungen unterscheiden.

Drei Stufen eingefuehrt:
- **VERBINDLICH** (AZ/GFZo)
- **GROBSCHAETZUNG** (Hoehen-System)
- **NICHT_MOEGLICH** (keine Werte)

Bei Schaetzungen erscheint:
- Header-Banner mit Warnung
- "GROBSCHAETZUNG zulaessig" statt "Theoretisch zulaessig"
- "Status: SCHAETZWERT - keine Investitionsentscheidung darauf basieren"
- Vollstaendige Berechnungsbasis transparent
- Annahmen-Sektion ("Annahme Gebaeudebreite kann zu hoch oder zu
  niedrig sein...")
- Plausibilitaetscheck gegen altes AZ-Recht (falls in JSON
  hinterlegt)

### Plausibilitaetscheck

Neues Feld `vergleichswert_az_alt` in `Bauparameter`. Bei jeder
Thun-Zone hinterlegt der alte AZ-Wert aus BR 2002.

Aussage:
- Faktor < 0.7: "auffaellig niedrig"
- Faktor 0.7-1.8: "plausibel"
- Faktor > 1.8: "auffaellig hoch"

### thun.json komplett ueberarbeitet

Sieben Zonen mit allen Werten plus `vergleichswert_az_alt`:
- W2, W3, W4
- WA3, WA4, WA5
- Arbeiten A
- Arealbonus bei WA5 ab 3000 m^2

### Empfehlungs-Block mit visueller Lagebeurteilung

Zwei reale Tests (Thunstrasse 40 mit "80% ausgeschoepft" und
Florastrasse 5 mit "Schaetzung 780 m^2") zeigten: Die nackten
Zahlen sind korrekt, aber **schwer in einer Sekunde zu erfassen**.
Ein Investor oder Architekt will sofort sehen, ob sich eine
Detailpruefung lohnt.

**Loesung**: Empfehlungs-Block mit ASCII-Fortschrittsbalken plus
verbaler Lagebeurteilung.

```
======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [################----]  80.0%
  Bauland-Reserve: [####----------------]  20.0%

  -> GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung
======================================================================
```

Vier Lagebeurteilungen anhand Bauland-Reserve:
- >= 60%: HOHES Verdichtungs-Potenzial
- 30-60%: MITTLERES Verdichtungs-Potenzial
- 10-30%: GERINGES Verdichtungs-Potenzial
- < 10%: PRAKTISCH AUSGESCHOEPFT

Bei Schaetzungen wird "(geschaetzt)" angehaengt und der Header
sagt "EMPFEHLUNG (Grobschaetzung - nur als Orientierung)".

### Bug-Fix: Ausschoepfung bei Oberhofen

Oberhofen-Test ergab vorher "111% ausgeschoepft" (zwei
Schaetzungen verglichen). Mit dem neuen Empfehlungs-Block wird die
Ausschoepfung auf 100% und die Reserve auf 0% gekappt.

### Verifikations-Tests (alle vier Adressen)

| Adresse | System | Datenqualitaet | Ergebnis | Empfehlung |
|---|---|---|---|---|
| Thunstrasse 40, Bern | GFZo | VERBINDLICH | 118 m^2, 80% | GERINGES Verdichtungs-Potenzial |
| Florastrasse 5, Thun W3 | Hoehen+GZ | GROBSCHAETZUNG | ~780 m^2, 46% | MITTLERES (geschaetzt) |
| Hirschweg 7, Thun W2 | Hoehen+GZ | GROBSCHAETZUNG | ~201 m^2, 93% | PRAKTISCH AUSGESCHOEPFT (geschaetzt) |
| U. Stadelstrasse 1, Oberhofen | Hoehen | GROBSCHAETZUNG | ~384 m^2, 100% | PRAKTISCH AUSGESCHOEPFT (geschaetzt) |

**Status**: Drei Bemessungssysteme im selben Tool funktional, mit
sauberer Datenqualitaets-Markierung und visueller Lagebeurteilung.

### Dokumentation aktualisiert

- README.md: Beispiel-Outputs mit Empfehlungs-Block fuer beide
  Datenqualitaeten, Test-Adressen mit Empfehlung
- docs/konzept.md: Neue Sektion "Empfehlungs-Block mit visueller
  Lagebeurteilung", aktualisierte Iteration 2
- docs/projektplan.md: Iteration 2 mit allen Schaetz- und
  Empfehlungs-Features dokumentiert, Iteration 4 mit grafischer
  Progress-Bar
- docs/journal.md: Dieser Eintrag
- docs/fachliche_grundlagen.md: Neue Sektion "Schaetz-Berechnung
  im Hoehen-System"

---

## 27. April 2026 (Montag) - Mehrsystem-Modell und Reglement-Daten

**Dauer**: ca. 4 Stunden

### Erkenntnis des Tages: Drei Bemessungssysteme parallel

Der Kanton Bern hat den Systemwechsel von AZ zu GFZo
(IVHB-konform) eingelaeutet, aber Gemeinden setzen ihn
unterschiedlich schnell um. Stadt Thun BR 2022 verzichtet sogar
ganz auf eine flaechen-bezogene Kennzahl und steuert ueber Hoehen
und Gruenflaechenziffer.

Datenmodell entsprechend erweitert:
- `BemessungsSystem`-Enum
- Felder fuer Hoehen, Grenzabstaende, Gebaeudelaenge, GZ
- `Bauparameter.ist_berechenbar` und `hauptkennzahl()`

### Stadt Bern komplett

Recherche gegen offizielle Bauordnung BO 2006 (Stand 28.09.2023):
- Bauklassen 2-6 mit FH/FHA/kGA/gGA (Art. 46)
- Bauklasse E mit GFZo 0.5 / 0.6 (Art. 57)
- ZoeN FA-FD mit GFZo (Art. 24)
- Arbeitszonen mit FH/FHA pro Bauklasse 1-6 (Art. 58)
- Altstadt-Spezialregimes Untere/Obere Altstadt (Art. 76-86)

`bern.json` mit 30+ Eintraegen vollstaendig erfasst. Hinweis: Die
GFZo-Werte pro Bauklasse-Zone-Kombination liegen aber im
Bauklassenplan (BKP), nicht in der BO. Schwager wird die liefern.

### Stadt Thun komplett

Schwager-Tabelle mit Art.-42-Werten BR 2022 eingepflegt:
- W2/W3/W4/WA3-WA5/Arbeiten A
- Strukturgebiet als Spezialfall
- Arealbonus ab 3000 m^2

`thun.json` mit allen Werten erfasst.

### Erste echte GFZo-Berechnung

Thunstrasse 40, 3005 Bern (Bauklasse E):
- Parzellenflaeche: 237 m^2
- GFZo = 0.5
- Theoretisch zulaessig: 118 m^2
- Status: GERING (80% Ausschoepfung)

Tool funktioniert technisch und fachlich.

### Erfassungs-Excel fuer Schwager

`docs/erfassung_baureglemente.xlsx` mit vier Tabs und acht
Tabellen erstellt. Soll dem Schwager helfen, die fehlenden
Bauklassenplan-Werte effizient nachzuliefern.

### Test-Adressen-Suite

Zehn realweltliche Adressen verifiziert. `demo.ps1` als
Regressionstest erstellt.

---

## (frueheres) - Iteration 1 abgeschlossen

Pipeline End-to-End funktional. Geocoding, OEREB-Abfrage,
XML-Parsing, Datenmodell. Erste Test-Adressen liefern korrekte
Daten.

---

## Verschiedene Beobachtungen

- Windows-PowerShell mit `start.ps1` automatisiert venv-Aktivierung
  und Wechsel ins Modul-Verzeichnis. Spart bei jedem Start drei
  Befehle.
- `demo.ps1` verwendet `$PSScriptRoot`, also ortsunabhaengig
  aufrufbar.
- OEREB-Webservice antwortet meist in unter 5 Sekunden, ab und zu
  laengere Wartezeiten.
- swisstopo SearchAPI ist sehr schnell und tolerant gegenueber
  Tippfehlern in Adressen.
- Iteratives Vorgehen mit Real-Tests deckt Schwachstellen auf, die
  in der Theorie nicht sichtbar sind. Beispiele:
  - Florastrasse-Test fuehrte direkt zur Schaetz-Berechnung
  - Thunstrasse 40 + Florastrasse 5 zusammen fuehrten zum
    Empfehlungs-Block (visuell statt rein numerisch)
- Information Design ist genauso wichtig wie korrekte Berechnung.
  Ein Architekt liest in einer Sekunde den Balken, nicht in zehn
  Sekunden die Zahl.
