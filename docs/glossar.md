**AZ (Ausnuetzungsziffer)**
Klassisches Bemessungs-System des Schweizer Baurechts.
AZ x Parzellenflaeche = maximale Geschossflaeche. Wird
zunehmend durch GFZo abgeloest.

**BFS-Nummer**
Eindeutige Identifikation einer Schweizer Gemeinde durch das
Bundesamt fuer Statistik. Z.B. BFS 942 = Thun, BFS 351 = Bern.

**BKP (Bauklassenplan)**
Stadtbern-spezifisches Instrument der Stadtplanung. Definiert
parzellenscharf die zulaessige Bauklasse (BK_2 bis BK_6, BK_E,
BK_SPEZ) und Bauweise. Verfuegbar als ArcGIS REST-API.

**EGRID**
Eindeutige Identifikation einer Schweizer Parzelle (Grundstueck)
nach kantonalem Schema. Format: CHnnnnnnnnnnnn.

**GFZo (Geschossflaechenziffer oberirdisch)**
Bemessungs-System nach IVHB-Standard. Definiert das Verhaeltnis
von Geschossflaeche zu Parzellenflaeche, gerechnet nur fuer
oberirdische Geschosse.

**GROBSCHAETZUNG**
Datenqualitaets-Stufe des Bauzonen-Radar. Wird verwendet, wenn
das Bemessungs-System keine direkte Kennzahl liefert (Hoehen+GZ-System)
und das Tool eine konservative Schaetzung anhand der Drei-Begrenzer-Logik
durchfuehrt.

**GWR (Eidg. Gebaeude- und Wohnungsregister)**
Schweizweites Register aller Gebaeude und Wohnungen. Gefuehrt
durch das Bundesamt fuer Statistik (BFS), oeffentlich abrufbar
ueber api3.geo.admin.ch. Liefert Grundflaeche, Geschosszahl,
Wohnungs-Anzahl, Baujahr, Sanierungsdaten.

**GRUDIS**
Berner Grundbuch-Informations-System. Ermoeglicht autorisierte
Eigentuemer-Recherche. Tool verwendet GRUDIS-Direktlinks
("Bruecken-Ansatz") statt Eigentuemer-Scraping.

**GZ (Gruenflaechenziffer)**
Mindestanteil unbebauter, begruenter Flaeche an der Parzelle.
Begrenzt indirekt die Geschossflaeche.

**IVHB (Interkantonale Vereinbarung ueber die Harmonisierung der
Baubegriffe)**
Standardisierungs-Werk fuer Baubegriffe in der Schweiz.
Definiert GFZo, Vollgeschoss, Gebaeudehoehe etc. einheitlich.

**NICHT_MOEGLICH**
Datenqualitaets-Stufe des Bauzonen-Radar. Wird verwendet bei
Spezialregimes (Altstadt UNESCO, UeO/UeP, Schutzzonen), wo eine
Berechnung weder verbindlich noch geschaetzt sinnvoll moeglich ist.

**OEREB (Oeffentlich-rechtliche Eigentumsbeschraenkungen)**
Bundesrechtliches Instrument fuer transparente Darstellung
aller eigentumsrelevanten Beschraenkungen einer Parzelle.
Verfuegbar als Webservice pro Kanton.

**Parzelle**
Grundstueck (im Schweizer Sprachgebrauch). Identifiziert ueber
Parzellennummer (innerhalb einer Gemeinde) oder EGRID (kantonal).

**Strukturgebiet**
Spezialregime in der Stadt Thun. Reduziert die Bauland-Reserve
in als wertvoll erkannten Quartiers-Strukturen.

**ueP / UeO (Ueberbauungsplan / Ueberbauungsordnung)**
Gemeindespezifisches Planungsinstrument fuer abweichende
Vorschriften gegenueber dem allgemeinen Baureglement.

**VERBINDLICH**
Datenqualitaets-Stufe des Bauzonen-Radar. Wird verwendet, wenn
direkte Kennzahlen (AZ oder GFZo) verfuegbar sind und die
Berechnung exakt ohne Schaetzung erfolgen kann.

**ZoeN (Zone fuer oeffentliche Nutzung)**
Spezielle Nutzungszone fuer Schulen, Verwaltung, Spitaeler etc.
Hat oft eigenstaendige Regeln, daher haeufig NICHT_MOEGLICH-Pfad.
