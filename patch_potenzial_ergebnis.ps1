# ============================================================================
# Patch: analyse_adresse.py mit AnalyseErgebnis-Datenklasse
# ============================================================================
# Trennt die Pipeline in:
#   - analysiere(adresse) -> AnalyseErgebnis  (Berechnung, kein Print)
#   - drucke_bericht(ergebnis)                (CLI-Output)
#   - main()                                  (CLI-Eintrittspunkt)
#
# Dadurch kann die Streamlit-GUI dieselbe analysiere()-Funktion nutzen
# und das Ergebnis-Objekt grafisch darstellen.
#
# Voraussetzung: analyse_adresse.py.NEU muss im Projekt-Root liegen
# (geliefert ueber den Chat).
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Patch: analyse_adresse.py mit AnalyseErgebnis-Datenklasse" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$ZielDatei = "src\bauzonenradar\analyse_adresse.py"
$NeueDatei = "analyse_adresse.py.NEU"
$BackupDatei = "src\bauzonenradar\analyse_adresse.py.bak_potenzial_ergebnis"

# Vorbedingungen pruefen
if (-not (Test-Path $ZielDatei)) {
    Write-Host "FEHLER: $ZielDatei nicht gefunden." -ForegroundColor Red
    Write-Host "Bist du im Projekt-Root (C:\Tools\bauzonen-radar)?" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $NeueDatei)) {
    Write-Host "FEHLER: $NeueDatei nicht gefunden." -ForegroundColor Red
    Write-Host "Lege die neue Datei zuerst ins Projekt-Root." -ForegroundColor Yellow
    exit 1
}

# Backup erstellen
Write-Host "1. Backup erstellen..." -ForegroundColor Green
Copy-Item -Path $ZielDatei -Destination $BackupDatei -Force
Write-Host "   -> $BackupDatei" -ForegroundColor Gray

# Neue Datei kopieren
Write-Host ""
Write-Host "2. Neue Datei einsetzen..." -ForegroundColor Green
Copy-Item -Path $NeueDatei -Destination $ZielDatei -Force
Write-Host "   -> $ZielDatei aktualisiert" -ForegroundColor Gray

# Syntax-Check
Write-Host ""
Write-Host "3. Syntax-Check..." -ForegroundColor Green
$syntaxOk = $true
try {
    python -c "import ast; ast.parse(open('$($ZielDatei.Replace('\','/'))', encoding='utf-8').read()); print('Syntax OK')"
    if ($LASTEXITCODE -ne 0) {
        $syntaxOk = $false
    }
} catch {
    $syntaxOk = $false
}

if (-not $syntaxOk) {
    Write-Host "   FEHLER: Syntax-Check fehlgeschlagen!" -ForegroundColor Red
    Write-Host "   Stelle Original wieder her..." -ForegroundColor Yellow
    Copy-Item -Path $BackupDatei -Destination $ZielDatei -Force
    exit 1
}

# Smoke-Test mit einer sicheren Adresse
Write-Host ""
Write-Host "4. Smoke-Test (Thunstrasse 40, 3005 Bern)..." -ForegroundColor Green
Push-Location src\bauzonenradar
try {
    $output = python analyse_adresse.py "Thunstrasse 40, 3005 Bern" 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   FEHLER: Smoke-Test fehlgeschlagen!" -ForegroundColor Red
        Write-Host $output -ForegroundColor Yellow
        Pop-Location
        Write-Host ""
        Write-Host "   Stelle Original wieder her..." -ForegroundColor Yellow
        Copy-Item -Path $BackupDatei -Destination $ZielDatei -Force
        exit 1
    }
    # Pruefe ob "EMPFEHLUNG" im Output ist (Sanity-Check)
    if ($output -notmatch "EMPFEHLUNG") {
        Write-Host "   WARNUNG: Output enthaelt kein EMPFEHLUNG-Block!" -ForegroundColor Yellow
        Write-Host $output
    } else {
        Write-Host "   Smoke-Test OK (EMPFEHLUNG-Block vorhanden)" -ForegroundColor Gray
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "FERTIG. analysiere() gibt jetzt AnalyseErgebnis zurueck." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Naechste Schritte:" -ForegroundColor Yellow
Write-Host "  1. Stresstest 12 Adressen laufen lassen:" -ForegroundColor Yellow
Write-Host "     .\tests\test_zwoelf_adressen.ps1" -ForegroundColor Gray
Write-Host "  2. Falls OK: NEU-Datei kann geloescht werden:" -ForegroundColor Yellow
Write-Host "     Remove-Item analyse_adresse.py.NEU" -ForegroundColor Gray
Write-Host "  3. Fabienne kann GUI bauen mit:" -ForegroundColor Yellow
Write-Host "     from bauzonenradar.analyse_adresse import analysiere" -ForegroundColor Gray
Write-Host ""
