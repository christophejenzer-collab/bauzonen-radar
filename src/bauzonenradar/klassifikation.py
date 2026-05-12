"""
klassifikation.py - Klassifiziert Parzellen in vier Geschaeftslogik-Kategorien.

Fuer Iter-5-Massen-Analyse: jede analysierte Parzelle wird einer
der folgenden Kategorien zugeordnet:

VERDICHTUNG     - Bebaute Parzelle mit ungenutzter Reserve (Aufstockung)
NEUGESCHAEFT    - Leere Parzelle mit Bauland-Reserve (Neubau)
ERSATZNEUBAU    - Alte Bauten + Reserve = hoher Hebel
AUSGEREIZT      - GWR uebersteigt theoretisches Soll (Bestandsschutz)
UNAUFFAELLIG    - Bebaute Parzelle mit zu wenig Reserve
AUSSCHLUSS_*    - Aus Listen ausgeschlossen (Reglement / zu klein / Fehler)

WICHTIG: Die Klassifikation nutzt die ECHTE Ausschoepfung aus GWR
(Ist / Soll * 100), nicht das `ausschoepfungsgrad_prozent`-Feld
aus dem AnalyseErgebnis. Letzteres basiert auf einem Platzhalter
(25% der Parzelle als Ist-Schaetzung) und ist deshalb fuer Iter-5
nicht aussagekraeftig.

Schwellen sind als Konstanten definiert - **am Schwager-Termin
zu verifizieren** (siehe docs/scope_iter5.md).

Iter 5 | Stand: 12. Mai 2026
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schwellen-Konstanten (am Schwager-Termin zu verifizieren!)
# ---------------------------------------------------------------------------

MIN_PARZELLEN_FLAECHE_M2 = 200.0
SCHWELLE_AUSGEREIZT_PROZENT = 95.0
MIN_RESERVE_M2 = 100.0
MIN_RESERVE_M2_NEUGESCHAEFT = 200.0
SCHWELLE_BAUPERIODE_ALT = 1980
MIN_RESERVE_M2_ERSATZNEUBAU = 200.0


# ---------------------------------------------------------------------------
# Kategorie-Konstanten
# ---------------------------------------------------------------------------

KAT_VERDICHTUNG = "VERDICHTUNG"
KAT_NEUGESCHAEFT = "NEUGESCHAEFT"
KAT_ERSATZNEUBAU = "ERSATZNEUBAU"
KAT_AUSGEREIZT = "AUSGEREIZT"
KAT_UNAUFFAELLIG = "UNAUFFAELLIG"
KAT_AUSSCHLUSS_REGLEMENT = "AUSSCHLUSS_REGLEMENT"
KAT_AUSSCHLUSS_ZU_KLEIN = "AUSSCHLUSS_ZU_KLEIN"
KAT_AUSSCHLUSS_FEHLER = "AUSSCHLUSS_FEHLER"


# ---------------------------------------------------------------------------
# Helper: echte Ausschoepfung aus GWR-Daten
# ---------------------------------------------------------------------------

def echte_ausschoepfung_prozent(ergebnis) -> Optional[float]:
    """Berechnet die echte Ausschoepfung Ist (GWR) / Soll * 100.

    Im Gegensatz zu ergebnis.ausschoepfungsgrad_prozent (basiert auf
    25%-Platzhalter) nutzt diese Funktion die echten GWR-Daten.

    Returns:
        Ausschoepfung in Prozent, oder None wenn nicht berechenbar.
    """
    soll = ergebnis.theoretisch_zulaessig_m2
    ist = ergebnis.gwr_summe_geschossflaeche_m2

    if soll is None or soll <= 0:
        return None
    if ist is None:
        return None

    return (ist / soll) * 100.0


def echte_reserve_m2(ergebnis) -> Optional[float]:
    """Berechnet die echte Reserve Soll - Ist (GWR).

    Bei leeren Parzellen (keine GWR-Gebaeude) entspricht die Reserve dem Soll.

    Returns:
        Reserve in m^2 (kann negativ sein bei Bestandsschutz), oder None.
    """
    soll = ergebnis.theoretisch_zulaessig_m2
    if soll is None:
        return None

    ist = ergebnis.gwr_summe_geschossflaeche_m2
    if ist is None:
        if not (ergebnis.gwr_gebaeude or []):
            return soll
        return None

    return soll - ist


# ---------------------------------------------------------------------------
# Helper: aeltestes Baujahr aus GWR-Liste
# ---------------------------------------------------------------------------

def _aeltestes_baujahr(gwr_gebaeude: list) -> Optional[int]:
    """Liefert das aelteste Baujahr aus einer GWR-Gebaeudeliste."""
    if not gwr_gebaeude:
        return None

    baujahre = []
    for g in gwr_gebaeude:
        bj = getattr(g, "baujahr", None)
        if bj is not None and isinstance(bj, int) and 1800 <= bj <= 2100:
            baujahre.append(bj)
            continue

        bp_code = getattr(g, "bauperiode_code", None)
        if bp_code is not None:
            jahr = _bauperiode_code_zu_jahr(bp_code)
            if jahr:
                baujahre.append(jahr)

    return min(baujahre) if baujahre else None


def _bauperiode_code_zu_jahr(code) -> Optional[int]:
    """Mappt GWR-Bauperiode-Codes auf approximative Baujahre.

    GWR-Codeliste:
        8011 = vor 1919      8019 = 1996-2000
        8012 = 1919-1945     8020 = 2001-2005
        8013 = 1946-1960     8021 = 2006-2010
        8014 = 1961-1970     8022 = 2011-2015
        8015 = 1971-1980     8023 = nach 2015
        8016 = 1981-1985
        8017 = 1986-1990
        8018 = 1991-1995
    """
    try:
        code_int = int(code)
    except (ValueError, TypeError):
        return None

    mapping = {
        8011: 1900, 8012: 1930, 8013: 1953, 8014: 1965, 8015: 1975,
        8016: 1983, 8017: 1988, 8018: 1993, 8019: 1998, 8020: 2003,
        8021: 2008, 8022: 2013, 8023: 2020,
    }
    return mapping.get(code_int)


# ---------------------------------------------------------------------------
# Haupt-Funktion: Klassifikation
# ---------------------------------------------------------------------------

def klassifiziere(ergebnis) -> str:
    """Ordnet ein AnalyseErgebnis einer Geschaeftslogik-Kategorie zu.

    Args:
        ergebnis: AnalyseErgebnis-Instanz

    Returns:
        Kategorie-String (siehe KAT_* Konstanten)

    Klassifikations-Logik:
    1. Fehler -> AUSSCHLUSS_FEHLER
    2. Datenqualitaet NICHT_MOEGLICH -> AUSSCHLUSS_REGLEMENT
    3. Parzelle zu klein -> AUSSCHLUSS_ZU_KLEIN
    4. Theoretisch zulaessig fehlt -> AUSSCHLUSS_REGLEMENT
    5. Leer (kein GWR-Gebaeude) -> NEUGESCHAEFT wenn Reserve gross genug
    6. Bebaut:
       a. Echte Ausschoepfung (Ist/Soll) > 95% -> AUSGEREIZT
       b. GWR-Daten unvollstaendig -> UNAUFFAELLIG (vorsichtig)
       c. Reserve <= 0 -> AUSGEREIZT
       d. Bestand alt + viel Reserve -> ERSATZNEUBAU
       e. Genug Reserve -> VERDICHTUNG
       f. Sonst -> UNAUFFAELLIG
    """
    # 1. Fehler bei der Analyse
    if ergebnis.fehler:
        return KAT_AUSSCHLUSS_FEHLER

    # 2. Datenqualitaet NICHT_MOEGLICH
    if ergebnis.datenqualitaet in ("nicht_moeglich", "NICHT_MOEGLICH"):
        return KAT_AUSSCHLUSS_REGLEMENT

    # 3. Parzelle zu klein
    flaeche = ergebnis.parzellen_flaeche_m2 or 0.0
    if flaeche < MIN_PARZELLEN_FLAECHE_M2:
        return KAT_AUSSCHLUSS_ZU_KLEIN

    # 4. Theoretisch zulaessig muss bekannt sein
    zulaessig = ergebnis.theoretisch_zulaessig_m2
    if zulaessig is None:
        return KAT_AUSSCHLUSS_REGLEMENT

    # 5. Leere Parzelle (kein GWR-Gebaeude)
    gebaeude = ergebnis.gwr_gebaeude or []
    if not gebaeude:
        if zulaessig >= MIN_RESERVE_M2_NEUGESCHAEFT:
            return KAT_NEUGESCHAEFT
        else:
            return KAT_UNAUFFAELLIG

    # 6. Bebaut: echte Ausschoepfung pruefen
    echte_ausschoepf = echte_ausschoepfung_prozent(ergebnis)
    if echte_ausschoepf is None:
        return KAT_UNAUFFAELLIG

    if echte_ausschoepf > SCHWELLE_AUSGEREIZT_PROZENT:
        return KAT_AUSGEREIZT

    # 6c. Reserve berechnen
    reserve = echte_reserve_m2(ergebnis)
    if reserve is None or reserve <= 0:
        return KAT_AUSGEREIZT

    # 6d. ERSATZNEUBAU-Kandidat
    bauperiode = _aeltestes_baujahr(gebaeude)
    if (bauperiode is not None
            and bauperiode < SCHWELLE_BAUPERIODE_ALT
            and reserve >= MIN_RESERVE_M2_ERSATZNEUBAU):
        return KAT_ERSATZNEUBAU

    # 6e. VERDICHTUNG
    if reserve >= MIN_RESERVE_M2:
        return KAT_VERDICHTUNG

    # 6f. Reserve zu klein
    return KAT_UNAUFFAELLIG


# ---------------------------------------------------------------------------
# Smoke-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))

    logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

    print("Smoke-Test fuer klassifiziere() v2 (mit echter Ausschoepfung):")
    print()

    from analyse_adresse import analysiere

    test_adressen = [
        ("Thunstrasse 40, 3005 Bern", "AUSGEREIZT (Ist 224 > Soll 118)"),
        ("Frutigenstrasse 25, 3604 Thun", "AUSGEREIZT (Ist 1520 > Soll 1080)"),
        ("Kramgasse 49, 3011 Bern", "AUSSCHLUSS_REGLEMENT (Altstadt)"),
        ("Murifeldweg 8, 3006 Bern", "AUSGEREIZT (Ist 435 > Soll 37, 1192%)"),
    ]

    for adresse, erwartung in test_adressen:
        print(f"--- {adresse} ---")
        print(f"    Erwartet:        {erwartung}")
        try:
            ergebnis = analysiere(adresse)
            kategorie = klassifiziere(ergebnis)
            echte_aus = echte_ausschoepfung_prozent(ergebnis)
            reserve = echte_reserve_m2(ergebnis)

            print(f"    Klassifikat:     {kategorie}")
            print(f"    Flaeche:         {ergebnis.parzellen_flaeche_m2}")
            print(f"    Soll:            {ergebnis.theoretisch_zulaessig_m2}")
            print(f"    Ist (GWR):       {ergebnis.gwr_summe_geschossflaeche_m2}")
            if echte_aus is not None:
                print(f"    Echte Ausschoepf: {echte_aus:.1f}%")
            else:
                print(f"    Echte Ausschoepf: -")
            if reserve is not None:
                print(f"    Echte Reserve:   {reserve:.1f} m^2")
            else:
                print(f"    Echte Reserve:   -")
            print(f"    Tool-Ausschoepf: {ergebnis.ausschoepfungsgrad_prozent}% (Platzhalter)")
            print(f"    Datenqualitaet:  {ergebnis.datenqualitaet}")
            print(f"    Gebaeude:        {len(ergebnis.gwr_gebaeude or [])}")
        except Exception as e:
            print(f"    FEHLER: {e}")
        print()

    print("===== SMOKE-TEST FERTIG =====")
