"""
Hauptskript: Komplette Analyse einer Adresse.

Fuehrt die gesamte Pipeline in einem einzigen Aufruf durch:

  Adresse -> OEREB-Daten -> Baureglement -> [BKP fuer Bern] -> Potenzialanalyse -> Bericht

Aufruf:
    python analyse_adresse.py "Kramgasse 49, 3011 Bern"

Architektur-Hinweis:
--------------------
Die Logik ist in zwei Funktionen getrennt:

  - analysiere(adresse) -> AnalyseErgebnis
       Macht die ganze Berechnung, gibt ein Datenobjekt zurueck. Kein Print.
       Wird von der Streamlit-GUI direkt aufgerufen.

  - drucke_bericht(ergebnis) -> None
       Macht die CLI-Ausgabe (print). Nutzt das Datenobjekt von analysiere().

Diese Trennung folgt dem Prinzip "Separation of Concerns": Berechnung ist
getrennt vom Output-Format. So kann die GUI dieselbe Berechnung nutzen.

BKP-Erweiterung (Stadt Bern):
-----------------------------
Fuer Adressen in der Stadt Bern wird zusaetzlich der Bauklassenplan (BKP)
ueber die ArcGIS REST-API von map.bern.ch abgefragt.
"""

from __future__ import annotations

import sys
import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Optional, Any

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


# ---------------------------------------------------------------------------
# Ergebnis-Datenklasse (fuer GUI und CLI gleichermassen)
# ---------------------------------------------------------------------------

@dataclass
class AnalyseErgebnis:
    """Strukturiertes Ergebnis einer Bauland-Analyse.

    Enthaelt alles was die GUI oder CLI braucht um einen Bericht
    darzustellen. Sammelt Daten aus allen Pipeline-Schritten.

    Felder die optional sind, koennen None sein, wenn der entsprechende
    Schritt nicht erfolgreich war (z.B. kein Reglement hinterlegt,
    BKP-API nicht erreichbar, etc).
    """
    # Eingabe
    adresse_eingabe: str

    # Status
    erfolgreich: bool = False
    fehler: Optional[str] = None
    warnungen: list[str] = field(default_factory=list)

    # Parzelle (aus OEREB)
    parzelle: Optional[Any] = None
    parzelle_kurzbericht: Optional[str] = None
    gemeinde: Optional[str] = None
    parzellen_nummer: Optional[str] = None
    parzellen_flaeche_m2: Optional[float] = None
    egrid: Optional[str] = None
    koordinate_lv95: Optional[tuple[float, float]] = None
    koordinate_wgs84: Optional[tuple[float, float]] = None  # (lat, lon) fuer st.map

    # Reglement
    reglement: Optional[Any] = None
    reglement_geladen: bool = False
    reglement_stand: Optional[str] = None
    reglement_struktur: Optional[str] = None
    reglement_meldung: Optional[str] = None  # z.B. "Kein Baureglement fuer X verfuegbar"

    # BKP (Stadt Bern)
    bkp_abgefragt: bool = False
    bkp_gefunden: bool = False
    bkp_meldung: Optional[str] = None
    bkp_nutzungszone: Optional[str] = None
    bkp_bauklasse: Optional[str] = None
    bkp_bauweise: Optional[str] = None
    bkp_gebaeudelaenge_m: Optional[float] = None
    bkp_gebaeudetiefe_m: Optional[float] = None
    bkp_gebaeudelaenge_unbeschraenkt: bool = False
    bkp_gebaeudetiefe_unbeschraenkt: bool = False

    # GWR (effektive Bestands-Bebauung)
    gwr_abgefragt: bool = False
    gwr_gefunden: bool = False
    gwr_meldung: Optional[str] = None
    gwr_gebaeude: list = field(default_factory=list)
    gwr_summe_geschossflaeche_m2: Optional[float] = None

    # Potenzialberechnung (das eigentliche Resultat)
    potenzial_ergebnis: Optional[Any] = None
    datenqualitaet: Optional[str] = None  # "VERBINDLICH" | "GROBSCHAETZUNG" | "NICHT_MOEGLICH"
    bemessungs_system: Optional[str] = None
    zulaessig_m2: Optional[float] = None
    realisiert_m2: Optional[float] = None
    reserve_m2: Optional[float] = None
    ausschoepfung_prozent: Optional[float] = None
    lagebeurteilung: Optional[str] = None  # "HOCH" | "MITTEL" | "GERING" | "AUSGESCHOEPFT"

    # GUI-Aliase aus PotenzialErgebnis (fuer Streamlit-Frontend)
    theoretisch_zulaessig_m2: Optional[float] = None
    ausschoepfungsgrad_prozent: Optional[float] = None
    reserve_prozent: Optional[float] = None
    zonen_betrachtet: list = field(default_factory=list)
    zone: Optional[str] = None
    arealbonus_anwendbar: bool = False
    bemerkungen: list = field(default_factory=list)

    # Original-Textbericht (fuer CLI-Ausgabe und Debug)
    textbericht: Optional[str] = None

    @property
    def hat_potenzial(self) -> bool:
        """True wenn die Potenzialberechnung erfolgreich war."""
        return self.potenzial_ergebnis is not None

    @property
    def koordinaten_fuer_karte(self) -> Optional[tuple[float, float]]:
        """Fuer st.map(): (lat, lon) in WGS84.

        Faellt zurueck auf None wenn keine Koordinaten verfuegbar.
        """
        return self.koordinate_wgs84


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

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


def _lv95_zu_wgs84(ost: float, nord: float) -> Optional[tuple[float, float]]:
    """Konvertiert LV95-Koordinaten zu WGS84 (lat, lon) via api3.geo.admin.ch.

    Returns:
        (lat, lon) als WGS84 oder None bei Fehler.
    """
    try:
        url = (
            "https://geodesy.geo.admin.ch/reframe/lv95towgs84?"
            f"easting={ost}&northing={nord}&format=json"
        )
        with urllib.request.urlopen(url, timeout=5) as resp:
            daten = json.loads(resp.read().decode("utf-8"))
        # api liefert "easting"=lon, "northing"=lat in WGS84
        lon = float(daten.get("easting"))
        lat = float(daten.get("northing"))
        return (lat, lon)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Hauptfunktion: Analyse (kein Print, gibt Datenobjekt zurueck)
# ---------------------------------------------------------------------------

def analysiere(adresse: str) -> AnalyseErgebnis:
    """Fuehrt die vollstaendige Analyse durch und gibt ein Ergebnis-Objekt zurueck.

    Diese Funktion macht KEINE print()-Aufrufe. Sie sammelt alle Daten in
    einem AnalyseErgebnis-Objekt, das von der CLI (drucke_bericht) oder
    der GUI (Streamlit) gerendert wird.

    Args:
        adresse: Schweizer Adresse, z.B. "Kramgasse 49, 3011 Bern"

    Returns:
        AnalyseErgebnis-Objekt mit allen gesammelten Daten und Status.
    """
    ergebnis = AnalyseErgebnis(adresse_eingabe=adresse)

    # --- Schritt 1: Parzelle laden via OEREB ---
    try:
        quelle = BernOerebQuelle()
        parzelle = quelle.adresse_zu_parzelle(adresse)
    except Exception as fehler:
        ergebnis.fehler = f"OEREB-Abfrage fehlgeschlagen: {fehler}"
        return ergebnis

    if not parzelle:
        ergebnis.fehler = "Keine Parzelle gefunden fuer diese Adresse."
        return ergebnis

    ergebnis.parzelle = parzelle
    ergebnis.parzelle_kurzbericht = parzelle.kurzbericht()
    ergebnis.gemeinde = getattr(parzelle, "gemeinde", None)
    ergebnis.parzellen_nummer = getattr(parzelle, "parzellennummer", None) \
        or getattr(parzelle, "nummer", None)
    ergebnis.parzellen_flaeche_m2 = getattr(parzelle, "flaeche_m2", None) \
        or getattr(parzelle, "flaeche", None)
    ergebnis.egrid = getattr(parzelle, "egrid", None)

    # Koordinate aus Parzelle holen oder via Geocoding nachreichen
    koordinate_lv95 = None
    for feldname in ("koordinate_lv95", "koordinaten", "lv95"):
        if hasattr(parzelle, feldname):
            wert = getattr(parzelle, feldname)
            if wert and len(wert) == 2:
                koordinate_lv95 = (float(wert[0]), float(wert[1]))
                break
    if koordinate_lv95 is None:
        koordinate_lv95 = _hole_lv95_koordinaten(adresse)

    if koordinate_lv95 is not None:
        ergebnis.koordinate_lv95 = koordinate_lv95
        # Auch auf Parzelle setzen damit BKP-Anreicherung sie findet
        try:
            parzelle.koordinate_lv95 = koordinate_lv95
        except AttributeError:
            pass
        # Konvertierung zu WGS84 fuer st.map()
        wgs84 = _lv95_zu_wgs84(*koordinate_lv95)
        if wgs84 is not None:
            ergebnis.koordinate_wgs84 = wgs84

    # --- Schritt 2: Baureglement laden ---
    reglement: Baureglement | None = None
    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        ergebnis.reglement = reglement
        ergebnis.reglement_geladen = True
        ergebnis.reglement_stand = reglement.stand
        ergebnis.reglement_struktur = reglement.struktur
    except FileNotFoundError:
        ergebnis.reglement_meldung = (
            f"Kein Baureglement fuer '{parzelle.gemeinde}' verfuegbar. "
            f"Potenzialberechnung wird nicht moeglich sein."
        )
        ergebnis.warnungen.append(ergebnis.reglement_meldung)

    # --- Schritt 3: BKP-Daten holen (Stadt Bern) ---
    bkp_quelle = None
    if (reglement is not None
            and parzelle.gemeinde == "Bern"
            and BKP_VERFUEGBAR
            and koordinate_lv95 is not None):
        ergebnis.bkp_abgefragt = True
        try:
            bkp_quelle = BernBkpQuelle()
            auskunft = bkp_quelle.hole_auskunft(*koordinate_lv95)
            if auskunft.gefunden:
                ergebnis.bkp_gefunden = True
                if auskunft.grundzone:
                    g = auskunft.grundzone
                    ergebnis.bkp_nutzungszone = (
                        f"{g.nutzungszone_kuerzel} ({g.nutzungszone_beschrieb})"
                    )
                    ergebnis.bkp_bauklasse = (
                        f"{g.bauklasse_kuerzel} ({g.bauklasse_beschrieb})"
                    )
                if auskunft.bauweise:
                    b = auskunft.bauweise
                    ergebnis.bkp_bauweise = b.bauweise_beschrieb
                    ergebnis.bkp_gebaeudelaenge_m = b.gebaeudelaenge
                    ergebnis.bkp_gebaeudetiefe_m = b.gebaeudetiefe
                    ergebnis.bkp_gebaeudelaenge_unbeschraenkt = b.gebaeudelaenge_unbeschraenkt
                    ergebnis.bkp_gebaeudetiefe_unbeschraenkt = b.gebaeudetiefe_unbeschraenkt
                else:
                    ergebnis.bkp_meldung = (
                        "Bauweise: keine Daten (z.B. BK_E oder Altstadt)"
                    )
            else:
                ergebnis.bkp_meldung = "Keine BKP-Daten gefunden fuer diese Koordinate."
        except Exception as fehler:
            ergebnis.bkp_meldung = f"BKP-Anfrage fehlgeschlagen: {fehler}"
            ergebnis.warnungen.append(ergebnis.bkp_meldung)
            bkp_quelle = None
    elif (reglement is not None
            and parzelle.gemeinde == "Bern"
            and BKP_VERFUEGBAR
            and koordinate_lv95 is None):
        ergebnis.bkp_meldung = (
            "BKP-Anfrage uebersprungen: keine LV95-Koordinaten verfuegbar."
        )

    # --- Schritt 4: GWR-Lookup fuer Ist-Werte ---
    if GWR_VERFUEGBAR:
        ergebnis.gwr_abgefragt = True
        try:
            gwr = GwrQuelle()
            gebaeude = gwr.gebaeude_zu_adresse(adresse)
            if gebaeude:
                # Filter auf Gebaeude der gefundenen Parzelle
                gebaeude_parzelle = [g for g in gebaeude if g.egrid == parzelle.egrid]
                if gebaeude_parzelle:
                    ergebnis.gwr_gefunden = True
                    ergebnis.gwr_gebaeude = gebaeude_parzelle
                    summe_geschossflaeche = 0.0
                    hat_summe = False
                    for g in gebaeude_parzelle:
                        if g.grundflaeche_m2 is not None and g.geschosse is not None:
                            gf = g.geschossflaeche_m2
                            if gf is not None:
                                summe_geschossflaeche += gf
                                hat_summe = True
                    if hat_summe:
                        ergebnis.gwr_summe_geschossflaeche_m2 = summe_geschossflaeche
                else:
                    ergebnis.gwr_meldung = (
                        "Keine GWR-Gebaeudedaten fuer diese Parzelle (evtl. unbebaut)."
                    )
        except GwrFehler as fehler:
            ergebnis.gwr_meldung = f"GWR-Anfrage fehlgeschlagen: {fehler}"
        except Exception as fehler:
            ergebnis.gwr_meldung = (
                f"GWR-Anfrage uebersprungen ({fehler.__class__.__name__})"
            )

    # --- Schritt 5: Potenzialberechnung ---
    try:
        berechner = PotenzialBerechner()
        potenzial = berechner.berechne(parzelle, reglement, bkp_quelle=bkp_quelle)
        ergebnis.potenzial_ergebnis = potenzial
        ergebnis.textbericht = potenzial.textbericht()

        # Direkt vom PotenzialErgebnis lesen (echte Feldnamen)
        ergebnis.datenqualitaet = _attr_zu_string(potenzial, "datenqualitaet")
        ergebnis.bemessungs_system = _attr_zu_string(potenzial, "bemessungs_system") \
            or _attr_zu_string(potenzial, "verwendetes_system") \
            or _attr_zu_string(potenzial, "system")
        ergebnis.zulaessig_m2 = getattr(potenzial, "theoretisch_zulaessig_m2", None)
        ergebnis.realisiert_m2 = getattr(potenzial, "geschaetzt_realisiert_m2", None)
        ergebnis.reserve_m2 = getattr(potenzial, "reserve_m2", None)
        ergebnis.ausschoepfung_prozent = getattr(potenzial, "ausschoepfungsgrad_prozent", None)
        ergebnis.lagebeurteilung = _attr_zu_string(potenzial,
            "lagebeurteilung", "status")

        # GUI-Aliase fuer Fabiennes Frontend
        ergebnis.theoretisch_zulaessig_m2 = getattr(potenzial, "theoretisch_zulaessig_m2", None)
        ergebnis.ausschoepfungsgrad_prozent = getattr(potenzial, "ausschoepfungsgrad_prozent", None)
        ergebnis.reserve_prozent = getattr(potenzial, "reserve_prozent", None)
        ergebnis.zonen_betrachtet = list(getattr(potenzial, "zonen_betrachtet", []) or [])
        ergebnis.zone = (ergebnis.zonen_betrachtet[0]
                         if ergebnis.zonen_betrachtet else None)
        ergebnis.arealbonus_anwendbar = bool(getattr(potenzial, "arealbonus_anwendbar", False))
        ergebnis.bemerkungen = list(getattr(potenzial, "bemerkungen", []) or [])
    except Exception as fehler:
        ergebnis.warnungen.append(f"Potenzialberechnung fehlgeschlagen: {fehler}")

    ergebnis.erfolgreich = True
    return ergebnis


def _attr_zu_string(obj: Any, *namen: str) -> Optional[str]:
    """Holt das erste vorhandene Attribut als String (fuer Enum-Werte etc)."""
    for name in namen:
        if hasattr(obj, name):
            wert = getattr(obj, name)
            if wert is None:
                continue
            # Enum? -> .name oder .value
            if hasattr(wert, "name"):
                return str(wert.name)
            if hasattr(wert, "value"):
                return str(wert.value)
            return str(wert)
    return None


def _zahlenfeld(obj: Any, *namen: str) -> Optional[float]:
    """Holt das erste vorhandene Zahlen-Feld."""
    for name in namen:
        if hasattr(obj, name):
            wert = getattr(obj, name)
            if wert is None:
                continue
            try:
                return float(wert)
            except (TypeError, ValueError):
                continue
    return None


# ---------------------------------------------------------------------------
# Bericht-Ausgabe (CLI)
# ---------------------------------------------------------------------------

def drucke_bericht(ergebnis: AnalyseErgebnis) -> None:
    """Druckt den Bericht zur CLI. Nutzt das AnalyseErgebnis von analysiere()."""
    print("=" * 70)
    print(f"Bauzonen-Radar - Analyse fuer: {ergebnis.adresse_eingabe}")
    print("=" * 70)

    # Fehler frueh anzeigen
    if ergebnis.fehler:
        print(ergebnis.fehler)
        return

    # OEREB-Kurzbericht
    if ergebnis.parzelle_kurzbericht:
        print()
        print(ergebnis.parzelle_kurzbericht)
        print()
        print("=" * 70)

    # Reglement-Status
    if ergebnis.reglement_geladen and ergebnis.reglement is not None:
        print(f"Baureglement geladen: {ergebnis.reglement.gemeinde} "
              f"(Stand: {ergebnis.reglement_stand}, "
              f"Struktur: {ergebnis.reglement_struktur})")
    elif ergebnis.reglement_meldung:
        print(ergebnis.reglement_meldung)

    # BKP-Block
    if ergebnis.bkp_abgefragt and ergebnis.koordinate_lv95:
        ost, nord = ergebnis.koordinate_lv95
        print()
        print(f"BKP-Anfrage Stadt Bern fuer LV95 {ost:.0f}/{nord:.0f}...")
        if ergebnis.bkp_gefunden:
            if ergebnis.bkp_nutzungszone:
                print(f"  Nutzungszone: {ergebnis.bkp_nutzungszone}")
            if ergebnis.bkp_bauklasse:
                print(f"  Bauklasse:    {ergebnis.bkp_bauklasse}")
            if ergebnis.bkp_bauweise:
                laenge = "unbeschr." if ergebnis.bkp_gebaeudelaenge_unbeschraenkt \
                    else f"{ergebnis.bkp_gebaeudelaenge_m} m"
                tiefe = "unbeschr." if ergebnis.bkp_gebaeudetiefe_unbeschraenkt \
                    else f"{ergebnis.bkp_gebaeudetiefe_m} m"
                print(f"  Bauweise:     {ergebnis.bkp_bauweise} "
                      f"(L: {laenge}, T: {tiefe})")
            elif ergebnis.bkp_meldung:
                print(f"  {ergebnis.bkp_meldung}")
        elif ergebnis.bkp_meldung:
            print(f"  {ergebnis.bkp_meldung}")
    elif ergebnis.bkp_meldung:
        print()
        print(ergebnis.bkp_meldung)

    print()

    # GWR-Block
    if ergebnis.gwr_gefunden and ergebnis.gwr_gebaeude:
        print("GWR-Daten (bestehende Bebauung):")
        for g in ergebnis.gwr_gebaeude:
            if g.grundflaeche_m2 is not None and g.geschosse is not None:
                gf = g.geschossflaeche_m2
                print(f"  {g.label}: "
                      f"{g.grundflaeche_m2} m^2 x {g.geschosse} Geschosse "
                      f"= {gf} m^2 Geschossflaeche")
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
                print(f"  {g.label}: GWR-Daten unvollstaendig (fehlt: {details})")
        if (ergebnis.gwr_summe_geschossflaeche_m2 is not None
                and len(ergebnis.gwr_gebaeude) > 1):
            print(f"  SUMME (alle Gebaeude): {ergebnis.gwr_summe_geschossflaeche_m2} m^2")
        print()
    elif ergebnis.gwr_meldung:
        print(ergebnis.gwr_meldung)
        print()

    # Potenzialbericht (nutzt Original-textbericht() der Berechnungslogik)
    if ergebnis.textbericht:
        print(ergebnis.textbericht)
        print()


# ---------------------------------------------------------------------------
# CLI-Eintrittspunkt
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# EGRID-basierter Eintrittspunkt fuer Iter 5 Massen-Analyse
# ---------------------------------------------------------------------------
def analysiere_per_egrid(egrid, koordinate_lv95=None, adresse_label=None):
    """Fuehrt die vollstaendige Analyse fuer einen EGRID durch.

    Im Gegensatz zu analysiere() braucht hier keine Adresse - direkt
    via EGRID in die OEREB-Pipeline. Eintrittspunkt fuer Iter 5
    Massen-Analyse einer Gemeinde via parzellen_liste.

    Args:
        egrid: Eidg. Grundstueck-ID (z.B. "CH382046359635")
        koordinate_lv95: Optional - (east, north) in LV95, falls bekannt
        adresse_label: Optional - Anzeige-Adresse (z.B. "Oberhofen Parz. 309")

    Returns:
        AnalyseErgebnis-Objekt mit allen gesammelten Daten.

    Im Gegensatz zu analysiere() wird:
    - der Geocoding-Schritt uebersprungen (EGRID bereits bekannt)
    - der GWR-Lookup nur durchgefuehrt wenn adresse_label vorhanden
      (oder Parzelle nach OEREB-Parse eine Adresse hat)
    """
    # Adresse-Label fuer Anzeige verwenden (Pflichtfeld AnalyseErgebnis)
    adresse_anzeige = adresse_label or f"EGRID {egrid}"
    ergebnis = AnalyseErgebnis(adresse_eingabe=adresse_anzeige)

    # --- Schritt 1: Parzelle via EGRID laden (kein Geocoding-Vorlauf!) ---
    try:
        quelle = BernOerebQuelle()
        parzelle = quelle.egrid_zu_parzelle(
            egrid,
            koordinate_lv95=koordinate_lv95,
            adresse_label=adresse_label,
        )
    except Exception as fehler:
        ergebnis.fehler = f"OEREB-Abfrage fehlgeschlagen: {fehler}"
        return ergebnis

    if not parzelle:
        ergebnis.fehler = f"Keine Parzelle gefunden fuer EGRID {egrid}."
        return ergebnis

    ergebnis.parzelle = parzelle
    ergebnis.parzelle_kurzbericht = parzelle.kurzbericht()         if hasattr(parzelle, "kurzbericht") else ""
    ergebnis.gemeinde = getattr(parzelle, "gemeinde", None)
    ergebnis.parzellen_nummer = getattr(parzelle, "parzellennummer", None)         or getattr(parzelle, "nummer", None)
    ergebnis.parzellen_flaeche_m2 = getattr(parzelle, "flaeche_m2", None)         or getattr(parzelle, "flaeche", None)
    ergebnis.egrid = getattr(parzelle, "egrid", None)

    if koordinate_lv95:
        ergebnis.koordinate_lv95 = koordinate_lv95

    # --- Schritt 2: Baureglement laden ---
    reglement = None
    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        ergebnis.reglement = reglement
        ergebnis.reglement_geladen = True
        ergebnis.reglement_stand = reglement.stand
        ergebnis.reglement_struktur = reglement.struktur
    except FileNotFoundError:
        ergebnis.reglement_meldung = (
            f"Kein Baureglement fuer '{parzelle.gemeinde}' verfuegbar. "
            f"Potenzialberechnung wird nicht moeglich sein."
        )
        ergebnis.warnungen.append(ergebnis.reglement_meldung)

    # --- Schritt 3: BKP-Daten (Stadt Bern) ---
    bkp_quelle = None
    if (reglement is not None
            and parzelle.gemeinde == "Bern"
            and BKP_VERFUEGBAR
            and koordinate_lv95 is not None):
        ergebnis.bkp_abgefragt = True
        try:
            bkp_quelle = BernBkpQuelle()
            auskunft = bkp_quelle.hole_auskunft(*koordinate_lv95)
            if auskunft.gefunden:
                ergebnis.bkp_gefunden = True
                if auskunft.grundzone:
                    g = auskunft.grundzone
                    ergebnis.bkp_nutzungszone = (
                        f"{g.nutzungszone_kuerzel} ({g.nutzungszone_beschrieb})"
                    )
                    ergebnis.bkp_bauklasse = (
                        f"{g.bauklasse_kuerzel} ({g.bauklasse_beschrieb})"
                    )
                if auskunft.bauweise:
                    b = auskunft.bauweise
                    ergebnis.bkp_bauweise = b.bauweise_beschrieb
                    ergebnis.bkp_gebaeudelaenge_m = b.gebaeudelaenge
                    ergebnis.bkp_gebaeudetiefe_m = b.gebaeudetiefe
                    ergebnis.bkp_gebaeudelaenge_unbeschraenkt = b.gebaeudelaenge_unbeschraenkt
                    ergebnis.bkp_gebaeudetiefe_unbeschraenkt = b.gebaeudetiefe_unbeschraenkt
                else:
                    ergebnis.bkp_meldung = (
                        "Bauweise: keine Daten (z.B. BK_E oder Altstadt)"
                    )
            else:
                ergebnis.bkp_meldung = "Keine BKP-Daten gefunden fuer diese Koordinate."
        except Exception as fehler:
            ergebnis.bkp_meldung = f"BKP-Anfrage fehlgeschlagen: {fehler}"
            ergebnis.warnungen.append(ergebnis.bkp_meldung)
            bkp_quelle = None

    # --- Schritt 4: GWR-Lookup ---
    # Nur moeglich wenn Adresse-Label vorhanden (sonst kein GWR-Eintrittspunkt)
    if GWR_VERFUEGBAR and adresse_label:
        ergebnis.gwr_abgefragt = True
        try:
            gwr = GwrQuelle()
            gebaeude = gwr.gebaeude_zu_adresse(adresse_label)
            if gebaeude:
                gebaeude_parzelle = [g for g in gebaeude if g.egrid == parzelle.egrid]
                if gebaeude_parzelle:
                    ergebnis.gwr_gefunden = True
                    ergebnis.gwr_gebaeude = gebaeude_parzelle
                    summe = 0.0
                    hat_summe = False
                    for g in gebaeude_parzelle:
                        if g.grundflaeche_m2 is not None and g.geschosse is not None:
                            gf = g.geschossflaeche_m2
                            if gf is not None:
                                summe += gf
                                hat_summe = True
                    if hat_summe:
                        ergebnis.gwr_summe_geschossflaeche_m2 = summe
                else:
                    ergebnis.gwr_meldung = (
                        "Keine GWR-Gebaeudedaten fuer diese Parzelle (evtl. unbebaut)."
                    )
        except Exception as fehler:
            ergebnis.gwr_meldung = f"GWR-Anfrage uebersprungen ({fehler.__class__.__name__})"
    else:
        ergebnis.gwr_meldung = (
            "GWR uebersprungen (kein Adress-Label - typisch fuer leere Parzellen)"
        )

    # --- Schritt 5: Potenzialberechnung ---
    try:
        berechner = PotenzialBerechner()
        potenzial = berechner.berechne(parzelle, reglement, bkp_quelle=bkp_quelle)
        ergebnis.potenzial_ergebnis = potenzial
        ergebnis.textbericht = potenzial.textbericht()

        # GUI-Aliase befuellen (gleiche Logik wie analysiere())
        ergebnis.datenqualitaet = (
            potenzial.datenqualitaet.value
            if hasattr(potenzial.datenqualitaet, "value")
            else str(potenzial.datenqualitaet)
        )
        ergebnis.zulaessig_m2 = getattr(potenzial, "theoretisch_zulaessig_m2", None)
        ergebnis.ausschoepfung_prozent = getattr(potenzial, "ausschoepfungsgrad_prozent", None)
        ergebnis.theoretisch_zulaessig_m2 = getattr(potenzial, "theoretisch_zulaessig_m2", None)
        ergebnis.ausschoepfungsgrad_prozent = getattr(potenzial, "ausschoepfungsgrad_prozent", None)
        ergebnis.reserve_prozent = getattr(potenzial, "reserve_prozent", None)
        ergebnis.zonen_betrachtet = list(getattr(potenzial, "zonen_betrachtet", []) or [])
        ergebnis.zone = ergebnis.zonen_betrachtet[0] if ergebnis.zonen_betrachtet else None
        ergebnis.arealbonus_anwendbar = bool(getattr(potenzial, "arealbonus_anwendbar", False))
        ergebnis.bemerkungen = list(getattr(potenzial, "bemerkungen", []) or [])

    except Exception as fehler:
        ergebnis.potenzial_meldung = f"Potenzialberechnung fehlgeschlagen: {fehler}"
        ergebnis.warnungen.append(ergebnis.potenzial_meldung)

    return ergebnis


def main() -> int:
    if len(sys.argv) < 2:
        print("Verwendung: python analyse_adresse.py \"Strasse Nr, PLZ Ort\"")
        print()
        print("Beispiele:")
        print('  python analyse_adresse.py "Kramgasse 49, 3011 Bern"')
        print('  python analyse_adresse.py "Rathausplatz 1, 3600 Thun"')
        print('  python analyse_adresse.py "Thunstrasse 40, 3005 Bern"')
        return 1

    ergebnis = analysiere(sys.argv[1])
    drucke_bericht(ergebnis)
    return 0 if ergebnis.erfolgreich and not ergebnis.fehler else 1


if __name__ == "__main__":
    sys.exit(main())
