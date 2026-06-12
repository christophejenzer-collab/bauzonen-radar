# Robustheit gegen falsche Bedienung

Dieses Dokument dokumentiert das Verhalten des Tools bei unerwarteten
oder fehlerhaften Eingaben. Es adressiert die Dozenten-Anforderung:
*"Kann das Programm mit falscher Bedienung zum Absturz gebracht werden?"*

**Antwort**: Nein. Drei kritische Edge-Cases wurden getestet, alle
werden sauber abgefangen.

---

## Test-Setup

Alle Tests wurden im CLI-Modus durchgefuehrt:

```powershell
cd C:\Tools\bauzonen-radar\src\bauzonenradar
python analyse_adresse.py "<eingabe>"
```

Datum der Tests: 12.06.2026
Python-Version: 3.13
Plattform: Windows 11 PowerShell

---

## Test 1 — Leere Eingabe

### Eingabe
```
python analyse_adresse.py ""
```

### Output
```
Verwendung: python analyse_adresse.py "Strasse Nr, PLZ Ort"
Beispiele:
  python analyse_adresse.py "Kramgasse 49, 3011 Bern"
  python analyse_adresse.py "Rathausplatz 1, 3600 Thun"
  python analyse_adresse.py "Thunstrasse 40, 3005 Bern"
```

### Bewertung
✅ **Robust.** Das Tool erkennt den leeren String, gibt eine kurze
Hilfe mit drei realistischen Beispiel-Adressen aus und beendet
sauber. Kein Crash, kein Stacktrace. Benutzerfuehrung ist klar.

---

## Test 2 — Unsinnige Eingabe

### Eingabe
```
python analyse_adresse.py "asdfasdf"
```

### Output
```
======================================================================
Bauzonen-Radar - Analyse fuer: asdfasdf
======================================================================
Keine Parzelle gefunden fuer diese Adresse.
```

### Bewertung
✅ **Robust.** Die swisstopo SearchAPI gibt keinen Treffer fuer
"asdfasdf" zurueck. Das Tool meldet das klar mit "Keine Parzelle
gefunden fuer diese Adresse." und beendet sauber.

Keine Endlosschleife, keine Exception, kein unverstaendlicher
Fehlertext.

---

## Test 3 — Adresse ausserhalb Kanton Bern

### Eingabe
```
python analyse_adresse.py "Bahnhofstrasse 1, 5000 Aarau"
```

### Output
```
======================================================================
Bauzonen-Radar - Analyse fuer: Bahnhofstrasse 1, 5000 Aarau
======================================================================
Keine Parzelle gefunden fuer diese Adresse.
```

### Bewertung
✅ **Robust.** Die Adresse existiert zwar (Aarau), aber das Tool
ist auf den Kanton Bern beschraenkt (OEREB-Webservice nur fuer BE).
Die Antwort ist konsistent mit Test 2 - das Tool meldet "Keine
Parzelle gefunden" und beendet sauber.

---

## Weitere Robustheits-Massnahmen im Code

### Im GWR-Modul (`datenquellen/gwr.py`)

```python
# Retry-Logic mit exponentialem Backoff bei API-Fehlern
def _http_get_json(url, retries=2):
    for versuch in range(retries + 1):
        try:
            ...
        except urllib.error.URLError:
            zeit.sleep(2 ** versuch)  # 1s, 2s, 4s
```

Transiente API-Fehler werden automatisch wiederholt. Erst nach drei
fehlgeschlagenen Versuchen wird ein Fehler ausgegeben.

### Im Massen-Analyse-Modul (`gemeinde_analyse.py`)

```python
# KeyboardInterrupt-sicheres Cache-Schreiben
try:
    ergebnis = analysiere_per_egrid(egrid, ...)
    cache.speichere(ergebnis)
except KeyboardInterrupt:
    print("Abbruch durch Benutzer - Cache bleibt konsistent")
    raise
```

Auch ein Strg+C waehrend einer Massen-Analyse hinterlaesst keinen
korrupten Cache. Die SQLite-Transaktionen sind atomar.

### Im Reglement-Loader (`baureglement.py`)

```python
if not reglement_pfad.exists():
    return None  # statt FileNotFoundError
```

Fehlende Reglemente fuehren nicht zum Crash, sondern zum sauberen
`Datenqualitaet.NICHT_MOEGLICH`-Pfad.

### In der Potenzialberechnung (`analyse/potenzial.py`)

```python
# Defensive Schraegdach-Bonus-Berechnung
try:
    bonus = berechne_dachbonus(zone)
except ValueError:
    bonus = 0  # Konservativ: kein Bonus statt Crash
```

---

## Stresstest zur Verifikation

Zusaetzlich zur Edge-Case-Robustheit wurde ein **50-Adressen-
Stresstest** durchgefuehrt (siehe `tests/test_fuenfzig_adressen.ps1`):

```
Resultat: 48/50 erfolgreich (96%)
Laufzeit: ca. 1.7 - 2.2 Minuten

Verteilung:
- VERBINDLICH:     6 Adressen
- GROBSCHAETZUNG: 21 Adressen
- NICHT_MOEGLICH: 21 Adressen
- API-Fehler:      2 Adressen (transient, beim 2. Versuch erfolgreich)
```

Die zwei Ausfaelle waren transiente API-Fehler ohne Code-Bug -
beim zweiten Versuch liefen sie problemlos durch. Das hat zur
Iter-5-Entscheidung gefuehrt, Throttling + Retry-Logic in die
Massen-Analyse einzubauen.

---

## Massen-Analyse-Stresstest

Der bisher groesste Robustheits-Test war die vollstaendige Analyse
der Stadt Thun:

```
8534 Parzellen analysiert
0 Programm-Abbrueche
440 API-Fehler abgefangen (5%, alle korrekt behandelt)
4h30 Laufzeit ohne Aufsicht
```

Bei diesem Lauf wurden vier Grossstadt-Bugs aufgedeckt (siehe
`journal.md`, Iter 6) und gefixt. Seitdem laeuft das System
robust auch fuer Grossstaedte durch.

---

## Bewusst nicht abgedeckt

Folgende Szenarien werden NICHT vom Tool abgefangen, weil sie
ausserhalb der Verantwortung der Anwendung liegen:

- **Komplett offline**: Wenn weder Internet noch Cache verfuegbar
  sind, kann das Tool naturgemaess nichts analysieren. Es meldet
  einen API-Timeout und beendet sauber.
- **Korrupter Cache**: Bei manuell beschaedigter SQLite-Datei
  wird ein Fehler ausgegeben. Loesung: Cache loeschen und neu
  starten (CLI-Flag `--no-cache`).
- **Veraenderte API-Schnittstelle**: Falls swisstopo die SearchAPI
  oder OEREB-Webservice fundamental aendert, muesste der Code
  angepasst werden. Das ist nicht durch Eingabe-Validierung loesbar.

---

## Fazit

Das Tool ist **robust gegen typische Benutzerfehler**:

- Leere Eingaben werden mit Hilfe-Output abgefangen
- Unsinnige Eingaben werden konsistent mit "Keine Parzelle gefunden"
  beantwortet
- Adressen ausserhalb des unterstuetzten Kantons werden sauber
  abgewiesen
- API-Fehler werden mit Retry-Logic abgefangen
- Massen-Analysen sind KeyboardInterrupt-sicher
- Korrupte oder fehlende Reglemente fuehren zum sauberen
  NICHT_MOEGLICH-Pfad statt zum Crash

Diese Robustheit ist Ergebnis iterativer Verbesserungen ueber
sieben Iterationen (siehe `journal.md`).
