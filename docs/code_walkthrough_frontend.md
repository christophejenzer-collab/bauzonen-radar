# Code-Walkthrough Frontend (Streamlit-GUI) — fuer die Verteidigung

Dieses Dokument erklaert die Frontend-Datei (`gui/frontend.py` von 
Fabienne) sektionsweise in Klartext. Ziel: bei jeder GUI-Frage 
strukturiert antworten koennen.

---

## TEIL 1: Was die GUI grundsaetzlich macht

```
Anwender oeffnet die Webseite (Browser zeigt Streamlit-Server)
   |
   v
Eingabefeld: "Frutigenstrasse 25, 3604 Thun"
   |
   v
Button "Analysieren" gedrueckt
   |
   v
Frontend ruft Backend-Funktion analysiere() auf
   |
   v
Backend liefert AnalyseErgebnis-Objekt zurueck
   |
   v
Frontend zeigt die Daten in Sektionen:
   - Karte (interaktiv, mit Marker)
   - Parzellen-Info (Gemeinde, Flaeche, Zone)
   - Potenzial-Block (Zahlen + Balken + Lagebeurteilung)
   - GWR-Block (Bestehende Gebaeude)
   - Hinweise & Disclaimer
```

**Wichtig:** Das Frontend hat KEINE eigene Berechnungslogik. Es ruft 
das Backend auf und zeigt die zurueckgegebenen Daten an. Das ist 
die saubere Trennung "Separation of Concerns".

---

## TEIL 2: Die Frontend-Datei in Sektionen

Die Datei ist nach `# ---` -Kommentar-Trennern in klare Sektionen 
unterteilt:

| Sektion | Zeilen | Was sie macht |
|---|---|---|
| 1. Backend-Import | 22-35 | Verbindet das Sichtbare mit dem Rechenwerk |
| 2. Seitenkonfiguration | 37-45 | Streamlit-Setup (Titel, Layout) |
| 3. CSS-Design | 47-180 | Definiert einmal das Aussehen fuer die ganze App |
| 4. Hilfsfunktionen | 182-249 | Kleine Werkzeuge die immer wieder gebraucht werden |
| 5. Header | 251-262 | Titel und Untertitel - immer sichtbar |
| 6. Fehlerbehandlung | 263-269 | Klare Meldung wenn etwas schieflaeuft |
| 7. Eingabe | 271-282 | Eingabefeld, Button und Ladeanzeige |
| 8. Analyse | 284+ | Hauptlogik nach Klick auf Button |

---

## TEIL 3: Sektion fuer Sektion

### Sektion 1: Backend-Import (Z.22-35)

**Was es ist:** Eine try-except-Konstruktion, die das Backend laedt.

```python
try:
    from bauzonenradar.analyse_adresse import analysiere, AnalyseErgebnis
    from bauzonenradar.analyse.potenzial import Datenqualitaet, PotenzialStatus
    BACKEND_OK = True
except ImportError as e:
    BACKEND_OK = False
    IMPORT_ERROR = str(e)
```

**Was es macht in Klartext:** Versucht, das Backend zu laden. Wenn 
das nicht klappt (z.B. weil etwas falsch installiert ist), wird 
das Flag `BACKEND_OK = False` gesetzt. Spaeter (Z.263) zeigt die 
App dann eine klare Fehlermeldung statt zu crashen.

**Warum so:** Defensive Programmierung. Eine GUI darf nie weiss bleiben 
mit kryptischer Fehlermeldung. Wenn das Backend fehlt, soll der 
Anwender wissen WAS fehlt.

---

### Sektion 2: Seitenkonfiguration (Z.37-45)

**Was es ist:** Streamlit-Konfiguration - Titel im Browser-Tab, 
Layout-Breite, Theme.

```python
st.set_page_config(
    page_title="Bauzonen-Radar",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

**Klartext:** Wie wenn ein Webdesigner sagt "die Seite soll Bauzonen-
Radar heissen, breit angeordnet sein, ohne Sidebar". Wird nur einmal 
gesetzt am Anfang.

---

### Sektion 3: CSS-Design (Z.47-180)

**Was es ist:** Das CSS - die Stilvorgaben fuer das Aussehen. Inter-
Schrift, Schwarz-/Rot-Akzent, ruhige Typografie. Sehr eigenstaendig, 
nicht Streamlit-Default.

**Was es macht in Klartext:** Definiert einmal das Aussehen fuer die 
ganze App: 
- Welche Schriftart (Inter)
- Welche Farben (Schwarz, Rot fuer Akzente, ruhige Graustufen)
- Wie Buttons aussehen (eigene Hover-Effekte)
- Wie Sektion-Titel formatiert sind (Smallcaps)
- Wie Trennlinien aussehen (2px schwarz)

**Warum so wichtig:** Streamlit hat ein Default-Aussehen, das sehr 
"techie" wirkt. Fabienne hat ein eigenstaendiges Design entwickelt 
(orientiert an za-ag.ch), das professionell wirkt - genau so wie ein 
Architekt oder Investor das erwartet.

**Klartext-Vergleich:** Wie wenn ein Innenarchitekt einmal entscheidet 
"alle Tueren weiss, alle Fussboeden Eiche, alle Lampen aus Messing", 
und dann gilt das fuer das ganze Haus.

---

### Sektion 4: Hilfsfunktionen (Z.182-249)

**Was es ist:** Vier kleine Werkzeuge, die spaeter immer wieder 
gebraucht werden.

**`lv95_zu_wgs84(ost, nord)`** (Z.184):
Wandelt Schweizer Koordinaten in Welt-Koordinaten um. Wird gebraucht 
fuer die Karten-Anzeige, weil OpenStreetMap WGS84 nutzt.

**`badge_html(datenqualitaet)`** (Z.210):
Erstellt einen farbigen "Badge" (kleines Etikett) je nach 
Datenqualitaet:
- VERBINDLICH = gruener Badge
- GROBSCHAETZUNG = oranger Badge
- NICHT_MOEGLICH = grauer Badge

**`lage_html(status, reserve)`** (Z.219):
Erstellt eine Box mit der verbalen Lagebeurteilung 
("HOHES Verdichtungs-Potenzial"). Farbe richtet sich nach dem Status.

**`zeige_progress_bar(label, prozent, farbe)`** (Z.232):
Erstellt einen visuellen Fortschrittsbalken fuer Ausschoepfung und 
Reserve.

**Klartext-Vergleich:** Wie wenn ein Tischler kleine Standard-Schablonen 
hat (Winkel, Rundungen, Standard-Verbindungen), die er bei jedem 
Moebelstueck wieder verwendet.

---

### Sektion 5: Header (Z.251-262)

**Was es ist:** Der Seitenkopf - "Bauzonen-Radar" gross, Untertitel 
"Analysewerkzeug fuer Bauland-Potenzial", danach die 2px-Trennlinie.

**Was es macht:** Immer sichtbar, bevor irgendwas anderes passiert. 
Gibt der Seite Identitaet.

---

### Sektion 6: Backend-Fehler abfangen (Z.263-269)

**Was es ist:** Wenn das Backend nicht geladen werden konnte 
(BACKEND_OK = False), zeigt diese Sektion eine klare Fehlermeldung 
und beendet die App.

```python
if not BACKEND_OK:
    st.error(f"Backend nicht verfuegbar: {IMPORT_ERROR}")
    st.stop()
```

**Warum so:** Defensive Praxis. Ohne Backend kann das Frontend nichts 
sinnvolles tun - lieber ehrlich sagen "geht nicht weil X fehlt" als 
spaeter crashen.

---

### Sektion 7: Eingabe (Z.271-282)

**Was es ist:** Das Eingabefeld fuer die Adresse plus den 
"Analysieren"-Button.

```python
adresse = st.text_input("Adresse oder Parzelle eingeben")
abschicken = st.button("Analysieren")
```

**Was es macht:** Wartet auf Anwender-Eingabe. Wenn der Button 
gedrueckt wird, ist `abschicken = True` und die Analyse-Sektion 
weiter unten wird ausgefuehrt.

---

### Sektion 8: Analyse (Z.284+)

**Was es ist:** Die Hauptlogik nach Klick auf den Button. 

```python
if abschicken:
    with st.spinner("Analyse laeuft..."):
        ergebnis = analysiere(adresse)
    
    # Dann: alle Sektionen anzeigen
    zeige_karte(ergebnis)
    zeige_parzellen_info(ergebnis)
    zeige_potenzial_block(ergebnis)
    zeige_gwr_block(ergebnis)
    zeige_hinweise(ergebnis)
```

**Was passiert in Klartext:**

1. **Ladeanzeige starten** ("Analyse laeuft...")
2. **Backend rufen**: `analysiere(adresse)` -> liefert AnalyseErgebnis
3. **Karte zeigen**: Interaktive Karte mit Marker auf der Parzelle
4. **Parzellen-Info**: Gemeinde, Flaeche, Zone, Datenqualitaets-Badge
5. **Potenzial-Block**: Zulaessig, Ausschoepfung, Reserve mit Balken
6. **GWR-Block**: Tabelle der bestehenden Gebaeude
7. **Plausibilitaets-Konflikt-Box** (das Highlight): Wenn GWR-Ist 
   den Soll-Wert deutlich uebersteigt, zeigt eine rote Box den 
   Konflikt an
8. **Hinweise & Disclaimer**: Wichtige Warnungen, 
   Haftungsausschluss

---

## TEIL 4: Die wichtigsten Konzepte fuer die Verteidigung

### 1. Backend-Frontend-Trennung (Separation of Concerns)

**Was es bedeutet:** Das Backend rechnet, das Frontend zeigt an. Beide 
sind voellig getrennt.

**Vorteile:**
- GUI und CLI nutzen dieselbe Berechnungslogik
- Keine Code-Duplikation
- Backend kann unabhaengig getestet werden
- Frontend kann ausgetauscht werden (z.B. zu einer mobilen App), 
  ohne Backend zu aendern

**Klartext-Vergleich:** Wie in einem Restaurant - die Kueche kocht, 
der Service serviert. Beide haben klare Rollen. Wenn man den Service 
neu schult (anderes Design), aendert sich am Essen nichts.

### 2. Defensive Programmierung mit Variant-Detection

**Was es ist:** Fabiennes Frontend hat eine Variant-Detection 
implementiert - es prueft, welche Backend-Version vorliegt und passt 
sich an.

**Warum:** Sie hat den Code geschrieben bevor das Backend final war. 
Statt zu raten, prueft sie die Felder zur Laufzeit:

```python
# Statt blind ergebnis.theoretisch_zulaessig_m2 zu lesen:
if hasattr(ergebnis, 'theoretisch_zulaessig_m2'):
    wert = ergebnis.theoretisch_zulaessig_m2
elif hasattr(ergebnis, 'zulaessig_m2'):
    wert = ergebnis.zulaessig_m2
```

**Klartext-Vergleich:** Wie ein universeller Adapter - funktioniert 
mit verschiedenen Steckdosentypen, weil er pruefen kann welcher gerade 
da ist.

### 3. Plausibilitaets-Konflikt-Box (das Iter-4-Highlight)

**Was es ist:** Eine rote Hinweis-Box, die erscheint wenn die 
GWR-Bebauung den Tool-Schaetzwert deutlich uebersteigt.

**Beispiel** (Frutigenstrasse 25):
- Tool schaetzt: 1080 m² Soll
- GWR misst: 1520 m² Ist
- Konflikt-Box: "GWR-Ist (1520 m²) uebersteigt den berechneten 
  Soll-Wert (1080 m²) - klassischer Bestandsschutz-Fall"

**Warum so wichtig:** Das ist der eigentliche INDIKATOR des Tools. Es 
sagt dem Anwender: "Schau hier hin - die Realitaet weicht von der 
Schaetzung ab. Detailpruefung lohnt sich."

**Iter-6-Erkenntnis:** Diese Konflikt-Visualisierung IST das 
Indikator-Konzept. Wir muessen keine erfundene Soll-Zahl liefern - 
es reicht zu zeigen WO Schaetzung und Realitaet auseinanderlaufen.

---

## TEIL 5: Was Fabienne ueber Christophes Code wissen muss

### Drei-Begrenzer-Logik

Sie muss erklaeren koennen (auch wenn er sie nicht selber programmiert 
hat):

```
Drei mathematische Begrenzer fuer das Soll, der kleinste gewinnt:
1. Geometrie: (Laenge - 2*grosser_GA) x (Breite - 2*kleiner_GA)
2. Parzelle: Parzellenflaeche x (1 - Gruenflaechenziffer)
3. GZ:       Parzelle / Geschosszahl

Geschossflaeche = min(diese drei) * Geschosszahl
```

Bei `max_gebaeudelaenge=None` (unbeschraenkt): wird `float("inf")` 
gesetzt. `min()` ignoriert `inf` automatisch.

### Warum Enums statt Strings

`Datenqualitaet` und `PotenzialStatus` sind Enums (Aufzaehlungstypen). 
Vorteile gegenueber Strings:
- Tippfehler werden vom IDE erkannt
- Endliche Menge von Zustaenden ist klar dokumentiert
- Selbstdokumentierend im Code

### Was berechne() zurueckgibt und wie die GUI das konsumiert

`PotenzialBerechner.berechne()` gibt ein `PotenzialErgebnis`-Objekt 
zurueck. Die GUI liest aus diesem Objekt:
- `datenqualitaet` -> bestimmt Badge-Farbe
- `theoretisch_zulaessig_m2` -> Zahl im Potenzial-Block
- `ausschoepfungsgrad_prozent` -> Progress-Bar
- `reserve_prozent` -> Progress-Bar + Lagebeurteilung
- `zonen_betrachtet` -> Zone(n)-Anzeige

### Der 25%-Platzhalter

Wird nur verwendet wenn GWR keine Daten liefert. Empirisch begruendet 
(20-30% typisch fuer Schweizer Wohnzonen). Wir starteten mit 40% in 
Iter 2, korrigierten auf 25% in Iter 3. Bei unbebauten Parzellen 
(NEUGESCHAEFT) konzeptionell falsch - das ist ein Punkt fuer Iter 7.

---

## TEIL 6: Was Christophe ueber Fabiennes Arbeit wissen muss

### Was Requirements-Engineering bedeutet

Requirements-Engineering ist die Disziplin, die Anforderungen an 
Software systematisch erfasst, dokumentiert und nachvollziehbar 
macht.

In unserem Projekt:
- `anforderungen_backend.md`: WAS das Backend koennen muss
- `anforderungen_frontend.md`: WAS die GUI koennen muss
- `requirements_backend.md`: WIE das Backend technisch aufgebaut ist
- `requirements_frontend.md`: WIE die GUI technisch aufgebaut ist

Die Trennung zwischen "anforderungen" (was) und "requirements" (wie) 
ist Fabiennes RE-Pruefungsleistung.

### Wie die GUI-Pipeline funktioniert

```
Adresse eingeben
   |
   v
Streamlit empfaengt das Input
   |
   v
Backend-Funktion analysiere() wird aufgerufen
   |
   v
AnalyseErgebnis kommt zurueck (40 Felder)
   |
   v
GUI liest die Felder und baut die Anzeige:
   - st.map() fuer die Karte
   - st.metric() fuer Zahlen
   - Eigenes CSS fuer Balken
   - HTML-Boxen fuer Lagebeurteilung
```

### Warum CSS-Design statt Streamlit-Default

Streamlit hat einen funktionalen aber "techie" Default-Look 
(blau-grau, Sans-Serif, Standard-Buttons). Das wirkt fuer 
Architekten und Investoren unprofessionell.

Fabienne hat ein eigenstaendiges Design entwickelt:
- Inter-Schrift (modern, professionell)
- Schwarz/Rot-Akzent (klare visuelle Hierarchie)
- Ruhige Typografie (keine Aufmerksamkeits-Konkurrenz)
- Eigene Trennlinien (2px schwarz)
- Smallcaps-Sektion-Titel

Das macht den Tool-Eindruck professionell und glaubwuerdig.

---

## TEIL 7: Wahrscheinliche Fragen + Antworten

### Frage: "Warum Streamlit und nicht Flask/Django?"

**Antwort:** "Streamlit ist fuer Daten-Apps gebaut. Wir brauchen kein 
komplexes Routing, keine User-Verwaltung, keine Datenbank-Anbindung 
auf Frontend-Seite. Streamlit gibt uns Karten, Metriken, Buttons 
out-of-the-box - das passt zum Use-Case. Flask/Django waeren 
Overkill fuer eine analytische Single-Page-App."

### Frage: "Wie wird datenqualitaet aus dem Backend in der GUI dargestellt?"

**Antwort:** "Ueber farbige Badges. Die `badge_html()`-Hilfsfunktion 
nimmt das Datenqualitaet-Enum entgegen und gibt HTML mit der 
passenden Farbe zurueck:
- VERBINDLICH = gruen (verlaessliche Berechnung)
- GROBSCHAETZUNG = orange (Vorsicht, Heuristik)
- NICHT_MOEGLICH = grau (keine Zahl)

Damit sieht der Anwender auf einen Blick, wie verlaesslich das 
Ergebnis ist."

### Frage: "Was passiert wenn das Backend einen Fehler hat?"

**Antwort:** "Zwei Ebenen. Beim Laden der App: try/except um den 
Import - wenn das Backend fehlt, zeigt die App eine klare 
Fehlermeldung und stoppt. Bei der Analyse selbst: das AnalyseErgebnis 
enthaelt ein `fehler`-Feld und ein `warnungen`-Feld - die werden in 
der Hinweise-Sektion am Ende angezeigt. So crasht die GUI nie - sie 
zeigt entweder das Ergebnis oder einen Fehler."

### Frage: "Wie funktioniert die Plausibilitaets-Konflikt-Box?"

**Antwort:** "Sie wird ausgeloest wenn die GWR-Geschossflaeche den 
berechneten Soll-Wert deutlich uebersteigt (Faktor > 1.2). Das 
sind klassische Bestandsschutz-Faelle - Gebaeude die nach altem 
Recht gebaut wurden und heute hoeher/breiter sind als das neue 
Reglement zulassen wuerde. 

Das ist eigentlich das wichtigste Feature der GUI - es macht den 
Unterschied zwischen rechtlich Zulaessigem und tatsaechlich Gebautem 
sichtbar. Genau dort lohnt sich eine Detailpruefung."

---

## TEIL 8: Wichtige Stichwoerter (auswendiglernen)

```
Streamlit:           Python-Framework fuer Daten-Apps
Separation:          Backend rechnet, Frontend zeigt
CSS:                 Eigenes Design statt Streamlit-Default
                     Inter-Schrift, Schwarz/Rot, ruhige Typografie
Variant-Detection:   Frontend prueft Backend-Version zur Laufzeit
Badges:              Farbige Etiketten fuer Datenqualitaet
Konflikt-Box:        Visuelles Highlight bei GWR > Soll
                     IST der Indikator des Tools
Defensive:           try/except, klare Fehlermeldungen
RE-Trennung:         anforderungen_*.md (was) vs requirements_*.md (wie)
```

---

## TEIL 9: Cheat-Sheet fuer den Verteidigungs-Tag

Diese vier Saetze koennt ihr auswendig lernen und in jeder Antwort 
unterbringen, wenn ihr Zeit braucht:

1. **"Bewusste Designentscheidung aus Iteration X..."**
   Zeigt iteratives Vorgehen, nicht zufaellig.

2. **"Wir kommunizieren Unsicherheit ehrlich..."**
   Datenqualitaets-Stufen sind euer Verkaufsargument.

3. **"Das ist Iter-6-Erkenntnis..."**
   Tool als Indikator, Konflikt-Box als zentrale Visualisierung.

4. **"Im Journal als Lessons-Learned dokumentiert..."**
   Selbstreflexion - Bugs werden nicht versteckt.

Bei Fragen wo ihr unsicher seid: **ehrlich sagen** "Das haben wir so 
gemacht weil [...] - im Nachhinein haetten wir [...] machen koennen". 
Selbstreflexion zeigt Reife, defensive Antworten zeigen Schwaeche.
