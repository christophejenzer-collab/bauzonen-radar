# Journal: Bauzonen-Radar

Chronologisches Arbeitsjournal zum Python-Abschlussprojekt.

## Hinweis zum KI-Einsatz

Fuer die Erstellung dieses Projekts wird Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Architektur, Code-Generierung,
Reglement-Strukturierung und Dokumentation entstehen in
Zusammenarbeit mit Claude. Fachliche Entscheidungen, Verifikation
gegen das Baureglement und die finale Code-Verantwortung liegen
beim Autor (Christophe Jenzer).

Das Journal selbst ist ebenfalls in Zusammenarbeit mit Claude
entstanden - es kombiniert tatsaechlich gefuehrte Entwicklungs-
schritte mit chronologischer Strukturierung. Die Git-Commits
liefern die Quellen-Wahrheit fuer Daten und Reihenfolge.

---

## 12. Mai 2026 - Iteration 5 komplett (~11h)

Massive Tagesarbeit, Iter 5 von 1/4 Modulen auf 4/4 + Bonus.
Ablauf grob: parzellen_liste -> gemeinde_analyse -> excel_export ->
GWR-Bug entdeckt + gefixt -> Verifikation -> Bodenbedeckungs-Filter.

### Iter-5-Module fertig

**parzellen_liste.py mit Praefix-Baum (180 Zeilen)**

Problem: swisstopo SearchAPI limitiert auf 50 Treffer pro Anfrage.
Loesung: rekursive Praefix-Suche (`Oberhofen`, dann `Oberhofen 1`,
`Oberhofen 10`, etc.) mit Deduplizierung via EGRID-Set.
Resultat fuer Oberhofen: 1176 Parzellen via 161 API-Calls in 126 Sek.

**gemeinde_cache.py (520 Zeilen)**

SQLite-Cache fuer komplette AnalyseErgebnisse via pickle-Serialisierung
(Strategie A - vollstaendige Serialisierung). Wiederaufnahme nach
Abbruch klappt, Cache ueberlebt Strg+C, neue Eintraege idempotent.

**klassifikation.py (250 Zeilen, mit v2)**

Sieben Geschaeftslogik-Kategorien:
VERDICHTUNG, NEUGESCHAEFT, ERSATZNEUBAU, UNAUFFAELLIG, AUSGEREIZT,
AUSSCHLUSS_REGLEMENT, AUSSCHLUSS_ZU_KLEIN.
Wichtig: nutzt die ECHTE Ausschoepfung aus GWR (Ist/Soll * 100),
nicht das `ausschoepfungsgrad_prozent`-Feld (basiert auf 25%-
Platzhalter und ist deshalb fuer Iter 5 unbrauchbar).
Schwellen als Konstanten - am Schwager-Termin zu verifizieren.

**gemeinde_analyse.py (340 Zeilen)**

Haupt-Pipeline: parzellen_liste -> pro Parzelle Cache-Check ->
analysiere_per_egrid -> klassifiziere -> Cache-Schreiben.
Throttling 0.7 Sek zwischen Live-Calls (nicht bei Cache-Hits),
Retry 3x mit 2s-Delay bei API-Fehler, Progress-Logging alle 25
Parzellen mit ETA, KeyboardInterrupt-sicher.
CLI-Flags: --kanton, --no-cache, --refresh-aelter-als TAGE,
--limit N, --throttling SEK.

**excel_export.py (470 Zeilen)**

XLSX-Export aus dem KantonsCache mit 6 Sheets:
Statistik / Verdichtung / Neugeschaeft / Ersatzneubau / Ausgereizt /
Alle. Header gestylt (Dunkelblau + weiss + bold), Borders, Auto-
Spaltenbreite, Freeze-Panes, GRUDIS-Direktlinks pro Parzelle.

### GWR-Bug entdeckt + gefixt

Erster voller Lauf Oberhofen 1176 Parzellen lieferte:
- 489 NEUGESCHAEFT (41% aller Parzellen leeres Bauland!?)
- 0 VERDICHTUNG, 0 ERSATZNEUBAU, 0 AUSGEREIZT
Statistisch unmoeglich fuer ein 2400-Einwohner-Dorf.

Ursache: `analysiere_per_egrid()` rief
`gwr.gebaeude_zu_adresse('Oberhofen Parz. N')` - das ist kein
echter Adress-String, GWR fand 0 Treffer fuer alle bebauten Parzellen.
Konsequenz: alle bebauten Parzellen ohne Adress-Label landeten in
NEUGESCHAEFT.

Loesung: neue Methode `gebaeude_zu_egrid(egrid, koordinate_lv95)`
in gwr.py. Nutzt swisstopo MapServer-identify Endpoint
(`ech/MapServer/identify`, tolerance=500) mit Punkt-Geometrie und
filtert die Response nach `properties.egrid`. Kein zweiter API-Call
zum MapServer noetig - identify liefert alle Gebaeude-Properties
direkt (egid, garea, gastw, gbaup, etc.).

Smoke-Test Schulthesserstrasse 38 (CH569646354766):
Soll 624 m^2, Ist GWR 202 m^2, Bauperiode 8011 (vor 1919), Klassifikation
ERSATZNEUBAU. Voller Re-Run nach Cache-Loeschen ergab:
- VERDICHTUNG: 0 -> 53
- ERSATZNEUBAU: 1 -> 40
- AUSGEREIZT: 0 -> 75
- NEUGESCHAEFT: 489 -> 285
- 168 hochwertige Kandidaten identifiziert

Performance unveraendert (1.83 Sek/Parzelle) - GWR-Call laeuft
parallel zur OEREB-Latenz.

### Verifikation 7 Stichproben via map.geo.admin.ch

Nach dem GWR-Fix das Excel angeschaut. Top NEUGESCHAEFT-Eintraege
sind verdaechtig: alle Mischzone M2, gleiche Soll-Werte. Stichprobe
verifiziert auf der swisstopo-Karte:
- Parz 1 (25789 m^2 M2): STRASSE
- Parz 677 (17801 m^2 W1): WALD
- Parz 370 (13994 m^2 W1): WALD
- Parz 375 (11541 m^2 M2): WALD
- Parz 44 (5491 m^2 W1): STRASSE
- Parz 35 (4614 m^2 M2): bebaut, GWR-Datenluecke
- Parz 100 (969 m^2 W2): bebaut, GWR-Datenluecke

Erkenntnis: 5/7 sind Strassen oder Wald, die im OEREB einen
Bauzonen-Eintrag haben (Datenluecke der OEREB-Quelle). 2/7 sind
bebaut, aber GWR ordnet die Gebaeude nicht via EGRID zu (Polygon-
Problem bei Grenzfaellen).

### Bodenbedeckungs-Filter (~3h)

Neue Datenquelle `src/bauzonenradar/datenquellen/tlm3d.py` (288 Zeilen):
- `TlmStrassenQuelle`: Layer `ch.swisstopo.swisstlm3d-strassen`,
  offizielle TLM3D-Strassen, 100% zuverlaessig
- `ArealstatistikQuelle`: Layer `ch.bfs.arealstatistik-bodenbedeckung`,
  NOLC04-Codes, Daten 2023, 100x100m-Raster, mit Wasser-False-Positive-
  Bug bei Ufer-Parzellen - deshalb konservativ als 'Verdacht' behandelt

Beide nutzen MapServer-identify (wie GWR). Sweet-spot Tolerance fuer
Arealstatistik bei 50m gefunden (10m=0 Treffer, 100m+=Nachbar-Parzellen).

Zwei neue Klassifikationen:
- AUSSCHLUSS_VERKEHR: TLM-Strasse + Arealstat=Befestigt
  (Code 11) + Flaeche>1500 + Geb=0 -> 99% sicher Strasse (4 Indikatoren)
- AUSSCHLUSS_WALD_VERDACHT: Arealstat=Wald (Code 41-47) + Flaeche>2000
  + Geb=0 -> grosse Waldparzellen. 'VERDACHT' weil Arealstatistik
  nicht 100% verlaesslich (Wasser-Bug, alte Erhebung 1981 in
  Edge-Cases sichtbar).

Voller Re-Run Nr. 3 mit Bodenbedeckungs-Filter (1176 Parzellen, 41 Min):
- VERDICHTUNG: 55, NEUGESCHAEFT: 257, ERSATZNEUBAU: 38,
  UNAUFFAELLIG: 132, AUSGEREIZT: 77,
  AUSSCHLUSS_VERKEHR: 20 (NEU), AUSSCHLUSS_WALD_VERDACHT: 3 (NEU),
  AUSSCHLUSS_REGLEMENT: 506, AUSSCHLUSS_ZU_KLEIN: 88
- 23 False-Positives erfolgreich umklassifiziert
- 170 hochwertige Kandidaten identifiziert

### Bekannte Limitationen (Iter 6)

- Schmale Waldparzellen (<2000 m^2 oder Zentroid am Rand) werden
  von der Arealstatistik nicht erwischt - braucht Polygon-Intersection
- GWR-Polygon-Bug: bei bebauten Parzellen wo das Hauptgebaeude weit
  weg vom Zentroid ist, findet identify mit tolerance=500 das
  Gebaeude nicht. Loesung in Iter 6 via geometrische Suche
- Arealstatistik 1981 ist veraltet - bei Ufer-Parzellen kommt
  manchmal "Wasser" zurueck, deshalb 'VERDACHT'-Suffix

### Erkenntnisse

- **Konservatives Filtern ist besser als aggressives.** 23 echte
  Treffer sind wertvoller als 80 mit False Positives. AUSSCHLUSS_VERKEHR
  verlangt 4 Indikatoren gleichzeitig (TLM + Areal + Flaeche + Geb=0).
- **Datenqualitaet ist ein Engineering-Befund**, kein Bug. Strassen
  mit Bauzonen-Eintrag im Kataster sind ein OEREB-Datenproblem, nicht
  unseres. Tool dokumentiert die Limitation transparent.
- **GWR via EGRID ist deutlich robuster als GWR via Adresse.** Bei
  Massen-Analyse gibt es kein echtes Adress-Label, nur Parzellen-
  Nummern. EGRID + Koordinate ist der richtige Eintrittspunkt.
- **Visuelle Verifikation auf map.geo.admin.ch ist Teil der Pipeline.**
  Pruefungs-Highlight: "Wir haben das Tool gegen die Karte verifiziert
  und einen weiteren Datenfehler im OEREB-Datensatz identifiziert."
- **MapServer-identify als zentraler Pattern** fuer alle swisstopo-
  Layer (GWR, TLM3D-Strassen, Arealstatistik). Einheitliche
  HTTP-Logik in `_MapServerIdentifyBasis`.

### Code-Bilanz

Heute neu:
- src/bauzonenradar/datenquellen/parzellen_liste.py (180 Zeilen)
- src/bauzonenradar/gemeinde_cache.py (520 Zeilen)
- src/bauzonenradar/klassifikation.py (250 Zeilen)
- src/bauzonenradar/gemeinde_analyse.py (340 Zeilen)
- src/bauzonenradar/excel_export.py (470 Zeilen)
- src/bauzonenradar/datenquellen/tlm3d.py (288 Zeilen)
- gwr.py erweitert (gebaeude_zu_egrid + _identify_features)
- analyse_adresse.py erweitert (AnalyseErgebnis +4 Felder, BB-Aufruf)

Total: ~2300 produktive Zeilen, 9 Commits.

### Test-Resultate Oberhofen am Thunersee (1176 Parzellen)

| Klassifikation | Anzahl | Anteil |
|---|---:|---:|
| AUSSCHLUSS_REGLEMENT | 506 | 43% |
| NEUGESCHAEFT | 257 | 22% |
| UNAUFFAELLIG | 132 | 11% |
| AUSSCHLUSS_ZU_KLEIN | 88 | 7% |
| AUSGEREIZT | 77 | 7% |
| VERDICHTUNG | 55 | 5% |
| ERSATZNEUBAU | 38 | 3% |
| AUSSCHLUSS_VERKEHR | 20 | 2% |
| AUSSCHLUSS_WALD_VERDACHT | 3 | 0.3% |

170 hochwertige Kandidaten (Verdichtung + Ersatzneubau + Ausgereizt)
zur weiteren Pruefung, 257 Neugeschaeft mit Datenluecken-Verdacht.

### Naechste Schritte

- Mail an Fabienne mit Excel-Anhang (Beispiel Oberhofen)
- Schwager-Termin: Schwellen-Verifikation + Fragen zu GWR-Polygon-Bug
- Beispiel-XLSX in docs/beispiele/ ablegen (versioniert)
- Iter 6: Polygon-Intersection fuer GWR + Wald

---

## 22. April 2026 (Dienstag) - Projekt-Setup und erster Proof-of-Concept

**Dauer**: ein Arbeitstag

### Was passiert ist

Projekt initialisiert, README + .gitignore + requirements.txt angelegt
(Commit `bf7aeb4`). Projektstruktur mit `src/`, `daten/`, `docs/`,
`tests/` aufgebaut (`c8fb261`). Erster Proof-of-Concept der
OEREB-Service-Anbindung fuer Stadt Bern lief noch am gleichen Tag
(`71a734c`).

Datenmodell (Parzelle, Restriction, Bauklasse usw.) und der
Bern-OEREB-Adapter kamen im naechsten Commit dazu (`5954320`). Ein
Beispiel-XML wurde lokal verwendet aber bewusst aus dem Repo entfernt
(`ad3cb96`) - es ist sowohl gross als auch potenziell nicht
weiterverteilbar.

Der XML-Parser wurde noch am gleichen Tag erweitert: Erkennt
Gefahrengebiete, Baulinien und Flaechen (`172e63c`) sowie die
vereinfachte Grundnutzungs-Form, die Gemeinden wie Koeniz liefern
(`4bb9499`). Den Tag abgeschlossen mit einem Update der README
(`74f2d54`).

### Entscheidungen

- **OEREB statt eigene Geodaten**: Der OEREB-Webservice liefert
  authentische, rechtsverbindliche Auskuenfte ohne lokales GIS.
  Damit muss das Tool keine grossen Geo-Files versionieren.
- **Geocoding via swisstopo SearchAPI**: schnell, tolerant gegen
  Tippfehler, kein API-Key noetig.
- **Datenklassen**: dataclass-basiertes Modell statt Dict, weil
  Type-Hints und Lesbarkeit wichtiger sind als Mikro-Performance.

### Stand am Ende des Tages

End-to-End-Pipeline lief: Adresse rein -> Parzelle + OEREB-Daten
raus. Funktional aber rohe Konsolen-Ausgabe.

---

## 23. April 2026 (Mittwoch) - Baureglement-Modul und Potenzial-Berechnung

**Dauer**: ein Arbeitstag

### Was passiert ist

Aufraeumarbeiten am Praefix-System fuer den Kurzbericht und
oeffentliche API fuer externe Diagnose-Tools (`66861af`).
Hauptarbeit war "Schritt B": Baureglement-Modul mit JSON-Files fuer
Bern und Thun (`5a59a8c`). Das Repo wurde dabei aufgeraeumt -
Strukturbaum-Datei und ein paar Karteileichen weg.

Ein praktischer Bugfix: Umlaut-sichere Dateinamen fuer
Gemeindenamen (`51516bf`). Wichtig weil die Schweiz Gemeinden mit
oe/ae/ue im Namen hat, und Windows-Filesystem mit URL-Encoding-
Resten unangenehm reagiert.

"Schritt C" am Abend: Potenzialberechnung mit Warnhinweisen,
auch wenn keine Ausnuetzungsziffer hinterlegt ist (`240b1e8`).

### Entscheidungen

- **Reglemente als JSON, nicht in Code**: ein Reglement aendert
  sich. Werte in JSON heisst: kein Python-Refactoring noetig wenn
  Stadt Bern oder Thun ihr BR aktualisieren.
- **Eine JSON pro Gemeinde**: skaliert besser als eine Mega-JSON.
  Plus: Gemeinden koennen unabhaengig versioniert werden.
- **Schritt B vor Schritt C**: erst Daten organisieren (B), dann
  Berechnung darueber legen (C). Klassisches Bottom-Up.

### Stand am Ende des Tages

Drei Saeulen funktionieren: Geocoding, OEREB-Abfrage, Reglement-
Anbindung. Erste vorsichtige Potenzialberechnung. Tool kann fuer
Bern und Thun eine Adresse durchschleusen.

---

## 24. April 2026 (Donnerstag) - Berner Systemwechsel und erste Doku-Welle

**Dauer**: ein langer Arbeitstag

### Was passiert ist

Grosse strukturelle Aenderung: Datenmodell, Reglemente und
Potenzialberechnung unterstuetzen jetzt **alle drei Berner
Bemessungssysteme** (`038ac8b`). Hintergrund: Bern hat mit dem BR
2022 die klassische Ausnuetzungsziffer abgeschafft. Wir brauchen
also AZ (alt), GFZo (Erhaltungsbauklasse) und ein Hoehen+GZ-System
(neue Wohnzonen).

README aktualisiert um diesen Berner Systemwechsel zu erklaeren
(`615b9c0`). Fachliche Grundlagen dokumentiert mit IVHB,
BR-Vergleich Thun, Stand Stadt Bern (`0ca4193`). Erstes Journal
schriftlich angelegt fuer den 22.-24. April (`e04fec1`).

Konzept-Dokument und Projektplan bis Abgabe 17. Juni 2026
(`e54e3c2`) - das ist der Anker fuer die ganze restliche Iteration.

Reglement-Daten erweitert: Thun bekommt OEREB-Schreibweisen "Wohnen
W2/W3" und ein `start.ps1` fuehrt direkt in den Modul-Ordner
(`2605976`). Bern bekommt Planungspflicht-Varianten und Zone im
oeffentlichen Interesse (`04fa292`, `27c1461`). Plus ein erstes
`demo.ps1` fuer Test-Adressen.

### Entscheidungen

- **Drei Bemessungssysteme parallel**: nicht "wir nehmen das
  modernste", sondern alle drei sauber unterstuetzt. Realitaet im
  Kanton Bern: Gemeinden haben unterschiedliche Stand-Zeitpunkte.
- **AZ als alter Bezugswert behalten**: zur Plausibilitaetspruefung
  der Schaetzung im Hoehen-System.
- **start.ps1 / demo.ps1**: Windows-PowerShell-Helper fuer reibungs-
  losen Tag-Anfang. Reduziert die Aktivierungs-Reibung.
- **Doku als erste Klasse**: Konzept, Projektplan, Fachliche
  Grundlagen, Journal - alle vier zusammen entstehen sauber neben
  dem Code, nicht nach.

### Stand am Ende des Tages

Tool funktioniert fuer Bern und Thun mit korrektem Bemessungs-
system. Erste Doku-Generation steht. Projektplan bis 17.6. ist
verschriftlicht.

---

## 27. April 2026 (Montag) - Mehrsystem-Modell und Reglement-Daten konsolidiert

**Dauer**: ca. 4 Stunden

### Was passiert ist

Stadt Bern erweitert um die volle Bauklassen-Hierarchie (BK_2 bis
BK_6, BK_E mit GFZo-Werten). Stadt Thun mit allen Wohnzonen und
WA-Zonen. Eingangsstruktur in `bern.json` und `thun.json` angeglichen
sodass das Tool beide gleichbehandelt. Reglement-Loader erkennt
Synonyme automatisch.

### Entscheidungen

- **Eine `bauklassen`-Map und eine `nutzungszonen`-Map pro Reglement**:
  saubere Trennung zwischen "was die Bauklasse erlaubt" und "was die
  Zone an Nutzung vorgibt".
- **Synonyme als separate Eintraege mit gleichem Inhalt**: kein
  Pointer-System, kein "siehe-Eintrag-X". Etwas mehr Daten, dafuer
  trivial zu lesen.

### Stand am Ende des Tages

Reglement-Daten fuer Bern und Thun konsolidiert. System-Erkennung
laeuft sauber. Bereit fuer die echte Schaetzungs-Implementierung am
naechsten Tag.

---

## 28. April 2026 (Dienstag) - Schaetz-Berechnung, Datenqualitaet, Empfehlungs-Block

**Dauer**: ca. 6 Stunden ueber den Tag verteilt

### Erster Meilenstein des Tages: erste echte Potenzialberechnung

Thunstrasse 40 berechnet GFZo=0.5 aus BO Art. 57 (`8f2c55a`). 10
Test-Adressen Regression lief gruen. Das war der erste Moment, wo
das Tool wirklich aussagekraeftige Zahlen lieferte und nicht nur
"hier sind die Daten".

### Oberhofen integriert

Hoehen-System ohne GZ funktioniert. Bugfix in `baureglement.py` und
`potenzial.py` (`9bb3661`). Drei Gemeinden vollstaendig abgedeckt:
Bern, Thun, Oberhofen.

### Mitstudentin Fabienne dazu

Doku-Update: Fabienne als Mitstudentin ergaenzt, Oberhofen
integriert, KI-Transparenz-Hinweis hinzugefuegt (`480a80b`). Drei
Bemessungssysteme dokumentiert. Iteration 1+2 abgeschlossen,
Iteration 3 laeuft.

### Schaetz-Berechnung mit Datenqualitaets-Konzept

Hier kam der konzeptionelle Schluesselgedanke des Tages (`fdff32f`):
Wir koennen nicht so tun, als ob die Schaetzung im Hoehen-System
genauso belastbar ist wie eine AZ-Berechnung. Loesung: drei
Datenqualitaetsstufen klar markiert:

- **VERBINDLICH** (AZ oder GFZo): exakte Berechnung
- **GROBSCHAETZUNG** (Hoehen-System): konservative Schaetzung
- **NICHT_MOEGLICH** (Spezialregime): keine Berechnung,
  Empfehlung statt Pseudozahl

Dazu kam: Plausibilitaetscheck gegen das alte AZ-Recht. Wenn die
Schaetzung mehr als Faktor 1.8x oder weniger als 0.7x vom alten
AZ abweicht, gibt es eine Warnung im Output.

### Empfehlungs-Block mit ASCII-Balken

Visuelle Lagebeurteilung in Prozent (`d7647b0`). Funktioniert bei
verbindlichen Berechnungen UND bei Grobschaetzungen. Vier
Lagebeurteilungs-Stufen anhand der Bauland-Reserve: HOCH, MITTEL,
GERING, AUSGESCHOEPFT. Doku-Update direkt hinterher in allen 5
Dokumenten (`69e7194`).

### Bauklassenplan-API Stadt Bern angebunden

Abends die grosse Architektur-Erweiterung (`227a9db`): die ArcGIS
REST-API von `map.bern.ch` liefert pro Parzelle parzellenscharfe
Werte fuer Bauweise (offen/geschlossen) und Gebaeudemasse
(Laenge/Tiefe). Neues Modul `bern_bkp.py`. Stadt Bern wird damit
zur einzigen BE-Gemeinde mit echter Live-API fuer Bauwerte.

NEUER PFAD `Datenqualitaet.NICHT_MOEGLICH` hinzugefuegt. Drei-
Begrenzer-Logik (Geometrie / Parzelle / GZ - der kleinste gewinnt)
mit transparenter Anzeige welcher Begrenzer aktiv ist.

Gleicher Commit enthielt auch das Doku-Update.

### Datenquellen-Evaluation Thun und geodienste.ch

Zwischen den anderen Aktivitaeten: schweizweite WFS-API von
`geodienste.ch` ausprobiert. Ergebnis: liefert nur Zonen-
Bezeichnungen, keine Bauwerte. ThunGIS getestet -- gleiche
Aussage. Koeniz angeschaut -- hat ein Bauklassen-System wie Bern,
aber auch keine Werte in der API, nur PDF-Links.

Erkenntnis: **Stadt Bern bleibt der Sonderfall** mit einer
echten Live-API fuer Bauwerte. Andere BE-Gemeinden brauchen
weiterhin manuelle JSON-Erfassung pro Gemeinde.

### Stichproben-Test mit 12 Adressen

Spaet abends noch eine Verifikations-Suite gebaut: 12 Adressen
quer durch die drei Gemeinden plus Edge-Cases. Skript
`tests/test_zwoelf_adressen.ps1`.

Resultat: 12/12 erfolgreich. Aber **3 Bug-Backlog-Punkte**
identifiziert:

1. Begrenzer-Logik bei kleinen Parzellen liefert 0 m^2
2. `Gebaeudelaenge unbeschraenkt` bricht Schaetzung ab
3. WA4 und ZPP fehlen in `thun.json`

Plus eine ehrliche Korrektur: Murifeldweg 8 ist tatsaechlich BK_3,
nicht BK_E (meine Erwartung war falsch).

### Stand am Ende des Tages

Iteration 3 (Verifikation) **konzeptionell abgeschlossen**. Alle
drei Bemessungssysteme funktionieren, Datenqualitaet wird ehrlich
markiert, Stadt Bern ist parzellenscharf, Empfehlungs-Block
visualisiert die Lage. 3 Bugs als Backlog dokumentiert.

---

## 29. April 2026 (Mittwoch) - Bug-Sweep und Iteration-5-Konzept

**Dauer**: ca. 4 Stunden, ueber den Tag verteilt

### Bug-Untersuchung gestartet (User-Beobachtung)

User hatte bei Stichproben-Tests in Thun auffaellig viele 100%
Ausschoepfung beobachtet. Code-Analyse zeigt drei Quellen des
Problems:

- `_schaetze_ist_bebauung` nutzt 40% Parzellenflaeche als Platzhalter
  (zu hoch fuer typische Wohnzonen)
- `_formatiere_empfehlung` deckelt stillschweigend auf 100% (verbirgt
  versagende Schaetzung)
- Begrenzer-Logik liefert bei kleinen Parzellen 0 m^2 (Murifeld-Bug
  vom Vortag)

### Vier Fixes umgesetzt

Im Commit `ac97892`:

1. **Ist-Platzhalter** von 40% auf 25% gesenkt (realistischer fuer
   Schweizer Wohnzonen, wo Bebauungsdichte typisch 20-30% ist)
2. **Ehrliche Anzeige** bei Ausschoepfung > 100%: echter Wert wird
   gezeigt mit Warnung "Ist > Soll - Schaetzung versagt"
3. **`max_gebaeudelaenge_m=None`** (unbeschraenkt) wird auf
   `float("inf")` gesetzt statt komplett auszusteigen
4. **Realistischere Parzellen-Form**: 1:1.5 Rechteck statt Quadrat
   (verhindert dass eine Seite negativ wird)

### Verifikation: 12 Stichproben durchgelaufen

Gleiche 12-Adressen-Suite wie am Vortag, jetzt mit Fixes:

- Effingerstrasse 35 (BK_5): erstmals ein Schaetzwert (vorher: kein
  Wert wegen unbeschraenkter Geometrie)
- Murifeldweg 8 (BK_3): 0 -> 37 m^2 mit Warnung "Ist > Soll" sichtbar
- Frutigenstrasse 25: 54.9% -> 34.3% (realistischer)
- Diverse weitere Zahlen sind jetzt plausibel statt verdaechtig hoch

12/12 erfolgreich.

### Iteration-5-Konzept geschrieben

Aus User-Vision entstanden: statt Einzeladressen abzufragen, eine
**ganze Gemeinde** analysieren und priorisierte Excel-Liste der
Verdichtungs-Kandidaten ausgeben. Konzept-Dokument
`docs/konzept_gemeinde_analyse.md` (`e75b7a7`).

Zwei-Phasen-Ansatz: erst Massen-Screening mit GWR-API als Ist-
Quelle, dann Detail-Verifikation der Top-Treffer. Statt
swissBUILDINGS3D (mehrere GB Download) nutzen wir die GWR-REST-API
fuer `garea` und `gastw` direkt.

Aufwand geschaetzt: 13-19 Stunden, also ca. 2 Tage. Zielgruppe:
Architekten und Investoren. Output: Excel-Liste fuer
Weiterverarbeitung. Iteration 5 in den Projektplan eingefuegt,
"Generalprobe" rueckt auf Iteration 6.

### Datenluecken thun.json geschlossen

Aus den Stichproben waren noch zwei "Zone im Reglement nicht
erfasst"-Faelle offen (`dce697f`):

- Seestrasse 72a (WA4): OEREB nutzt "Wohnen/Arbeiten WA4" mit
  Slash, JSON hatte "Wohnen + Arbeiten WA4" mit Plus
- Allmendstrasse 4 (ZPP): Zone mit Planungspflicht ueberhaupt
  nicht erfasst

Loesung: 5 neue Eintraege - Slash-Synonyme fuer WA3/4/5 plus die
ZPP-Zone (NICHT_MOEGLICH-Pfad mit klarem UeO-Hinweis).

Patch-Skript `patch_thun_json.ps1` mit automatischem Backup.

### Stresstest mit 50 Adressen

Letzter Test des Tages: Stichprobe vergroessert auf 50 echte
Adressen verteilt ueber vier Bereiche (Bern, Thun, Oberhofen,
fremde Gemeinden). Skript `tests/test_fuenfzig_adressen.ps1`.

Resultat:
```
48/50 erfolgreich (96%)
Laufzeit: 1.7 Minuten (2 Sek/Adresse)

VERBINDLICH:    6
GROBSCHAETZUNG: 21
NICHT_MOEGLICH: 21
```

Die zwei Ausfaelle (Effingerstrasse, Schoenburgstrasse) liefen
**einzeln nochmal angesteuert problemlos durch**. Befund:
**transienter API-Fehler**, kein Bug. Hochrechnung auf 500
Parzellen waeren ca. 20 Ausfaelle, was Risiko 1 (Rate-Limiting)
aus dem Iteration-5-Konzept empirisch bestaetigt. Die dort
geplanten Massnahmen (Throttling, Retry, Caching) bekommen damit
eine konkrete Begruendung.

### Stand am Ende des Tages

- Bug-Backlog vom 28.04. komplett abgearbeitet (4 Fixes)
- Datenluecken in `thun.json` geschlossen (5 neue Eintraege)
- 50-Adressen-Stresstest mit 96% Erfolgsquote bestanden
- Datenqualitaets-Verteilung ausgewogen ueber alle drei Pfade
- Iteration-5-Konzept verschriftlicht und im Projektplan verankert
- 4 Doku-Files aktualisiert (Journal, Konzept, Projektplan,
  Fachliche Grundlagen)

Tool ist demonstrationsreif fuer die Verteidigung am 17.6.

### Spaeter Abend: Strategische Diskussion zu Datenschutz und Parzellenabfrage

Beim Nachdenken ueber Iteration 5 kamen zwei strategische Punkte
hoch, die das Konzept noch nicht abgedeckt hat:

**1. Unbebaute Parzellen ohne Adresse**: Im Kanton Bern haben sie
meist keine Hausnummer. Wie spricht man die im Tool an? Loesung:
drei zusaetzliche Eintrittspunkte ins Iteration-5-Konzept:
- Parzellennummer + Gemeinde ("Oberhofen 309")
- EGRID direkt ("CH382046359635")
- Koordinate LV95 ("2614500, 1178500")
Aufwand: ca. 2-3 Stunden. Technisch trivial weil swisstopo
SearchAPI das bereits unterstuetzt.

**2. Eigentuemer-Daten**: Naheliegende Frage - kann das Tool nach
Identifikation einer interessanten Parzelle gleich auch den
Eigentuemer rauslassen? Recherche zu GRUDIS public und Geoportal
BEO ergab vier Probleme:

- **Captcha-Schutz** (5-stellige Eingabe vor jeder Abfrage) ist die
  explizite technische Barriere des Datenherrn. Umgehung waere
  unbefugter Zugriff (Art. 143bis StGB).
- **AGOV-Login seit 1.9.2025** macht Tool-Weitergabe mit
  eingebetteten Credentials unmoeglich.
- **revDSG seit 1.9.2023** verbietet automatisches Profilieren
  personenbezogener Daten ohne Rechtsgrundlage.
- **Reputationsrisiko** bei Massenanschreiben "Sehr geehrter Herr X
  geboren 15.3.1965, Ihre Parzelle hat 480 m^2 Reserve...".

**Entscheidung**: Brueckenansatz. Tool greift NICHT automatisch auf
Eigentuemer-Daten zu. Stattdessen Direktlink zu GRUDIS public im
Output. User loggt sich selber ein und macht die Abfrage manuell.
Skaliert ehrlich: 50 Klicks bei interessanter Liste sind zumutbar,
500 nicht - was korrekt ist, weil dann Direktanfrage beim
Grundbuchamt der korrekte Weg waere.

Beide Punkte ergaenzt in `docs/konzept_gemeinde_analyse.md`:
- Neuer Abschnitt "Eingabewege fuer die Detail-Analyse"
- Neuer Abschnitt "Eigentuemer-Daten: bewusster Verzicht auf Automatisierung"
- CLI-Beispiele erweitert um Parzellen-Eintrittspunkte

Diese Diskussion ist wertvoll fuer die Verteidigung am 17.6. -
sie zeigt Engineering-Verantwortung: rechtliche Implikationen
werden vor der Implementierung geklaert, nicht nachher.

### Quick-API-Test: Parzellen-Suche fuer Iteration 5 verifiziert

Im Anschluss noch ein Spike (insgesamt ca. 30 Min) um die zentralen
API-Annahmen fuer Iteration 5 zu verifizieren. Vier Tests
durchgefuehrt:

**Test 1: Parzellen-Suche per Gemeinde + Nummer**
```
GET .../SearchServer?type=locations&origins=parcel&searchText=Oberhofen+309
```
-> 1 Treffer mit EGRID `ch382046359635`, BFS-Nr `934`, Koordinaten
LV03. Funktioniert wie erwartet.

**Test 2: Massen-Suche per Gemeinde**
```
GET .../SearchServer?type=locations&origins=parcel&searchText=Oberhofen
```
-> 50 Treffer, sortiert nach Parzellennummer aufsteigend (Parzelle
1, 2, 3, 4, 6, 8, 9, ..., 61). Die SearchAPI **defaultet auf 50
Treffer ohne Pagination-Parameter** in der offiziellen Doku. Fuer
die Massen-Analyse einer ganzen Gemeinde brauchen wir entweder:
- alphabetische Suchstrategie (Suche nach jeder Strasse einzeln) oder
- bbox-basierte Suche (Geometrie der Gemeinde aufteilen) oder
- alternative Datenquelle (z.B. AV-Daten direkt vom Kanton)

Diesen Punkt **dokumentieren wir als offenen Implementierungsentscheid
fuer Iteration 5**, bei der die ersten Schritte mit einer kleinen
Pilot-Gemeinde wie Oberhofen sowieso funktionieren.

**Test 3: Adresse -> featureId via SearchAPI**
```
GET .../SearchServer?type=locations&origins=address&searchText=Frutigenstrasse+25+Thun
```
-> 2 Treffer:
- Frutigenstrasse 25 mit `featureId: 1435137_0`
- Frutigenstrasse 25a mit `featureId: 502105207_0`

Pro Treffer kommt im `links`-Feld direkt die URL zum GWR-Datensatz
mit. Wir muessen die URL nicht selber basteln.

**Test 4: GWR-Detail-Abfrage**
```
GET .../MapServer/ch.bfs.gebaeude_wohnungs_register/1435137_0
```
-> Reichhaltige Daten zum Gebaeude:

```
egid:     1435137
egrid:    CH394601433582
lparz:    324
ggdename: Thun
garea:    304    (Grundflaeche m^2)
gastw:    5      (Vollgeschosse)
ganzwhg:  7      (Wohnungen)
gbaup:    8016   (Bauperiode-Code, ~1996-2000)
warea:    [85, 105, 45, 75, 95, 105, 75]  (Wohnungs-Flaechen)
gwaerzh1: 7432   (Waermepumpe, saniert 29.06.2021)
```

### Drei wichtige Erkenntnisse aus den Tests

**1. GWR-Felder sind alle da wie aus Doku erwartet.**
`garea`, `gastw`, `egrid`, `lparz`, `ggdename` - alle vorhanden und
sauber typisiert. Keine boesen Ueberraschungen.

**2. Mehrere Adressen koennen auf VERSCHIEDENEN Parzellen sein.**
Frutigenstrasse 25 liegt auf Parzelle 324, Frutigenstrasse 25a auf
einer eigenen Parzelle 4029 (5 m^2 Nebengebaeude). Die Aggregation
muss also **pro EGRID** erfolgen, nicht pro Strassenadresse - das
ist die robuste und korrekte Identifikation.

**3. Plausibilitaets-Konflikt aufgedeckt.**
Frutigenstrasse 25 zeigt im Vergleich:
- Ist mit Platzhalter 25%:    371 m^2
- Ist aus GWR (304 x 5):     1520 m^2
- Soll (unsere Schaetzung):  1080 m^2 (Hoehen-System konservativ)

Die Parzelle ist **bereits zu 141% ausgeschoepft** wenn man die
echten GWR-Werte nimmt. Unsere Schaetzung sagte 34%. Das ist KEIN
Tool-Bug, sondern die Konsequenz daraus dass die Hoehen-System-
Schaetzung mit 12m Default-Gebaeudebreite konservativ rechnet,
waehrend in Realitaet breiter gebaut wurde (304 m^2 / 25 m =
12.2 m Breite, knapp ueber Default). Plus: das Mehrfamilienhaus
mit 7 Wohnungen aus 1999 nutzt vermutlich Dachgeschoss-Bonus voll
aus.

**Genau dieser Konflikt ist die Existenzberechtigung von Iteration 5**:
echte Ist-Werte aus GWR statt Platzhalter zeigen die Realitaet.

### Konsequenzen fuer Iteration 5

Konzept ergaenzt um die empirisch verifizierten Befunde:
- GWR-Sektion mit echtem Beispiel statt Lausanne-Hypothese
- Drei "Empirische Befunde" als Architektur-Entscheidungs-Grundlage
- Aggregation pro EGRID dokumentiert
- Bonus-Daten (Wohnungen, Heizung, Sanierung) als Excel-Spalten-
  Kandidaten

Damit ist die zentrale Annahme von Iteration 5 nicht nur
**theoretisch begruendet**, sondern **empirisch verifiziert**. Die
Implementierung kann mit Vertrauen starten - es gibt keine
verborgenen Showstopper.

---

## 30. April 2026 (Donnerstag) - Aufraeumen und Strukturierung

**Dauer**: ca. 1.5 Stunden

### Ausgangslage

Nach dem Marathon-Tag vom 29.04. (Bug-Fixes, Konzept, Stresstest, Konzept-
Verfeinerung, API-Spike) gab es zwei Punkte zu klaeren bevor Iteration 4
starten kann:

1. **Projektstruktur bereinigen**: Frueh entstandene Artefakte (Proof-of-
   Concept, alte Strukturbaum-Snapshots, Test-XMLs) lagen unaufgeraeumt
   im Repo. Das war fuer Iteration 3 OK, ist aber fuer eine Uebergabe an
   Fabienne nicht praesentabel.
2. **Datenbaum dokumentieren**: Bevor neue Module dazukommen, sollte der
   aktuelle Stand strukturiert festgehalten sein.

### Datenbaum dokumentiert

Aktuelle Struktur per `Get-ChildItem -Recurse` exportiert und in
`docs/struktur.md` dokumentiert. Das Dokument enthaelt:

- Visualisierung des Verzeichnisbaums mit Beschreibung
- Module im Detail mit Verantwortlichkeiten
- Reglement-Uebersicht in Tabelle
- Test-Suiten dokumentiert
- Aufraeum-Kandidaten als Backlog
- Geplante Erweiterungen fuer Iter 4 und 5

Damit gibt es jetzt eine **Architektur-Karte** fuer die Verteidigung
am 17.6. und fuer Fabienne als Onboarding-Hilfe.

### Aufraeum-Skript erstellt und ausgefuehrt

`aufraeumen_30_04_2026.ps1` mit 6 Schritten und Sicherheits-ZIP-Backup
verschoben in den richtigen Ordner:

| Was | Wohin |
|---|---|
| `proof_of_concept.py` | `docs/archiv/` (lokal, nicht im Repo) |
| `Strukturbaum-bauzonen-radar.txt` | `docs/archiv/` |
| `extract_beispiel.xml` | `docs/archiv/` |
| `tests/test_zwoelf_adressen.py` (Python-Version) | `docs/archiv/` |
| `extract_koeniz.xml`, `pruefen.xml`, `thun.xml` | `tests/fixtures/` |
| `src/bauzonenradar/test_bern_batch.py` | `tests/test_bern_batch.py` |

`docs/archiv/` wurde via `.gitignore` aus dem Repo ausgeschlossen.

### Strategische Entscheidung: Test-Fixtures im Repo

Diskussion fuer und gegen `tests/fixtures/*.xml`:

- **Fuer**: Reproduzierbare Tests offline, Verteidigungs-Demo ohne
  Internetzugriff, Schwager kann Tests laufen lassen ohne API-Setup
- **Gegen**: 564 KB im Repo, OEREB-Daten aendern sich, vielleicht nur
  einmalig verwendet

Entscheidung: **Im Repo behalten**, mit Whitelist-Ausnahme in
`.gitignore` (Standard-Sperre `**/*.xml` ausser fuer
`tests/fixtures/`). Plus `README.md` der erklaert was die XMLs sind
und wie sie genutzt werden koennen.

Begruendung: Lieber jetzt 564 KB im Repo behalten als spaeter
feststellen "Mist, haetten wir gebraucht". Das Aufraeumen kann
spaeter immer noch erfolgen.

### Klaerung Iteration 5 - noch nicht starten

Frage aufgeworfen ob Iteration-5-Code (gwr.py, parzellen_liste.py)
schon geschrieben werden kann. Antwort:

- **Technisch ja** (Architektur und Datenmodell sind verifiziert)
- **Strategisch nein** (Iteration 4 mit Fabienne kommt zuerst,
  parallele Aenderungen am Backend wuerden Konflikte produzieren)

Stattdessen: Iteration 4 abwarten, dann Iteration 5 sauber starten.
Das Konzept liegt fertig vor, Iteration 5 ist startklar wenn die
Streamlit-GUI steht.

### Strukturelle Zustand am Ende des Tages

```
bauzonen-radar/
+-- docs/
|   +-- archiv/        (LOKAL: PoC, alte Strukturbaeume, Aufraeum-Skript)
|   +-- konzept.md, projektplan.md, journal.md, fachliche_grundlagen.md
|   +-- konzept_gemeinde_analyse.md (708 Zeilen, Iteration 5 bereit)
|   `-- struktur.md (NEU)
+-- src/bauzonenradar/
|   +-- (Hauptmodule wie bisher)
|   +-- analyse/, ausgabe/, datenquellen/, gui/  (gui+datenquellen leer fuer Iter 4+5)
+-- tests/
|   +-- fixtures/      (3 XMLs + README, getrackt via Whitelist)
|   +-- test_bern_batch.py (verschoben aus src)
|   +-- test_zwoelf_adressen.ps1, test_fuenfzig_adressen.ps1
|   `-- __init__.py
+-- daten/baureglemente/  (3 JSONs)
+-- README.md, requirements.txt, start.ps1, demo.ps1
```

### Bilanz

- Projekt-Struktur ist sauber und dokumentiert
- 8 Dateien an die richtige Stelle verschoben
- `tests/fixtures/` als getrackter Snapshot-Ordner mit README
- `docs/struktur.md` als Architektur-Karte
- `docs/archiv/` als lokale Geschichts-Sammlung
- Tool ist demonstrationsreif **und** uebergabereif

Damit kann Fabienne sauber starten und die Verteidigung kann
strukturiert vorbereitet werden.

### Spaeter Abend: GWR-Modul fuer Iteration 5 vorgebaut

Da Sonntag ein gemeinsamer Coding-Tag mit Fabienne ansteht, wurde
das **GWR-Modul als isoliertes Stueck Iteration 5** vorgebaut. Die
Streamlit-GUI (Iter 4) bleibt unberuehrt.

**Neues Modul** `src/bauzonenradar/datenquellen/gwr.py` (~330 Zeilen):

- `GwrGebaeude`-Datenklasse mit allen Feldern aus der GWR-API
- `GwrQuelle`-Hauptklasse mit:
  - Zwei-Stufen-Workflow (SearchAPI -> MapServer)
  - Caching fuer Adressen UND featureIds (in-memory)
  - Cache-Limit MAX_CACHE_SIZE 5000 zur Verhinderung von Speicherproblemen
  - Retry-Logic mit exponentialem Backoff (2 Versuche default)
  - Throttling-Parameter fuer Massenabfragen (Iter 5 vorbereitet)
  - 3 Exception-Klassen (GwrFehler, GwrApiFehler, GwrParseFehler)
- Aggregation `geschossflaeche_pro_parzelle()` fuer mehrere Gebaeude
- Robuster Parser fuer unvollstaendige Antworten

**Integration in `analyse_adresse.py`** mit minimalen, additiven
Aenderungen (Pattern wie BKP-Modul - try/except-Import, keine Aenderung
an bestehenden Schritten).

**Test-Verifikation mit 4 verschiedenen Szenarien**:

| Adresse | Szenario | Resultat |
|---|---|---|
| Frutigenstrasse 25, Thun | bebautes MFH | 304 m^2 x 5 = 1520 m^2 angezeigt |
| Allmendstrasse 4, Thun | grosse ZPP, keine Hauptbau-Adresse | "evtl. unbebaut" Hinweis |
| Effingerstrasse 35, Bern | BKP + GWR parallel | beide Module ergaenzen sich |
| Seestrasse 2, Spiez | fremde Gemeinde ohne Reglement | GWR liefert Wert auch ohne Soll |

Wichtigste empirische Befunde:

1. **Plausibilitaets-Konflikt sichtbar**: Frutigenstrasse 25 zeigt im
   GWR 1520 m^2 echte Bebauung, das Tool schaetzt 1080 m^2 als Soll.
   Die Schaetzung ist konservativ (12m Default-Breite), Realitaet ist
   breiter gebaut. **Genau das ist die Existenzberechtigung des
   Moduls** - Architekten sehen jetzt beide Werte.

2. **Adressen-basierte Suche limitiert**: Die Allmendstrasse 4
   (220'151 m^2 ZPP-Parzelle) hat 9 Bauinventar-Eintraege, aber GWR
   findet ueber die Adresse nichts. Fuer Iteration 5 Massen-Analyse
   braucht es Bbox- oder EGRID-basierte Suche.

3. **Mehrwert auch ohne Reglement**: Selbst wenn das Tool fuer eine
   Gemeinde kein Soll berechnen kann (z.B. Spiez), liefert GWR den
   Ist-Wert. Damit hat das Tool fuer **alle** BE-Gemeinden mindestens
   eine nuetzliche Information.

4. **GWR-Daten manchmal unvollstaendig**: Effingerstrasse 35 hat einen
   EGID, aber `garea` und/oder `gastw` fehlen. Das Modul faengt das
   sauber ab mit "GWR-Daten unvollstaendig" statt zu crashen.

### Stresstest mit 50 Adressen mit GWR

Nach den 4 manuellen Tests wurde der bestehende 50-Adressen-Stresstest
mit dem integrierten GWR-Modul wiederholt:

| Metric | Vor GWR (29.04.) | Mit GWR (30.04.) |
|---|---|---|
| Erfolgsquote | 96% (48/50) | **96% (48/50)** identisch |
| Laufzeit | 1.7 Min | **2.2 Min** (+30 Sek) |
| Datenqualitaet | 6 V / 21 G / 21 N | gleiche Verteilung |
| Funktionalitaet | Soll-Berechnung | **Soll + Ist + Plausibilitaet** |

**Ergebnis: GWR-Integration kostet nur 30 Sekunden mehr Laufzeit**
fuer massiven Mehrwert. Sehr effizient.

**Wichtige Beobachtungen aus dem Stresstest**:

1. **Plausibilitaets-Konflikt jetzt sichtbar bei vielen Adressen**:
   - Murifeldweg 8, Bern: Soll 37 m^2 vs. Ist 435 m^2 (Faktor 12x)
   - Tellstrasse 4, Bern: Soll 23 m^2 vs. Ist 644 m^2 (Faktor 28x)
   - Hofstettenstrasse 8, Thun: Soll 879 m^2 vs. Ist 732 m^2 (Faktor 0.83x)

   Das sind die kleinen Stadt-Parzellen mit dicht ueberbauter Realitaet,
   die unsere Schaetzung am Begrenzer "Parzelle minus Grenzabstaende"
   konservativ unterschaetzt. GWR macht das endlich sichtbar.

2. **Aggregation mehrerer Gebaeude funktioniert sauber**:
   - Untere Sadelstrasse 1, Oberhofen: 2 Gebaeude (1 vollstaendig +
     1 unvollstaendig) -> SUMME: 339 m^2 mit klarer Anzeige.
   - Bahnhofstrasse 5, Heimberg: 3 Gebaeude -> SUMME: 863 m^2.

3. **"Unvollstaendig (fehlt: Feld)"-Anzeige nuetzlich**: Bei BK_E
   und Altstadt-Adressen fehlt typischerweise `gastw`. Die explizite
   Anzeige hilft zu unterscheiden zwischen "kein Gebaeude" und
   "Gebaeude da, Daten luckenhaft".

4. **2 Fehler sind die gleichen wie ohne GWR**: Schoenburgstrasse 5
   und Effingerstrasse 35 schlagen mit UnicodeEncodeError fuer das
   `\u221e` (Unendlich-Zeichen) fehl. Das ist ein bekannter Bug bei
   Bauklasse 5 ohne Laengenbegrenzung auf Windows-Konsole - **NICHT
   durch GWR verursacht**.

### Bilanz

- Projekt-Struktur sauber und dokumentiert
- 8 Dateien an die richtige Stelle verschoben
- `tests/fixtures/` als getrackter Snapshot-Ordner mit README
- `docs/struktur.md` als Architektur-Karte
- `docs/archiv/` als lokale Geschichts-Sammlung
- **GWR-Modul als erstes Iteration-5-Stueck fertig**
- **Stresstest 96% bei 2.2 Min Laufzeit mit GWR**
- Tool ist demonstrationsreif **und** uebergabereif

Damit kann Fabienne am Sonntag-Coding-Tag sauber starten und
parallel an Streamlit arbeiten, waehrend das Backend bereits
Iter-5-Funktionen liefert.

---

## 03. Mai 2026 (Sonntag) - Coding-Tag mit Fabienne und Iter-4-Start

**Dauer**: 0800-1100 (Vormittag mit Fabienne digital), Nachmittag Familienfest

### Fabiennes Sonntag-Vorarbeit (in den Pausen am Vortag)

Fabienne hat schon am Samstag Abend eigenstaendig die Doku-Architektur
restrukturiert:

- `Anforderungen.md` -> `docs/anforderungen_backend.md` (umbenannt + Endung)
- `Glossar` -> `docs/glossar.md` (Markdown-Endung, wird nun gerendert)
- Neu: `docs/anforderungen_frontend.md` (54 Zeilen)
- Neu: `docs/releasenotes_backend.md` (25 Zeilen)
- Neu: `docs/releasenotes_frontend.md` (27 Zeilen)

Saubere Trennung Backend/Frontend, getrennte Releasenotes pro Bereich.
Das ist eigenstaendige RE-Pruefungsleistung. Ihre Releasenotes sind
endkunden-orientiert (Capabilities, nicht Code-Aenderungen).

### Vormittag (0800-1100): Backend-Refactoring

Iter 4 braucht eine GUI, die GUI braucht ein **Datenobjekt** statt
print-Output. Bisher hat `analyse_adresse.py` direkt geprintet.
Refactoring noetig: Trennung Berechnung von Ausgabe.

#### Neue Datenklasse `AnalyseErgebnis`

In `analyse_adresse.py` ergaenzt: Datenklasse mit ~30 Feldern.
Sammelt **alles** was GUI oder CLI brauchen:

- Adresse, Status, Fehler, Warnungen
- Parzelle (gemeinde, parzellen_nummer, parzellen_flaeche_m2, egrid)
- Koordinaten (LV95 und WGS84)
- Reglement-Status
- BKP-Daten (Stadt Bern)
- GWR-Daten (Liste der Gebaeude, Summe Geschossflaeche)
- Potenzial (datenqualitaet, zulaessig_m2, ausschoepfung_prozent, ...)
- Original-Textbericht fuer Debug

#### Neue Funktions-Architektur

```
analysiere(adresse) -> AnalyseErgebnis    # reine Logik, kein Print
drucke_bericht(ergebnis) -> None           # CLI-Output
main()                                     # ruft beide nacheinander
```

**Separation of Concerns**: GUI und CLI nutzen dieselbe `analysiere()`-
Funktion. Beim Refactoring auch defensive Helper-Funktionen
`_attr_zu_string()` und `_zahlenfeld()` eingefuehrt fuer robusten
Field-Zugriff.

Bonus: `koordinate_wgs84` (lat, lon) wird automatisch berechnet -
direkt nutzbar fuer `st.map()` in der GUI.

#### Verifikation

- Smoke-Test "Thunstrasse 40, 3005 Bern": EMPFEHLUNG-Block korrekt
- Stresstest 12 Adressen: **12/12 erfolgreich** (100%)
- Output rueckwaertskompatibel zum bisherigen CLI-Verhalten

### Fabiennes Frontend (parallel)

Sie hat **eigenstaendig** angefangen mit Streamlit-GUI:
- `src/bauzonenradar/gui/app.py` ~370 Zeilen
- Eigenes CSS (Inter-Schrift, Schwarz/Rot-Akzent, ruhige Typografie)
- Drei Sektionen: Lage (Karte) / Parzelle / Bebauungspotenzial / GWR
- Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz
- Defensive Programmierung mit Variant-Detection (A/B fuer Backend-API)

Sie hat es per Mail geschickt, noch nicht gepushed (wartet auf
Backend-Stabilitaet).

### Nachmittag: Familienfest mit Schwager

Geplant war ein Verifikations-Smalltalk. Realitaet: kein konzentrierter
Slot moeglich am Fest. Schwager hat aber Interesse signalisiert,
besonders an der **Iter-5-Idee** (Massen-Analyse einer Gemeinde,
oder bei interessanter Parzelle aehnliche Parzellen finden).

Termin fuer naechste Woche vereinbart fuer richtige Reglement-
Verifikation und Annahmen-Plausibilisierung.

### Releasenote ergaenzt

Backend-Releasenote zum Refactoring eingetragen in
`docs/releasenotes_backend.md` (im Format von Fabiennes etabliertem
Stil, endkunden-orientiert):

- Strukturiertes Analyse-Ergebnis als Objekt
- WGS84-Koordinaten fuer Karten
- Trennung Berechnung/Ausgabe
- Verifikation auf 12 Test-Adressen

### Commits am Sonntag

- a971720: docs: Backend-Releasenote zum analysiere()-Refactoring
- (Refactoring war schon im vorigen Commit drin)

### Bilanz

- Backend-API stabil und GUI-tauglich
- Iter 3 + 5/Modul-1 (GWR) abgeschlossen, Iter 4 (Frontend) angefangen
- Doku-Architektur durch Fabienne verbessert (Backend/Frontend-Trennung)
- Schwager-Termin auf naechste Woche verschoben
- Mit Stand 03.05. ist das Tool weiter **demonstrationsreif**

---

## 05. Mai 2026 (Dienstag) - Frontend-Test und Crash-Diagnose

**Dauer**: ca. 1 Stunde

### Ausgangslage

Fabienne hat ihre `app.py` per Mail geschickt aber noch nicht ins
Repo gepushed (wartet auf Backend-API). Damit sie Layout-Feedback
schon bekommen kann, lokale Test-Datei eingefuehrt.

### Lokaler Frontend-Test

Vorgehen:
- Streamlit installiert (`pip install streamlit pandas`)
- Fabiennes Code als `src/bauzonenradar/gui/app_christophe_test.py`
  lokal abgelegt (NICHT committed, ueber `.gitignore` ausgeschlossen)
- App gestartet: `streamlit run src/bauzonenradar/gui/app_christophe_test.py`

### Layout-Bewertung

Sehr starkes Design:
- Header "Bauzonen-Radar" mit Untertitel
- 2px schwarze Trennlinie
- Eingabefeld + "Analysieren"-Button
- Sektion-Titel "PARZELLE", "GEMEINDE" als Smallcaps
- Schwarze Grundtypografie, rotes Akzent bei Hover
- Inter-Schrift, ruhige Anmutung
- Sehr eigenstaendig - nicht Streamlit-Default

### Crash-Diagnose

Wie erwartet crasht es beim ersten Backend-Feldzugriff:

```
AttributeError: 'AnalyseErgebnis' object has no attribute 'parzellenflaeche_m2'.
Did you mean: 'parzellen_flaeche_m2'?
```

Python schlaegt den korrekten Namen selbst vor - sehr nuetzlich.

Ursache: Fabienne hat ihren Code gegen ein **vermutetes**
Backend-Interface geschrieben, weil ich ihr am Sonntag nur den
Mini-Snippet `from analyse_adresse import analysiere` geschickt hatte
ohne die komplette Feldliste. Mein Fehler.

#### Beobachtete Mismatches

| Frontend nutzt | Backend hat | Anmerkung |
|---|---|---|
| `parzellenflaeche_m2` | `parzellen_flaeche_m2` | Underscore-Konvention |
| `theoretisch_zulaessig_m2` | `zulaessig_m2` | |
| `ausschoepfungsgrad_prozent` | `ausschoepfung_prozent` | |
| `reserve_prozent` | aus `100 - ausschoepfung_prozent` zu berechnen | |
| `zonen_betrachtet` | `[ergebnis.zone]` | Wrap als Liste |
| `status` (Enum) | `lagebeurteilung` (String) | Type anders |
| `bemerkungen` | `warnungen` | |
| `arealbonus_anwendbar` | nicht im Backend | Default `False` |
| `parzelle.X` | `ergebnis.X` direkt | Kein separates Parzelle-Objekt |

### Strategie-Entscheidung

Mit Fabienne abgesprochen: **Frontend wird angepasst**, nicht das
Backend. Argumente:
- Backend-Datenmodell bleibt sauber und stabil
- Aliase im Backend wuerden Tech-Debt erzeugen
- Sie lernt das Backend-Interface kennen (gut fuers Pruefungs-
  Verstaendnis im Team)
- Software-Engineering-Disziplin: GUI passt sich an Backend an

Komplette Mapping-Tabelle und Feldliste an Fabienne geschickt.
Sie kann mit Search & Replace alle Aenderungen in 15-20 Min machen.

### Aufraeum-Aktivitaet

- Lokale Backup-Datei `analyse_adresse.py.bak_potenzial_ergebnis`
  geloescht (Git ist eh Backup)
- `.gitignore` ergaenzt um `app_christophe_test.py`, sodass die
  Test-Datei nicht versehentlich committet werden kann
- Commit 0aeb5b3: "chore: app_christophe_test.py lokal ignorieren"

### Bilanz Dienstag

- Layout-Test erfolgreich (auch mit Crash informativ)
- Crash sauber diagnostiziert mit Python-Auto-Vorschlag
- Klare Mapping-Vorlage fuer Fabienne
- Repo aufgeraeumt
- Standby fuer Fabiennes Fix

### Commits am Dienstag

- 0aeb5b3: chore: app_christophe_test.py lokal ignorieren

---

## 11. Mai 2026 (Montag) - Iter-4-Abschluss: Frontend live, Backend-Fix, Repo aufgeraeumt

**Dauer**: ca. 3 Stunden ueber den Vormittag verteilt

### Ausgangslage

Fabienne hat ihr Frontend gepushed mit Anpassungen nach unserem
Sonntags-Stand. Letzter Stand vom Dienstag (05.05.) war: Frontend
crasht beim ersten Backend-Feldzugriff (`parzellenflaeche_m2` statt
`parzellen_flaeche_m2`), Mapping-Tabelle an Fabienne uebergeben.

Heute startet sie mit dem aktualisierten Frontend, und wir testen
gemeinsam ob alles laeuft.

### Erste Tests: GUI laeuft, aber Daten fehlen

Streamlit startet sauber, Layout sieht super aus. Bei den 4 Test-
Adressen (Thunstrasse 40, Frutigenstrasse 25, Kramgasse 49,
Murifeldweg 8):

- ✅ Karten rendern mit roten Markern
- ✅ Datenqualitaets-Badges in allen drei Pfaden korrekt
- ✅ GWR-Tabelle wird sauber gerendert
- ❌ Aber: Bebauungspotenzial zeigt nur Striche statt Zahlen
- ❌ Zone(n) ist leer
- ❌ "Keine Berechnung moeglich" auch bei VERBINDLICH-Pfad

### Diagnose: Backend-Bug entdeckt

Verdacht war zunaechst Frontend-Code. CLI-Test hat aber gezeigt:

```
datenqualitaet: 'VERBINDLICH'
zulaessig_m2: None              <- Bug!
ausschoepfung_prozent: None     <- Bug!
zone: NICHT VORHANDEN           <- Feld existiert gar nicht
```

Das `PotenzialErgebnis`-Objekt hat aber die Daten:
```
potenzial_ergebnis.theoretisch_zulaessig_m2 = 118.5
potenzial_ergebnis.ausschoepfungsgrad_prozent = 50.0
potenzial_ergebnis.zonen_betrachtet = ['Bauklasse E ...']
```

**Ursache**: Beim Sonntag-Refactoring (`AnalyseErgebnis`) hatte ich
einen `_zahlenfeld()`-Helper geschrieben der nach **falschen** Feldnamen
suchte (`zulaessig_m2`, `geschossflaeche_zulaessig`). Die echten
Namen im `PotenzialErgebnis` sind `theoretisch_zulaessig_m2` und
`ausschoepfungsgrad_prozent`. Daher kam immer `None` zurueck.

### Strategie-Entscheidung: Backend fixen, nicht Frontend

Mit Fabienne abgesprochen: **Backend wird angepasst**. Argumente:
- Backend-API war von Anfang an als flache Aliase gedacht
- Aliase im Backend waeren keine Tech-Debt, sondern explizit so geplant
- Fabiennes Code aendert sich nicht
- Frontend-Code bleibt sauber, Backend stellt korrekt zur Verfuegung

### Backend-Fix: AnalyseErgebnis-Aliase

In `analyse_adresse.py`:

**Aenderung 1**: AnalyseErgebnis-Klasse um 7 neue Felder erweitert:
```python
theoretisch_zulaessig_m2: Optional[float] = None
ausschoepfungsgrad_prozent: Optional[float] = None
reserve_prozent: Optional[float] = None
zonen_betrachtet: list = field(default_factory=list)
zone: Optional[str] = None
arealbonus_anwendbar: bool = False
bemerkungen: list = field(default_factory=list)
```

**Aenderung 2**: Befuellung mit direkten `getattr()`-Aufrufen statt
defensiver `_zahlenfeld()`-Helper. Direkte Zugriffe auf die echten
Feldnamen aus `PotenzialErgebnis`.

### Verifikation: Drei CLI-Smoke-Tests

```
Test 1 (VERBINDLICH):    Thunstrasse 40, 3005 Bern
   theoretisch_zulaessig_m2 = 118.5 m^2
   ausschoepfungsgrad = 50.0%
   zone = "Bauklasse E, Erhaltung..."

Test 2 (GROBSCHAETZUNG): Frutigenstrasse 25, 3604 Thun
   theoretisch_zulaessig_m2 = 1080 m^2
   reserve_prozent = 65.67%
   gwr_summe = 1520 m^2 (Plausibilitaets-Konflikt!)

Test 3 (NICHT_MOEGLICH): Kramgasse 49, 3011 Bern
   datenqualitaet = "NICHT_MOEGLICH"
   zulaessig = None (korrekt)
```

Alle drei gruen.

### Live-Test in der GUI

Streamlit neu gestartet. **Vier Test-Adressen durchgespielt**:

**Thunstrasse 40, 3005 Bern** (VERBINDLICH):
- Bebauungspotenzial: 118 m^2 zulaessig, 50.0% Ausschoepfung, 50.0% Reserve
- Progress-Bars rendern (rot fuer Ausschoepfung, gruen fuer Reserve)
- Lagebeurteilung "Mittleres Verdichtungs-Potenzial"
- ZONE(N) zeigt "Bauklasse E, Erhaltung..."
- GWR-Tabelle mit 1 Gebaeude, 224 m^2 Geschossflaeche
- **Plausibilitaets-Konflikt-Box** ausgeloest (GWR 224 m^2 > Soll 118 m^2)

**Frutigenstrasse 25, 3604 Thun** (GROBSCHAETZUNG - das Highlight!):
- GROBSCHAETZUNG-Badge mit Warnung
- Theoretisch zulaessig: 1080 m^2, Ausschoepfung: 34.3%, Reserve: 65.7%
- "Hohes Verdichtungs-Potenzial"
- GWR-Tabelle: 304 m^2 x 5 Geschosse = 1520 m^2 (7 Wohnungen)
- **Plausibilitaets-Konflikt-Box**: "GWR-Ist (1520 m^2) uebersteigt den
  berechneten Soll-Wert (1080 m^2)"

Das ist das Pruefungs-Highlight: Tool zeigt den 1.4-fachen Unterschied
zwischen rechtlichem Soll und gebauter Realitaet. Klassischer Bestandsschutz-
Fall, jetzt sichtbar.

**Kramgasse 49, 3011 Bern** (NICHT_MOEGLICH):
- NICHT MOEGLICH-Badge, "Quantitative Potenzialberechnung nicht moeglich"
- Verweis auf Bauverwaltung
- Keine Pseudo-Werte
- "Keine GWR-Daten gefunden - Parzelle moeglicherweise unbebaut"

**Murifeldweg 8, 3006 Bern** (Edge-Case):
- GROBSCHAETZUNG mit 230.1% Ausschoepfung
- Bauland-Reserve -130.1% (negativ wegen >100%)
- "Praktisch ausgeschoepft"
- GWR: 145 m^2 x 3 Geschosse = 435 m^2 (Tool schaetzte 37 m^2)
- Konflikt-Box: "GWR-Ist (435 m^2) uebersteigt den berechneten Soll-Wert (37 m^2)"

### Beobachtungen fuer Fabienne (optional UX)

- Negative Reserve (-130.1%) visuell etwas seltsam.
  Vorschlag: bei >100% Ausschoepfung "Reserve: 0%" anzeigen
- Zone "Wohnen W3 [hoehen_und_gz]" — Klammer-Suffix ist intern-technisch,
  fuer Endanwender koennte das ausgeblendet werden
- Karten-Marker (roter Kreis) sehr gross, ueberdeckt die Parzelle

Diese Punkte sind **optional fuer Phase 3 (Generalprobe Mitte Juni)**.
Iter 4 ist substantiell fertig.

### Repo-Aufraeumen vor Iter-4-Abschluss

**Aufraeum-Aktion**:
- Temp-Dateien geloescht: `analyse_adresse_aktuell.txt`, `patch_aliase.ps1`
- `docs/START JenzC.txt` -> `docs/start_cheatsheet.md` (Markdown, klarer
  Name, persoenliche Quick-Reference)
- `tests/## interessante Objekte.txt` -> `docs/archiv/output_baumgarten_thun.md`
  (lokal, nicht im Repo - interessante Output-Snapshots)
- Patch-Skripte (5 im Repo, plus `patch_potenzial_ergebnis.ps1` vom 03.05.)
  bleiben im Repo als **Beleg fuer iterative Entwicklung** mit Backup-
  Mechanismus, Syntax-Check und Smoke-Tests
- Backup-ZIP des Aufraeum-Stands unter `docs/archiv/`

### struktur.md aktualisiert

Stand 11.05. mit:
- `gui/frontend.py` statt `gui/app.py`
- `AnalyseErgebnis` mit ~40 Feldern (inkl. 7 neue GUI-Aliase)
- Neue Doku-Dateien aufgenommen
- Patch-Skripte-Sektion als Dokumentation
- Iter-4-Status-Sektion mit Bilanz

### Commits am 11.05.

- b0fc2cd: fix: AnalyseErgebnis-Aliase korrekt aus PotenzialErgebnis befuellen
- 40d3f0d: chore: Repo aufgeraeumt vor Iter-4-Abschluss
- 440a26f: docs: struktur.md auf Stand 11.05.
- (Plus weitere Doku-Updates folgen heute: projektplan, journal, releasenotes)

### Bilanz Iter-4-Abschluss

- Streamlit-GUI funktioniert vollstaendig mit echten Daten
- Alle drei Datenqualitaets-Pfade sichtbar in der GUI
- Plausibilitaets-Konflikt-Box als Pruefungs-Highlight
- Backend-API stabil und sauber dokumentiert
- Repo aufgeraeumt und konsistent
- Fabiennes Design ist eine eigenstaendige Leistung mit Wow-Effekt

**Iter 4 ist substantiell abgeschlossen**. Verbleibende UX-Polish kann
in Iter 6 (Generalprobe) eingebaut werden.

**Naechste Schritte**:
- Schwager-Termin naechste Woche fuer Reglement-Verifikation
- Iter 5 ab Anfang Juni: parzellen_liste.py, gemeinde_analyse.py, Excel-Export
- Iter 6 Mitte Juni: Generalprobe + UX-Polish

---

## Verschiedene Beobachtungen waehrend der Entwicklung

- **Windows-PowerShell** mit `start.ps1` automatisiert venv-Aktivierung
  und Wechsel ins Modul-Verzeichnis. Spart bei jedem Start drei
  Befehle.
- **`demo.ps1`** verwendet `$PSScriptRoot`, also ortsunabhaengig
  aufrufbar.
- **OEREB-Webservice** antwortet meist in unter 5 Sekunden, ab und zu
  laengere Wartezeiten. Bei 50 Aufrufen kommen vereinzelt transiente
  Fehler vor (siehe 29.04.).
- **swisstopo SearchAPI** ist sehr schnell und tolerant gegenueber
  Tippfehlern in Adressen.
- **Iteratives Vorgehen mit Real-Tests** deckt Schwachstellen auf,
  die in der Theorie nicht sichtbar sind. Beispiele:
  - Florastrasse-Test fuehrte direkt zur Schaetz-Berechnung
  - Thunstrasse 40 + Florastrasse 5 zusammen fuehrten zum
    Empfehlungs-Block (visuell statt rein numerisch)
  - Murifeldweg 8 zeigte den Begrenzer-Logik-Bug bei kleinen
    Parzellen
  - Effingerstrasse 35 zeigte den `unbeschraenkt`-Bug
- **Information Design ist genauso wichtig wie korrekte Berechnung.**
  Ein Architekt liest in einer Sekunde den Balken, nicht in zehn
  Sekunden die Zahl. Plausibilitaets-Hinweise und Warnungen sind
  Teil der Berechnung, nicht Beiwerk.
- **Drei Tier von Datenquellen** im Berner Raum:
  1. OEREB (alle Gemeinden) - Zonen-Code, bereits implementiert
  2. Spezialisierte Stadt-API (nur map.bern.ch BKP) - parzellenscharfe
     Geometrie, implementiert
  3. geodienste.ch (schweizweit) - liefert nur was OEREB schon
     liefert, KEIN Mehrwert
- **Stadt Bern ist der Sonderfall.** Andere BE-Gemeinden brauchen
  weiterhin JSON-Erfassung pro Gemeinde. Koeniz hat ein Bauklassen-
  System wie Bern und ist als naechster Kandidat im Backlog.
- **Separation of Concerns durch analysiere() / drucke_bericht():**
  Die Backend-Trennung war eine zentrale Architektur-Voraussetzung
  fuer die Streamlit-GUI. Ohne sie haetten wir Berechnung in der
  GUI dupliziert. Mit ihr kann jede beliebige Oberflaeche dieselbe
  Logik nutzen.
- **Defensive `_zahlenfeld()`-Helper waren ein Bug:** Beim Sonntag-
  Refactoring habe ich `getattr()` mit mehreren moeglichen Feldnamen
  versucht. Aber wenn keiner der Namen matcht, bekommt man `None`.
  Lesson learned: bei stabilen Datenklassen direkt `getattr(obj, "name", None)`
  mit dem korrekten Namen ist klarer als "Schema-Drift-Defensive".

---

## Backlog (Stand 11.05.2026)

### Iteration 4 (Streamlit-GUI - ABGESCHLOSSEN)

**Erledigt**:
- [x] Fabienne: GitHub-Account aktiv, gepushed mehrfach
- [x] Fabienne: Anforderungs-Liste in `docs/anforderungen_frontend.md`
- [x] Doku-Architektur Backend/Frontend getrennt (Fabienne)
- [x] Backend-API mit `AnalyseErgebnis` stabilisiert
- [x] Streamlit-GUI mit eigenem CSS-Design (Fabienne)
- [x] AnalyseErgebnis-Aliase fuer GUI ergaenzt (7 Felder)
- [x] Live-Test mit 4 Test-Adressen erfolgreich (alle 3 Pfade gruen)
- [x] Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz funktioniert

**Optional Phase 3 (Generalprobe Mitte Juni)**:
- [ ] Negative Reserve bei >100% Ausschoepfung visuell sauberer
- [ ] Zonen-Suffix `[hoehen_und_gz]` ausblenden fuer Endanwender
- [ ] Karten-Marker eventuell kleiner
- [ ] PDF-Export (Could have, nicht Pflicht)
- [ ] Variable gGA aus Art. 46 BO Bern (verschoben)
- [ ] Subtypen FA-FD der ZoeN (verschoben)
- [ ] Schwager: stichprobenartige Verifikation BKP-Werte
      (Termin naechste Woche)

### Iteration 5 (Gemeinde-Analyse - 1 von 4 Modulen erledigt)

Detail siehe `docs/konzept_gemeinde_analyse.md`.

**Bereits umgesetzt am 30.04.2026**:
- [x] Modul `gwr.py` (GWR-API fuer bestehende Gebaeude)

**Noch zu tun (Anfang Juni 2026)**:
- [ ] Modul `parzellen_liste.py` (alle Parzellen einer Gemeinde)
- [ ] Modul `gemeinde_analyse.py` (Massen-Pipeline mit Throttling)
- [ ] Excel/CSV-Export-Funktionen
- [ ] Lokales SQLite-Caching der OEREB-Auskuenfte
- [ ] Retry-Logic bei transienten API-Fehlern
- [ ] Pilot-Test mit Oberhofen am Thunersee

### Iteration 6 (Generalprobe, Mitte Juni 2026)

- [ ] Pitch-Text auf 5 Minuten trimmen
- [ ] Live-Demo-Adressen auswaehlen
- [ ] Drei moegliche Code-Fragen vorbereiten
- [ ] Backup-Plan falls Internet/OEREB-Webservice down
- [ ] README finalisieren mit GUI-Screenshots
- [ ] Koeniz als 4. Gemeinde aufnehmen (optional)
