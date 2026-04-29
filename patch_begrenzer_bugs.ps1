# patch_begrenzer_bugs.ps1 - Fix der zwei Begrenzer-Bugs
#
# Bug 1 (Murifeld): Bei kleinen Parzellen + grossen Grenzabstaenden
# liefert die quadratische Approximation 0 m^2.
#   -> Loesung: Realistischere Parzellen-Form (1:1.5 statt Quadrat)
#
# Bug 2 (Effinger): Bei Gebaeudelaenge=None (unbeschraenkt) bricht
# die Schaetzung komplett ab.
#   -> Loesung: Geometrie-Begrenzer ueberspringen, andere zwei nutzen
#
# Aufruf vom Projekt-Root:
#   .\patch_begrenzer_bugs.ps1

$ErrorActionPreference = "Stop"

$pfad = "src\bauzonenradar\analyse\potenzial.py"
$backup = "$pfad.bak2"

if (-not (Test-Path $pfad)) {
    Write-Host "FEHLER: $pfad nicht gefunden. Bist du im Projekt-Root?" -ForegroundColor Red
    exit 1
}

Copy-Item $pfad $backup -Force
Write-Host "Backup erstellt: $backup" -ForegroundColor Green

$inhalt = Get-Content $pfad -Raw -Encoding UTF8

# --- Fix Bug 2: Bei max_gebaeudelaenge_m = None NICHT komplett abbrechen ---
$alt_b2 = '        if parameter.max_geschosse is None:
            return None
        if parameter.max_gebaeudelaenge_m is None:
            return None'

$neu_b2 = '        if parameter.max_geschosse is None:
            return None
        # Bei unbeschraenkter Gebaeudelaenge (z.B. BK_5 geschlossen) ist
        # der Geometrie-Begrenzer "kein Begrenzer". Wir ueberspringen ihn
        # und nutzen die anderen zwei (Parzelle, GZ).
        gebaeudelaenge_unbeschraenkt = parameter.max_gebaeudelaenge_m is None'

if ($inhalt.Contains($alt_b2)) {
    $inhalt = $inhalt.Replace($alt_b2, $neu_b2)
    Write-Host "Fix Bug 2a angewendet: max_gebaeudelaenge=None bricht nicht mehr ab" -ForegroundColor Green
} else {
    Write-Host "Fix Bug 2a NICHT noetig" -ForegroundColor Yellow
}

# --- Fix Bug 2 (Forts.): Geometrie-Begrenzer nur wenn Laenge bekannt ---
$alt_b2b = '        # Breite-Annahme: Wenn der BKP eine echte Gebaeudetiefe geliefert
        # hat, nutzen wir die statt des pauschalen Defaults. Sonst Default.
        if parameter.bkp_gebaeudetiefe_m is not None:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           parameter.bkp_gebaeudetiefe_m)
            breite_quelle = "BKP"
        else:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           DEFAULT_GEBAEUDEBREITE_M)
            breite_quelle = "Default"
        grundflaeche_geometrie = parameter.max_gebaeudelaenge_m * breite_m'

$neu_b2b = '        # Breite-Annahme: Wenn der BKP eine echte Gebaeudetiefe geliefert
        # hat, nutzen wir die statt des pauschalen Defaults. Sonst Default.
        if gebaeudelaenge_unbeschraenkt:
            # Bei unbegrenzter Laenge ist die Geometrie kein Begrenzer.
            # Setze inf, damit min() in der Begrenzer-Auswahl ihn ignoriert.
            breite_m = (parameter.bkp_gebaeudetiefe_m
                        if parameter.bkp_gebaeudetiefe_m is not None
                        else DEFAULT_GEBAEUDEBREITE_M)
            breite_quelle = "BKP" if parameter.bkp_gebaeudetiefe_m is not None else "Default"
            grundflaeche_geometrie = float("inf")
        elif parameter.bkp_gebaeudetiefe_m is not None:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           parameter.bkp_gebaeudetiefe_m)
            breite_quelle = "BKP"
            grundflaeche_geometrie = parameter.max_gebaeudelaenge_m * breite_m
        else:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           DEFAULT_GEBAEUDEBREITE_M)
            breite_quelle = "Default"
            grundflaeche_geometrie = parameter.max_gebaeudelaenge_m * breite_m'

if ($inhalt.Contains($alt_b2b)) {
    $inhalt = $inhalt.Replace($alt_b2b, $neu_b2b)
    Write-Host "Fix Bug 2b angewendet: Geometrie-Begrenzer bei unbegrenzter Laenge = inf" -ForegroundColor Green
} else {
    Write-Host "Fix Bug 2b NICHT noetig" -ForegroundColor Yellow
}

# --- Fix Bug 1: Realistischere Parzellen-Form (1:1.5 statt Quadrat) ---
$alt_b1 = '        grundflaeche_parzelle = grundflaeche_geometrie
        if (parameter.grenzabstand_klein_m is not None
                and parameter.grenzabstand_gross_m is not None):
            seite_m = parzelle.flaeche_m2 ** 0.5
            nutzbare_seite = max(0, seite_m - 2 * parameter.grenzabstand_klein_m)
            nutzbare_seite_lang = max(0, seite_m - 2 * parameter.grenzabstand_gross_m)
            grundflaeche_parzelle = nutzbare_seite * nutzbare_seite_lang'

$neu_b1 = '        grundflaeche_parzelle = grundflaeche_geometrie
        if (parameter.grenzabstand_klein_m is not None
                and parameter.grenzabstand_gross_m is not None):
            # Annahme: typische Parzelle ist nicht quadratisch sondern
            # eher rechteckig im Verhaeltnis 1:1.5 (laengere Seite zur
            # Strasse hin). Das ist realistischer als die quadratische
            # Naeherung und verhindert Ausreisser bei kleinen Parzellen.
            verhaeltnis = 1.5
            kurze_seite = (parzelle.flaeche_m2 / verhaeltnis) ** 0.5
            lange_seite = kurze_seite * verhaeltnis
            # Kleiner Grenzabstand auf den kurzen Seiten,
            # grosser Grenzabstand auf den langen Seiten
            nutzbare_kurz = max(0, kurze_seite - 2 * parameter.grenzabstand_klein_m)
            nutzbare_lang = max(0, lange_seite - 2 * parameter.grenzabstand_gross_m)
            grundflaeche_parzelle = nutzbare_kurz * nutzbare_lang'

if ($inhalt.Contains($alt_b1)) {
    $inhalt = $inhalt.Replace($alt_b1, $neu_b1)
    Write-Host "Fix Bug 1 angewendet: Parzellen-Form 1:1.5 statt Quadrat" -ForegroundColor Green
} else {
    Write-Host "Fix Bug 1 NICHT noetig" -ForegroundColor Yellow
}

# --- Fix: Wenn Geometrie inf, dann ist Begrenzer nicht "geometrie" ---
# (Das ist schon natuerlich durch min() abgedeckt - aber prueffe Anzeige-Text)
$alt_marker = '            f"    1. Gebaeudemasse: {schaetzung[''grundflaeche_geometrie_m2'']:.0f} m^2 "
                f"({parameter.max_gebaeudelaenge_m} m x {schaetzung[''breite_m'']:.1f} m "
                f"aus {schaetzung[''breite_quelle'']}){geo_marker}"'

# Nur anzeigen wenn die Datei das alte Pattern noch hat
# (Falls schon angepasst, ueberspringen)

# --- Anzeige-Anpassung: bei inf den Geometrie-Block auch sichtbar machen ---
$alt_geom_anzeige = '            geo_marker = " <- aktiv" if schaetzung["begrenzer"] == "geometrie" else ""
            ergebnis.bemerkungen.append(
                f"    1. Gebaeudemasse: {schaetzung[''grundflaeche_geometrie_m2'']:.0f} m^2 "
                f"({parameter.max_gebaeudelaenge_m} m x {schaetzung[''breite_m'']:.1f} m "
                f"aus {schaetzung[''breite_quelle'']}){geo_marker}"
            )'

$neu_geom_anzeige = '            geo_marker = " <- aktiv" if schaetzung["begrenzer"] == "geometrie" else ""
            if schaetzung["grundflaeche_geometrie_m2"] == float("inf"):
                ergebnis.bemerkungen.append(
                    f"    1. Gebaeudemasse: unbegrenzt "
                    f"(Gebaeudelaenge unbeschraenkt){geo_marker}"
                )
            else:
                ergebnis.bemerkungen.append(
                    f"    1. Gebaeudemasse: {schaetzung[''grundflaeche_geometrie_m2'']:.0f} m^2 "
                    f"({parameter.max_gebaeudelaenge_m} m x {schaetzung[''breite_m'']:.1f} m "
                    f"aus {schaetzung[''breite_quelle'']}){geo_marker}"
                )'

if ($inhalt.Contains($alt_geom_anzeige)) {
    $inhalt = $inhalt.Replace($alt_geom_anzeige, $neu_geom_anzeige)
    Write-Host "Fix Anzeige angewendet: 'unbegrenzt' bei inf-Geometrie" -ForegroundColor Green
} else {
    Write-Host "Fix Anzeige NICHT noetig" -ForegroundColor Yellow
}

Set-Content -Path $pfad -Value $inhalt -Encoding UTF8 -NoNewline
Write-Host ""
Write-Host "Fertig! Datei aktualisiert: $pfad" -ForegroundColor Green
Write-Host "Falls etwas schiefgeht: Restore mit:" -ForegroundColor Gray
Write-Host "  Copy-Item $backup $pfad -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "Naechster Schritt: Stichproben-Test laufen lassen" -ForegroundColor Yellow
Write-Host "  .\tests\test_zwoelf_adressen.ps1" -ForegroundColor Yellow
