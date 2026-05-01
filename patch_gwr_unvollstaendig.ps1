# patch_gwr_unvollstaendig.ps1 - Verbesserung der "unvollstaendig"-Anzeige
#
# Aktuell: "GWR-Daten unvollstaendig"
# Neu:     "GWR-Daten unvollstaendig (fehlt: Grundflaeche, Geschosszahl)"
#
# Aufruf vom Projekt-Root:
#   .\patch_gwr_unvollstaendig.ps1

$ErrorActionPreference = "Stop"

$pfad = "src\bauzonenradar\analyse_adresse.py"
$backup = "$pfad.bak4"

if (-not (Test-Path $pfad)) {
    Write-Host "FEHLER: $pfad nicht gefunden." -ForegroundColor Red
    exit 1
}

Copy-Item $pfad $backup -Force
Write-Host "Backup erstellt: $backup" -ForegroundColor Green

$inhalt = Get-Content $pfad -Raw -Encoding UTF8

$alt = '                        else:
                            print(f"  {g.label}: GWR-Daten unvollstaendig")'

$neu = '                        else:
                            fehlende = []
                            if g.grundflaeche_m2 is None:
                                fehlende.append("Grundflaeche")
                            if g.geschosse is None:
                                fehlende.append("Geschosszahl")
                            details = ", ".join(fehlende) if fehlende else "?"
                            print(f"  {g.label}: GWR-Daten unvollstaendig "
                                  f"(fehlt: {details})")'

if ($inhalt.Contains($alt)) {
    $inhalt = $inhalt.Replace($alt, $neu)

    [System.IO.File]::WriteAllText(
        (Resolve-Path $pfad).Path,
        $inhalt,
        (New-Object System.Text.UTF8Encoding $false)
    )

    Write-Host "Patch angewendet: 'unvollstaendig'-Anzeige erweitert" -ForegroundColor Green
} else {
    Write-Host "Patch NICHT noetig oder bereits angewendet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Naechster Schritt: Stresstest" -ForegroundColor Yellow
Write-Host '  .\tests\test_fuenfzig_adressen.ps1' -ForegroundColor White
