Set-Location $PSScriptRoot
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"
Set-Location "$PSScriptRoot\src\bauzonenradar"
Write-Host ""
Write-Host "Bauzonen-Radar bereit." -ForegroundColor Green
Write-Host "Du bist im Modul-Ordner und kannst direkt loslegen, z.B.:" -ForegroundColor Gray
Write-Host '  python analyse_adresse.py "Rathausplatz 1, 3600 Thun"' -ForegroundColor DarkGray
Write-Host ""