# Konzept: Bauzonen-Radar

Pflichtdokument zum Python-Abschlussprojekt.
Stand: 23. Mai 2026.

## Projektidee

Architekten, Bau-Investoren und private Grundstueckeigentuemer wollen
oft schnell wissen: *Was darf ich auf dieser Parzelle bauen? Wie viel
Reserve ist noch da?* Bauzonen-Radar beantwortet das automatisiert -
aus offiziellen Quellen, mit ehrlicher Datenqualitaets-Kennzeichnung.

Das Tool funktioniert in zwei Modi:
- **Einzelfall**: Adresse rein, strukturierter Bericht raus (CLI + GUI).
- **Massen-Analyse**: Eine ganze Gemeinde wird in einem Durchgang
  analysiert und als priorisierte Excel-Liste ausgegeben.

## Problem

Das Schweizer Baurecht ist hochkomplex:

- Drei Bemessungssysteme parallel im Einsatz (AZ, GFZo, Hoehen+GZ)
- Gemeindespezifische Baureglemente, oft im Uebergang
- Kantonale Unterschiede in den Vermessungsdaten
- Spezialregimes fuer Altstaedte, Schutzgebiete, Zonen mit
  Planungspflicht
- Plausibilitaets-Konflikte zwischen rechtlich Zulaessigem und
  tatsaechlich Gebautem (Bestandsschutz)

Wer eine Parzelle pruefen will, muss heute manuell durch OEREB-Auszug,
Baureglement, Bauklassenplan, Gebaeuderegister - mehrere Tage Arbeit
pro Parzelle. Bei der Frage "welche Parzelle einer Gemeinde lohnt sich
ueberhaupt fuer eine Detailpruefung?" wird das voellig unpraktikabel.

## Loesung

Bauzonen-Radar automatisiert die Recherche und liefert pro Parzelle:

1. Adresse oder Parzelle eingeben (z.B. "Frutigenstrasse 25, 3604 Thun")
2. Tool holt sich Parzellen- und Zonen-Daten aus dem offiziellen
   OEREB-Webservice des Kantons Bern
3. Tool laedt das passende Gemeinde-Baureglement
4. Bei Stadt Bern: parzellenscharfe Werte aus dem Bauklassenplan (BKP)
5. Tool ruft GWR-API ab und zeigt die effektive Bestands-Bebauung
6. Tool rechnet das theoretische Bebauungspotenzial aus und
   markiert die Datenqualitaet klar
7. Ausgabe: Strukturierter Bericht mit Empfehlungs-Block,
   visuellem Balken und verbaler Lagebeurteilung

Bei der Massen-Analyse laufen die Schritte 2-6 fuer alle Parzellen
einer Gemeinde automatisiert durch (Throttling, Caching, Retry), und
die Resultate werden als Excel mit Klassifikation, Karten-Link und
Baujahr exportiert.

## Drei Bemessungssysteme

Das Schweizer Baurecht kennt drei parallel gueltige Bemessungssysteme.
Das Tool unterstuetzt alle drei:

- **AZ** (klassische Ausnuetzungsziffer): AZ x Parzellenflaeche =
  maximale Geschossflaeche. Wird zunehmend abgeloest, aber noch in
  vielen Gemeinden gueltig.
- **GFZo** (Geschossflaechenziffer oberirdisch, IVHB-konform):
  modernes flaechenbezogenes Mass, ueberirdische Geschossflaeche pro
  Parzelle. Stadt Bern nutzt das im Bauklassenplan.
- **Hoehen + GZ**: Dichte wird ueber Gebaeudehoehe, Geschosszahl,
  Grenzabstaende und (optional) Gruenflaechenziffer gesteuert. Kein
  flaechenbezogenes Limit. Verbreitet in neueren Reglementen wie
  Thun BR 2022 oder Oberhofen.

## Datenqualitaet als zentrales Konzept

Eine Besonderheit des Tools: Es unterscheidet drei klar getrennte
Qualitaetsstufen seiner Aussagen.

### VERBINDLICH

AZ oder GFZo vorhanden, exakte Berechnung moeglich.
Beispiel: Stadt Bern Bauklasse E (GFZo 0.5) -> 118 m^2 zulaessig
fuer eine 237 m^2 Parzelle.

### GROBSCHAETZUNG

Hoehen-System ohne flaechenbezogene Kennzahl. Eine konservative
Schaetzung via Drei-Begrenzer-Logik (Geometrie / Parzelle / GZ -
kleinster gewinnt). Das Resultat wird im Output explizit als
Schaetzung markiert; alle Annahmen werden offengelegt.

Konzeptionelle Anmerkung (Iter-6-Erkenntnis): Im Hoehensystem gibt
das Reglement im Einzelfall keine eindeutige zulaessige Geschoss-
flaeche her - das ist nicht eine Schwaeche des Codes, sondern
Eigenschaft des Baurechts ("kein Generalrezept", Architekten-
Verifikation Mai 2026). Die Grobschaetzung ist eine Heuristik mit
bekannten Grenzen (Kollaps bei sehr kleinen, Deckel bei sehr grossen
Parzellen). Das Tool kommuniziert das ehrlich durch die explizite
Status-Kennzeichnung und die GWR-Plausibilitaets-Konflikt-Box.

### NICHT_MOEGLICH

Keine Werte verfuegbar (z.B. Zone noch nicht erfasst, Spezialregime
wie Zone mit Planungspflicht). Das Tool liefert dann keine Pseudo-
zahlen, sondern verweist auf die zustaendige Bauverwaltung.

## Bauklassenplan Stadt Bern (BKP-API)

Stadt Bern bietet als einzige BE-Gemeinde eine echte Live-API fuer
parzellenscharfe Bauwerte: die ArcGIS REST-API des Bauklassenplans
(`map.bern.ch`). Das Modul `bern_bkp.py` ruft pro Parzelle:

- Layer 88 (Bauweise): offen / geschlossen / Reihen / verdichtet
- Layer 95 (Grundzonen): Bauklasse 2-6, Bauklasse E, ZoeN, Altstadt

Diese parzellenscharfen Werte ergaenzen das Baureglement um die
konkrete Geometrie (max. Gebaeudelaenge/-tiefe), die im Reglement
nur abstrakt steht. Andere BE-Gemeinden brauchen weiterhin manuelle
JSON-Erfassung pro Gemeinde - die Stadt-Bern-API ist der Sonderfall.

## GWR-Integration und Plausibilitaets-Konflikt

Das Tool ruft das Eidgenoessische Gebaeude- und Wohnungsregister
(GWR) ab und zeigt die effektive Bestands-Bebauung an. Der Vergleich
zwischen rechtlich Zulaessigem (Soll) und real Gebautem (Ist) ist
das **zentrale Pruefungs-Highlight** des Tools.

**Konkretes Beispiel** (Frutigenstrasse 25, Thun):

```
Soll (Schaetzung):  1080 m^2 (Hoehen+GZ, konservativ)
Ist  (GWR):         1520 m^2 (304 m^2 x 5 Geschosse, 7 Wohnungen)
```

Die Schaetzung sagt: rechtlich waere konservativ ca. 1080 m^2
zulaessig. Die Realitaet sagt: es stehen 1520 m^2 - das Gebaeude ist
hoeher/breiter gebaut, als die konservative Schaetzung annimmt.
Klassischer Bestandsschutz-Fall. Die Plausibilitaets-Konflikt-Box in
der GUI macht das sofort sichtbar.

**Diese Konflikt-Visualisierung ist der Indikator des Tools.** Sie
zeigt dem Anwender ohne falsche Praezision, welche Parzellen
Aufmerksamkeit verdienen. In der Massen-Analyse uebernehmen die
Klassifikations-Kategorien (VERDICHTUNG, ERSATZNEUBAU etc.) dieselbe
Rolle: sie ranken Parzellen nach Hinweis-Staerke, nicht nach
vermeintlich exaktem Soll.

## Massen-Analyse (Iteration 5 + 6)

Eine ganze Gemeinde wird in einem Durchgang analysiert und als
priorisierte Excel-Liste ausgegeben.

**Pipeline**: Parzellen-Liste (rekursiver Praefix-Baum ueber die
swisstopo SearchAPI) -> pro Parzelle Cache-Check -> wenn nicht
gecacht: OEREB + Reglement + GWR + Klassifikation -> SQLite-Cache ->
Excel-Export mit 6 Sheets (Statistik + 4 Klassifikations-Kategorien
+ Alle).

**Klassifikations-Kategorien**: VERDICHTUNG (bebaut + Reserve),
NEUGESCHAEFT (leer + Bauland), ERSATZNEUBAU (alt + Reserve),
AUSGEREIZT (Bestandsschutz), UNAUFFAELLIG, KLEINPARZELLE
(200-500 m2, neutral), plus AUSSCHLUSS-Kategorien fuer Strassen,
Wald-Verdacht, Reglement-Sperre, Fehler.

**Pilot Oberhofen am Thunersee** (1176 Parzellen, 41 Min, 0 Fehler):
55 VERDICHTUNG, 257 NEUGESCHAEFT, 38 ERSATZNEUBAU.

**Grossstadt-Lauf Thun** (8534 Parzellen, 4h30, 0 Fehler):
890 VERDICHTUNG, 354 NEUGESCHAEFT, 1514 ERSATZNEUBAU. Damit ist
die Grossstadt-Tauglichkeit nachgewiesen.

## Empfehlungs-Block mit visueller Lagebeurteilung

Jede Einzelanalyse mundet in einen klar markierten Empfehlungs-Block
mit ASCII-Fortschrittsbalken.

### Drei Ebenen der Empfehlung

Datenqualitaet (VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH),
Ausschoepfungsgrad, verbale Lagebeurteilung. Bei Grobschaetzungen
wird der Block deutlich gekennzeichnet ("(geschaetzt)").

### Beispiel verbindliche Berechnung

```
======================================================================
EMPFEHLUNG (verbindliche Berechnung)
======================================================================
  Ausschoepfung:    [################----]  80.0%
  Bauland-Reserve:  [####----------------]  20.0%

  -> GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung
======================================================================
```

### Beispiel Grobschaetzung

```
======================================================================
EMPFEHLUNG (Grobschaetzung - nur als Orientierung)
======================================================================
  Ausschoepfung:    [#######-------------]  34.3%
  Bauland-Reserve:  [#############-------]  65.7%

  -> HOHES Verdichtungs-Potenzial - attraktive Bauland-Reserve
     (geschaetzt)
======================================================================
```

### Vier Lagebeurteilungen

- **>= 60%**: HOHES Verdichtungs-Potenzial (attraktive Reserve)
- **30-60%**: MITTLERES Verdichtungs-Potenzial (lohnt Detailpruefung)
- **10-30%**: GERINGES Verdichtungs-Potenzial (Bestandsoptimierung)
- **< 10%**: PRAKTISCH AUSGESCHOEPFT (kein nennenswertes Potenzial)

## Aufgabenverteilung

### Christophe Jenzer

- Backend: OEREB-Pipeline, BKP-Integration, GWR-Modul,
  Reglement-Daten, Potenzialberechnung
- Massen-Analyse: Parzellen-Liste, Gemeinde-Pipeline, SQLite-Cache,
  Klassifikation, Excel-Export
- Bodenbedeckungs-Filter (TLM3D, Arealstatistik)
- Verifikation gegen Reglemente und Karte

### Fabienne

- Streamlit-GUI (Iteration 4) mit eigenstaendigem Design
- Doku-Architektur (Backend/Frontend-Trennung)
- Requirements-Engineering-Pruefung
- Anforderungs- und Releasenotes-Dokumentation

## Werkzeuge und Hilfsmittel

### Datenkomplexitaet als Herausforderung

Eine korrekte Umsetzung erfordert exakte Werte aus offiziellen
Reglementen, korrekte Interpretation der IVHB-Begriffe, Kenntnis
der kantonalen Uebergangsphasen, und das Erkennen von Spezialregimes.
Das Tool versucht nicht, baurechtliche Expertise zu ersetzen - es
liefert eine schnelle Indikation, die ein Architekt im Detail prueft.

### Einsatz von KI-Assistenten

Fuer die Erstellung dieses Projekts wurde Claude.AI (Anthropic) als
Programmier-Assistent eingesetzt. Konkret unterstuetzte Claude bei
Architektur-Entscheidungen, Code-Generierung, Strukturierung der
Reglement-JSONs, Recherche gegen offizielle Quellen sowie der
Dokumentations-Erstellung.

Die fachlichen Entscheidungen, die Verifikation der Werte gegen die
offiziellen Reglemente und die finale Architektur lagen beim
Projektteam. Eine fachliche Verifikation der Soll-Methodik durch
einen Architekten (Schwager) hat die Konzept-Entscheidungen
(Indikator statt Pseudo-Praezision) bestaetigt.

## Iterationen

### Iteration 1: Pipeline (abgeschlossen)

Geocoding, OEREB-Anbindung, XML-Parser, Datenmodell, Hauptprogramm.

### Iteration 2: Potenzialberechnung (abgeschlossen)

Reglement-Modul, drei Bemessungssysteme, Schaetz-Berechnung,
Empfehlungs-Block, Plausibilitaetscheck.

### Iteration 3: Verifikation (abgeschlossen 29.04.2026)

Bauklassenplan-Anbindung Stadt Bern, Bug-Fixes der Begrenzer-Logik,
Datenluecken Thun geschlossen, Stresstest 50 Adressen (96% Erfolg).

### Iteration 4: Webseite (abgeschlossen 11.05.2026)

Streamlit-GUI von Fabienne mit eigenem Design, Backend-Refactoring
(`AnalyseErgebnis`-Datenklasse), drei Datenqualitaets-Pfade
visualisiert, Plausibilitaets-Konflikt-Box.

### Iteration 5: Gemeinde-Analyse (abgeschlossen 12.05.2026)

Massen-Pipeline (parzellen_liste, gemeinde_analyse, gemeinde_cache,
klassifikation, excel_export) plus Bodenbedeckungs-Filter (tlm3d).
Pilot Oberhofen mit 1176 Parzellen erfolgreich.

### Iteration 6: Grossstadt-Tauglichkeit + Konzept-Klaerung (abgeschlossen 20.-23.05.2026)

Skalierung auf Stadt-Groesse (Thun 8534 Parzellen). Vier Bugs gefixt
(GWR-tolerance-Cap, EGRID-Fallback, Gemeinde-Filter, MAX_API_CALLS),
Karten-Link auf map.geo.admin.ch (Kanton BE hat geo.apps.be.ch zum
1.9.2025 abgeschafft), Reserve-% GWR-konsistent, Baujahr-Spalte,
neue Kategorie KLEINPARZELLE als faktischer Fokus-Indikator (200-500
m2 neutral).

Konzeptionelle Klaerung: Die geometrische Soll-Berechnung im
Hoehensystem ist eine Heuristik, kein exaktes Mass. Das Tool ist
als faktenbasierter Indikator konzipiert - die GWR-Plausibilitaets-
Konflikt-Box (Einzelfall) und die Klassifikations-Kategorien
(Massen-Analyse) zeigen ohne falsche Praezision, welche Parzellen
Aufmerksamkeit verdienen.

### Iteration 7: Indikator-Verfeinerung und Generalprobe (geplant, Juni 2026)

Architekt-Antwort zur Soll-Methodik (GFZ-Frage) einarbeiten,
Generalprobe vorbereiten (Pitch 5 Min, Demo-Adressen, Live-Demo
Massen-Analyse), README finalisieren.

## Bewertungskriterien (laut Kursvorgabe)

Das Projekt erfuellt die Kursanforderungen:

- **Funktionalitaet**: end-to-end-Pipeline von Adresse zu strukturiertem
  Ergebnis, plus Massen-Analyse-Modus
- **Code-Qualitaet**: dataclass-basiertes Modell, Separation of Concerns
  (analysiere() vs. drucke_bericht()), Type-Hints, defensive Fehler-
  behandlung
- **Architektur**: modulare Trennung (datenquellen/, analyse/, gui/,
  ausgabe/), wiederverwendbare Bausteine
- **Doku**: Konzept, Projektplan, Journal, struktur.md, fachliche
  Grundlagen, separate Anforderungs- und Releasenotes-Dokumente
- **Tests**: 12-Adressen-Regressionstest, 50-Adressen-Stresstest,
  zwei Pilot-Laeufe Oberhofen + Thun
- **Iteratives Vorgehen**: 6 abgeschlossene Iterationen, Git-Historie
  als Beleg

## Aktueller Stand (23.05.2026)

Das Tool ist fuer den Einzelfall-Modus und die Massen-Analyse
einsatzbereit:

- **Einzelfall** (Streamlit-GUI, Iter 4): Adresse rein, alle drei
  Datenqualitaets-Pfade werden korrekt erkannt, GWR-Plausibilitaets-
  Konflikt-Box ist das visuelle Highlight bei Bestandsbauten.
- **Massen-Analyse** (Iter 5+6): Eine ganze Gemeinde wird in einem
  Durchgang analysiert (Throttling, SQLite-Cache, Excel-Export).
  Pilot Oberhofen (1176 Parzellen) und Grossstadt-Lauf Thun
  (8534 Parzellen, 0 Fehler) erfolgreich.

**Erprobte Gemeinden**: Stadt Bern (Einzelfall), Stadt Thun (Einzelfall
+ Massen-Analyse), Oberhofen am Thunersee (Einzelfall + Massen-Analyse).

**Konzept-Erkenntnis aus Iter 6**: Die geometrische Soll-Berechnung
im Hoehensystem ist eine Heuristik mit bekannten Grenzen - das
Reglement gibt im Einzelfall keine eindeutige Zahl her ("kein
Generalrezept", Architekten-Verifikation). Das Tool kommuniziert das
ehrlich: Bei Grobschaetzungen ist die Datenqualitaet klar markiert,
und die GWR-Plausibilitaets-Konflikt-Box zeigt direkt, wo Schaetzung
und Realitaet auseinanderlaufen. Diese Konflikt-Visualisierung **ist**
der zentrale Indikator des Tools - sie zeigt dem Anwender ohne falsche
Praezision, welche Parzellen Aufmerksamkeit verdienen.

**Naechste Schritte (Iter 7, Juni 2026)**: Generalprobe vorbereiten,
Pitch trimmen, Demo-Adressen waehlen, README finalisieren. Optional
Architekt-Antwort zur Soll-Methodik (GFZ-Frage) in die Doku einarbeiten.

**Abgabe**: 12. Juni 2026 (vorzeitige Abgabe, regulaer 17. Juni 2026).
