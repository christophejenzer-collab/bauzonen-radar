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

---

## Backlog fuer Iteration 4 und 5

### Iteration 4 (Streamlit-GUI mit Fabienne, Mai 2026)

- [ ] Fabienne: GitHub-Username fuer Collaborator-Einladung
- [ ] Fabienne: erste Anforderungs-Liste in `docs/anforderungen.md`
- [ ] Streamlit-GUI mit visueller Datenqualitaets-Ampel
      (gruen / orange / grau)
- [ ] Empfehlungs-Block als grafische Progress-Bar statt ASCII
- [ ] PDF-Export fuer Kundendossier
- [ ] Variable gGA aus Art. 46 BO Bern in Code umsetzen
- [ ] Subtypen FA-FD der ZoeN aus OEREB klaeren
- [ ] Schwager: stichprobenartige Verifikation BKP-Werte

### Iteration 5 (Gemeinde-Analyse, Anfang Juni 2026)

Detail siehe `docs/konzept_gemeinde_analyse.md`.

- [ ] Modul `gwr.py` (GWR-API fuer bestehende Gebaeude)
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
