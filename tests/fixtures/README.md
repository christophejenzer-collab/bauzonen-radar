# Test-Fixtures: OEREB-XML-Snapshots

Dieser Ordner enthaelt **historische OEREB-Auszuege** als XML-Dateien.

## Inhalt

| Datei | Gemeinde | Stand | Groesse |
|---|---|---|---|
| `extract_thun.xml` | Stadt Thun | 22.04.2026 | 346 KB |
| `extract_pruefen.xml` | Test-Adresse | 22.04.2026 | 144 KB |
| `extract_koeniz.xml` | Koeniz | 22.04.2026 |  73 KB |

## Wofuer

Diese XMLs sind **Snapshots** der OEREB-Webservice-Antworten zu
einem bestimmten Zeitpunkt waehrend der Iteration-1-Entwicklung. Sie
wurden urspruenglich genutzt um den **XML-Parser** ohne Live-API-Zugriff
zu entwickeln und zu testen.

Status: **Einmalig verwendet, aufbewahrt fuer eventuellen spaeteren
Bedarf**.

## Moegliche Verwendungen

- **Offline-Tests**: Parser-Tests ohne Internetzugriff
- **Verteidigungs-Demo**: Falls am Praesentations-Tag der OEREB-Webservice
  ausfaellt, kann die Pipeline mit diesen XMLs demonstriert werden
- **Regressions-Tests**: Vergleich ob eine Code-Aenderung die Pipeline-
  Ausgabe veraendert
- **Schema-Doku**: Zeigt welche OEREB-Felder real geliefert werden

## Wichtig

- **Datenstand 22.04.2026**: OEREB-Antworten aendern sich (z.B. neue
  Bauklassen). Bei aktuellen Tests besser Live-API nutzen.
- **Keine Personendaten**: Die Snapshots enthalten nur Zonen,
  Bauklassen, Geometrie und Naturgefahren - keine Eigentuemerdaten.
- **Reproduzierbarkeit**: Aehnliche XMLs koennen jederzeit neu geholt
  werden via:
  ```
  GET https://www.oereb.bgdi.ch/extract/xml?EGRID=<egrid>
  ```

## Wann diese Dateien aktualisieren

Wenn die Verwendungen oben aktiv genutzt werden (z.B. produktive
Test-Suite mit XML-Fixtures), sollten die Snapshots periodisch
erneuert werden - etwa alle 6 Monate. Sonst nicht noetig.
