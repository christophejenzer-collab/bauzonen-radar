# patch_potenzial.ps1 - Fixes fuer das 100%-Ausschoepfungs-Problem
#
# Drei Aenderungen in src\bauzonenradar\analyse\potenzial.py:
#   1. _schaetze_ist_bebauung: 40% -> 25% (realistischer fuer Wohnzonen)
#   2. _formatiere_empfehlung: ehrliche Anzeige statt Deckel auf 100%
#   3. Bei Soll <= 0: keine Ausschoepfung berechnen
#
# Aufruf vom Projekt-Root:
#   .\patch_potenzial.ps1
#
# Sicherheitskopie wird automatisch erstellt: potenzial.py.bak

$ErrorActionPreference = "Stop"

$pfad = "src\bauzonenradar\analyse\potenzial.py"
$backup = "$pfad.bak"

if (-not (Test-Path $pfad)) {
    Write-Host "FEHLER: $pfad nicht gefunden. Bist du im Projekt-Root?" -ForegroundColor Red
    exit 1
}

# Sicherheitskopie
Copy-Item $pfad $backup -Force
Write-Host "Backup erstellt: $backup" -ForegroundColor Green

$inhalt = Get-Content $pfad -Raw -Encoding UTF8

# --- Fix 1: Ist-Platzhalter von 40% auf 25% ---
$alt1 = '"""Platzhalter: 40% der Parzellenflaeche."""
        return parzelle.flaeche_m2 * 0.4'
$neu1 = '"""Platzhalter: 25% der Parzellenflaeche.

        Empirisch in Schweizer Wohnzonen sind 20-30% Bebauungsdichte
        typisch (Einfamilien- bis kleine Mehrfamilienhaeuser auf
        normalen Parzellen). 40% war fuer dichte Quartiere zu hoch.

        Bei einer realistischen Datenquelle (swissBUILDINGS3D) wird
        dieser Platzhalter ersetzt.
        """
        return parzelle.flaeche_m2 * 0.25'

if ($inhalt -match [regex]::Escape('return parzelle.flaeche_m2 * 0.4')) {
    $inhalt = $inhalt -replace [regex]::Escape('"""Platzhalter: 40% der Parzellenflaeche."""'), '"""Platzhalter: 25% der Parzellenflaeche (realistischer als 40%)."""'
    $inhalt = $inhalt -replace [regex]::Escape('return parzelle.flaeche_m2 * 0.4'), 'return parzelle.flaeche_m2 * 0.25'
    Write-Host "Fix 1 angewendet: Ist-Platzhalter 40% -> 25%" -ForegroundColor Green
} else {
    Write-Host "Fix 1 NICHT noetig (alter Wert nicht gefunden)" -ForegroundColor Yellow
}

# --- Fix 2: Ehrliche Anzeige der Ausschoepfung ---
$alt2 = '        # Werte sicherstellen (im Bereich 0-100 fuer die Anzeige)
        ausschoepfung = max(0.0, min(100.0, self.ausschoepfungsgrad_prozent))
        reserve = max(0.0, 100.0 - ausschoepfung)
        if self.reserve_prozent is not None:
            reserve = max(0.0, min(100.0, self.reserve_prozent))'

$neu2 = '        # Ehrliche Anzeige: bei Ueber-100% wird das gezeigt mit Warnung
        ausschoepfung_echt = max(0.0, self.ausschoepfungsgrad_prozent)
        ueberzeichnet = ausschoepfung_echt > 100.0
        # Fuer den Balken: auf 100 deckeln, damit er nicht ueberlaeuft
        ausschoepfung = min(100.0, ausschoepfung_echt)
        reserve = max(0.0, 100.0 - ausschoepfung)
        if self.reserve_prozent is not None:
            reserve = max(0.0, min(100.0, self.reserve_prozent))'

if ($inhalt -match [regex]::Escape('ausschoepfung = max(0.0, min(100.0, self.ausschoepfungsgrad_prozent))')) {
    $inhalt = $inhalt.Replace($alt2, $neu2)
    Write-Host "Fix 2a angewendet: Ehrliche Ausschoepfungs-Berechnung" -ForegroundColor Green
} else {
    Write-Host "Fix 2a NICHT noetig (alter Wert nicht gefunden)" -ForegroundColor Yellow
}

# --- Fix 2b: Anzeige des echten Werts mit Warnung ---
$alt2b = '        # Balken Ausschoepfung
        balken_ausschoepfung = self._zeichne_balken(ausschoepfung)
        zeilen.append(
            f"  Ausschoepfung:    {balken_ausschoepfung} {ausschoepfung:5.1f}%"
        )'

$neu2b = '        # Balken Ausschoepfung (ehrlich, mit Warnung wenn >100%)
        balken_ausschoepfung = self._zeichne_balken(ausschoepfung)
        if ueberzeichnet:
            zeilen.append(
                f"  Ausschoepfung:    {balken_ausschoepfung} {ausschoepfung_echt:5.1f}% (!! Ist > Soll - Schaetzung versagt)"
            )
        else:
            zeilen.append(
                f"  Ausschoepfung:    {balken_ausschoepfung} {ausschoepfung:5.1f}%"
            )'

if ($inhalt.Contains($alt2b)) {
    $inhalt = $inhalt.Replace($alt2b, $neu2b)
    Write-Host "Fix 2b angewendet: Warnung bei >100% Ausschoepfung" -ForegroundColor Green
} else {
    Write-Host "Fix 2b NICHT noetig" -ForegroundColor Yellow
}

# --- Fix 3: Vergleichs-Text aktualisieren (40% -> 25%) ---
$alt3 = 'f"  Vergleich Ist (Platzhalter 40% der Parzelle): {ist_schaetzung:.0f} m^2 "'
$neu3 = 'f"  Vergleich Ist (Platzhalter 25% der Parzelle): {ist_schaetzung:.0f} m^2 "'

if ($inhalt.Contains($alt3)) {
    $inhalt = $inhalt.Replace($alt3, $neu3)
    Write-Host "Fix 3 angewendet: Vergleichs-Text 40% -> 25%" -ForegroundColor Green
} else {
    Write-Host "Fix 3 NICHT noetig" -ForegroundColor Yellow
}

# --- Fix 4: Hinweistext beim VERBINDLICHEN Pfad auch aktualisieren ---
$alt4 = '"Ist-Bebauung ist derzeit ein Platzhalter (40% der Parzelle). "'
$neu4 = '"Ist-Bebauung ist derzeit ein Platzhalter (25% der Parzelle). "'

if ($inhalt.Contains($alt4)) {
    $inhalt = $inhalt.Replace($alt4, $neu4)
    Write-Host "Fix 4 angewendet: Bemerkungstext 40% -> 25%" -ForegroundColor Green
} else {
    Write-Host "Fix 4 NICHT noetig" -ForegroundColor Yellow
}

# Schreiben
Set-Content -Path $pfad -Value $inhalt -Encoding UTF8 -NoNewline
Write-Host ""
Write-Host "Fertig! Datei aktualisiert: $pfad" -ForegroundColor Green
Write-Host "Falls etwas schiefgeht: Restore mit:" -ForegroundColor Gray
Write-Host "  Copy-Item $backup $pfad -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "Naechster Schritt: Stichproben-Test laufen lassen" -ForegroundColor Yellow
Write-Host "  .\tests\test_zwoelf_adressen.ps1" -ForegroundColor Yellow
