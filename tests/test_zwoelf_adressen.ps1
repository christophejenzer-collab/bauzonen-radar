# test_zwoelf_adressen.ps1 - Stichproben-Test mit 12 Adressen aus dem Berner Raum
#
# Ziel: Robustheits-Pruefung der gesamten Pipeline ueber drei
# Datenqualitaets-Pfade und drei Gemeinden hinweg.
#
# Aufruf vom Projekt-Root:
#   .\tests\test_zwoelf_adressen.ps1
#
# Erwartung:
# - Stadt Bern: Mix aus VERBINDLICH/GROBSCHAETZUNG/NICHT_MOEGLICH
# - Thun + Oberhofen: meistens GROBSCHAETZUNG oder NICHT_MOEGLICH
# - Edge-Cases: fehlertolerant, mit klarer Meldung wenn Daten fehlen

$ProjektRoot = Split-Path -Parent $PSScriptRoot
Set-Location "$ProjektRoot\src\bauzonenradar"

Write-Host ""
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host "# Stichproben-Test: 12 Adressen aus dem Berner Raum" -ForegroundColor Cyan
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host ""

# Format: @(Region, Adresse, Erwartung)
$testfaelle = @(
    # --- Stadt Bern ---
    @("Bern",      "Effingerstrasse 35, 3008 Bern",      "BK_4/BK_5 - GROBSCHAETZUNG"),
    @("Bern",      "Murifeldweg 8, 3006 Bern",           "BK_E - VERBINDLICH (GFZo)"),
    @("Bern",      "Kramgasse 49, 3011 Bern",            "OA Altstadt - NICHT_MOEGLICH"),
    @("Bern",      "Wankdorffeldstrasse 102, 3014 Bern", "Gewerbe/UeO"),
    # --- Stadt Thun ---
    @("Thun",      "Frutigenstrasse 25, 3604 Thun",      "Standard-Wohnzone"),
    @("Thun",      "Berntorstrasse 4, 3600 Thun",        "Altstadt-Schutz"),
    @("Thun",      "Allmendstrasse 4, 3600 Thun",        "Wohnzone W3"),
    @("Thun",      "Seestrasse 72a, 3604 Thun",          "WA4 (laut ThunGIS heute)"),
    # --- Oberhofen ---
    @("Oberhofen", "Hauptstrasse 30, 3653 Oberhofen",    "Zentrum/Wohn"),
    @("Oberhofen", "Alpenstrasse 1, 3653 Oberhofen",     "Wohnzone"),
    # --- Edge-Cases ---
    @("Gwatt",     "Saegeweg 1, 3645 Gwatt",             "Stadtteil Thun"),
    @("Gunten",    "Schwarzeneggstrasse 1, 3654 Gunten", "Unbekannte Gemeinde")
)

$nr = 0
$gesamt = $testfaelle.Count
$erfolgreich = 0
$fehler = @()

foreach ($fall in $testfaelle) {
    $nr++
    $region    = $fall[0]
    $adresse   = $fall[1]
    $erwartung = $fall[2]

    Write-Host ("=" * 80) -ForegroundColor DarkGray
    Write-Host ("[{0,2}/{1}] {2,-10} | {3}" -f $nr, $gesamt, $region, $adresse) -ForegroundColor Yellow
    Write-Host ("        Erwartung: {0}" -f $erwartung) -ForegroundColor Gray
    Write-Host ("-" * 80) -ForegroundColor DarkGray

    try {
        python analyse_adresse.py $adresse
        if ($LASTEXITCODE -eq 0) {
            $erfolgreich++
        } else {
            $fehler += "$adresse (Returncode $LASTEXITCODE)"
        }
    } catch {
        Write-Host ("FEHLER: {0}" -f $_.Exception.Message) -ForegroundColor Red
        $fehler += "$adresse ($_)"
    }
    Write-Host ""
}

Write-Host ""
Write-Host "################################################################################" -ForegroundColor Cyan
Write-Host ("# Zusammenfassung: {0}/{1} erfolgreich" -f $erfolgreich, $gesamt) -ForegroundColor Cyan
if ($fehler.Count -gt 0) {
    Write-Host ("# Fehlgeschlagen ({0}):" -f $fehler.Count) -ForegroundColor Red
    foreach ($f in $fehler) {
        Write-Host "#   - $f" -ForegroundColor Red
    }
}
Write-Host "################################################################################" -ForegroundColor Cyan

# Zurueck zum Projekt-Root
Set-Location $ProjektRoot
