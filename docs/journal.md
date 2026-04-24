# Projekt-Journal: Bauzonen-Radar

Fortlaufendes Entwicklungstagebuch. Neue Einträge **oben** anfügen, damit der aktuellste Stand zuerst sichtbar ist.

Format pro Session:
- Datum und ungefähre Dauer
- Was gemacht wurde (stichwortartig)
- Technische Änderungen (Code, Daten, Doku)
- Git-Commits mit Hashes
- Offene Punkte / nächste Schritte

---

## 24. April 2026 (Abend, ~3 Stunden)

- Test mit Kramgasse 1, Bern: Bug entdeckt — Berner Altstadt verwendet Spezialnamen statt numerischer Bauklassen
- Fix: bern.json um vier Altstadt-Bereiche erweitert (Untere/Obere Altstadt, Innere/Aeussere Neustadt)
- Fix in beiden Blöcken (bauklassen und nutzungszonen), weil OEREB beide Felder mit gleichem Namen befüllt
- Erkenntnis: Praxistests in verschiedenen Stadtteilen sind unverzichtbar

### Kontext
Nach Recherche zum Berner Baurecht (Systemwechsel AZ → GFZo, Thun-Spezialfall BR 2022): komplette Umstellung des Datenmodells auf Mehrsystem-Unterstützung.

### Geleistet

**Etappe 1 — Datenmodell erweitern**
- `BemessungsSystem`-Enum neu eingeführt (`AZ`, `GFZo`, `hoehen_und_gz`, `dualitaet`, `unbekannt`)
- `Bauparameter`-Klasse erweitert um GFZo, Fassadenhöhe, Grünflächenziffer, Rechtsgrundlage, Gültigkeits-Datum
- Neue Methoden: `ist_berechenbar`, `hauptkennzahl()` mit Priorität GFZo → AZ
- `Baureglement`-Klasse kriegt `system_default`-Feld
- `zusammenfassung()` zeigt System in eckigen Klammern

**Etappe 2 — JSONs neu aufsetzen**
- `thun.json` auf BR 2022 umgestellt, `system_default: "hoehen_und_gz"`
- Historische AZ-Werte (W2: 0.5, W3: 0.7) als `ausnuetzungsziffer_historisch` erhalten
- Thun W2/W3 mit 6 m grossem Grenzabstand aus Recherche
- `bern.json` mit `system_default: "AZ"` (Stadt Bern noch nicht umgestellt)
- Bauklasse E explizit auf `hoehen_und_gz` (Erhaltungsregime)
- Pro Zone `rechtsgrundlage`, `gueltig_ab`, `hinweise` ergänzt

**Etappe 3 — Potenzialberechnung anpassen**
- `PotenzialBerechner` mit drei Berechnungspfaden: AZ/GFZo, Höhen+GZ, nichts
- `PotenzialErgebnis` um `verwendetes_system` und `verwendete_kennzahl` erweitert
- Bei `hoehen_und_gz`: qualitative Ausgabe von Höhen, Grenzabständen, GZ
- Bei Dualitäts-System: explizite Warnung über doppelte Prüfung
- Warnhinweise (Überlagerungen, Naturgefahren, Baulinien) greifen in allen Pfaden

**Dokumentation**
- README um Abschnitt "Der Systemwechsel im Berner Baurecht" erweitert
- Funktionsumfang, Datenflussdiagramm, Entwurfsprinzipien aktualisiert
- Beispielausgabe mit neuem `[hoehen_und_gz]`-Format
- Minimalziel-Liste: 8 erledigt, 3 offen
- Neu: `docs/fachliche_grundlagen.md` mit 8 Abschnitten, Quellenverzeichnis
- IVHB, BMBV, BR 2002 vs. BR 2022, Stand Stadt Bern, Konsequenzen für Datenmodell

**Infrastruktur**
- `start.ps1` aus Unterordner in Projekt-Root verschoben (funktioniert endlich)

### Getestete Adressen
- Thunstrasse 40, 3005 Bern → Bauklasse E `[hoehen_und_gz]`, saubere Fehlermeldung
- Rathausplatz 1, 3600 Thun → Bestandeszone + Uferzone, beide `[hoehen_und_gz]`, mit OEREB-Warnhinweisen

### Git
- `038ac8b` Systemwechsel AZ/GFZo/Hoehen+GZ: Datenmodell, Reglemente und Potenzialberechnung
- `615b9c0` README: Dokumentiere den Berner Systemwechsel
- `0ca4193` Fachliche Grundlagen dokumentiert

### Offene Punkte
- [ ] Konkrete Kennzahlen einpflegen (AZ/GFZo pro Zone/Bauklasse) → wartet auf Schwager
- [ ] Einfache GUI (Streamlit oder guizero)
- [ ] Rangliste mehrerer Adressen nach Potenzial
- [ ] Stadt Bern: Umstellungsstand auf GFZo verifizieren

---

## 23. April 2026 (Abend, ~4 Stunden)

### Kontext
Erstmaliger kompletter Durchstich der Pipeline von Adresse bis Potenzialanalyse. Parser auf Profi-Niveau bringen, Baureglement-Modul bauen, Potenzialberechnung implementieren.

### Geleistet

**Parser-Ausbau**
- OEREB-XML für Thun analysiert (`extract_thun.xml`, 354 KB)
- Fünf SubCode-Kategorien erkannt: Grundnutzung, Überlagerung, Gefahrengebiete, FlaecheAndere, Linie
- `modelle.py` komplett neu geschrieben: Duplikate entfernt, sechs Kategorien abgedeckt
- Kurzbericht aufgeräumt mit Helper-Methoden `_block_einfach` und `_block_mit_flaeche`
- Land-Dialekt (Köniz, Thun) und Stadt-Dialekt (Bern) beide robust

**Baureglement-Modul**
- `baureglement.py` neu erstellt: `Baureglement` und `Bauparameter`-Klassen
- Drei Matching-Strategien: exakt, Suchtext in Schlüssel, Schlüssel in Suchtext
- Unterstützung für "bauklassen"- und "kombiniert"-Struktur
- Umlaut-sichere Dateinamen (Köniz → `koeniz.json`)

**Potenzialberechnung**
- `analyse/potenzial.py` mit `PotenzialBerechner` und `PotenzialErgebnis`
- Status-Enum: HOCH, MITTEL, GERING, AUSGESCHOEPFT, NICHT_BERECHENBAR
- Automatische Warnhinweise bei OEREB-Einschränkungen
- Ist-Bebauung als Platzhalter (40% der Parzelle, später aus swissBUILDINGS3D)

**CLI-Hauptschnittstelle**
- `analyse_adresse.py` als Wrapper: ein Aufruf, komplette Pipeline
- Beispiele: Kramgasse 49 (Bern), Thunstrasse 40 (Bern), Dorfstrasse 10 (Spiegel), Rathausplatz 1 (Thun)

**Basis-JSONs**
- `bern.json` mit Bauklassen A-E, Nutzungszonen inkl. Altstadtperimeter
- `thun.json` mit vier Zonen aus OEREB-Tests (Bestandeszone, Uferzone, WA5, Zone mit ÜO)

**Repo-Aufräumen**
- `WORK SHEET JenzC.txt` aus Git entfernt (lokal erhalten)
- Drei XML-Dateien aus Git entfernt
- `.gitignore` erweitert: `**/*.xml`, `extract_*.xml`, `WORK SHEET*.txt`, `persoenlich/`
- Kosmetik-Fix: einfaches Präfix bei Naturgefahren (kein `- !` mehr)
- Öffentliche API in `bern.py`: `geocode()`, `getegrid()`, `get_extract_xml()`

**Dokumentation**
- README auf professionelle Anleitung umgeschrieben (268 neue Zeilen, 57 ersetzt)
- Inhaltsverzeichnis, Datenflussdiagramm, Entwurfsprinzipien, Beispielausgabe
- Minimalziel-Checkliste mit `[x]`-Haken

### Getestete Adressen (4 Gemeinden)
- Kramgasse 49, Bern → Altstadt-Komplexfall (UNESCO)
- Thunstrasse 40, Bern → Stadt-Dialekt, Erhaltungsklasse
- Dorfstrasse 10, Spiegel → Land-Dialekt, kein Reglement
- Rathausplatz 1, Thun → Vollausstattung mit 13 OEREB-Einträgen

### Git (Auszug)
- `66861af` Kosmetik: einfaches Präfix im Kurzbericht, öffentliche API für Diagnose
- `5a59a8c` Schritt B: Baureglement-Modul, JSON-Reglemente, Repo aufgeräumt
- `051516bf` Schritt C: Potenzialberechnung und Hauptskript
- `240b1e8` Potenzialberechnung mit Warnhinweisen auch ohne AZ

### Gelernt
- `git add .` ist relativ zum aktuellen Ordner — für ganze Repos `git add -A` oder aus Root
- Venv-Aktivierung ist pro PowerShell-Session nötig (`(.venv)` als Indikator)
- `git rm --cached` entfernt aus Tracking, behält lokal
- Execution Policy unter Windows: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 22. April 2026 (Abend, ~3 Stunden)

### Kontext
Projekt-Gründung. Erste Idee-Entwicklung, Git-Setup, Proof-of-Concept für OEREB-Zugriff.

### Geleistet

**Projekt-Setup**
- Projekt-Repository auf GitHub angelegt (privat): `bauzonen-radar`
- Lokales Arbeitsverzeichnis `C:\Tools\bauzonen-radar\`
- Python-venv mit `requests`, `owslib`, `geopandas`, `shapely`, `pyproj`, `folium`, `guizero`
- Grundstruktur: `src/bauzonenradar/`, `daten/`, `tests/`, `docs/`

**Konzeption**
- Projekt-Idee: Bauzonen-Radar für ungenutztes Bebauungspotenzial
- Fokus-Entscheid: Kanton Bern, Städte Bern und Thun
- Philosophie: Tool als Arbeitsmittel, nicht als Verkaufsprodukt
- Fünf Pitches erstellt: Schwager (Architekt), Investorin (Freundin), Mitstudentin, Dozent, Follow-up

**Erster Code-Durchstich**
- `modelle.py` v1 mit `Parzelle`, `Restriction`, `Lawstatus`
- `bern.py` mit kompletter Pipeline Adresse → XML → Parzelle
- `xml_speichern.py` als Diagnose-Skript
- Geocoding via swisstopo SearchAPI
- OEREB-Zugriff via offiziellem Webservice `oereb2.apps.be.ch`

**Dokumentation**
- Erste README mit Projektbeschreibung und Installation
- `.gitignore` für Python-Projekte

### Getestete Adressen
- Kramgasse 49, Bern → Proof-of-Concept erfolgreich

### Git
- Initial commit + mehrere iterative Commits zur Pipeline-Entwicklung

---

## Vorlage für neue Einträge

Kopiere diesen Block nach oben und fülle ihn aus:

```markdown
## [Datum] ([Tageszeit], ~[Dauer])

### Kontext
[Warum diese Session, was war der Anlass]

### Geleistet
[Stichwortartig, gern in Unterkategorien wie "Code", "Daten", "Doku"]

### Getestete Adressen
- [Falls neue Gemeinden oder Adressen getestet wurden]

### Git
- `[Hash]` [Commit-Nachricht]

### Offene Punkte
- [ ] [Was noch ansteht]

### Gelernt
[Falls etwas Neues in Python, Git, oder Fach gelernt]
```

---

## Offene Punkte insgesamt (Stand 24. April 2026)

### Hohe Priorität
- [ ] Konkrete AZ-/GFZo-Werte für Stadt Bern einpflegen (via Schwager)
- [ ] Gebäudehöhen, Grünflächenziffer für Thun W2/W3/W4 einpflegen
- [ ] Stadt-Bern-Umstellungsstand auf GFZo verifizieren

### Mittlere Priorität
- [ ] Rangliste mehrerer Adressen nach Reserve-Potenzial
- [ ] Einfache GUI (Streamlit favorisiert)
- [ ] Dozent als GitHub-Collaborator hinzufügen (GitHub-Username nötig)
- [ ] Mitstudentin ansprechen (WhatsApp-Pitch bereit)

### Längerfristig
- [ ] Integration swissBUILDINGS3D für echte Ist-Bebauung
- [ ] Erweiterung Kanton Zürich (Validierung Kanton-Abstraktion)
- [ ] PDF-Export für Kundendossiers
- [ ] Kartenvisualisierung mit folium
- [ ] Weitere Gemeinden: Köniz, Steffisburg, Münsingen

### Kleinere Baustellen
- [ ] README-Platzhalter `[Name Teampartner:in]` ausfüllen
- [ ] README-Platzhalter `[E-Mail-Adresse einfügen]` ausfüllen
- [ ] Unit-Tests schreiben (Ordner `tests/` ist leer)
