# patch_thun_json.ps1 - Ergaenzt thun.json mit fehlenden Synonymen
#
# Behebt zwei Datenluecken aus den Stichproben vom 28.04.:
#   - Seestrasse 72a (WA4) -> "Zone im Reglement nicht erfasst"
#     Grund: OEREB liefert "Wohnen/Arbeiten WA4" mit Slash,
#     thun.json hat "Wohnen + Arbeiten WA4" mit Plus.
#   - Allmendstrasse 4 (ZPP) -> "Zone im Reglement nicht erfasst"
#     Grund: ZPP-Zone (Zone mit Planungspflicht) war ueberhaupt nicht erfasst.
#
# Vorgehen: Ersetzt thun.json komplett mit erweiterter Version.
# Backup wird automatisch erstellt: thun.json.bak
#
# Aufruf vom Projekt-Root:
#   .\patch_thun_json.ps1

$ErrorActionPreference = "Stop"

$pfad = "daten\baureglemente\thun.json"
$backup = "$pfad.bak"

if (-not (Test-Path $pfad)) {
    Write-Host "FEHLER: $pfad nicht gefunden. Bist du im Projekt-Root?" -ForegroundColor Red
    exit 1
}

Copy-Item $pfad $backup -Force
Write-Host "Backup erstellt: $backup" -ForegroundColor Green

$neuerInhalt = @'
{
  "gemeinde": "Thun",
  "bfs_nr": 942,
  "kanton": "BE",
  "stand": "2026-04-29",
  "quelle": "Baureglement der Stadt Thun (BR 2022), Februar 2025. Schwager-Tabelle Art. 42.",
  "quelle_url": "https://www.thun.ch/verwaltung/stadtplanung/ortsplanungsrevision",
  "struktur": "kombiniert",
  "system_default": "hoehen_und_gz",
  "hinweis": "Stadt Thun hat mit BR 2022 die klassische AZ in Wohnzonen abgeschafft. Steuerung erfolgt ueber Hoehen, Grenzabstaende, Gebaeudelaenge und Gruenflaechenziffer. Das Feld vergleichswert_az_alt enthaelt den AZ-Wert aus dem alten BR 2002 zur Plausibilitaetspruefung der Schaetzung.",

  "nutzungszonen": {
    "Wohnen W2": {
      "system": "hoehen_und_gz",
      "max_geschosse": 2,
      "max_fassadenhoehe_traufseitig_m": 7.0,
      "max_fassadenhoehe_giebelseitig_m": 11.0,
      "max_fassadenhoehe_anderes_dach_m": 9.0,
      "max_gebaeudelaenge_m": 15.0,
      "grenzabstand_klein_m": 4.0,
      "grenzabstand_gross_m": 8.0,
      "gruenflaechenziffer": 0.45,
      "vergleichswert_az_alt": 0.5,
      "hinweise": "Bei anderen Dachformen als Schraegdach: Volumen und Dachformen koennen innerhalb der Begrenzung durch ein gleichgeneigtes Satteldach mit Fh tr und Fh gi frei gewaehlt werden (Fussnote 3 BR). Im alten BR 2002 galt AZ=0.5.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen W3": {
      "system": "hoehen_und_gz",
      "max_geschosse": 3,
      "max_fassadenhoehe_traufseitig_m": 8.0,
      "max_fassadenhoehe_giebelseitig_m": 12.0,
      "max_fassadenhoehe_anderes_dach_m": 10.0,
      "max_gebaeudelaenge_m": 25.0,
      "grenzabstand_klein_m": 4.0,
      "grenzabstand_gross_m": 10.0,
      "gruenflaechenziffer": 0.45,
      "vergleichswert_az_alt": 0.7,
      "hinweise": "Bei begehbarer Flachdach-Bruestung (offen) erhoeht sich die zulaessige Fassadenhoehe um 1 m (Fussnote 4 BR). Im alten BR 2002 galt AZ=0.7.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen W4": {
      "system": "hoehen_und_gz",
      "max_geschosse": 4,
      "max_fassadenhoehe_traufseitig_m": 11.0,
      "max_fassadenhoehe_giebelseitig_m": 15.0,
      "max_fassadenhoehe_anderes_dach_m": 13.0,
      "max_gebaeudelaenge_m": 30.0,
      "grenzabstand_klein_m": 5.0,
      "grenzabstand_gross_m": 12.0,
      "gruenflaechenziffer": 0.40,
      "vergleichswert_az_alt": 0.9,
      "hinweise": "Im alten BR 2002 galt AZ=0.9.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen + Arbeiten WA3": {
      "system": "hoehen_und_gz",
      "max_geschosse": 3,
      "max_fassadenhoehe_traufseitig_m": 8.0,
      "max_fassadenhoehe_giebelseitig_m": 12.0,
      "max_fassadenhoehe_anderes_dach_m": 10.0,
      "max_gebaeudelaenge_m": 25.0,
      "grenzabstand_klein_m": 4.0,
      "grenzabstand_gross_m": 10.0,
      "gruenflaechenziffer": 0.30,
      "vergleichswert_az_alt": 0.8,
      "hinweise": "Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=0.8.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen/Arbeiten WA3": {
      "system": "hoehen_und_gz",
      "max_geschosse": 3,
      "max_fassadenhoehe_traufseitig_m": 8.0,
      "max_fassadenhoehe_giebelseitig_m": 12.0,
      "max_fassadenhoehe_anderes_dach_m": 10.0,
      "max_gebaeudelaenge_m": 25.0,
      "grenzabstand_klein_m": 4.0,
      "grenzabstand_gross_m": 10.0,
      "gruenflaechenziffer": 0.30,
      "vergleichswert_az_alt": 0.8,
      "hinweise": "OEREB-Synonym (Slash-Schreibweise) zu 'Wohnen + Arbeiten WA3'. Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=0.8.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen + Arbeiten WA4": {
      "system": "hoehen_und_gz",
      "max_geschosse": 4,
      "max_fassadenhoehe_traufseitig_m": 11.0,
      "max_fassadenhoehe_giebelseitig_m": 15.0,
      "max_fassadenhoehe_anderes_dach_m": 13.0,
      "max_gebaeudelaenge_m": 30.0,
      "grenzabstand_klein_m": 5.0,
      "grenzabstand_gross_m": 12.0,
      "gruenflaechenziffer": 0.25,
      "vergleichswert_az_alt": 1.0,
      "hinweise": "Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=1.0.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen/Arbeiten WA4": {
      "system": "hoehen_und_gz",
      "max_geschosse": 4,
      "max_fassadenhoehe_traufseitig_m": 11.0,
      "max_fassadenhoehe_giebelseitig_m": 15.0,
      "max_fassadenhoehe_anderes_dach_m": 13.0,
      "max_gebaeudelaenge_m": 30.0,
      "grenzabstand_klein_m": 5.0,
      "grenzabstand_gross_m": 12.0,
      "gruenflaechenziffer": 0.25,
      "vergleichswert_az_alt": 1.0,
      "hinweise": "OEREB-Synonym (Slash-Schreibweise) zu 'Wohnen + Arbeiten WA4'. Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=1.0.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen + Arbeiten WA5": {
      "system": "hoehen_und_gz",
      "max_geschosse": 5,
      "max_fassadenhoehe_traufseitig_m": 14.0,
      "max_fassadenhoehe_giebelseitig_m": 18.0,
      "max_fassadenhoehe_anderes_dach_m": 16.0,
      "max_gebaeudelaenge_m": 40.0,
      "grenzabstand_klein_m": 6.0,
      "grenzabstand_gross_m": 14.0,
      "gruenflaechenziffer": 0.20,
      "vergleichswert_az_alt": 1.2,
      "arealbonus_ab_flaeche_m2": 3000.0,
      "arealbonus_zusaetzliche_geschosse": 1,
      "hinweise": "Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=1.2. Arealbonus ab 3000 m^2.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Wohnen/Arbeiten WA5": {
      "system": "hoehen_und_gz",
      "max_geschosse": 5,
      "max_fassadenhoehe_traufseitig_m": 14.0,
      "max_fassadenhoehe_giebelseitig_m": 18.0,
      "max_fassadenhoehe_anderes_dach_m": 16.0,
      "max_gebaeudelaenge_m": 40.0,
      "grenzabstand_klein_m": 6.0,
      "grenzabstand_gross_m": 14.0,
      "gruenflaechenziffer": 0.20,
      "vergleichswert_az_alt": 1.2,
      "arealbonus_ab_flaeche_m2": 3000.0,
      "arealbonus_zusaetzliche_geschosse": 1,
      "hinweise": "OEREB-Synonym (Slash-Schreibweise) zu 'Wohnen + Arbeiten WA5'. Mischzone Wohnen + Arbeiten. Im alten BR 2002 galt AZ=1.2. Arealbonus ab 3000 m^2.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Arbeiten A": {
      "system": "hoehen_und_gz",
      "max_geschosse": 4,
      "max_fassadenhoehe_traufseitig_m": 11.0,
      "max_fassadenhoehe_giebelseitig_m": 15.0,
      "max_fassadenhoehe_anderes_dach_m": 13.0,
      "max_gebaeudelaenge_m": 50.0,
      "grenzabstand_klein_m": 5.0,
      "grenzabstand_gross_m": 12.0,
      "gruenflaechenziffer": 0.15,
      "hinweise": "Reine Arbeitszone. Im alten BR 2002 als Arbeitszone gefuehrt.",
      "rechtsgrundlage": "BR Thun 2022, Art. 42"
    },
    "Zone mit Planungspflicht": {
      "system": "nicht_moeglich",
      "max_geschosse": null,
      "hinweise": "Zone mit Planungspflicht (ZPP). Bauwerte werden projektspezifisch in einer Ueberbauungsordnung (UeO) festgelegt. Die Standard-Bauordnung ist NICHT anwendbar. Konkrete Werte muessen aus dem UeO-Dossier der Parzelle entnommen werden, wenn vorhanden. Falls keine UeO existiert, ist die Parzelle aktuell nicht bebaubar.",
      "rechtsgrundlage": "BR Thun 2022, Art. 71-75 (ZPP-Bestimmungen)"
    },
    "ZPP": {
      "system": "nicht_moeglich",
      "max_geschosse": null,
      "hinweise": "Kurzform-Synonym zu 'Zone mit Planungspflicht'. Bauwerte werden projektspezifisch in einer Ueberbauungsordnung (UeO) festgelegt.",
      "rechtsgrundlage": "BR Thun 2022, Art. 71-75"
    }
  }
}
'@

# UTF-8 ohne BOM schreiben
[System.IO.File]::WriteAllText(
    (Resolve-Path $pfad).Path,
    $neuerInhalt,
    (New-Object System.Text.UTF8Encoding $false)
)

Write-Host ""
Write-Host "Fertig! Datei aktualisiert: $pfad" -ForegroundColor Green
Write-Host ""
Write-Host "Neue Eintraege:" -ForegroundColor Yellow
Write-Host "  - 'Wohnen/Arbeiten WA3' (Slash-Synonym)" -ForegroundColor Gray
Write-Host "  - 'Wohnen/Arbeiten WA4' (Slash-Synonym)" -ForegroundColor Gray
Write-Host "  - 'Wohnen/Arbeiten WA5' (Slash-Synonym)" -ForegroundColor Gray
Write-Host "  - 'Zone mit Planungspflicht' (NICHT_MOEGLICH)" -ForegroundColor Gray
Write-Host "  - 'ZPP' (Kurzform-Synonym)" -ForegroundColor Gray
Write-Host ""
Write-Host "Falls etwas schiefgeht: Restore mit:" -ForegroundColor Gray
Write-Host "  Copy-Item $backup $pfad -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "Naechster Schritt: Stichproben-Test laufen lassen" -ForegroundColor Yellow
Write-Host "  .\tests\test_zwoelf_adressen.ps1" -ForegroundColor Yellow
