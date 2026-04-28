# Fachliche Grundlagen: Bauzonen-Radar

Sammlung der baurechtlichen Recherche fuer das Projekt.
Stand: 28. April 2026.

## Schweizer Baurecht im Ueberblick

Das Baurecht in der Schweiz ist dreistufig:

1. **Bund**: Raumplanungsgesetz (RPG), Raumplanungsverordnung (RPV)
2. **Kanton**: Baugesetz (BauG), Bauverordnung (BauV)
3. **Gemeinde**: Baureglement (BR), Zonenplan, Sondernutzungsplaene

Fuer das Bebauungspotenzial einer konkreten Parzelle ist primaer
das Gemeinde-Baureglement massgebend, eingebettet in die
kantonalen Vorgaben.

## Drei Bemessungssysteme

### AZ - Klassische Ausnuetzungsziffer

Verhaeltnis der zulaessigen Geschossflaeche zur Parzellenflaeche.
AZ = 0.5 bedeutet: Auf einer 1000 m^2 Parzelle duerfen 500 m^2
Geschossflaeche realisiert werden. Verbreitetes altes System,
wird zunehmend durch GFZo abgeloest.

### GFZo - Geschossflaechenziffer oberirdisch

Aehnlich wie AZ, aber:
- Nur oberirdische Geschossflaeche
- Definitionen nach Interkantonaler Vereinbarung ueber die
  Harmonisierung der Baubegriffe (IVHB)
- Im Kanton Bern eingefuehrt mit der BMBV-Verordnung
- Stadt Bern verwendet GFZo seit BO 2006

### Hoehen + GZ - Steuerung ueber Gebaeudemasse

Statt einer Flaechen-Kennzahl werden steuern:
- Maximale Vollgeschosse
- Fassadenhoehen (traufseitig, giebelseitig)
- Maximale Gebaeudelaenge
- Grenzabstaende klein und gross
- Optional: Gruenflaechenziffer (mindestens unversiegelt zu
  haltende Flaeche)

Stadt Thun verwendet dieses System seit BR 2022.
Oberhofen verwendet es seit BR 2012, allerdings ohne GZ.

## Stadt Bern

### Quelle

- Bauordnung der Stadt Bern (BO 2006), Stand 28.09.2023
- URL: https://stadtrecht.bern.ch/lexoverview-home/lex-721_1
- PDF: https://oerebfiles.apps.be.ch/35101/5072/Bern_SSSB_721_1_Bauordnung_der_Stadt_Bern.pdf

### Bauklassen 2-6

- Art. 46 BO: Tabelle mit FH (Fassadenhoehe), FHA (FH Anbau),
  kGA (kleiner Grenzabstand), gGA (grosser Grenzabstand)
- gGA variiert mit Gebaeudelaenge - zweidimensionale Tabelle
- TODO: Variable gGA noch nicht in Code umgesetzt

### Bauklasse E

- Art. 56-57 BO: Erhaltung der bestehenden Bebauungsstruktur
- GFZo 0.5 (zwei Geschosse) oder 0.6 (drei und mehr Geschosse)
- Beispiel Thunstrasse 40, 3005 Bern: GFZo 0.5

### Zonen mit Nutzungsplanung (ZoeN)

- Art. 24 BO: Sondernutzungen mit individueller GFZo
- FA = 0.1 (Freihaltezonen)
- FB = 0.6
- FC = 1.2
- FD = projekt-abhaengig

### Arbeitszonen

- Art. 58 BO: FH/FHA pro Bauklasse 1-6

### Altstadt-Spezialregimes

- Art. 76-86 BO
- Untere Altstadt: UNESCO-Welterbe, strenge Vorschriften
- Obere Altstadt: Laubenfluchtlinien, Sandstein-Pflicht
- Biberschwanzziegel als Pflichtmaterial fuer Daecher

### Offene Punkte

GFZo-Werte pro Zone-Bauklasse-Kombination liegen im
**Bauklassenplan (BKP)**, nicht in der BO. Schwager (Architekt)
soll diese Werte aus seiner Bueropraxis liefern. Erfassungs-Excel
ist vorbereitet.

## Stadt Thun

### Quelle

- Baureglement (BR) der Stadt Thun, Februar 2025
- Ortsplanungsrevision OPR 2022
- URL: https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision

### Wesentliche Aenderung gegenueber BR 2002

- AZ in Wohnzonen abgeschafft
- Steuerung ueber Hoehen, Grenzabstaende, Gebaeudelaenge,
  Gruenflaechenziffer

### Art. 42 - Tabelle

Vom Schwager geliefert, in `thun.json` eingepflegt:

| Zone | kA | gA | GL | Fh tr | Fh gi | GZ |
|---|---|---|---|---|---|---|
| W2 | 4 | 8 | 15 | 7.0 | 11.0 | 0.45 |
| W3 | ... | ... | ... | ... | ... | ... |
| W4 | ... | ... | ... | ... | ... | ... |
| WA3 | ... | ... | ... | ... | ... | ... |
| WA4 | ... | ... | ... | ... | ... | ... |
| WA5 | ... | ... | ... | ... | ... | ... |
| Arbeiten A | ... | ... | ... | ... | ... | ... |

### Spezialfaelle

- **Strukturgebiet**: Beirat Stadtbild kann Vorgaben machen, die
  das BR aushebeln. Tool erkennt das automatisch.
- **Arealbonus**: Ab 3000 m^2 Parzelle plus ein Vollgeschoss
  bewilligungsfaehig.

## Oberhofen am Thunersee

### Quelle

- Baureglement (BR) der Einwohnergemeinde Oberhofen am Thunersee
  vom 14. Mai 2012
- Nachfuehrung bis 31. Dezember 2024
- AGR-genehmigt (Amt fuer Gemeinden und Raumordnung)
- URL: https://www.oberhofen.ch/verwaltung/reglemente-verordnungen
- PDF: https://www.oberhofen.ch/images/files/Reglemente-und-Verordnungen/Bau/AGR-Gemeindebaureglement.pdf

### System

Hoehen-System ohne GZ. Steuerung ueber:
- Vollgeschosse
- Fassadenhoehen
- Gebaeudelaenge
- Grenzabstaende
- Erstwohnungsanteil 80% (EWA)

### Art. 212 - Tabelle

Vier Wohn-/Mischzonen mit kompletten Werten:

| Zone | kA | gA | GL | Fh tr | Fh gi | VG |
|---|---|---|---|---|---|---|
| W1 | 3.0 | 6.0 | 20.0 | 6.0 | 9.0 | 1 |
| W2 | 4.0 | 8.0 | 20.0 | 7.0 | 10.0 | 2 |
| W3 | 4.0 | 8.0 | 25.0 | 9.5 | 13.0 | 3 |
| M2 | 2.0 | 6.0 | 20.0 | 8.5 | 13.5 | 2 |

Plus Fussnoten:
- Reduktion gA an Steilhaengen um 2.0 m
- Bei Bauten am Hang +1.0 m Mehrhoehe (ausser Hangseite)
- W2 gegenueber Rebbauzone 10.0 m Abstand
- M2 seeseitig max. 15.0 m Gebaeudebreite

### Weitere Zonen

- Zonen fuer oeffentliche Nutzungen (ZOEN 1-11): Schule, Kirche,
  Schloessli, Laendte, Mehrzweckhalle usw.
- Zehn Zonen mit Planungspflicht (ZPP A-J)
- Sechs Ortsbildschutzgebiete (O I bis O VI)
- Landwirtschaftszone (LWZ)
- Rebbauzone (RB) - Bauverbot
- Gruenzone (GR) - Freihaltezone

### Dachgestaltung (Art. 414)

- Satteldach: Neigung 22-40 Grad
- Flachdach grundsaetzlich nicht zulaessig (nur in ZOEN/ZPP/UeO)
- Dachvorspruenge traufseitig 0.2-2.5 m
- Dachaufbauten max. 35% der Fassadenbreite (50% bei
  qualifiziertem Verfahren)

## Naturgefahren

OEREB liefert Naturgefahrengebiete als separate Restrictions:
- Mittlere Gefaehrdung
- Geringe Gefaehrdung
- Restgefahrengebiet

Tool gibt Warnung aus: "Bebaubarkeit muss im Detail geprueft
werden."

## Spezialfaelle

### Strukturgebiet (Thun)

Spezielle Ueberlagerung der Stadt Thun. Beirat Stadtbild kann
gestalterische Vorgaben machen, die das BR aushebeln. Tool
erkennt das anhand der OEREB-Legende und gibt Hinweis aus.

### Arealbonus

Schwellenwerte sind reglements- bzw. gemeindespezifisch:
- Thun BR 2022: 3000 m^2 → +1 Geschoss
- Oberhofen: kein Arealbonus

### Baulinien

OEREB liefert Baulinien als Restrictions. Tool gibt Hinweis aus,
dass die effektive Bauflaeche kleiner als die Gesamtflaeche ist.

### Laufende Aenderungen

Wenn die OEREB-Daten "laufendes Verfahren" oder "geplante
Aenderung" anzeigen, gibt das Tool eine Warnung aus.

## Quellen-Zusammenfassung

| Gemeinde | Reglement | Stand | URL |
|---|---|---|---|
| Bern | BO 2006 | 28.09.2023 | stadtrecht.bern.ch |
| Thun | BR 2022 | Februar 2025 | thun.ch |
| Oberhofen | BR 2012 | 31.12.2024 | oberhofen.ch |

## Zu klaerende Punkte

- Stadt Bern Bauklassenplan: GFZo-Werte pro Zone-Bauklasse-
  Kombination (von Schwager)
- Variable gGA aus Art. 46 BO Bern (zweidimensionale Tabelle)
  in Code umsetzen
- Eventuell vierte Gemeinde aufnehmen (Koeniz wegen Test-Adresse
  Spiegel)
