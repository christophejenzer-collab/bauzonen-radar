# test_fuenfzig_adressen.ps1 - Stresstest mit 50 echten Adressen
#
# Ziel: Robustheits-Pruefung auf groesserer Stichprobe.
# Mix aus allen Gemeinden + Zonen + Edge-Cases.
#
# Verteilung:
#   - Bern:       22 Adressen (alle Bauklassen, Altstadt, BK_E, UeO, IG)
#   - Thun:       15 Adressen (W2-W4, WA3-WA5, ZPP)
#   - Oberhofen:   8 Adressen (W1, W2, M1, M2)
#   - Edge-Cases:  5 Adressen (umliegende Gemeinden)
#
# Aufruf vom Projekt-Root:
#   .\tests\test_fuenfzig_adressen.ps1
#
# Laufzeit: ~5-10 Minuten (50 OEREB-Calls)

$ProjektRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$ProjektRoot\src\bauzonenradar"

Write-Host ""
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host "# Stresstest: 50 Adressen aus dem Berner Raum" -ForegroundColor Cyan
Write-Host "# Geschaetzte Laufzeit: 5-10 Minuten" -ForegroundColor Cyan
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host ""

$startzeit = Get-Date

# Format: @(Region, Adresse, Erwartung)
$testfaelle = @(
    # ===== STADT BERN (22) =====
    # Bauklasse 2-3 (klassische Wohnquartiere)
    @("Bern",      "Murifeldweg 8, 3006 Bern",            "BK_3 Wohnzone"),
    @("Bern",      "Sulgenrain 12, 3007 Bern",            "BK_3 Sulgenbach"),
    @("Bern",      "Brunnmattstrasse 25, 3007 Bern",      "BK_3 Mattenhof"),
    @("Bern",      "Schoenburgstrasse 5, 3013 Bern",      "BK_3 Spitalacker"),
    @("Bern",      "Tellstrasse 4, 3014 Bern",            "BK_3 Breitenrain"),
    # Bauklasse 4-5 (urban dichter)
    @("Bern",      "Effingerstrasse 35, 3008 Bern",       "BK_5 Mattenhof"),
    @("Bern",      "Laupenstrasse 18, 3008 Bern",         "BK_4-5"),
    @("Bern",      "Optingenstrasse 30, 3013 Bern",       "BK_4 Spitalacker"),
    @("Bern",      "Eigerstrasse 60, 3007 Bern",          "BK_4-5"),
    @("Bern",      "Seftigenstrasse 48, 3007 Bern",       "BK_4 Sulgenbach"),
    # Bauklasse 6 (urbaner Kern)
    @("Bern",      "Bahnhofplatz 2, 3011 Bern",           "BK_6 oder K"),
    @("Bern",      "Bundesplatz 3, 3011 Bern",            "BK_6 Bundesgebiet"),
    @("Bern",      "Bollwerk 21, 3011 Bern",              "BK_6 Innenstadt"),
    # BK_E (Erhaltungsbauklasse)
    @("Bern",      "Thunstrasse 40, 3005 Bern",           "BK_E Kirchenfeld"),
    @("Bern",      "Junkerngasse 47, 3011 Bern",          "Altstadt OA"),
    # Altstadt OA/UA (NICHT_MOEGLICH erwartet)
    @("Bern",      "Kramgasse 1, 3000 Bern",              "OA UNESCO"),
    @("Bern",      "Marktgasse 25, 3011 Bern",            "OA UNESCO"),
    @("Bern",      "Gerechtigkeitsgasse 5, 3011 Bern",    "UA Untere Altstadt"),
    @("Bern",      "Postgasse 15, 3011 Bern",             "OA"),
    # Industrie/Gewerbe (BK_4 IG)
    @("Bern",      "Wankdorffeldstrasse 102, 3014 Bern",  "IG Industrie"),
    @("Bern",      "Murtenstrasse 137, 3008 Bern",        "IG/Mischgebiet"),
    # UeO/Spezial
    @("Bern",      "Bumplitzstrasse 100, 3018 Bern",      "BK_SPEZ UeO"),

    # ===== STADT THUN (15) =====
    # Wohnzonen
    @("Thun",      "Frutigenstrasse 25, 3604 Thun",       "W3"),
    @("Thun",      "Allmendstrasse 10, 3600 Thun",        "evtl. ZPP"),
    @("Thun",      "Hofstettenstrasse 8, 3600 Thun",      "W3"),
    @("Thun",      "Lauenenstrasse 4, 3600 Thun",         "W2-W3"),
    @("Thun",      "Steigerhubelstrasse 30, 3604 Thun",   "W3"),
    @("Thun",      "Krattigenstrasse 5, 3604 Thun",       "W3"),
    @("Thun",      "Bostudenstrasse 12, 3604 Thun",       "W2-W3"),
    # Mischzonen WA
    @("Thun",      "Seestrasse 72a, 3604 Thun",           "WA4 Slash-Test"),
    @("Thun",      "Seestrasse 25, 3600 Thun",            "WA4-WA5"),
    @("Thun",      "Bahnhofstrasse 10, 3600 Thun",        "WA5 Zentrum"),
    # Altstadt/Schutz
    @("Thun",      "Berntorstrasse 4, 3600 Thun",         "W2 mit UeO"),
    @("Thun",      "Hauptgasse 50, 3600 Thun",            "Altstadt-Bereich"),
    @("Thun",      "Obere Hauptgasse 30, 3600 Thun",      "Altstadt Aarefeld"),
    # Industrie/Gewerbe
    @("Thun",      "Schoreinhubelstrasse 1, 3604 Thun",   "Arbeiten A"),
    # Stadtteil Gwatt
    @("Thun",      "Saegeweg 1, 3645 Gwatt",              "Gwatt W2"),

    # ===== OBERHOFEN am Thunersee (8) =====
    @("Oberhofen", "Hauptstrasse 30, 3653 Oberhofen",     "W1 Dorfzentrum"),
    @("Oberhofen", "Alpenstrasse 1, 3653 Oberhofen",      "M2"),
    @("Oberhofen", "Untere Sadelstrasse 1, 3653 Oberhofen", "Wohnzone"),
    @("Oberhofen", "Stationsstrasse 10, 3653 Oberhofen",  "evtl. M oder W"),
    @("Oberhofen", "Schorenstrasse 5, 3653 Oberhofen",    "Wohnzone"),
    @("Oberhofen", "Schlossstrasse 3, 3653 Oberhofen",    "Schloss-Naehe"),
    @("Oberhofen", "Aebnitstrasse 7, 3653 Oberhofen",     "Wohnzone"),
    @("Oberhofen", "Heinrichsbergstrasse 12, 3653 Oberhofen", "Wohnzone Hang"),

    # ===== EDGE-CASES Umliegende Gemeinden (5) =====
    @("Hilterfingen", "Hauptstrasse 35, 3652 Hilterfingen", "kein BR"),
    @("Sigriswil",    "Schwarzeneggstrasse 1, 3654 Gunten", "kein BR (Sigriswil)"),
    @("Spiez",        "Seestrasse 2, 3700 Spiez",            "kein BR"),
    @("Steffisburg",  "Bernstrasse 180, 3612 Steffisburg",   "kein BR"),
    @("Heimberg",     "Bahnhofstrasse 5, 3627 Heimberg",     "kein BR")
)

$nr = 0
$gesamt = $testfaelle.Count
$erfolgreich = 0
$fehler = @()
$kategorien = @{
    "VERBINDLICH"    = 0
    "GROBSCHAETZUNG" = 0
    "NICHT_MOEGLICH" = 0
    "UNBEKANNT"      = 0
}

foreach ($fall in $testfaelle) {
    $nr++
    $region    = $fall[0]
    $adresse   = $fall[1]
    $erwartung = $fall[2]

    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor DarkGray
    Write-Host ("[{0,2}/{1}] {2,-13} | {3}" -f $nr, $gesamt, $region, $adresse) -ForegroundColor Yellow
    Write-Host ("        Erwartung: {0}" -f $erwartung) -ForegroundColor Gray
    Write-Host ("-" * 80) -ForegroundColor DarkGray

    try {
        $output = python analyse_adresse.py $adresse 2>&1 | Out-String
        Write-Host $output

        if ($LASTEXITCODE -eq 0) {
            $erfolgreich++

            # Kategorie aus Output erkennen
            if ($output -match "VERBINDLICH") {
                $kategorien["VERBINDLICH"]++
            } elseif ($output -match "GROBSCHAETZUNG") {
                $kategorien["GROBSCHAETZUNG"]++
            } elseif ($output -match "KEINE BERECHNUNG MOEGLICH|NICHT_BERECHENBAR") {
                $kategorien["NICHT_MOEGLICH"]++
            } else {
                $kategorien["UNBEKANNT"]++
            }
        } else {
            $fehler += "$adresse (Returncode $LASTEXITCODE)"
        }
    } catch {
        Write-Host ("FEHLER: {0}" -f $_.Exception.Message) -ForegroundColor Red
        $fehler += "$adresse ($_)"
    }
}

$endzeit = Get-Date
$dauer = ($endzeit - $startzeit).TotalMinutes

Write-Host ""
Write-Host ""
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host "# ZUSAMMENFASSUNG" -ForegroundColor Cyan
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host ""
Write-Host ("Gesamt:               {0}/{1} erfolgreich" -f $erfolgreich, $gesamt) -ForegroundColor Green
Write-Host ("Laufzeit:             {0:F1} Minuten" -f $dauer) -ForegroundColor Gray
Write-Host ""
Write-Host "Datenqualitaets-Verteilung:" -ForegroundColor Yellow
Write-Host ("  VERBINDLICH:        {0}" -f $kategorien["VERBINDLICH"]) -ForegroundColor Green
Write-Host ("  GROBSCHAETZUNG:     {0}" -f $kategorien["GROBSCHAETZUNG"]) -ForegroundColor Yellow
Write-Host ("  NICHT_MOEGLICH:     {0}" -f $kategorien["NICHT_MOEGLICH"]) -ForegroundColor DarkGray
if ($kategorien["UNBEKANNT"] -gt 0) {
    Write-Host ("  UNBEKANNT:          {0}" -f $kategorien["UNBEKANNT"]) -ForegroundColor Red
}

if ($fehler.Count -gt 0) {
    Write-Host ""
    Write-Host ("Fehlgeschlagen ({0}):" -f $fehler.Count) -ForegroundColor Red
    foreach ($f in $fehler) {
        Write-Host "  - $f" -ForegroundColor Red
    }
}
Write-Host ""
Write-Host "################################################################################" -ForegroundColor Cyan

# Zurueck zum Projekt-Root
Set-Location $ProjektRoot
