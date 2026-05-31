\## ✅ Neue Funktionalitäten (23.05.2026)

\*\*Grossstadt-Tauglichkeit (Stadt Thun)\*\*
Die Massen-Analyse läuft jetzt auch für ganze Städte. Pilotlauf
Stadt Thun mit 8534 Parzellen lief in 4h30 fehlerfrei durch und
identifizierte 890 Verdichtungs-, 354 Neugeschäft- und 1514
Ersatzneubau-Kandidaten.

\*\*Baujahr-Spalte im Excel-Export\*\*
Jede Parzelle zeigt jetzt das älteste GWR-Baujahr (mit Bauperiode-
Code als Fallback). Bei Verdichtungs-Objekten lassen sich so alte
Bausubstanzen mit hohem Ersatzneubau-Hebel direkt erkennen
(Thun: 540 von 890 Verdichtungs-Objekten vor 1980 gebaut).

\*\*Neue Kategorie KLEINPARZELLE\*\*
Parzellen zwischen 200 und 500 m² werden neu als KLEINPARZELLE
klassifiziert: neutral, ausserhalb der Fokus-Reiter (Verdichtung/
Neugeschäft/Ersatzneubau), aber sichtbar in der Gesamtliste.
Umsetzt den Architekten-Hinweis: kleine Grundstücke sind für die
Verdichtungs-Analyse weniger relevant, sollen aber nicht
weggelassen werden.

\*\*Karten-Link auf map.geo.admin.ch\*\*
Der Karten-Direktlink in der Excel zeigt jetzt auf den eidg.
Kartendienst (login-frei). Der vorherige Berner Grundbuch-Link
existiert nicht mehr — der Kanton BE hat die freie Direktabfrage
zum 1.9.2025 abgeschafft (Eigentumsauskunft jetzt nur noch über
GRUDIS public mit AGOV-Login). Saubere Anpassung an externe
Änderung.

---

\## ✅ Neue Funktionalitäten (12.05.2026)

\*\*Massen-Analyse einer ganzen Gemeinde\*\*
Statt einzelne Adressen abzufragen, kann jetzt eine komplette Gemeinde
in einem Durchgang analysiert werden. Pilotlauf Oberhofen am Thunersee
(1176 Parzellen) lief in 41 Minuten fehlerfrei durch und identifizierte
170 hochwertige Verdichtungs-, Ersatzneubau- und Bestandsschutz-Kandidaten.

\*\*Strukturierte Excel-Auswertung mit sechs Themen-Reitern\*\*
Die Ergebnisse einer Gemeinde-Analyse werden als Excel-Datei mit
sechs Reitern bereitgestellt: Statistik-Übersicht, Verdichtung,
Neugeschäft, Ersatzneubau, Ausgereizt und Gesamtliste. Pro Parzelle
sind Direktlinks zu GRUDIS für die manuelle Eigentümer-Abfrage enthalten.

\*\*Geschäftslogische Klassifikation aller Parzellen\*\*
Jede Parzelle wird automatisch einer von sieben Kategorien zugeordnet
(Verdichtung, Neugeschäft, Ersatzneubau, Ausgereizt, Unauffällig,
Ausschluss Reglement, Ausschluss zu klein). Die Schwellenwerte sind
als nachvollziehbare Konstanten dokumentiert und werden mit einem
Fach-Architekten verifiziert.

\*\*Bodenbedeckungs-Filter zur Datenbereinigung\*\*
Strassen-Parzellen und grosse Waldflächen, die im Bauzonen-Kataster
fälschlich als Bauzone gelten, werden über die offizielle Strassen-
Datenbank (swissTLM3D) und die BFS-Arealstatistik erkannt und sauber
ausgeschlossen. Im Pilotlauf wurden 23 Falsch-Treffer im "Neugeschäft"
korrekt umklassifiziert.

\## 🔧 Verbesserungen \& Qualität

\*\*GWR-Anbindung über EGRID statt Adress-Label\*\*
Die Gebäudedaten werden jetzt direkt über die Grundstück-ID und die
Koordinate abgefragt — viel zuverlässiger als der vorherige Weg über
das Adress-Label. Bebaute Parzellen werden so korrekt erkannt, auch
wenn keine Postadresse vorliegt (z.B. bei der Massen-Analyse).

\*\*Lokales Zwischen­speichern aller Analysen (SQLite)\*\*
Jede Parzelle wird einmal analysiert und im lokalen Cache abgelegt.
Wiederholte Läufe oder Abbrüche während einer Massen-Analyse können
nahtlos fortgesetzt werden, ohne dass die externen APIs erneut
belastet werden.

\*\*Drossel- und Wiederholungs-Logik bei externen APIs\*\*
Zwischen Live-Abfragen wird gewartet (0.7 Sek), bei API-Fehlern wird
bis zu dreimal mit ansteigender Wartezeit wiederholt. Eine Massen-
Analyse läuft so auch bei kurzzeitigen Netz- oder Server-Problemen
durch.

\*\*Visuelle Verifikation mit der amtlichen Karte\*\*
Die Resultate einer Stichprobe wurden gegen map.geo.admin.ch geprüft.
Dabei wurden zwei Datenquellen-Lücken sauber identifiziert und im
Tool transparent ausgewiesen: Strassen mit Bauzonen-Eintrag im
Kataster sowie vereinzelte fehlende Gebäudezuordnungen im GWR.

\## ⚠️ Hinweise

\*\*Bekannte Datenquellen-Lücken transparent gekennzeichnet\*\*
Schmale Waldparzellen und vereinzelte bebaute Parzellen mit
ungewöhnlicher Geometrie können von der Bodenbedeckungs- bzw.
GWR-Abfrage nicht erkannt werden. Sie verbleiben in der Kategorie
"Neugeschäft" und sind als Punkte für eine geometrische Verfeinerung
in der nächsten Iteration vorgemerkt.

\*\*Schwellenwerte der Klassifikation sind vorläufig\*\*
Mindestgrössen, Reserve-Schwellen und Bauperioden-Grenzen sind als
gut begründete Anfangswerte gesetzt und werden in einem Fachgespräch
mit einem Architekten verifiziert, bevor das Tool produktiv genutzt
wird.

---

\## ✅ Neue Funktionalitäten (11.05.2026)


\*\*Vollständige GUI-Anbindung des Backends\*\*

Die Streamlit-GUI greift jetzt zuverlässig auf alle berechneten

Bauland-Werte zu. Theoretisch zulässige Geschossflächen, Ausschöpfungsgrad,

Reserve, Zonenangaben und Empfehlungs-Status werden direkt aus dem

Analyse-Ergebnis ausgelesen und im Frontend visualisiert.


\*\*Plausibilitäts-Konflikt zwischen Soll und Ist sichtbar\*\*

Wenn die effektive Bestandsbebauung (aus dem Gebäuderegister) den

berechneten theoretischen Wert übersteigt, wird dies jetzt automatisch

als Hinweis dargestellt — wichtig für Bestandsbauten mit Bestandesschutz.


\## 🔧 Verbesserungen \& Qualität


\*\*Konsolidierte Datenstruktur\*\*

Alle für die Visualisierung relevanten Werte sind nun unter eindeutigen,

einheitlichen Feldnamen direkt im Analyse-Ergebnis verfügbar. Damit

können Frontends ohne Umwege auf die Daten zugreifen.


\*\*Live-Verifikation mit vier Test-Adressen\*\*

Alle drei Datenqualitäts-Pfade (verbindlich / geschätzt / nicht möglich)

und ein Edge-Case (über 200% Ausschöpfung) wurden mit echten Daten

in der GUI verifiziert.


\## ⚠️ Hinweise


\*\*Frontend-Backend-Kompatibilität\*\*

Bestehende Skripte, die den Textbericht oder die Original-Felder nutzen,

funktionieren unverändert weiter — die neuen Felder sind additiv ergänzt.

---

\## ✅ Neue Funktionalitäten (03.05.2026)


\*\*Strukturiertes Analyse-Ergebnis\*\*

Die Analyse-Funktion liefert jetzt zusätzlich zum Textbericht ein

strukturiertes Ergebnis-Objekt mit allen Einzelwerten — Datenqualität,

Zonenangaben, Berechnung, Empfehlung, GWR-Daten und Geokoordinaten

sind direkt zugreifbar.


\*\*WGS84-Koordinaten für Karten-Visualisierung\*\*

Zu jeder analysierten Adresse wird automatisch die Position in

WGS84-Koordinaten berechnet, sodass die Parzelle direkt auf einer

Karte dargestellt werden kann.


\*\*Robusterer Adress-Workflow\*\*

Bei nicht hinterlegten Gemeinden, fehlenden Koordinaten oder

unvollständigen GWR-Daten läuft die Pipeline weiter und liefert

soweit möglich Teilergebnisse mit klaren Status-Hinweisen.


\## 🔧 Verbesserungen \& Qualität


\*\*Trennung Berechnung und Ausgabe\*\*

Die Logik der Berechnung ist sauber getrennt von der Bericht-Ausgabe.

Damit können verschiedene Oberflächen (CLI, Web) dieselbe Analyse

nutzen, ohne den Berechnungs-Code anzupassen.


\*\*Verifikation auf 12 Test-Adressen\*\*

Alle drei Datenqualitäts-Pfade (verbindlich / geschätzt / nicht möglich),

GWR-Plausibilitätskonflikte und Edge-Cases (Altstadt-Schutz,

Planungspflicht-Zonen, fehlende Reglemente) sind durch automatisierten

Stresstest abgedeckt.


\## ⚠️ Hinweise


\*\*Backup-Dateien lokal\*\*

Beim Refactoring wurde eine Sicherheitskopie der vorherigen Version

erstellt (`analyse\_adresse.py.bak\_potenzial\_ergebnis`). Diese liegt

nur lokal und wird nicht ins Repository übernommen.

---

✅ Neue Funktionalitäten

Adressbasierte Parzellenanalyse
Schweizer Adressen können zuverlässig analysiert werden – inkl. Geokodierung, Parzellen‑Identifikation und Zonenbestimmung.
Integration externer Fachdaten
OEREB‑Daten (z. B. Nutzungsplanung, Baulinien, Naturgefahren) sowie – sofern verfügbar – GWR‑Daten zur effektiven Bestandsbebauung werden berücksichtigt.
Gemeindespezifische Reglement‑Logik
Unterstützung verschiedener Bemessungssysteme (z. B. AZ, GFZo, Höhen‑/Geschosszonen‑Modelle) inkl. transparenter Berechnungsgrundlagen.
Datenqualitäts‑Bewertung
Ergebnisse werden klar in drei Qualitätsstufen eingeteilt: verbindlich, geschätzt oder nicht möglich – inklusive konsequenter Regeln, wann welche Stufe gilt.
Automatische Ableitung einer Lage‑ bzw. Potenzialbeurteilung mit nachvollziehbarer Herleitung.

🔧 Verbesserungen \& Qualität

Hohe Robustheit bei API‑Ausfällen
Einzelne externe Dienste können ausfallen, ohne dass die gesamte Analyse abbricht.
Performance‑Optimierungen
Einzelabfragen sind auf kurze Laufzeiten optimiert; wiederholte Analysen liefern konsistente Ergebnisse.
Datenschutz‑konformes Design
Keine Speicherung von personenbezogenen Daten oder Eigentümerinformationen.

⚠️ Hinweise / bekannte Einschränkungen

Für Gemeinden ohne hinterlegte Reglementdaten wird bewusst keine Schein‑Berechnung durchgeführt.
Erweiterte Funktionen wie Gemeinde‑Massenanalysen oder Excel‑Ranglisten sind vorbereitet, aber noch nicht produktiv verfügbar.
