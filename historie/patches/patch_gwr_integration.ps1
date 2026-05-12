# patch_gwr_integration.ps1 - Integriert GWR-Modul in analyse_adresse.py
#
# Aenderung ist additiv und minimal:
#  - Neuer Import: GwrQuelle (mit try/except wie BKP)
#  - Neuer Schritt 4b nach BKP: GWR-Lookup mit Anzeige
#  - Keine Aenderung an bestehenden Schritten
#
# Aufruf vom Projekt-Root:
#   .\patch_gwr_integration.ps1

$ErrorActionPreference = "Stop"

$pfad = "src\bauzonenradar\analyse_adresse.py"
$backup = "$pfad.bak3"

if (-not (Test-Path $pfad)) {
    Write-Host "FEHLER: $pfad nicht gefunden." -ForegroundColor Red
    exit 1
}

Copy-Item $pfad $backup -Force
Write-Host "Backup erstellt: $backup" -ForegroundColor Green

$inhalt = Get-Content $pfad -Raw -Encoding UTF8

# --- Patch 1: Import nach dem BKP-Import ergaenzen --------------------------
$alt1 = '# BKP-Modul ist optional - wenn es fehlt, laeuft alles ohne BKP-Anreicherung
try:
    from bern_bkp import BernBkpQuelle
    BKP_VERFUEGBAR = True
except ImportError:
    BernBkpQuelle = None  # type: ignore
    BKP_VERFUEGBAR = False'

$neu1 = '# BKP-Modul ist optional - wenn es fehlt, laeuft alles ohne BKP-Anreicherung
try:
    from bern_bkp import BernBkpQuelle
    BKP_VERFUEGBAR = True
except ImportError:
    BernBkpQuelle = None  # type: ignore
    BKP_VERFUEGBAR = False

# GWR-Modul ist optional - wenn es fehlt, laeuft alles ohne GWR-Ist-Werte
try:
    from datenquellen.gwr import GwrQuelle, GwrFehler
    GWR_VERFUEGBAR = True
except ImportError:
    GwrQuelle = None  # type: ignore
    GwrFehler = Exception  # type: ignore
    GWR_VERFUEGBAR = False'

if ($inhalt.Contains($alt1)) {
    $inhalt = $inhalt.Replace($alt1, $neu1)
    Write-Host "Patch 1 angewendet: GWR-Import ergaenzt" -ForegroundColor Green
} else {
    Write-Host "Patch 1 NICHT noetig oder bereits angewendet" -ForegroundColor Yellow
}

# --- Patch 2: Nach BKP-Block (vor Schritt 5) GWR-Block einfuegen -----------
$alt2 = '    print()

    # Schritt 5: Potenzialberechnung (optional mit BKP-Anreicherung)
    berechner = PotenzialBerechner()
    ergebnis = berechner.berechne(parzelle, reglement, bkp_quelle=bkp_quelle)'

$neu2 = '    print()

    # Schritt 4b: GWR-Lookup fuer Ist-Werte (zusaetzliche Information)
    if GWR_VERFUEGBAR:
        try:
            gwr = GwrQuelle()
            gebaeude = gwr.gebaeude_zu_adresse(adresse)
            if gebaeude:
                # Filter auf das/die Gebaeude der gefundenen Parzelle
                gebaeude_parzelle = [g for g in gebaeude if g.egrid == parzelle.egrid]
                if gebaeude_parzelle:
                    print("GWR-Daten (bestehende Bebauung):")
                    summe_geschossflaeche = 0
                    hat_summe = False
                    for g in gebaeude_parzelle:
                        if g.grundflaeche_m2 is not None and g.geschosse is not None:
                            gf = g.geschossflaeche_m2
                            print(f"  {g.label}: "
                                  f"{g.grundflaeche_m2} m^2 x {g.geschosse} Geschosse "
                                  f"= {gf} m^2 Geschossflaeche")
                            if gf is not None:
                                summe_geschossflaeche += gf
                                hat_summe = True
                            if g.anzahl_wohnungen:
                                print(f"    {g.anzahl_wohnungen} Wohnungen, "
                                      f"Baujahr {g.baujahr or g.bauperiode_code or ''}")
                            if g.heizung_saniert_datum and g.heizung_saniert_datum != "-":
                                print(f"    Heizung saniert: {g.heizung_saniert_datum}")
                        else:
                            print(f"  {g.label}: GWR-Daten unvollstaendig")
                    if hat_summe and len(gebaeude_parzelle) > 1:
                        print(f"  SUMME (alle Gebaeude): {summe_geschossflaeche} m^2")
                    print()
                else:
                    print("GWR: Keine Gebaeudedaten fuer diese Parzelle (evtl. unbebaut).")
                    print()
        except GwrFehler as fehler:
            print(f"GWR-Anfrage fehlgeschlagen: {fehler}")
            print()
        except Exception as fehler:
            # Robuster Fallback: GWR-Probleme stoppen die Pipeline nicht
            print(f"GWR-Anfrage uebersprungen ({fehler.__class__.__name__})")
            print()

    # Schritt 5: Potenzialberechnung (optional mit BKP-Anreicherung)
    berechner = PotenzialBerechner()
    ergebnis = berechner.berechne(parzelle, reglement, bkp_quelle=bkp_quelle)'

if ($inhalt.Contains($alt2)) {
    $inhalt = $inhalt.Replace($alt2, $neu2)
    Write-Host "Patch 2 angewendet: GWR-Block in Pipeline integriert" -ForegroundColor Green
} else {
    Write-Host "Patch 2 NICHT noetig oder bereits angewendet" -ForegroundColor Yellow
}

# UTF-8 ohne BOM schreiben
[System.IO.File]::WriteAllText(
    (Resolve-Path $pfad).Path,
    $inhalt,
    (New-Object System.Text.UTF8Encoding $false)
)

Write-Host ""
Write-Host "Fertig! Datei aktualisiert: $pfad" -ForegroundColor Green
Write-Host ""
Write-Host "Falls etwas schiefgeht: Restore mit:" -ForegroundColor Gray
Write-Host "  Copy-Item $backup $pfad -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "Naechster Schritt - Test:" -ForegroundColor Yellow
Write-Host '  python src\bauzonenradar\analyse_adresse.py "Frutigenstrasse 25, 3604 Thun"' -ForegroundColor White
