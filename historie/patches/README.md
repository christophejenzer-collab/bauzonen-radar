# Historie: Patch-Skripte (Iter 2-4)

Dieser Ordner enthaelt PowerShell-Patches die waehrend Iteration 2 bis 4
genutzt wurden um Code iterativ zu evolvieren. Sie sind **nicht mehr
ausfuehrbar** (sie bauen auf Vorgaenger-Code-Staenden auf die laengst
ueberschrieben sind) und dienen als **Belegspur der iterativen
Entwicklungsmethode** fuer die Projekt-Pruefung.

## Inhalt

| Skript | Zweck | Datum |
|---|---|---|
| `patch_potenzial.ps1` | Drei-Begrenzer-Logik PotenzialBerechner | 29.04.2026 |
| `patch_begrenzer_bugs.ps1` | 4 Bug-Fixes Begrenzer-Logik | 29.04.2026 |
| `patch_thun_json.ps1` | thun.json-Erweiterung WA-Slash + ZPP | 29.04.2026 |
| `patch_gwr_integration.ps1` | GWR-Modul in analysiere() einhaengen | 01.05.2026 |
| `patch_gwr_unvollstaendig.ps1` | GWR-Anzeige bei Datenluecken | 01.05.2026 |
| `patch_potenzial_ergebnis.ps1` | AnalyseErgebnis als Datenklasse | 03.05.2026 |

## Warum hier statt im Root?

Die Patches sind Geschichte, nicht aktiv genutzter Code. Im Repo-Root
wirken sie wie laufende Werkzeuge. Im Ordner `historie/patches/` zeigen
sie den Entwicklungsweg ohne die taegliche Sicht zu verstopfen.

## Aufbau eines Patch-Skripts (typisch)

Jedes Skript folgt einem aehnlichen Muster:

1. Backup der Ziel-Datei (`.bak_*`)
2. String-Replace mit eindeutigen Ankern
3. Syntax-Check via `python -m py_compile`
4. Rollback aus Backup bei Fehler
5. Verifikation mit Smoke-Test

Diese Methode ermoeglichte iterative Aenderungen mit hoher Sicherheit
und ohne git-Konflikte zwischen Backend (Christophe) und Frontend
(Fabienne) waehrend Iter 4.

## Stand 12.05.2026

Mit der Iter-5-Abschluss-Session ist diese Patch-basierte Methode
verbessert worden: ab Iter 5 werden Python-Patch-Skripte mit
integrierter Idempotenz-Pruefung verwendet (siehe Commit-Historie).
