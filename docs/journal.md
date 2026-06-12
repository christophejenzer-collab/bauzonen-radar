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
(`71a734c`). Datenmodell und Bern-OEREB-Adapter im naechsten Commit
(`5954320`). XML-Parser erweitert um Gefahrengebiete, Baulinien,
Flaechen (`172e63c`) und vereinfachte Grundnutzungs-Form (`4bb9499`).

### Entscheidungen

- **OEREB statt eigene Geodaten**: rechtsverbindliche Auskuenfte
  ohne lokales GIS
- **Geocoding via swisstopo SearchAPI**: schnell, tolerant gegen
  Tippfehler, kein API-Key noetig
- **Datenklassen** statt Dict, weil Type-Hints und Lesbarkeit
  wichtiger sind als Mikro-Performance

### Stand am Ende des Tages

End-to-End-Pipeline lief: Adresse rein -> Parzelle + OEREB-Daten raus.

---

## 23. April 2026 (Mittwoch) - Baureglement-Modul und Potenzial-Berechnung

**Dauer**: ein Arbeitstag

### Was passiert ist

Praefix-System aufgeraeumt + oeffentliche API fuer externe Diagnose
(`66861af`). Hauptarbeit "Schritt B": Baureglement-Modul mit JSON-
Files fuer Bern und Thun (`5a59a8c`). Umlaut-sichere Dateinamen fuer
Gemeindenamen (`51516bf`). Abends "Schritt C": Potenzialberechnung
mit Warnhinweisen, auch ohne Ausnuetzungsziffer (`240b1e8`).

### Entscheidungen

- **Reglemente als JSON, nicht in Code**: ein Reglement aendert
  sich, ohne Python-Refactoring updaten zu muessen
- **Eine JSON pro Gemeinde**: skaliert besser als eine Mega-JSON
- **Schritt B vor Schritt C**: erst Daten organisieren, dann
  Berechnung darueber legen

### Stand am Ende des Tages

Drei Saeulen funktionieren: Geocoding, OEREB-Abfrage, Reglement.
Erste vorsichtige Potenzialberechnung.

---

## 24. April 2026 (Donnerstag) - Berner Systemwechsel und erste Doku-Welle

**Dauer**: ein langer Arbeitstag

### Was passiert ist

Grosse strukturelle Aenderung: Datenmodell, Reglemente und
Potenzialberechnung unterstuetzen jetzt **alle drei Berner
Bemessungssysteme** (`038ac8b`). Hintergrund: Bern hat mit dem BR
2022 die klassische Ausnuetzungsziffer abgeschafft. Also AZ (alt),
GFZo (Erhaltungsbauklasse) und Hoehen+GZ-System (neue Wohnzonen).

README aktualisiert (`615b9c0`). Fachliche Grundlagen dokumentiert
mit IVHB, BR-Vergleich Thun (`0ca4193`). Erstes Journal angelegt
(`e04fec1`). Konzept-Dokument und Projektplan bis Abgabe 17. Juni
2026 (`e54e3c2`).

Thun bekommt OEREB-Schreibweisen "Wohnen W2/W3" und `start.ps1`
(`2605976`). Bern bekommt Planungspflicht-Varianten und Zone im
oeffentlichen Interesse (`04fa292`, `27c1461`). Plus `demo.ps1`.

### Entscheidungen

- **Drei Bemessungssysteme parallel**: nicht "wir nehmen das
  modernste", sondern alle drei sauber unterstuetzt
- **AZ als alter Bezugswert behalten**: zur Plausibilitaetspruefung
- **start.ps1 / demo.ps1**: Windows-PowerShell-Helper
- **Doku als erste Klasse**: Konzept, Projektplan, Fachliche
  Grundlagen, Journal entstehen neben dem Code, nicht nach

### Stand am Ende des Tages

Tool funktioniert fuer Bern und Thun mit korrektem Bemessungs-
system. Erste Doku-Generation steht.

---

## 27. April 2026 (Montag) - Mehrsystem-Modell und Reglement-Daten konsolidiert

**Dauer**: ca. 4 Stunden

Stadt Bern erweitert um die volle Bauklassen-Hierarchie (BK_2 bis
BK_6, BK_E mit GFZo-Werten). Stadt Thun mit allen Wohnzonen und
WA-Zonen. Eine `bauklassen`-Map und eine `nutzungszonen`-Map pro
Reglement - saubere Trennung. Synonyme als separate Eintraege mit
gleichem Inhalt, kein Pointer-System.

### Stand am Ende des Tages

Reglement-Daten fuer Bern und Thun konsolidiert. Bereit fuer die
echte Schaetzungs-Implementierung.

---

## 28. April 2026 (Dienstag) - Schaetz-Berechnung, Datenqualitaet, Empfehlungs-Block

**Dauer**: ca. 6 Stunden ueber den Tag verteilt

### Erste echte Potenzialberechnung

Thunstrasse 40 berechnet GFZo=0.5 aus BO Art. 57 (`8f2c55a`). 10
Test-Adressen Regression lief gruen.

### Oberhofen integriert

Hoehen-System ohne GZ funktioniert. Bugfix in `baureglement.py` und
`potenzial.py` (`9bb3661`). Drei Gemeinden vollstaendig abgedeckt:
Bern, Thun, Oberhofen.

### Mitstudentin Fabienne dazu

Doku-Update: Fabienne als Mitstudentin ergaenzt, Oberhofen
integriert, KI-Transparenz-Hinweis hinzugefuegt (`480a80b`).

### Schaetz-Berechnung mit Datenqualitaets-Konzept

Hier kam der konzeptionelle Schluesselgedanke des Tages (`fdff32f`):
Wir koennen nicht so tun, als ob die Schaetzung im Hoehen-System
genauso belastbar ist wie eine AZ-Berechnung. Loesung: drei
Datenqualitaetsstufen klar markiert:

- **VERBINDLICH** (AZ oder GFZo): exakte Berechnung
- **GROBSCHAETZUNG** (Hoehen-System): konservative Schaetzung
- **NICHT_MOEGLICH** (Spezialregime): keine Berechnung, Empfehlung
  statt Pseudozahl

Dazu Plausibilitaetscheck gegen das alte AZ-Recht. Wenn die
Schaetzung mehr als Faktor 1.8x oder weniger als 0.7x vom alten
AZ abweicht, Warnung im Output.

### Empfehlungs-Block mit ASCII-Balken

Visuelle Lagebeurteilung in Prozent (`d7647b0`). Vier Stufen anhand
der Bauland-Reserve: HOCH, MITTEL, GERING, AUSGESCHOEPFT.

### Bauklassenplan-API Stadt Bern angebunden

Abends die grosse Architektur-Erweiterung (`227a9db`): die ArcGIS
REST-API von `map.bern.ch` liefert pro Parzelle parzellenscharfe
Werte fuer Bauweise und Gebaeudemasse. Neues Modul `bern_bkp.py`.

NEUER PFAD `Datenqualitaet.NICHT_MOEGLICH` hinzugefuegt. Drei-
Begrenzer-Logik (Geometrie / Parzelle / GZ - der kleinste gewinnt)
mit transparenter Anzeige welcher Begrenzer aktiv ist.

### Datenquellen-Evaluation Thun und geodienste.ch

Schweizweite WFS-API von `geodienste.ch` liefert nur Zonen-
Bezeichnungen, keine Bauwerte. ThunGIS gleiche Aussage. Koeniz hat
Bauklassen-System wie Bern, aber auch keine Werte in der API.

Erkenntnis: **Stadt Bern bleibt der Sonderfall** mit einer echten
Live-API fuer Bauwerte.

### Stichproben-Test mit 12 Adressen

Verifikations-Suite gebaut. 12/12 erfolgreich. Aber **3 Bug-Backlog-
Punkte** identifiziert:

1. Begrenzer-Logik bei kleinen Parzellen liefert 0 m^2
2. `Gebaeudelaenge unbeschraenkt` bricht Schaetzung ab
3. WA4 und ZPP fehlen in `thun.json`

### Stand am Ende des Tages

Iteration 3 konzeptionell abgeschlossen. Alle drei Bemessungs-
systeme funktionieren, Datenqualitaet wird ehrlich markiert, Stadt
Bern ist parzellenscharf, Empfehlungs-Block visualisiert die Lage.

---

## 29. April 2026 (Mittwoch) - Bug-Sweep und Iteration-5-Konzept

**Dauer**: ca. 4 Stunden

### Vier Fixes umgesetzt (Commit `ac97892`)

1. **Ist-Platzhalter** von 40% auf 25% gesenkt
2. **Ehrliche Anzeige** bei Ausschoepfung > 100%: echter Wert mit
   Warnung "Ist > Soll - Schaetzung versagt"
3. **`max_gebaeudelaenge_m=None`** -> `float("inf")` statt Crash
4. **Realistischere Parzellen-Form**: 1:1.5 Rechteck statt Quadrat

### Iteration-5-Konzept geschrieben

Aus User-Vision: statt Einzeladressen eine **ganze Gemeinde**
analysieren und priorisierte Excel-Liste der Verdichtungs-
Kandidaten ausgeben. Konzept-Dokument `docs/konzept_gemeinde_
analyse.md` (`e75b7a7`).

Zwei-Phasen-Ansatz: erst Massen-Screening mit GWR-API als Ist-
Quelle, dann Detail-Verifikation der Top-Treffer.

### Datenluecken thun.json geschlossen (Commit `dce697f`)

5 neue Eintraege - Slash-Synonyme fuer WA3/4/5 plus die ZPP-Zone
(NICHT_MOEGLICH-Pfad mit klarem UeO-Hinweis).

### Stresstest mit 50 Adressen

```
48/50 erfolgreich (96%)
Laufzeit: 1.7 Minuten (2 Sek/Adresse)
VERBINDLICH: 6, GROBSCHAETZUNG: 21, NICHT_MOEGLICH: 21
```

Die zwei Ausfaelle liefen einzeln nochmal angesteuert problemlos
durch - **transienter API-Fehler**, kein Bug.

### Spaeter Abend: Strategische Diskussion zu Datenschutz

Zwei Punkte hochgekommen:

**1. Unbebaute Parzellen ohne Adresse**: Drei zusaetzliche
Eintrittspunkte ins Konzept (Parzellennummer + Gemeinde, EGRID
direkt, Koordinate LV95).

**2. Eigentuemer-Daten**: Recherche zu GRUDIS public ergab vier
Probleme (Captcha, AGOV-Login seit 1.9.2025, revDSG seit 1.9.2023,
Reputationsrisiko). **Entscheidung**: Brueckenansatz. Tool greift
NICHT automatisch auf Eigentuemer-Daten zu. Direktlink zu GRUDIS
public im Output.

### Quick-API-Test: Parzellen-Suche fuer Iteration 5 verifiziert

4 Tests durchgefuehrt. Zentrale Erkenntnisse: GWR-Felder sind alle
da wie erwartet. Aggregation muss pro EGRID erfolgen, nicht pro
Strassenadresse. Plausibilitaets-Konflikt sichtbar bei Frutigen-
strasse 25 (Soll 1080 m^2 vs. Ist GWR 1520 m^2 = 141% ausgeschoepft).

**Genau dieser Konflikt ist die Existenzberechtigung von Iteration 5**.

---

## 30. April 2026 (Donnerstag) - Aufraeumen + GWR-Modul vorgebaut

**Dauer**: ca. 1.5 Stunden Aufraeumen + 3 Stunden GWR-Modul

### Aufraeum-Skript erstellt und ausgefuehrt

`aufraeumen_30_04_2026.ps1` mit 6 Schritten und ZIP-Backup. 8 Dateien
verschoben: PoC, alte Strukturbaum-Snapshots, Test-XMLs in
`docs/archiv/` bzw. `tests/fixtures/`.

Strategische Entscheidung: Test-Fixtures im Repo **behalten** mit
Whitelist-Ausnahme in `.gitignore`. Lieber jetzt 564 KB im Repo
behalten als spaeter feststellen "Mist, haetten wir gebraucht".

### Spaeter Abend: GWR-Modul vorgebaut (~3h)

**Neues Modul** `src/bauzonenradar/datenquellen/gwr.py` (~330 Zeilen):

- `GwrGebaeude`-Datenklasse
- `GwrQuelle`-Hauptklasse mit Zwei-Stufen-Workflow, Caching,
  Cache-Limit, Retry-Logic mit exponentialem Backoff,
  Throttling-Parameter
- Aggregation `geschossflaeche_pro_parzelle()`
- 3 Exception-Klassen

### Stresstest mit 50 Adressen mit GWR

| Metric | Vor GWR | Mit GWR |
|---|---|---|
| Erfolgsquote | 96% | **96%** |
| Laufzeit | 1.7 Min | **2.2 Min** (+30 Sek) |
| Funktionalitaet | Soll | **Soll + Ist + Plausibilitaet** |

**Ergebnis: GWR-Integration kostet nur 30 Sekunden mehr Laufzeit**
fuer massiven Mehrwert.

---

## 03. Mai 2026 (Sonntag) - Coding-Tag mit Fabienne und Iter-4-Start

**Dauer**: 0800-1100 Vormittag, Nachmittag Familienfest

### Fabiennes Sonntag-Vorarbeit (Samstag-Abend)

Doku-Architektur restrukturiert:
- `Anforderungen.md` -> `docs/anforderungen_backend.md`
- Neu: `docs/anforderungen_frontend.md` (54 Zeilen)
- Neu: `docs/releasenotes_backend.md` (25 Zeilen)
- Neu: `docs/releasenotes_frontend.md` (27 Zeilen)

Saubere Trennung Backend/Frontend, getrennte Releasenotes pro Bereich.

### Vormittag: Backend-Refactoring

**Neue Datenklasse `AnalyseErgebnis`** mit ~30 Feldern. Sammelt
alles was GUI oder CLI brauchen.

**Neue Funktions-Architektur**:
```
analysiere(adresse) -> AnalyseErgebnis    # reine Logik
drucke_bericht(ergebnis) -> None           # CLI-Output
main()                                     # ruft beide nacheinander
```

**Separation of Concerns**: GUI und CLI nutzen dieselbe
`analysiere()`-Funktion.

### Fabiennes Frontend parallel

`src/bauzonenradar/gui/app.py` ~370 Zeilen. Eigenes CSS (Inter-
Schrift, Schwarz/Rot-Akzent). Per Mail geschickt, noch nicht
gepushed (wartet auf Backend-Stabilitaet).

---

## 05. Mai 2026 (Dienstag) - Frontend-Test und Crash-Diagnose

**Dauer**: ca. 1 Stunde

### Crash-Diagnose

```
AttributeError: 'AnalyseErgebnis' object has no attribute 
'parzellenflaeche_m2'.
Did you mean: 'parzellen_flaeche_m2'?
```

Fabienne hat ihren Code gegen ein vermutetes Backend-Interface
geschrieben. Komplette Mapping-Tabelle an sie geschickt.

### Strategie-Entscheidung

Mit Fabienne abgesprochen: **Frontend wird angepasst**, nicht das
Backend (Backend-Datenmodell bleibt sauber).

---

## 11. Mai 2026 (Montag) - Iter-4-Abschluss

**Dauer**: ca. 3 Stunden

### Diagnose: Backend-Bug entdeckt

CLI-Test zeigt: das `PotenzialErgebnis`-Objekt hat die Daten, aber
`_zahlenfeld()`-Helper suchte nach **falschen** Feldnamen.

**Strategie-Entscheidung**: Backend wird angepasst. AnalyseErgebnis-
Klasse um 7 neue Felder erweitert (`theoretisch_zulaessig_m2`,
`ausschoepfungsgrad_prozent`, `reserve_prozent`, `zonen_betrachtet`,
`zone`, `arealbonus_anwendbar`, `bemerkungen`).

### Live-Test in der GUI mit 4 Test-Adressen

**Thunstrasse 40, 3005 Bern** (VERBINDLICH): 118 m^2 zulaessig,
50.0% Ausschoepfung, Konflikt-Box ausgeloest.

**Frutigenstrasse 25, 3604 Thun** (GROBSCHAETZUNG - das Highlight!):
GWR-Tabelle 304 m^2 x 5 Geschosse = 1520 m^2 (7 Wohnungen).
**Plausibilitaets-Konflikt-Box**: "GWR-Ist (1520 m^2) uebersteigt
den berechneten Soll-Wert (1080 m^2)".

**Kramgasse 49** (NICHT_MOEGLICH): Verweis auf Bauverwaltung,
keine Pseudo-Werte.

**Murifeldweg 8** (Edge-Case): 230.1% Ausschoepfung mit Konflikt-Box.

### Bilanz Iter-4-Abschluss

- Streamlit-GUI funktioniert vollstaendig mit echten Daten
- Alle drei Datenqualitaets-Pfade sichtbar
- Plausibilitaets-Konflikt-Box als Pruefungs-Highlight
- Backend-API stabil

---

## 12. Mai 2026 (Dienstag) - Iteration 5 komplett (~11h)

Massive Tagesarbeit, Iter 5 von 1/4 Modulen auf 4/4 + Bonus.

### Iter-5-Module fertig

**parzellen_liste.py** (180 Zeilen): rekursive Praefix-Suche fuer
swisstopo SearchAPI mit 50-Treffer-Limit. Oberhofen: 1176 Parzellen
via 161 API-Calls in 126 Sek.

**gemeinde_cache.py** (520 Zeilen): SQLite-Cache, pickle-Serialisierung,
Wiederaufnahme nach Abbruch.

**klassifikation.py** (250 Zeilen): Sieben Geschaeftslogik-Kategorien
(VERDICHTUNG, NEUGESCHAEFT, ERSATZNEUBAU, UNAUFFAELLIG, AUSGEREIZT,
AUSSCHLUSS_REGLEMENT, AUSSCHLUSS_ZU_KLEIN).

**gemeinde_analyse.py** (340 Zeilen): Haupt-Pipeline mit Throttling
0.7 Sek, Retry 3x, Progress-Logging alle 25 Parzellen, KeyboardInterrupt-
sicher.

**excel_export.py** (470 Zeilen): XLSX-Export mit 6 Sheets
(Statistik / Verdichtung / Neugeschaeft / Ersatzneubau / Ausgereizt /
Alle).

### GWR-Bug entdeckt + gefixt

Erster Lauf Oberhofen lieferte 489 NEUGESCHAEFT (41%) und 0
VERDICHTUNG - statistisch unmoeglich. Ursache:
`gwr.gebaeude_zu_adresse('Oberhofen Parz. N')` ist kein echter
Adress-String.

Loesung: neue Methode `gebaeude_zu_egrid(egrid, koordinate_lv95)`
via MapServer-identify Endpoint. Re-Run ergab:
- VERDICHTUNG: 0 -> 53
- ERSATZNEUBAU: 1 -> 40
- AUSGEREIZT: 0 -> 75
- 168 hochwertige Kandidaten identifiziert

### Bodenbedeckungs-Filter (~3h)

Neue Datenquelle `tlm3d.py` (288 Zeilen): TLM3D-Strassen-Layer +
Arealstatistik. Zwei neue Klassifikationen: AUSSCHLUSS_VERKEHR
(4 Indikatoren!) und AUSSCHLUSS_WALD_VERDACHT.

Voller Re-Run (1176 Parzellen, 41 Min): 23 False-Positives umklas-
sifiziert, 170 hochwertige Kandidaten.

### Code-Bilanz

~2300 produktive Zeilen, 9 Commits.

### Erkenntnisse

- **Konservatives Filtern ist besser als aggressives**. 23 echte
  Treffer wertvoller als 80 mit False Positives.
- **Datenqualitaet ist ein Engineering-Befund**, kein Bug.
- **GWR via EGRID ist deutlich robuster als GWR via Adresse**.
- **Visuelle Verifikation auf map.geo.admin.ch ist Teil der Pipeline**.
- **MapServer-identify als zentraler Pattern** fuer alle swisstopo-
  Layer.

---

## 20.-23. Mai 2026 - Iteration 6: Grossstadt-Tauglichkeit + Konzept-Klaerung

Mehrtaegige Session. Ziel war zunaechst, die Massen-Analyse von
Oberhofen (Dorf) auf eine ganze Stadt (Thun) zu skalieren. Am Ende
stand eine wichtigere, konzeptionelle Erkenntnis: Die geometrische
Soll-Berechnung ist im Hoehensystem nicht ohne Annahme bestimmbar -
das Tool muss als faktenbasierter Indikator gedacht werden, nicht
als exakter Soll-Rechner.

Quellen-Wahrheit: Commits 435d518, 082e542, 1327ddc, 2414788.

### GWR-tolerance-Cap-Bug (Commit 435d518)

In dichten Berner Quartieren (Buempliz, Wabern, Spiegel) fanden
sich Gebaeude nicht. Ursache: MapServer-identify mit tolerance=500
ueberschritt in dichten Gebieten den Treffer-Cap (201) der API.
Fix: tolerance 500 -> 100. Verifikation: 60/60 EFH-Parzellen
Gebaeude gefunden (vorher 3/50).

### Vier Grossstadt-Bugs (Commit 082e542)

**1. EGRID-Fallback**: ergebnis.egrid wurde nur aus parzelle.egrid
gesetzt. Bei Thun lieferte OEREB teils kein egrid -> Cache-Skip.
Fix: uebergebener egrid-Parameter als Fallback.

**2. Gemeinde-Filter**: SearchAPI macht Praefix-Matching. "Thun"
matchte auch Thundorf (TG), Thunstetten, Oberhofen. Von 50 Treffern
bei "Thun 4" waren nur 2 echtes Thun. Fix: Gemeindename im detail-
Feld exakt pruefen.

**3. MAX_API_CALLS 500 -> 3000**: Wegen vieler Fremdtreffer reichten
500 API-Calls nicht.

**4. Karten-Link**: Alte URL geo.apps.be.ch existiert nicht mehr
(Kanton Bern hat die freie Grundbuch-Direktabfrage zum 1.9.2025
abgeschafft). Ersetzt durch login-freien Kartendienst
`map.geo.admin.ch/?swisssearch=<EGRID>`.

### Reserve-%-Fix

Excel-Spalte "Reserve %" zeigte zusammenhanglose Werte (z.B. Reserve
-16 m^2 aber +40%). Ursache: reserve_prozent wurde aus interner
Modell-Schaetzung berechnet, waehrend Spalten Soll/Ist/Reserve(m^2)
die echten GWR-Daten nutzen. Fix nur im Export: Reserve% direkt aus
reserve_m2/Soll.

### Vollstaendiger Thun-Lauf: 8534 Parzellen

Nach den Fixes lief ganz Thun durch: 8974 Parzellen analysiert,
0 Fehler, ~4h30 Laufzeit. Nach Dedup 8534 eindeutige EGRID, kein
Thundorf mehr.

Klassifikation: VERDICHTUNG 890, NEUGESCHAEFT 354, ERSATZNEUBAU 1514,
UNAUFFAELLIG 1271, AUSGEREIZT 1752, AUSSCHLUSS_REGLEMENT 1824,
ZU_KLEIN 800, FEHLER 440 (~5%), VERKEHR 123, WALD_VERDACHT 6.

Grossstadt-Tauglichkeit nachgewiesen.

### Baujahr-Spalte (Commit 1327ddc)

Auf Wunsch des Architekten (Alter der Bausubstanz = Hebel-Indikator
bei Verdichtung). Baujahr steckt bereits in daten_json - kein Re-Run
noetig. Resultat Thun: 884/890 VERDICHTUNG mit Baujahr (99%), davon
540 vor 1980.

### Schwager-Verifikation: Soll-Grenzabstand

Fragenliste mit echten Thun-Zahlen verschickt: 829/1752 AUSGEREIZT
haben Flaeche <500 m^2, 55 mit Soll <10 m^2 (faktisch 0). Antwort:
Bei kleinen/aneinandergebauten Parzellen sollte der seitliche
Grenzabstand wegfallen. Ausdruecklich **"kein Generalrezept"**.
Zusatz: Fokus ab 500 m^2, Baujahr im Export erwuenscht.

### KLEINPARZELLE-Indikator (Commit 2414788)

Neue Kategorie KLEINPARZELLE fuer Parzellen 200-500 m^2: neutral,
ausserhalb der Fokus-Sheets, sichtbar im "Alle"-Sheet. Die Schwelle
(<500 m^2) ist ein **FAKTISCHER Indikator** - beruht allein auf der
amtlich vermessenen Parzellenflaeche, nicht auf geschaetzter Soll-
Berechnung. Damit gueltig auch bei Expansion auf andere Gemeinden.

Re-Klassifikation Thun: ~800 fruehere AUSGEREIZT/UNAUFFAELLIG-
Kleinparzellen jetzt sauber abgegrenzt.

### Konzeptionelle Klaerung: faktischer Indikator statt erfundenes Soll

Die wichtigste Erkenntnis dieser Iteration. Ein Versuch, die
Schwager-Geometrie umzusetzen, deckte ein zweites Problem auf: Bei
grossen Parzellen deckelt der Geometrie-Begrenzer das Soll auf feste
Werte (z.B. 1080 m^2 unabhaengig von der Parzellengroesse), weil das
Modell nur EIN Gebaeude rechnet. 343 grosse Parzellen so betroffen.

Recherche zur etablierten Methodik (ARE/GFR, Raum+, bauzonen-
kapazitaet.ch) zeigte: Die offizielle Schaetzung arbeitet mit
Ausnuetzungs-/Geschossflaechenziffern und Ausschoepfungsgraden,
nicht mit geometrischer Nachbildung. Pruefung der eigenen Reglement-
Daten ergab: Thun (BR 2022) hat KEINE gueltige AZ/GFZ mehr - System
"hoehen_und_gz". Der alte AZ-Wert 0.5 ist nur historischer Vergleichs-
wert.

Schlussfolgerung: Die zulaessige Geschossflaeche ist im Hoehensystem
ohne Annahme nicht eindeutig bestimmbar (Architekt: **"kein
Generalrezept"**). Jede geometrische Annahme kippt bei irgendeiner
Parzellenklasse. Das ist keine Schwaeche des Codes, sondern
Eigenschaft des Baurechts.

Konsequenz fuer das Konzept: Klare Trennung von (1) wahren
Gegebenheiten (GWR-Ist, Baujahr, Geschosszahl, Parzellenflaeche,
Reglement-Kennzahlen, Gruenflaechenziffer - alles Fakten) und (2)
Indikator (transparente Heuristik). Der Indikator soll kuenftig ein
Ranking aus mehreren faktischen Signalen sein.

Daher wurde der Soll-Geometrie-Fix bewusst zurueckgenommen
(`git checkout potenzial.py`) - er verbessert nur die Kruecke und
loest das Deckel-Problem nicht. KLEINPARZELLE blieb erhalten
(faktischer Indikator).

### Stand am Ende der Iteration

Committed: GWR-tolerance, Grossstadt-Tauglichkeit (4 Bugs), Reserve-%,
Baujahr-Spalte, KLEINPARZELLE. Thun + Oberhofen laufen sauber durch,
Excel mit funktionierenden Karten-Links.

**Erkenntnis des Tages**: An der richtigen Stelle innehalten und das
Konzept klaeren ist mehr wert als eine weitere Heuristik einzubauen.

---

## 31. Mai 2026 (Sonntag) - Iter-7-Start: Doku-Konsolidierung + Repo-Hygiene

**Dauer**: ca. 4 Stunden Doku + 1 Stunde Repo-Aufraeumung

Erster Teil der Pruefungs-Vorbereitung. Ziel: alle Dokumente auf
Stand 23.05. bringen und Repo gemaess Dozenten-Feedback aufraeumen.

### Doku-Update (5 Dokumente neu/aktualisiert)

- `konzept.md` - Iter 4-6 integriert, KLEINPARZELLE-Kategorie
  ergaenzt, Indikator-Konzept aufgenommen
- `struktur.md` - alle Iter-5/6-Module dokumentiert
- `fachliche_grundlagen.md` - Indikator-Erkenntnis als neuer Abschnitt
- `konzept_gemeinde_analyse.md` - Status UMGESETZT statt TEILWEISE
- `releasenotes_backend.md` - Iter-6-Block ergaenzt (Fabienne)

### Verteidigungs-Vorbereitung (2 neue Dokumente)

- `code_walkthrough_backend.md` - Sektion-fuer-Sektion-Erklaerung
  des Backends in Klartext fuer IT-Fremde
- `code_walkthrough_frontend.md` - Sektion-fuer-Sektion-Erklaerung
  der Streamlit-GUI

Plus internes Verteidigungs-Quiz mit 20 Fragen (lokal, nicht im Repo).

### Repo-Aufraeumung gemaess Dozenten-Feedback

Dozent hatte ueber Mail angesprochen, dass "Dateien die keinen Sinn
ergeben" im Repo nichts zu suchen haben. Umgesetzt:

- `historie/patches/` (7 Patch-Skripte) komplett entfernt - Git
  als Beleg der iterativen Entwicklung ist ausreichend
- `start.ps1` und `demo.ps1` entfernt - Helper-Skripte sind im Repo
  fehl am Platz; Funktionalitaet steht jetzt direkt in der README
- `docs/start_cheatsheet.md` lokal behalten ueber `.gitignore`

### README neu strukturiert

`README.md` komplett ueberarbeitet:
- DAU-freundlicher Schnellstart in 5 Schritten
- Plattform-agnostisch (Windows/Linux/Mac) statt nur PowerShell
- KI-Disclaimer am Ende
- Doku-Verknuepfungen ueber Markdown-Links

### Lessons Learned

- Dozenten-Feedback "Dateien die keinen Sinn ergeben" war
  berechtigt. Patch-Skripte gehoeren ins Git-Log, nicht ins Repo-
  Verzeichnis. Ein sauberes Repo signalisiert Reife.
- Single Source of Truth gilt auch fuer Schnellstart-Anleitungen:
  start.ps1 + README + start_cheatsheet hatten drei Versionen.
  Jetzt ausschliesslich in der README.

### Bilanz 31.05.

- 5 Doku-Dokumente auf aktuellen Stand
- 2 Code-Walkthroughs neu fuer die Verteidigung
- Repo aufgeraeumt: 9 Dateien entfernt
- README neu mit DAU-Schnellstart + KI-Disclaimer

---

## 08. Juni 2026 (Sonntag) - Iter-7-Teil-2: Demo-Konzept und Praesentation v4

**Dauer**: ca. 6 Stunden

Zweiter Teil der Pruefungs-Vorbereitung. Ziel: strukturiertes Demo-
Konzept fuer die 10-Minuten-Praesentation und Praesentation v4
erstellen.

### Adress-Verifikation lokal

Drei Kandidaten-Adressen lokal getestet:

**Loetschenenweg 1, 3608 Thun** (Investor A - Verdichtung):
- Tool findet Parzelle 2034 (643 m^2 W3)
- Reserve 345 m^2 (68%), Baujahr 1965, 2 Wohnungen
- GWR-Diskrepanz "Laengmatt 1" entdeckt (entscheiden: ignorieren)

**Ruettiweg 2, 3608 Thun** (Investor B - Neugeschaeft):
- Tool findet Parzelle 422 (Bauernhof, Baujahr 1927)
- ABER gewuenschte Parzelle 4204 (leeres Bauland) ist via Adresse
  nicht aufrufbar - leeres Bauland hat keine Hausnummer
- Demo-Trick im Drehbuch eingebaut: "Ruettiweg 2" eingeben, dann
  Excel-Wechsel zur Parzelle 4204 mit 100% Reserve

**Frutigenstrasse 74, 3608 Thun** (Investor C - Ersatzneubau):
- Tool findet Parzelle 3708 exakt wie erwartet
- 1465 m^2 WA4, Reserve 1233 m^2 (78%), Baujahr 1900
- PLUS 4 zusaetzliche Restriktionen: Archaeologisches Schutzgebiet,
  Strassenraumzone, Naturgefahr Grundwasseraufstoss, Baulinie
  Frutigenstrasse - Story-Bonus

### Demo-Konzept "Bauzonen-Radar AG"

Wir treten als Berater-Duo auf, nicht als Studenten. Drei Investoren-
Stories aus Thun-Goldiwil:

1. **Verdichtung** - Frau Meier, EFH 1965 am Loetschenenweg 1
2. **Neugeschaeft** - Herr Steiner, Bauland am Ruettiweg
   (Parz 4204, mit Excel-Wechsel-Trick)
3. **Ersatzneubau** - Herr Berger, 1900er-Haus an der
   Frutigenstrasse 74 (mit 4 Restriktionen als Bonus)

Pro Investor ca. 1:30 Min, total Demo 5 Min, Rest fuer Slides.

### Praesentation v4 (docs/20260615_bauzonen_radar.pptx)

Auf Basis von Fabiennes v2 erstellt:

- 14 Slides total (vorher 10)
- Slide 8 neu: Live-Demo Setup mit 3 Investoren-Karten in
  3-Spalten-Layout, Foto-Platzhalter eingebaut
- Slides 8a/b/c neu und VERSTECKT: Backup-Screenshots fuer Notfall
- Slide 8d neu und sichtbar: Excel-Lookahead mit 4 Zahlen
  (8534 Parzellen, 890 / 354 / 196 Kandidaten)
- Slide 9 erweitert um zwei Punkte:
  - 05: Tool als Indikator, nicht als Architekt (Iter-6-Erkenntnis)
  - 06: KI als Werkzeug, transparent eingesetzt

### Backup-Strategien fuer Live-Demo

Drei Krisen-Szenarien geplant und dokumentiert:

- **Internet/API-Timeout** -> Wechsel zu versteckten Slides 8a/b/c.
  "Ah, das Netz ist heute langsam - hier die vorab gespeicherte
  Analyse aus dem SQLite-Cache." (Bug zu Feature)
- **Streamlit faengt nicht an** -> CLI-Modus als Fallback,
  demonstriert Separation of Concerns
- **Daten anders als erwartet** -> ehrlich kommentieren,
  Datenqualitaets-Konzept als Erklaerung nutzen

### Email-Draft an Fabienne

Praesentation v4 als PPTX + strukturierte Email mit Begleittext,
5 konkreten Fragen und klarem Plan fuer den 12.06. an Fabienne
verschickt zur Pruefung.

### Iter-7-Fazit (Stand 08.06.)

Die siebte Iteration war keine Code-Iteration, sondern eine
**Praesentations- und Repo-Iteration**. Drei Aspekte:

1. **Doku-Konsolidierung** - alle Dokumente auf Stand 23.05.,
   neue Code-Walkthroughs
2. **Repo-Hygiene** - Dozenten-Feedback umgesetzt: 9 Dateien
   entfernt, README neu strukturiert
3. **Demo-Konzept** - strukturierte 3-Investoren-Story mit Backup-
   Plaenen; Praesentation v4 (14 Slides, 3 versteckt) committed

Iter-6-Erkenntnis bestaetigt durch Demo-Vorbereitung: Die gewaehlten
Test-Adressen zeigen alle drei verschiedene Datenqualitaets-Stufen
UND drei verschiedene Klassifikations-Kategorien. Genau wofuer das
Tool gebaut wurde - ehrliche Indikation mit klar markierter
Unsicherheit.

### Geplante Schritte bis 17.06.

```
12.06. Sonntag:  Generalprobe mit Fabienne
                 Fotos einbauen + Live-Probelauf mit Stoppuhr
                 Backup-Plaene durchspielen

15.06. 12:00:    Push-Deadline einhalten

16.06.:          Technik-Check Laptop/Beamer/HDMI

17.06. 10:00:    Praesentation in Raum o408
                 10 Minuten strikt
```

---

## Verschiedene Beobachtungen waehrend der Entwicklung

- **OEREB-Webservice** antwortet meist in unter 5 Sekunden, ab und
  zu laengere Wartezeiten. Bei 50 Aufrufen kommen vereinzelt
  transiente Fehler vor (siehe 29.04.).
- **swisstopo SearchAPI** ist sehr schnell und tolerant gegenueber
  Tippfehlern in Adressen.
- **Iteratives Vorgehen mit Real-Tests** deckt Schwachstellen auf,
  die in der Theorie nicht sichtbar sind:
  - Florastrasse-Test fuehrte direkt zur Schaetz-Berechnung
  - Thunstrasse 40 + Florastrasse 5 zusammen fuehrten zum
    Empfehlungs-Block (visuell statt rein numerisch)
  - Murifeldweg 8 zeigte den Begrenzer-Logik-Bug bei kleinen
    Parzellen
  - Effingerstrasse 35 zeigte den `unbeschraenkt`-Bug
  - Buempliz/Wabern-Tests zeigten den GWR-tolerance-Bug
  - Thun-Massenanalyse zeigte vier Grossstadt-Bugs auf einmal
- **Information Design ist genauso wichtig wie korrekte Berechnung.**
  Ein Architekt liest in einer Sekunde den Balken, nicht in zehn
  Sekunden die Zahl. Plausibilitaets-Hinweise und Warnungen sind
  Teil der Berechnung, nicht Beiwerk.
- **Drei Tier von Datenquellen** im Berner Raum:
  1. OEREB (alle Gemeinden) - Zonen-Code, bereits implementiert
  2. Spezialisierte Stadt-API (nur map.bern.ch BKP) -
     parzellenscharfe Geometrie, implementiert
  3. geodienste.ch (schweizweit) - liefert nur was OEREB schon
     liefert, KEIN Mehrwert
- **Stadt Bern ist der Sonderfall.** Andere BE-Gemeinden brauchen
  weiterhin JSON-Erfassung pro Gemeinde. Koeniz hat ein Bauklassen-
  System wie Bern und ist als naechster Kandidat im Backlog.
- **Separation of Concerns durch analysiere() / drucke_bericht():**
  Die Backend-Trennung war eine zentrale Architektur-Voraussetzung
  fuer die Streamlit-GUI. Mit ihr kann jede beliebige Oberflaeche
  dieselbe Logik nutzen.
- **Defensive `_zahlenfeld()`-Helper waren ein Bug:** Beim Sonntag-
  Refactoring `getattr()` mit mehreren moeglichen Feldnamen
  versucht. Wenn keiner matcht, kommt `None`. Lesson learned: bei
  stabilen Datenklassen direkt `getattr(obj, "name", None)` mit
  dem korrekten Namen ist klarer als "Schema-Drift-Defensive".
- **MapServer-identify als zentraler Pattern** fuer alle swisstopo-
  Layer (GWR, TLM3D-Strassen, Arealstatistik). Einheitliche
  HTTP-Logik in `_MapServerIdentifyBasis`.
- **GWR via EGRID ist deutlich robuster als GWR via Adresse.** Bei
  Massen-Analyse gibt es kein echtes Adress-Label, nur Parzellen-
  Nummern. EGRID + Koordinate ist der richtige Eintrittspunkt.
- **Konservatives Filtern ist besser als aggressives.**
  AUSSCHLUSS_VERKEHR verlangt 4 Indikatoren gleichzeitig (TLM +
  Areal + Flaeche + Geb=0). 23 echte Treffer sind wertvoller als
  80 mit False Positives.
- **Datenqualitaet ist ein Engineering-Befund**, kein Bug. Strassen
  mit Bauzonen-Eintrag im Kataster sind ein OEREB-Datenproblem,
  nicht unseres. Tool dokumentiert die Limitation transparent.
- **Faktischer Indikator statt erfundenes Soll** (Iter-6-Erkenntnis):
  Im Hoehensystem ist die zulaessige Geschossflaeche ohne Annahme
  nicht eindeutig bestimmbar. Das Tool zeigt eine konservative
  Grobschaetzung und kommuniziert die Unsicherheit ehrlich -
  Architekten-verifiziert: "kein Generalrezept".

---

## Backlog (Stand 08.06.2026)

### Iteration 4 (Streamlit-GUI - ABGESCHLOSSEN 11.05.)

- [x] Fabienne: GitHub-Account aktiv, gepushed mehrfach
- [x] Doku-Architektur Backend/Frontend getrennt
- [x] Backend-API mit `AnalyseErgebnis` stabilisiert
- [x] Streamlit-GUI mit eigenem CSS-Design (Fabienne)
- [x] AnalyseErgebnis-Aliase fuer GUI ergaenzt (7 Felder)
- [x] Live-Test mit 4 Test-Adressen erfolgreich (alle 3 Pfade gruen)
- [x] Plausibilitaets-Konflikt-Box bei GWR-Diskrepanz funktioniert

### Iteration 5 (Gemeinde-Analyse - ABGESCHLOSSEN 12.05.)

- [x] Modul `gwr.py` (GWR-API)
- [x] Modul `parzellen_liste.py` (Praefix-Baum-Suche)
- [x] Modul `gemeinde_analyse.py` (Massen-Pipeline)
- [x] Modul `gemeinde_cache.py` (SQLite-Caching)
- [x] Modul `klassifikation.py` (7 Kategorien)
- [x] Modul `excel_export.py` (6 Sheets)
- [x] Modul `tlm3d.py` (Bodenbedeckungs-Filter, BONUS)
- [x] Retry-Logic bei transienten API-Fehlern
- [x] Pilot-Test mit Oberhofen (1176 Parzellen)

### Iteration 6 (Grossstadt + Konzept - ABGESCHLOSSEN 23.05.)

- [x] GWR-tolerance-Cap-Bug gefixt
- [x] Vier Grossstadt-Bugs gefixt
- [x] Reserve-% GWR-konsistent
- [x] Baujahr-Spalte im Excel
- [x] KLEINPARZELLE als faktischer Indikator
- [x] Vollstaendiger Thun-Lauf: 8534 Parzellen, 0 Fehler
- [x] Konzept-Klaerung: Soll als Indikator
- [x] Architekten-Verifikation der Indikator-Logik

### Iteration 7 (Pruefungs-Vorbereitung - IN ARBEIT bis 17.06.)

**Erledigt 31.05.**:
- [x] Doku-Update auf Stand 23.05. (5 Dokumente)
- [x] Code-Walkthroughs Backend + Frontend
- [x] Repo-Aufraeumung gemaess Dozenten-Feedback
- [x] README mit DAU-Schnellstart + KI-Disclaimer

**Erledigt 08.06.**:
- [x] Demo-Konzept "Bauzonen-Radar AG"
- [x] Drei Adressen lokal verifiziert
- [x] Praesentation v4 mit 14 Slides committed
- [x] Email-Draft an Fabienne
- [x] Journal + Struktur auf Iter-7-Stand

**Noch zu tun**:
- [ ] 12.06.: Generalprobe mit Fabienne
- [ ] 12.06.: Fotos in Slide 8 einbauen
- [ ] 12.06.: Live-Probelauf mit Stoppuhr
- [ ] 12.06.: Edge-Case-Tests + Backup-Plaene durchspielen
- [ ] 15.06. 12:00: Push-Deadline
- [ ] 16.06.: Technik-Check
- [ ] 17.06. 10:00: Praesentation in Raum o408

### Iteration 8 (Nach der Pruefung - falls Projekt weitergefuehrt)

- [ ] Direkter EGRID-Input im Streamlit-Frontend
- [ ] pytest-Unit-Tests fuer Drei-Begrenzer-Logik
- [ ] Result-Pattern statt Optional[float] = None
- [ ] Polygon-Intersection statt 1:1.5-Rechteck-Annahme
- [ ] Indikator-Konzept auf rein faktischen Signalen
- [ ] Koeniz als 4. Gemeinde
- [ ] PDF-Export der Einzelanalyse (Kundendossier)
- [ ] Ausweitung auf weitere Kantone (z.B. Zuerich)
