"""
Hauptskript: Komplette Analyse einer Adresse.

Fuehrt die gesamte Pipeline in einem einzigen Aufruf durch:

  Adresse -> OEREB-Daten -> Baureglement -> [BKP fuer Bern] -> Potenzialanalyse -> Bericht

Aufruf:
    python analyse_adresse.py "Kramgasse 49, 3011 Bern"

Dies ist die Hauptschnittstelle fuer Demos und den spaeteren
Einsatz als Kommandozeilen-Tool.

BKP-Erweiterung (Stadt Bern):
-----------------------------
Fuer Adressen in der Stadt Bern wird zusaetzlich der Bauklassenplan (BKP)
ueber die ArcGIS REST-API von map.bern.ch abgefragt. Daraus kommen
parzellenscharf:
  - Bauklasse (BK_2 bis BK_6, BK_E, OA, UA)
  - Nutzungszone (W, WG, K, D, IG)
  - Bauweise (offen/geschlossen)
  - Gebaeudelaenge und Gebaeudetiefe in m

Diese Werte werden den Bauparametern hinzugefuegt, sodass die
Potenzialschaetzung mit echten Geometrie-Werten arbeitet statt mit
pauschalen Defaults.
"""

from __future__ import annotations

import sys
import json
import urllib.parse
import urllib.request

from bern import BernOerebQuelle
from baureglement import Baureglement
from analyse.potenzial import PotenzialBerechner

# BKP-Modul ist optional - wenn es fehlt, laeuft alles ohne BKP-Anreicherung
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
    GWR_VERFUEGBAR = False


def _hole_lv95_koordinaten(adresse: str) -> tuple[float, float] | None:
    """Holt LV95-Koordinaten fuer eine Adresse via api3.geo.admin.ch.

    Falls die Parzelle bereits eine Koordinate enthaelt, wird diese
    bevorzugt - aber als Fallback funktioniert das auch ohne.

    Returns:
        Tuple (ost, nord) in LV95, oder None bei Fehler.
    """
    try:
        params = {
            "searchText": adresse,
            "type": "locations",
            "origins": "address",
            "limit": "1",
            "sr": "2056",  # LV95
        }
        url = (
            "https://api3.geo.admin.ch/rest/services/api/SearchServer?"
            + urllib.parse.urlencode(params)
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            daten = json.loads(resp.read().decode("utf-8"))
        treffer = daten.get("results") or []
        if not treffer:
            return None
        attrs = treffer[0].get("attrs") or {}
        ost = attrs.get("y")  # geo.admin.ch tauscht x/y!
        nord = attrs.get("x")
        if ost is None or nord is None:
            return None
        return (float(ost), float(nord))
    except Exception:
        return None


def analysiere(adresse: str) -> None:
    """Fuehrt die vollstaendige Analyse durch und gibt den Bericht aus."""
    print("=" * 70)
    print(f"Bauzonen-Radar - Analyse fuer: {adresse}")
    print("=" * 70)

    # Schritt 1: Parzelle laden via OEREB
    quelle = BernOerebQuelle()
    parzelle = quelle.adresse_zu_parzelle(adresse)
    if not parzelle:
        print("Keine Parzelle gefunden fuer diese Adresse.")
        return

    # Schritt 2: OEREB-Kurzbericht anzeigen
    print()
    print(parzelle.kurzbericht())
    print()
    print("=" * 70)

    # Schritt 3: Baureglement laden (falls vorhanden)
    reglement: Baureglement | None = None
    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        print(f"Baureglement geladen: {reglement.gemeinde} "
              f"(Stand: {reglement.stand}, Struktur: {reglement.struktur})")
    except FileNotFoundError:
        print(f"Kein Baureglement fuer '{parzelle.gemeinde}' verfuegbar.")
        print("Potenzialberechnung wird nicht moeglich sein.")

    # Schritt 4: Bei Stadt Bern - BKP-Daten holen
    bkp_quelle = None
    if (reglement is not None
            and parzelle.gemeinde == "Bern"
            and BKP_VERFUEGBAR):
        # Versuche zuerst, Koordinaten aus der Parzelle zu holen,
        # falls die Klasse so ein Feld hat. Sonst Fallback auf Geocoding.
        koordinate = None
        for feldname in ("koordinate_lv95", "koordinaten", "lv95"):
            if hasattr(parzelle, feldname):
                wert = getattr(parzelle, feldname)
                if wert and len(wert) == 2:
                    koordinate = (float(wert[0]), float(wert[1]))
                    break

        if koordinate is None:
            koordinate = _hole_lv95_koordinaten(adresse)

        # WICHTIG: Koordinate auch aufs parzelle-Objekt setzen, damit der
        # Berechner sie spaeter fuer die BKP-Anreicherung wiederfindet.
        if koordinate is not None:
            try:
                parzelle.koordinate_lv95 = koordinate
            except AttributeError:
                # Falls Parzelle ein __slots__-dataclass ist, geht das nicht.
                # Dann muss der Berechner mit dem Geocoding-Fallback klarkommen.
                pass

        if koordinate is not None:
            ost, nord = koordinate
            print()
            print(f"BKP-Anfrage Stadt Bern fuer LV95 {ost:.0f}/{nord:.0f}...")
            try:
                bkp_quelle = BernBkpQuelle()
                auskunft = bkp_quelle.hole_auskunft(ost, nord)
                if auskunft.gefunden:
                    if auskunft.grundzone:
                        g = auskunft.grundzone
                        print(f"  Nutzungszone: {g.nutzungszone_kuerzel} "
                              f"({g.nutzungszone_beschrieb})")
                        print(f"  Bauklasse:    {g.bauklasse_kuerzel} "
                              f"({g.bauklasse_beschrieb})")
                    if auskunft.bauweise:
                        b = auskunft.bauweise
                        laenge = ("unbeschr." if b.gebaeudelaenge_unbeschraenkt
                                  else f"{b.gebaeudelaenge} m")
                        tiefe = ("unbeschr." if b.gebaeudetiefe_unbeschraenkt
                                 else f"{b.gebaeudetiefe} m")
                        print(f"  Bauweise:     {b.bauweise_beschrieb} "
                              f"(L: {laenge}, T: {tiefe})")
                    else:
                        print("  Bauweise:     (keine Daten - "
                              "z.B. BK_E oder Altstadt)")
                else:
                    print("  Keine BKP-Daten gefunden fuer diese Koordinate.")
            except Exception as fehler:
                print(f"  BKP-Anfrage fehlgeschlagen: {fehler}")
                bkp_quelle = None
        else:
            print()
            print("BKP-Anfrage uebersprungen: keine LV95-Koordinaten "
                  "verfuegbar fuer diese Adresse.")

    print()

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
                            fehlende = []
                            if g.grundflaeche_m2 is None:
                                fehlende.append("Grundflaeche")
                            if g.geschosse is None:
                                fehlende.append("Geschosszahl")
                            details = ", ".join(fehlende) if fehlende else "?"
                            print(f"  {g.label}: GWR-Daten unvollstaendig "
                                  f"(fehlt: {details})")
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
    ergebnis = berechner.berechne(parzelle, reglement, bkp_quelle=bkp_quelle)

    print(ergebnis.textbericht())
    print()


def main() -> int:
    if len(sys.argv) < 2:
        print("Verwendung: python analyse_adresse.py \"Strasse Nr, PLZ Ort\"")
        print()
        print("Beispiele:")
        print('  python analyse_adresse.py "Kramgasse 49, 3011 Bern"')
        print('  python analyse_adresse.py "Rathausplatz 1, 3600 Thun"')
        print('  python analyse_adresse.py "Thunstrasse 40, 3005 Bern"')
        return 1

    analysiere(sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
