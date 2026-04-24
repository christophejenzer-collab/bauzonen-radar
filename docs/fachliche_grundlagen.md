# Fachliche Grundlagen: Berner Baurecht und Bemessungssysteme

Dieses Dokument hält die fachlichen Grundlagen fest, auf denen das Datenmodell des Bauzonen-Radars aufbaut. Es richtet sich an Entwicklerinnen und Entwickler des Projekts, die verstehen müssen, **warum** die Baureglement-JSON-Dateien so strukturiert sind, wie sie sind — und an externe Leserinnen und Leser (Dozent, Architekturbüro, neue Teammitglieder), die einen schnellen Überblick über die rechtlichen Rahmenbedingungen benötigen.

Das Dokument ersetzt keine juristische Beratung. Es fasst den öffentlich zugänglichen Stand von April 2026 zusammen, basierend auf kantonalen und kommunalen Quellen.

---

## Inhalt

1. [Ausgangslage: Die Ausnützungsziffer (AZ)](#ausgangslage-die-ausnuetzungsziffer-az)
2. [Der IVHB-Systemwechsel und die GFZo](#der-ivhb-systemwechsel-und-die-gfzo)
3. [Umsetzung im Kanton Bern (BMBV)](#umsetzung-im-kanton-bern-bmbv)
4. [Fallstudie Stadt Thun: BR 2002 vs. BR 2022](#fallstudie-stadt-thun-br-2002-vs-br-2022)
5. [Stadt Bern: Stand der Umstellung](#stadt-bern-stand-der-umstellung)
6. [Konsequenzen für das Datenmodell](#konsequenzen-fuer-das-datenmodell)
7. [Offene Punkte und Verifikationsbedarf](#offene-punkte-und-verifikationsbedarf)
8. [Quellenverzeichnis](#quellenverzeichnis)

---

## Ausgangslage: Die Ausnützungsziffer (AZ)

Die **Ausnützungsziffer (AZ)** war über Jahrzehnte das zentrale Mass zur Steuerung der baulichen Dichte in der Schweiz. Sie definiert das Verhältnis zwischen der anrechenbaren Bruttogeschossfläche (BGF) und der anrechenbaren Grundstücksfläche (aGSF):

```
AZ = BGF / aGSF
```

Beispiel: Eine Parzelle von 1'000 m² mit einer AZ von 0.5 erlaubt eine BGF von 500 m².

### Was zählt zur BGF?

- Wohnräume, Schlafzimmer, Küchen, Bäder
- Büroflächen
- Alle dem Wohnen oder Arbeiten dienenden ober- **und unterirdischen** Geschossflächen inklusive Aussenmauern

### Was zählt nicht zur BGF?

- Keller- und Lagerräume
- Waschküchen, Trockenräume, Heiz- und Tankräume
- Einstellräume für Velos und Fahrzeuge
- Treppenhäuser und Lifte (teilweise)
- Dachräume ohne Wohnnutzung

### Historische Richtwerte

In ländlichen Berner Gemeinden galt traditionell eine AZ von etwa 0.3, in Zentren deutlich höhere Werte. In der Stadt Thun lagen die AZ-Werte bis 2022 bei:

| Zone | AZ (BR 2002) |
|---|---|
| Wohnzone W2 | 0.5 |
| Wohnzone W3 | 0.7 |

---

## Der IVHB-Systemwechsel und die GFZo

### Die interkantonale Vereinbarung

Die **Interkantonale Vereinbarung über die Harmonisierung der Baubegriffe (IVHB)** vom 22. September 2005 vereinheitlicht schweizweit die Begriffe und Messweisen im Bauwesen. Für die Kantone, die der Vereinbarung beigetreten sind (darunter Bern), gelten seither harmonisierte Definitionen für Gebäudehöhen, Grenzabstände, Nutzungsziffern und weitere Parameter.

### Die Geschossflächenziffer oberirdisch (GFZo)

Die klassische AZ wird durch die **Geschossflächenziffer oberirdisch (GFZo)** ersetzt:

```
GFZo = anrechenbare Geschossfläche oberirdisch (GFo) / anrechenbare Grundstücksfläche (aGSF)
```

### Der entscheidende Unterschied

Die AZ zählte sowohl ober- als auch unterirdische Nutzflächen mit. Die GFZo bezieht sich ausschliesslich auf Flächen **oberhalb des massgebenden Terrains**.

In der Praxis bedeutet dies: Ein Souterrain mit Wohnraum belastete unter AZ das Kontingent, unter GFZo nicht mehr. Der Systemwechsel führt deshalb in vielen Fällen zu einer leichten Erhöhung der effektiv nutzbaren Fläche.

---

## Umsetzung im Kanton Bern (BMBV)

### Die kantonale Rechtsgrundlage

Der Kanton Bern hat die IVHB-konformen Begriffe durch die **Verordnung über die Begriffe und Messweisen im Bauwesen (BMBV)** in kantonales Recht überführt. Die BMBV ergänzt das kantonale Baugesetz (BauG) und die Bauverordnung (BauV).

### Die Gemeinden sind am Zug

Jede Berner Gemeinde muss ihre **baurechtliche Grundordnung (BNO)** an die BMBV anpassen. Bis zur erfolgten Anpassung gelten die bisherigen AZ-Bestimmungen nach BauV Art. 93 bis 98 weiter.

Daraus folgt: Innerhalb des Kantons Bern stehen Gemeinden gleichzeitig auf unterschiedlichen Rechtsständen. Das Tool muss diese Heterogenität berücksichtigen.

### Besonderheit: Bauen ausserhalb der Bauzone

Für Bauvorhaben ausserhalb der Bauzone bleibt der alte BauV Art. 93 massgebend. Die BGF wird dort weiterhin nach der klassischen Methode berechnet, um die Gebäudeidentität bei Umbauten zu wahren. Das Datenmodell des Bauzonen-Radars fokussiert derzeit auf Parzellen innerhalb der Bauzone.

---

## Fallstudie Stadt Thun: BR 2002 vs. BR 2022

Die Stadt Thun ist ein instruktives Beispiel für die weitestgehende Umsetzung des Systemwechsels. Mit der **Ortsplanungsrevision (OPR) und dem neuen Baureglement BR 2022** hat Thun nicht nur die AZ durch die GFZo ersetzt, sondern in den meisten Wohnzonen auch auf eine einzelne Kennzahl zur Dichtesteuerung verzichtet.

### Altes Recht: BR 2002

Im Baureglement von 2002 war die AZ das zentrale Mass:

- Wohnzone W2: AZ 0.5
- Wohnzone W3: AZ 0.7

Die BGF umfasste ober- und unterirdische Wohn- und Arbeitsflächen.

### Neues Recht: BR 2022

Das neue Reglement, schrittweise in Kraft ab Februar 2025, steuert die bauliche Dichte über:

- **Gebäude- und Fassadenhöhen** (maximale Gebäudevolumen)
- **Grenz- und Gebäudeabstände** (in W2 und W3 einheitlich 6 m grosser Grenzabstand)
- **Grünflächenziffer (GZ)** (Anteil der Parzelle, der unversiegelt bleiben muss)
- **Geschossflächenziffer oberirdisch (GFZo)** in ausgewählten Zonen (Mischzonen, Zonen mit gemeinnützigem Wohnbau)

Die klassische AZ entfällt in W2, W3 und W4 komplett.

### Die Dualitätsphase

Seit der öffentlichen Auflage der OPR im **März 2022** gilt in Thun eine Phase der Vorwirkung. Baugesuche werden sowohl nach altem BR 2002 als auch nach neuem BR 2022 geprüft. Ein Projekt muss in der Regel die Anforderungen beider Regelwerke erfüllen, sofern das neue Recht strenger ist oder die Planungsziele der Revision nicht gefährdet werden.

Für das Tool bedeutet dies: Zonen in Thun werden im Datenmodell mit dem System `dualitaet` oder `hoehen_und_gz` markiert. Die historischen AZ-Werte bleiben als `ausnuetzungsziffer_historisch` in den JSONs erhalten, um die Vergleichbarkeit zu gewährleisten.

---

## Stadt Bern: Stand der Umstellung

Die Stadt Bern arbeitet weiterhin vorwiegend mit der **Baurechtlichen Grundordnung (BGO)**, die nach dem klassischen Modell aus Nutzungszone und Bauklasse funktioniert:

- **Nutzungszonen** legen die erlaubte Art der Nutzung fest (Wohnen, Wohn- und Gewerbe, Kernzone, Altstadtperimeter etc.).
- **Bauklassen A bis E** bestimmen die Dichte und Höhe. Bauklasse A ist die kleinste (2 Geschosse, 7.5 m), Bauklasse D die grösste typische Klasse (5 Geschosse, 16.5 m), Bauklasse E steht für Erhaltungsregime ohne fixe Kennzahl.

### Dualitätscharakter der Bauklasse E

Die Bauklasse E (Erhaltung der bestehenden Bebauungsstruktur) funktioniert de facto nach einem Höhen- und Volumenregime — die bestehende Bebauung ist die Richtgrösse. Im Datenmodell wird sie deshalb dem System `hoehen_und_gz` zugeordnet, auch wenn das im BR-Text nicht explizit so bezeichnet ist.

### Umstellungsstand zu GFZo

Der Stand der Umstellung der Stadt Bern auf GFZo gemäss BMBV ist mit den Fachstellen der Stadt (Amt für Hochbau, Stadtplanung) zu verifizieren. Das Datenmodell ist darauf vorbereitet: Pro Bauklasse sind sowohl `ausnuetzungsziffer` als auch `geschossflaechenziffer_oberirdisch` als optionale Felder hinterlegt.

---

## Konsequenzen für das Datenmodell

Die fachliche Situation wird im Datenmodell über die Enum-Klasse `BemessungsSystem` in `baureglement.py` abgebildet.

### Die vier Systemwerte

| System | Beschreibung | Typische Gemeinden |
|---|---|---|
| `AZ` | Klassische Ausnützungsziffer, altes Recht | Ländliche Berner Gemeinden, Stadt Bern (mehrheitlich) |
| `GFZo` | Geschossflächenziffer oberirdisch, IVHB-konform | Gemeinden mit revidierter BNO |
| `hoehen_und_gz` | Steuerung über Gebäudehöhen und Grünflächenziffer | Thun W2/W3/W4 nach BR 2022, Erhaltungszonen |
| `dualitaet` | Übergangsphase, altes und neues Recht parallel | Thun seit März 2022 |

### Pro Zone, nicht pro Gemeinde

Entscheidend ist, dass das `system`-Feld **pro Zone** gesetzt ist, nicht nur pro Gemeinde. Eine Gemeinde kann in einer Zone bereits das neue Recht anwenden und in einer anderen noch das alte. Der Gemeinde-Default (`system_default` im JSON) ist nur der Fallback, falls eine Zone kein eigenes System trägt.

### Die drei Berechnungspfade

Der `PotenzialBerechner` in `analyse/potenzial.py` kennt drei Pfade:

1. **Mit Kennzahl (AZ oder GFZo):** Theoretisch zulässige BGF = Parzellenfläche × Kennzahl. Prioritätsregel: Falls GFZo hinterlegt ist, wird diese bevorzugt, sonst AZ.
2. **Höhen + GZ:** Keine direkte Kennzahl, stattdessen qualitative Ausgabe der Gebäudehöhen, Grenzabstände und Grünflächenziffer.
3. **Keine Kennzahl vorhanden:** Status `NICHT_BERECHENBAR`, präzise Fehlermeldung mit Zonen- und Systemangabe.

### Dokumentation in den Daten

Die Baureglement-JSONs pflegen neben den Kennzahlen auch Metadaten:

- `rechtsgrundlage`: Welches Regelwerk (z.B. "BR 2022 Art. 23")
- `gueltig_ab`: Ab welchem Datum das neue Recht greift
- `hinweise`: Fachliche Erläuterung (z.B. Erhaltungsregime, Uferzonen-Einschränkung)
- `ausnuetzungsziffer_historisch`: Der historische AZ-Wert, wenn Gemeinde umgestellt hat

Diese Felder erlauben dem Tool, auch bei fehlenden Kennzahlen **aussagekräftige Berichte** zu erzeugen.

---

## Offene Punkte und Verifikationsbedarf

Die folgenden Punkte sind mit Fachpersonen (Architekturbüros, kantonale oder kommunale Fachstellen) zu verifizieren, bevor das Tool produktiv genutzt werden kann:

**Stadt Bern:**
- Exakter Umstellungsstand auf GFZo pro Bauklasse-Zone-Kombination
- Konkrete AZ- bzw. GFZo-Werte pro Bauklasse und Zone
- Grenzabstände klein/gross pro Bauklasse

**Stadt Thun:**
- Konkrete Gebäudehöhen pro Wohnzone (W2, W3, W4)
- Grünflächenziffer-Werte gemäss Merkblatt der Stadt Thun
- GFZo-Werte für Mischzonen und Zonen mit gemeinnützigem Wohnbau
- Kern- und Gewerbezonen im BR 2022

**Generell:**
- Systematische Integration weiterer Gemeinden (Köniz, Steffisburg, Münsingen)
- Validierung des Matching-Verhaltens bei Zonennamen, die von der Gemeinde-Praxis abweichen

---

## Quellenverzeichnis

### Kantonale Rechtsgrundlagen

- Kanton Bern: Baugesetz (BauG), BSG 721.0
- Kanton Bern: Bauverordnung (BauV), BSG 721.1
- Kanton Bern: Verordnung über die Begriffe und Messweisen im Bauwesen (BMBV)
- Interkantonale Vereinbarung über die Harmonisierung der Baubegriffe (IVHB), BSG 721.2-1

### Kommunale Baureglemente

- Stadt Bern: Baurechtliche Grundordnung (BGO)
  https://www.bern.ch/themen/planen-und-bauen/nutzungsplanung/baurechtliche-grundordnung

- Stadt Thun: Baureglement BR 2002 (alte Fassung) und BR 2022 (neue Fassung)
  https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision

### Technische Datenquellen

- ÖREB-Webservice Kanton Bern: https://www.oereb2.apps.be.ch/
- ÖREB-Schema V2.0: Bundesamt swisstopo
- swisstopo SearchAPI: https://api3.geo.admin.ch/rest/services/api/SearchServer

### Fachliche Erläuterungen

- Kanton Bern, Abteilung Bauen: Rechtliche Grundlagen
- Stadt Thun: "Ausnützungsziffer fällt – mehr Schutz für Bäume" (Kommunikation zur Ortsplanungsrevision)
- Stadt Thun: "Bauvorhaben richtig vorbereiten – Ein Leitfaden für Gesuchstellende"

---

_Dokument-Stand: April 2026. Aktualisierung bei Änderungen im kantonalen oder kommunalen Recht erforderlich. Das Tool selbst bleibt von diesen Rechtsänderungen unabhängig lauffähig — es genügen Anpassungen der Baureglement-JSON-Dateien im Ordner `daten/baureglemente/`._
