"""
Bauklassenplan Stadt Bern - ArcGIS REST-API-Anbindung.

Holt parzellenscharfe Daten aus dem Bauklassenplan (BKP) der Stadt Bern
ueber die ArcGIS REST-API von map.bern.ch:

- Layer 88 (BKP_Bauweise): Bauweise (offen/geschlossen), Gebaeudelaenge,
  Gebaeudetiefe pro Parzelle.
- Layer 95 (BKP_Grundzonen_Flaechen): Nutzungszone (W, WG, G, ...)
  und Bauklasse (BK_1 bis BK_6, E, Spez).

Beide Layer werden mit Punkt-in-Polygon-Abfragen kombiniert, sodass wir
fuer jede Adresse in der Stadt Bern die volle Information bekommen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import urllib.parse
import urllib.request
import json


# ArcGIS REST-API Endpoint Stadt Bern
BASE_URL = "https://map.bern.ch/arcgis/rest/services/Geoportal/Bauklassenplan/MapServer"
LAYER_BAUWEISE = 88
LAYER_GRUNDZONEN = 95

# HTTP-Timeout (Sekunden)
TIMEOUT = 10


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BkpBauweise:
    """Daten aus Layer 88 (BKP_Bauweise)."""

    bauweise_typologie: int
    bauweise_beschrieb: str  # z.B. "offen", "geschlossen"
    gebaeudelaenge: Optional[int]  # m, None falls unbeschraenkt
    gebaeudetiefe: Optional[int]  # m, None falls unbeschraenkt
    gebaeudelaenge_unbeschraenkt: bool
    gebaeudetiefe_unbeschraenkt: bool


@dataclass(frozen=True)
class BkpGrundzone:
    """Daten aus Layer 95 (BKP_Grundzonen_Flaechen)."""

    nutzungszone_code: int  # z.B. 1000
    nutzungszone_kuerzel: str  # z.B. "W"
    nutzungszone_beschrieb: str  # z.B. "W - Wohnzone"
    bauklasse_code: int  # z.B. 1001
    bauklasse_kuerzel: str  # z.B. "BK_2", "E"
    bauklasse_beschrieb: str  # z.B. "BK_2 - Bauklasse 2"


@dataclass(frozen=True)
class BkpAuskunft:
    """Kombinierte Auskunft aus Layer 88 + 95 fuer einen Punkt."""

    bauweise: Optional[BkpBauweise]
    grundzone: Optional[BkpGrundzone]

    @property
    def gefunden(self) -> bool:
        """True falls mindestens einer der beiden Layer Daten lieferte."""
        return self.bauweise is not None or self.grundzone is not None


# ---------------------------------------------------------------------------
# Hilfsfunktionen: Code -> Kuerzel
# ---------------------------------------------------------------------------


def _kuerzel_aus_beschrieb(beschrieb: Optional[str]) -> str:
    """Extrahiert das Kuerzel aus einem Beschrieb-String.

    Beispiele:
        'W - Wohnzone'        -> 'W'
        'BK_2 - Bauklasse 2'  -> 'BK_2'
        'BK_E - Bauklasse E'  -> 'BK_E'
    """
    if not beschrieb:
        return ""
    teil = beschrieb.split(" - ", 1)[0].strip()
    return teil


# ---------------------------------------------------------------------------
# HTTP-Aufruf
# ---------------------------------------------------------------------------


def _arcgis_punkt_query(layer_id: int, ost_lv95: float, nord_lv95: float) -> dict:
    """Fuehrt eine Punkt-in-Polygon-Abfrage gegen einen ArcGIS-Layer aus.

    Args:
        layer_id: ID des MapServer-Layers (z.B. 88 oder 95).
        ost_lv95: Ostkoordinate in LV95 (z.B. 2601810).
        nord_lv95: Nordkoordinate in LV95 (z.B. 1200030).

    Returns:
        Geparstes JSON-Dict des ArcGIS-Servers.

    Raises:
        urllib.error.URLError, ValueError bei Netz- oder Parse-Fehlern.
    """
    geometry = f"{ost_lv95},{nord_lv95}"
    params = {
        "geometry": geometry,
        "geometryType": "esriGeometryPoint",
        "inSR": "2056",  # LV95
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "false",
        "f": "pjson",
    }
    url = f"{BASE_URL}/{layer_id}/query?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url, timeout=TIMEOUT) as response:
        rohdaten = response.read().decode("utf-8")
    return json.loads(rohdaten)


# ---------------------------------------------------------------------------
# Layer 88: Bauweise
# ---------------------------------------------------------------------------


def _parse_bauweise(antwort: dict) -> Optional[BkpBauweise]:
    """Parst die Antwort von Layer 88 in ein BkpBauweise-Objekt."""
    features = antwort.get("features") or []
    if not features:
        return None
    attrs = features[0].get("attributes") or {}

    laenge_unbeschr = attrs.get("Gebaeudelaenge_unbeschraenkt") == 1
    tiefe_unbeschr = attrs.get("Gebaeudetiefe_unbeschraenkt") == 1

    return BkpBauweise(
        bauweise_typologie=attrs.get("Bauweise_typologie") or 0,
        bauweise_beschrieb=attrs.get("Bauweise_typologie_beschrieb") or "",
        gebaeudelaenge=None if laenge_unbeschr else attrs.get("Gebaeudelaenge"),
        gebaeudetiefe=None if tiefe_unbeschr else attrs.get("Gebaeudetiefe"),
        gebaeudelaenge_unbeschraenkt=laenge_unbeschr,
        gebaeudetiefe_unbeschraenkt=tiefe_unbeschr,
    )


# ---------------------------------------------------------------------------
# Layer 95: Grundzonen
# ---------------------------------------------------------------------------


def _parse_grundzone(antwort: dict) -> Optional[BkpGrundzone]:
    """Parst die Antwort von Layer 95 in ein BkpGrundzone-Objekt."""
    features = antwort.get("features") or []
    if not features:
        return None
    attrs = features[0].get("attributes") or {}

    nutzungszone_beschrieb = attrs.get("U_nutzungszone_beschrieb") or ""
    bauklasse_beschrieb = attrs.get("U_bauklasse_beschrieb") or ""

    return BkpGrundzone(
        nutzungszone_code=attrs.get("U_nutzungszone") or 0,
        nutzungszone_kuerzel=_kuerzel_aus_beschrieb(nutzungszone_beschrieb),
        nutzungszone_beschrieb=nutzungszone_beschrieb,
        bauklasse_code=attrs.get("U_bauklasse") or 0,
        bauklasse_kuerzel=_kuerzel_aus_beschrieb(bauklasse_beschrieb),
        bauklasse_beschrieb=bauklasse_beschrieb,
    )


# ---------------------------------------------------------------------------
# Hauptklasse: BernBkpQuelle
# ---------------------------------------------------------------------------


class BernBkpQuelle:
    """ArcGIS-Anbindung fuer den Bauklassenplan Stadt Bern.

    Nutzt einen Cache pro Session, um wiederholte Abfragen fuer die gleiche
    Koordinate zu vermeiden.
    """

    def __init__(self) -> None:
        # Cache: Schluessel ist (ost_lv95_gerundet, nord_lv95_gerundet)
        self._cache: dict[tuple[int, int], BkpAuskunft] = {}

    def hole_auskunft(self, ost_lv95: float, nord_lv95: float) -> BkpAuskunft:
        """Holt die kombinierte BKP-Auskunft fuer einen Punkt in LV95.

        Args:
            ost_lv95: Ostkoordinate in LV95.
            nord_lv95: Nordkoordinate in LV95.

        Returns:
            BkpAuskunft mit Daten aus Layer 88 und Layer 95.
            Wenn fuer eine der beiden Quellen keine Daten gefunden wurden,
            ist das jeweilige Feld None.
        """
        cache_key = (round(ost_lv95), round(nord_lv95))
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Layer 88: Bauweise
        bauweise: Optional[BkpBauweise] = None
        try:
            antwort_88 = _arcgis_punkt_query(LAYER_BAUWEISE, ost_lv95, nord_lv95)
            bauweise = _parse_bauweise(antwort_88)
        except Exception:
            # Bei Fehlern bleibt bauweise None - die App soll trotzdem
            # funktionieren (Fallback auf Grobschaetzung).
            bauweise = None

        # Layer 95: Grundzone
        grundzone: Optional[BkpGrundzone] = None
        try:
            antwort_95 = _arcgis_punkt_query(LAYER_GRUNDZONEN, ost_lv95, nord_lv95)
            grundzone = _parse_grundzone(antwort_95)
        except Exception:
            grundzone = None

        auskunft = BkpAuskunft(bauweise=bauweise, grundzone=grundzone)
        self._cache[cache_key] = auskunft
        return auskunft


# ---------------------------------------------------------------------------
# Manueller Test (CLI)
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Test mit Thunstrasse 40, Bern (LV95: 2601810, 1200030)
    quelle = BernBkpQuelle()
    auskunft = quelle.hole_auskunft(2601810, 1200030)

    print("=" * 60)
    print("BKP-Auskunft fuer Thunstrasse 40, Bern (LV95: 2601810/1200030)")
    print("=" * 60)
    print()

    if auskunft.bauweise:
        b = auskunft.bauweise
        print("Layer 88 - BKP_Bauweise:")
        print(f"  Bauweise:        {b.bauweise_beschrieb} (Code {b.bauweise_typologie})")
        if b.gebaeudelaenge_unbeschraenkt:
            print("  Gebaeudelaenge:  unbeschraenkt")
        else:
            print(f"  Gebaeudelaenge:  {b.gebaeudelaenge} m")
        if b.gebaeudetiefe_unbeschraenkt:
            print("  Gebaeudetiefe:   unbeschraenkt")
        else:
            print(f"  Gebaeudetiefe:   {b.gebaeudetiefe} m")
    else:
        print("Layer 88 - BKP_Bauweise: keine Daten gefunden")

    print()

    if auskunft.grundzone:
        g = auskunft.grundzone
        print("Layer 95 - BKP_Grundzonen_Flaechen:")
        print(f"  Nutzungszone:    {g.nutzungszone_kuerzel}  ({g.nutzungszone_beschrieb})")
        print(f"  Bauklasse:       {g.bauklasse_kuerzel}  ({g.bauklasse_beschrieb})")
    else:
        print("Layer 95 - BKP_Grundzonen_Flaechen: keine Daten gefunden")
