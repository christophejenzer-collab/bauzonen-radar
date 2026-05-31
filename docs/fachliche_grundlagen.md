# Fachliche Grundlagen: Bauzonen-Radar

Sammlung der baurechtlichen Recherche fuer das Projekt.
Stand: 23. Mai 2026.

## Schweizer Baurecht im Ueberblick

Das Schweizer Baurecht ist hochkomplex. Die wichtigsten Punkte:

- Drei Bemessungssysteme sind parallel im Einsatz (AZ, GFZo, Hoehen+GZ)
- Jede Gemeinde hat ihr eigenes Reglement, gewachsen ueber Jahrzehnte
- Kantonale Uebergangsphasen: das BernerSchweizweite IVHB-Konkordat
  (2014) verlangt einen Wechsel weg von der AZ
- Spezialregimes fuer Altstaedte, Schutzgebiete, Zonen mit
  Planungspflicht (ZPP/UeO)
- Bestandsschutz: gebaute Realitaet weicht oft vom heute rechtlich
  Zulaessigen ab

Eine korrekte Umsetzung verlangt: exakte Werte aus offiziellen
Reglementen, IVHB-konforme Interpretation, Kenntnis der kantonalen
Uebergangsregelung, Erkennen von Spezialregimes.

## Drei Bemessungssysteme

### AZ - Klassische Ausnuetzungsziffer

Aeltestes System der Schweiz. AZ x Parzellenflaeche = maximale
Geschossflaeche. Einfach zu rechnen, aber durch das IVHB-Konkordat
in Ablösung. Im Kanton Bern noch in einzelnen Gemeinden gueltig,
zunehmend durch GFZo ersetzt.

### GFZo - Geschossflaechenziffer oberirdisch

IVHB-konformes Mass: ueberirdische Geschossflaeche pro Parzelle.
Etwas komplexer als AZ (Unterscheidung Untergeschosse, anrechenbare
Flaechen nach IVHB), aber flaechenbezogen und damit eindeutig
berechenbar. Stadt Bern nutzt GFZo im Bauklassenplan.

### Hoehen + GZ - Steuerung ueber Gebaeudemasse

Dichte wird ueber Gebaeudehoehe, Geschosszahl, Grenzabstaende und
(optional) Gruenflaechenziffer gesteuert. Es gibt **kein flaechen-
bezogenes Limit** fuer die Geschossflaeche. Verbreitet in neueren
Reglementen wie Thun BR 2022 oder Oberhofen. Vorteil: gestalterisch
flexibler. Nachteil fuer ein Tool wie dieses: die "zulaessige
Geschossflaeche" ist im Einzelfall nicht eindeutig bestimmbar -
sie haengt davon ab, wie ein konkretes Gebaeude auf die konkrete
Parzelle gesetzt wird.

## Schaetz-Berechnung im Hoehen-System

Da im Hoehen-System keine direkte flaechenbezogene Kennzahl
existiert, schaetzt das Tool das Soll ueber eine geometrische
Drei-Begrenzer-Logik. Das Resultat wird **explizit als Schaetzung
markiert** (Datenqualitaet: GROBSCHAETZUNG).

### Berechnungsformel

```
nutzbare_lange_seite = lange_seite - 2 * grosser_grenzabstand
nutzbare_kurze_seite = kurze_seite - 2 * kleiner_grenzabstand
grundflaeche_geometrie = nutzbare_lange_seite * nutzbare_kurze_seite

grundflaeche_parzelle  = parzellenflaeche * (1 - gruenflaechenziffer)
grundflaeche_gz        = grundflaeche_parzelle / geschosszahl

grundflaeche_zulaessig = min(geometrie, parzelle, gz)
geschossflaeche        = grundflaeche_zulaessig * geschosszahl
```

Der kleinste der drei Begrenzer gewinnt - das ist die konservative
Schaetzung.

### Annahmen

- Parzellen-Form: Rechteck mit Verhaeltnis 1:1.5 (statt Quadrat -
  verhindert dass eine Seite negativ wird bei langen Parzellen)
- Grenzabstaende werden auf allen vier Seiten voll abgezogen
- `max_gebaeudelaenge_m=None` (unbeschraenkt) wird als float("inf")
  behandelt (statt Crash)
- Wenn Ist-Bebauung unbekannt: 25%-Platzhalter (realistischer fuer
  Schweizer Wohnzonen als die fruehere 40%-Annahme)

### Plausibilitaetscheck

Wenn fuer die Zone ein historischer AZ-Wert hinterlegt ist
(`vergleichswert_az_alt`), vergleicht das Tool die Schaetzung
gegen die AZ-basierte Berechnung. Bei Abweichung mehr als Faktor
1.8x oder weniger als 0.7x gibt es eine Warnung im Output.

Im Einzelfall-Modus wird zusaetzlich der GWR-Ist-Wert angezeigt -
wenn der die Schaetzung deutlich uebersteigt, ist das ein klares
Signal fuer Bestandsschutz (Plausibilitaets-Konflikt-Box).

### Wichtig: Datenqualitaets-Markierung

Bei einer Schaetzung wird das im Output **deutlich markiert** mit
Banner und einer Berechnungsbasis, die alle Annahmen offenlegt.
Architekten und Investoren sollen klar sehen, ob sie einer Zahl
trauen koennen.

Drei Stufen:

- **VERBINDLICH**: AZ oder GFZo vorhanden -> exakte Berechnung
- **GROBSCHAETZUNG**: Hoehen-System -> konservative Schaetzung mit
  klarer Markierung
- **NICHT_MOEGLICH**: Spezialregime (z.B. ZPP) -> keine Pseudo-
  zahlen, Verweis auf Bauverwaltung

## Empfehlungs-Block mit visueller Lagebeurteilung

Jede Einzelanalyse mundet in einen klar markierten Empfehlungs-Block
mit ASCII-Fortschrittsbalken zur visuellen Lagebeurteilung.

### Bauland-Reserve in Prozent

```
reserve_prozent = 100 - ausschoepfungsgrad_prozent
```

Anschauliche Kennzahl: 65% Reserve heisst, der Anwender kann die
Parzelle noch zu 65% des theoretischen Potenzials weiterentwickeln.

### ASCII-Fortschrittsbalken

```
Ausschoepfung:    [################----]  80.0%
Bauland-Reserve:  [####----------------]  20.0%
```

20 Zeichen breit, Hash-Zeichen fuer den ausgeschoepften Anteil,
Bindestriche fuer die Reserve. Auf der Konsole und in der GUI
gleich lesbar.

### Vier Lagebeurteilungen

- **>= 60%**: HOHES Verdichtungs-Potenzial (attraktive Reserve)
- **30-60%**: MITTLERES Verdichtungs-Potenzial (lohnt Detailpruefung)
- **10-30%**: GERINGES Verdichtungs-Potenzial (Bestandsoptimierung)
- **< 10%**: PRAKTISCH AUSGESCHOEPFT (kein nennenswertes Potenzial)

### Bei Schaetzungen wird "(geschaetzt)" angehaengt

```
HOHES Verdichtungs-Potenzial - attraktive Bauland-Reserve (geschaetzt)
```

Damit ist auf den ersten Blick sichtbar, ob die Lagebeurteilung auf
verbindlichen Werten oder einer Grobschaetzung beruht.

## Stadt Bern

### Quelle

- Bauordnung BO 2006, Stand 2023:
  https://stadtrecht.bern.ch/lexoverview-home/lex-721_1
- Bauklassenplan BKP via ArcGIS REST-API:
  https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer

### Bauklassen 2-6

Hoehen+GZ-System mit parzellenscharfen Werten aus dem BKP fuer:
- Bauweise (Layer 88): offen / geschlossen / Reihen / verdichtet
- Grundzonen (Layer 95): max. Gebaeudelaenge, Gebaeudetiefe

Die Bauklasse selbst legt Geschosszahl, Hoehe, Gruenflaechenziffer
fest. Die parzellenscharfen Werte aus dem BKP ergaenzen das um die
konkrete Geometrie.

### Bauklasse E

Erhaltungsbauklasse mit GFZo 0.5 (Art. 23 BO). Verbindliche
Berechnung moeglich. Beispiel: Thunstrasse 40 -> 237 m^2 Parzelle x
0.5 = 118 m^2 zulaessig.

### Zonen mit Nutzungsplanung (ZoeN)

Spezialregime: Konkrete Werte stehen erst in der UeO (Ueberbauungs-
ordnung) fest. Datenqualitaet -> NICHT_MOEGLICH, Verweis auf
Bauverwaltung.

### Arbeitszonen

Eigene Bauklassen mit eigenen Werten. In `bern.json` als separate
Eintraege hinterlegt.

### Altstadt-Spezialregimes

Untere und Obere Altstadt: UNESCO-Welterbe, Laubenfluchtlinien,
Hoehenfluchtlinien. Datenqualitaet -> NICHT_MOEGLICH bzw.
Spezialvermerk.

### Offene Punkte

- Variable gGA (Gruenflaechen-Geschossanrechnung) aus Art. 46 BO:
  fuer Iter 7 oder Folgeprojekt
- Subtypen FA-FD der ZoeN: aktuell als ZoeN allgemein behandelt

## Stadt Thun

### Quelle

- Baureglement 2022 + Ortsplanungsrevision:
  https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision

### Wesentliche Aenderung gegenueber BR 2002

Mit BR 2022 hat Thun die klassische Ausnuetzungsziffer abgeschafft.
System ist `hoehen_und_gz` ohne flaechenbezogene Kennzahl. Der alte
AZ-Wert (0.5 in vielen Wohnzonen) ist nur noch als
`vergleichswert_az_alt` im JSON enthalten - nicht mehr rechtsgueltig.

Konsequenz fuer das Tool: alle Thun-Parzellen laufen in den
GROBSCHAETZUNG-Pfad (Drei-Begrenzer-Logik), nicht in den VERBINDLICH-
Pfad.

### Art. 42 - Tabelle (in thun.json hinterlegt)

Alle Wohnzonen W1-W4, Wohn-/Mischzonen WA2-WA5 (mit Slash-
Schreibweise als Synonym), Mischzonen M1-M5. Pro Zone: max. Hoehe,
Vollgeschoss-Zahl, kleiner/grosser Grenzabstand,
Gruenflaechenziffer 0.45.

### Spezialfaelle

- Strukturgebiet: Bestandsmasse statt Reglement-Masse
- Arealbonus: max. 10% Mehrausnuetzung bei integrierter Planung
- Zone mit Planungspflicht (ZPP): NICHT_MOEGLICH, UeO erforderlich
- Slash-Synonyme: "Wohnen/Arbeiten WA4" matcht "Wohnen + Arbeiten WA4"

## Oberhofen am Thunersee

### Quelle

- Baureglement 2012, revidiert 2024:
  https://www.oberhofen.ch/verwaltung/reglemente-verordnungen

### System

`hoehen_und_gz` **ohne Gruenflaechenziffer** (Sonderfall). Steuerung
nur ueber Gebaeudehoehe, Geschosszahl, Grenzabstaende. Schaetzung
laeuft nur ueber die geometrischen Begrenzer.

### Art. 212 - Tabelle

Wohnzonen W1-W3 mit den ueblichen Parametern. Misch- und Arbeits-
zonen separat hinterlegt.

### Weitere Zonen

- Dorfkernzonen mit Bestandsschutz
- Landwirtschaftszone (ausserhalb Bauzone, NICHT_MOEGLICH)
- Verkehrszonen, Gruenzonen

### Dachgestaltung (Art. 414)

Spezielle Bestimmungen fuer Dachformen und -neigungen, im Tool
nicht direkt abgebildet (waere fuer Detailpruefung beim Architekten).

## Naturgefahren

OEREB-Auszug liefert Naturgefahren-Layer:
- Gefahrenstufe 1 (gering) bis 3 (erheblich)
- Naturgefahr-Art (Wasser, Rutsch, Sturz, Lawine)

Das Tool listet alle Naturgefahren-Eintraege im Output. Bei
Gefahrenstufe 2/3 ist im Reglement-Bereich eine zusaetzliche
Bewilligung erforderlich - Hinweis im Output.

## Spezialfaelle

### Strukturgebiet (Thun)

In bestimmten Quartieren (Innenstadt, historische Aussenviertel)
gelten **Bestandsmasse statt Reglement-Masse**. Die zulaessige
Bebauung orientiert sich am Bestand der Parzelle. Im Tool als
Spezialfall erkannt, Hinweis im Output.

### Arealbonus

Bei integrierter Planung mehrerer Parzellen kann ein Arealbonus
(typisch +10% Hoehe oder Geschossflaeche) gewaehrt werden. Im Tool
als Hinweis sichtbar, Berechnung nicht automatisch eingerechnet.

### Baulinien

OEREB-Layer "Baulinien" und "Strassen-Baulinien". Wenn die Parzelle
betroffen ist, gilt die Baulinie zusaetzlich zum Grenzabstand. Das
Tool zeigt Baulinien im Output, rechnet sie aber nicht automatisch
in die Geometrie ein (waere Detailpruefung).

### Laufende Aenderungen

Reglemente werden periodisch revidiert. Das Tool fuehrt fuer jede
Gemeinde ein eigenes JSON, das bei Reglement-Aenderungen aktualisiert
werden muss (kein Code-Aenderung noetig).

## Bauklassenplan Stadt Bern (BKP) - ArcGIS REST-API

### Layer 88: BKP_Bauweise

Felder:
- `BAUWEISE`: offen / geschlossen / Reihen / verdichtet
- Geometrie: Multipolygon der zusammenhaengenden Bauweise-Flaeche

Das Tool fragt mit der Parzellen-Koordinate die Bauweise ab.

### Layer 95: BKP_Grundzonen_Flaechen

Felder:
- `BKP_BEZ`: BK_2, BK_3, BK_4, BK_5, BK_6, BK_E, ZoeN, Altstadt
- `MAX_GEBL`: maximale Gebaeudelaenge in Metern
- `MAX_GEBT`: maximale Gebaeudetiefe in Metern

Das Tool fragt mit der Parzellen-Koordinate die Grundzone ab.

### Drei Faelle in der Stadt Bern

1. **Bauklasse 2-6**: `hoehen_und_gz` aus dem JSON, ergaenzt um die
   parzellenscharfen Werte aus dem BKP (Bauweise, max_gebaeudelaenge,
   max_gebaeudetiefe)
2. **Bauklasse E**: GFZo 0.5 aus dem JSON, verbindliche Berechnung
3. **ZoeN / Altstadt**: NICHT_MOEGLICH, Verweis auf Bauverwaltung

### Wichtige Erkenntnis

Stadt Bern ist die **einzige BE-Gemeinde mit einer Live-API fuer
parzellenscharfe Bauwerte**. Andere BE-Gemeinden (auch Koeniz mit
seinem Bauklassen-System) liefern in der Public-API nur die Zonen-
Bezeichnung, keine konkreten Werte. Diese Gemeinden brauchen
weiterhin manuelle JSON-Erfassung der Reglement-Werte.

Schweizweite WFS-APIs wie geodienste.ch wurden geprueft: liefern
ebenfalls nur Zonen-Bezeichnungen, keine Bauwerte.

## Quellen-Zusammenfassung

- IVHB (Interkantonale Vereinbarung ueber die Harmonisierung der
  Baubegriffe): https://www.bpuk.ch/ivhb
- Stadt Bern Bauordnung BO 2006:
  https://stadtrecht.bern.ch/lexoverview-home/lex-721_1
- Stadt Thun Ortsplanungsrevision:
  https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision
- Oberhofen Baureglement:
  https://www.oberhofen.ch/verwaltung/reglemente-verordnungen
- OEREB-Webservice Kanton Bern: https://www.oereb2.apps.be.ch
- swisstopo SearchAPI: https://api3.geo.admin.ch
- GWR (Eidg. Geb.- und Wohnungsregister) ueber api3.geo.admin.ch
- BFS-Arealstatistik (NOLC04-Codes), swissTLM3D-Strassen

## Zu klaerende Punkte

- Variable gGA aus Art. 46 BO Bern (verschoben fuer Folgeprojekt)
- Subtypen FA-FD der ZoeN (verschoben)
- Schwager-Antwort zur grundsaetzlichen Soll-Methodik (GFZ-Frage)
  steht noch aus (siehe naechster Abschnitt)

## Indikator-Erkenntnis aus Iteration 6 (23.05.2026)

Beim Grossstadt-Lauf in Thun (8534 Parzellen) wurde sichtbar, dass
die geometrische Soll-Berechnung im Hoehensystem an ihre Grenzen
kommt:

- **Bei kleinen Parzellen** kollabiert das Soll, weil die beidseitig
  abgezogenen Grenzabstaende fast die ganze Flaeche aufzehren.
- **Bei grossen Parzellen** wird das Soll vom Begrenzer
  `max_gebaeudelaenge * Breite` gedeckelt - das Modell rechnet nur
  ein einzelnes Gebaeude statt mehrerer (Arealueberbauung).

### Was das Reglement (nicht) hergibt

Eine Pruefung der Berner Reglement-Daten zeigte: Thun (BR 2022) hat
**keine gueltige Ausnuetzungs- oder Geschossflaechenziffer** mehr.
System `hoehen_und_gz` steuert die Dichte ausschliesslich ueber
Hoehen, Geschosse, Grenzabstaende und (optional) die Gruenflaechen-
ziffer. Der fruehere AZ-Wert (0.5 in Thun BR 2002) ist im JSON nur
als `vergleichswert_az_alt` enthalten, nicht mehr rechtsgueltig.

Konsequenz: Im Hoehensystem existiert die "zulaessige Geschoss-
flaeche" als eindeutige Zahl gar nicht - sie haengt davon ab, wie
ein konkretes Gebaeude auf die konkrete Parzelle gesetzt wird. Das
ist keine Schwaeche des Codes, sondern Eigenschaft des Baurechts.

### Architekt-Verifikation (Schwager, Mai 2026)

Bestaetigt: "Kein Generalrezept." Bei kleinen oder aneinander-
gebauten Parzellen sollte der seitliche Grenzabstand wegfallen,
vorne und hinten sollten beide Grenzabstaende voll zaehlen. Aber
selbst diese Heuristik kippt bei der naechsten Parzellenklasse.
Fokus aus Architekten-Sicht: Parzellen ab 500 m2, kleinere neutral
mitfuehren.

Konkrete Auswirkung im Code: neue Kategorie KLEINPARZELLE (200-500
m2, neutral - ausserhalb der Fokus-Reiter Verdichtung/Neugeschaeft/
Ersatzneubau, aber sichtbar in der Gesamtliste).

### ARE/GFR-Methodik als Referenz

Die offizielle Schaetzung des Bundesamts fuer Raumentwicklung (ARE)
arbeitet nicht mit geometrischer Nachbildung, sondern mit
Ausnuetzungs-/Geschossflaechenziffern multipliziert mit empirischen
Ausschoepfungsgraden (typisch 60% bei bebauten, 90% bei
Geschossflaechen-Reserven). Diese Methode skaliert sauber, ist aber
auf Reglemente mit GFZ angewiesen - bei reinem Hoehensystem nicht
direkt anwendbar.

### Schlussfolgerung fuer das Tool

Das Tool ist als **faktenbasierter Indikator** konzipiert, nicht
als exakter Soll-Rechner. Die zentrale Visualisierung ist die
GWR-Plausibilitaets-Konflikt-Box: sie zeigt den Unterschied zwischen
konservativer Schaetzung (Soll) und tatsaechlich gebauter Realitaet
(GWR-Ist) - genau dort, wo dieser Konflikt gross ist, lohnt sich
eine Detailpruefung.

In der Massen-Analyse uebernehmen die Klassifikations-Kategorien
(VERDICHTUNG, ERSATZNEUBAU, AUSGEREIZT, KLEINPARZELLE etc.) dieselbe
Rolle: sie ranken Parzellen nach Hinweis-Staerke, nicht nach
vermeintlich exaktem Soll. Die Datenqualitaets-Markierung
(VERBINDLICH / GROBSCHAETZUNG / NICHT_MOEGLICH) sagt dem Anwender
ehrlich, wie belastbar die Zahl im Einzelfall ist.

### Offen fuer Iteration 7

Die Architekt-Antwort zur grundsaetzlichen Methodik (GFZ vs.
Geometrie) ist gestellt, aber noch nicht eingearbeitet. In Iteration
7 kann das ggf. zu einer feineren Indikator-Logik fuehren - die
aktuelle Architektur ist robust genug, dass kleine methodische
Anpassungen ohne grossen Umbau moeglich sind.
