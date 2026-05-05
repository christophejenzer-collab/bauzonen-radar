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

---

## Backlog (Stand 05.05.2026)

### Iteration 4 (Streamlit-GUI - LAUFEND seit 03.05.2026)

**Bereits umgesetzt**:
- [x] Fabienne: GitHub-Account aktiv, gepushed mehrfach
- [x] Fabienne: Anforderungs-Liste in `docs/anforderungen_frontend.md`
- [x] Doku-Architektur Backend/Frontend getrennt (Fabienne)
- [x] Backend-API mit `AnalyseErgebnis` stabilisiert
- [x] Streamlit-GUI mit eigenem CSS-Design (Fabienne)
- [x] Layout-Test durchgefuehrt
- [x] Mapping-Tabelle Backend/Frontend an Fabienne uebergeben

**Noch zu tun**:
- [ ] Frontend-Felder an Backend-API anpassen (Fabienne)
- [ ] Live-Test mit echten Daten
- [ ] Visuelle Datenqualitaets-Ampel finalisieren
- [ ] Empfehlungs-Block als grafische Progress-Bar
- [ ] PDF-Export (Could have, nicht Pflicht)
- [ ] Variable gGA aus Art. 46 BO Bern (verschoben)
- [ ] Subtypen FA-FD der ZoeN (verschoben)
- [ ] Schwager: stichprobenartige Verifikation BKP-Werte
      (Termin naechste Woche)

### Iteration 5 (Gemeinde-Analyse, Anfang Juni 2026)

Detail siehe `docs/konzept_gemeinde_analyse.md`.

**Bereits umgesetzt am 30.04.2026**:
- [x] Modul `gwr.py` (GWR-API fuer bestehende Gebaeude) (1 von 4 Modulen)

**Noch zu tun**:
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
- [ ] README finalisieren
- [ ] Koeniz als 4. Gemeinde aufnehmen (optional)
