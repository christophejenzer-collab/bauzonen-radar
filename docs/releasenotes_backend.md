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



✅ Neue Funktionalitäten

Adressbasierte Parzellenanalyse
Schweizer Adressen können zuverlässig analysiert werden – inkl. Geokodierung, Parzellen‑Identifikation und Zonenbestimmung.
Integration externer Fachdaten
OEREB‑Daten (z. B. Nutzungsplanung, Baulinien, Naturgefahren) sowie – sofern verfügbar – GWR‑Daten zur effektiven Bestandsbebauung werden berücksichtigt.
Gemeindespezifische Reglement‑Logik
Unterstützung verschiedener Bemessungssysteme (z. B. AZ, GFZo, Höhen‑/Geschosszonen‑Modelle) inkl. transparenter Berechnungsgrundlagen.
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

