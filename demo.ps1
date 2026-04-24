# demo.ps1 — Fuehrt alle verifizierten Test-Adressen durch.
# Nuetzlich fuer Demo und Regressions-Test nach Code-Aenderungen.

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Bauzonen-Radar Demo: 10 Adressen" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$adressen = @(
    "Kramgasse 1, 3000 Bern",
    "Kramgasse 49, 3011 Bern",
    "Junkerngasse 47, 3011 Bern",
    "Marktgasse 1, 3011 Bern",
    "Bundesgasse 26, 3011 Bern",
    "Thunstrasse 40, 3005 Bern",
    "Rathausplatz 1, 3600 Thun",
    "Hirschweg 7, 3604 Thun",
    "Dorfstrasse 10, 3095 Spiegel",
    "Untere Sadelstrasse 1, 3653 Oberhofen"
)

foreach ($adresse in $adressen) {
    Write-Host ""
    Write-Host "----- $adresse -----" -ForegroundColor Yellow
    python analyse_adresse.py $adresse
    Write-Host ""
}

Write-Host "Demo fertig - 10 Adressen verarbeitet." -ForegroundColor Green "Bundesgasse 26, 3011 Bern"