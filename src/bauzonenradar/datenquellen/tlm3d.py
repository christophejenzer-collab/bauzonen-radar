"""
tlm3d.py - Datenquellen swissTLM3D Strassen + BFS Arealstatistik Bodenbedeckung.

Zweck Iter 5: NEUGESCHAEFT-False-Positives reduzieren indem Strassen und
Waldparzellen als solche erkannt werden.

Layer:
- ch.swisstopo.swisstlm3d-strassen (TLM3D Strassen, offiziell, aktuell)
- ch.bfs.arealstatistik-bodenbedeckung (Arealstatistik NOLC04, 1979/85,
  100x100m-Raster - mit Vorsicht zu geniessen!)

Beide via MapServer-identify-Endpoint (wie GWR).
"""
from __future__ import annotations

import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

API_BASIS = "https://api3.geo.admin.ch/rest/services/ech/MapServer/identify"

LAYER_STRASSEN = "ch.swisstopo.swisstlm3d-strassen"
LAYER_AREALSTATISTIK = "ch.bfs.arealstatistik-bodenbedeckung"

# Bodenbedeckungs-Codes (lc09r_27) der Arealstatistik
# https://www.bfs.admin.ch/asset/de/26565195
NOLC_WALD = {41, 42, 43, 44, 45}  # Geschlossene/offene Baumbestaende
NOLC_BEFESTIGT = {11, 12, 13, 14, 15, 16, 17}  # Gebaeude/befestigt
NOLC_WASSER = {61, 62}  # Stehendes / fliessendes Wasser

DEFAULT_THROTTLE = 0.0
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 2.0


# ---------------------------------------------------------------------------
# Fehlerklasse
# ---------------------------------------------------------------------------

class TlmFehler(RuntimeError):
    """API-Fehler bei TLM3D / Arealstatistik-Abfragen."""


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------

@dataclass
class StrassenTreffer:
    """Ein Strassen-Feature aus TLM3D."""
    strassenname: str | None
    objektart: int | None  # 10=Autobahn,11=Hauptstrasse,...,16=Wegspur
    belagsart: int | None
    verkehrsbedeutung: int | None
    eigentuemer: int | None


@dataclass
class ArealstatistikTreffer:
    """Ein Bodenbedeckungs-Feature aus der BFS-Arealstatistik."""
    code: int  # lc09r_27
    beschreibung: str  # desc_lc09r_27_de
    jahr: int | None  # year

    @property
    def ist_wald(self) -> bool:
        return self.code in NOLC_WALD

    @property
    def ist_befestigt(self) -> bool:
        return self.code in NOLC_BEFESTIGT

    @property
    def ist_wasser(self) -> bool:
        return self.code in NOLC_WASSER


# ---------------------------------------------------------------------------
# Basis-Klasse
# ---------------------------------------------------------------------------

class _MapServerIdentifyBasis:
    """Gemeinsame HTTP/Cache-Logik fuer TLM3D + Arealstatistik."""

    def __init__(self, throttle: float = DEFAULT_THROTTLE,
                 retries: int = DEFAULT_RETRIES,
                 retry_delay: float = DEFAULT_RETRY_DELAY):
        self.throttle = throttle
        self.retries = retries
        self.retry_delay = retry_delay

    def _identify(self, koord_lv95: tuple[float, float], layer: str,
                  tolerance: int = 15) -> list[dict[str, Any]]:
        """Identify am MapServer mit Punkt-Geometrie."""
        if koord_lv95 is None or len(koord_lv95) != 2:
            return []
        east, north = koord_lv95
        params = {
            "geometryType": "esriGeometryPoint",
            "geometry": f"{east},{north}",
            "geometryFormat": "geojson",
            "imageDisplay": "1000,1000,96",
            "mapExtent": f"{east-500},{north-500},{east+500},{north+500}",
            "tolerance": str(int(tolerance)),
            "layers": f"all:{layer}",
            "sr": "2056",
            "returnGeometry": "false",
        }
        url = API_BASIS + "?" + urllib.parse.urlencode(params)
        return self._http_get_json(url).get("results") or []

    def _http_get_json(self, url: str) -> dict[str, Any]:
        if self.throttle > 0:
            time.sleep(self.throttle)
        letzter_fehler: Exception | None = None
        delay = self.retry_delay
        for versuch in range(self.retries):
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    import json as _json
                    return _json.loads(resp.read())
            except urllib.error.HTTPError as fehler:
                # 400 = Layer kann nicht via identify abgefragt werden -> nicht retryen
                if fehler.code == 400:
                    raise TlmFehler(f"Layer nicht via identify abfragbar: {fehler.code}") from fehler
                letzter_fehler = fehler
            except (urllib.error.URLError, TimeoutError) as fehler:
                letzter_fehler = fehler
            time.sleep(delay)
            delay *= 1.5
        raise TlmFehler(f"API-Abfrage fehlgeschlagen nach {self.retries} Versuchen: {letzter_fehler}")


# ---------------------------------------------------------------------------
# TlmStrassenQuelle
# ---------------------------------------------------------------------------

class TlmStrassenQuelle(_MapServerIdentifyBasis):
    """Fragt swissTLM3D Strassen-Layer ab."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache: dict[tuple[float, float, int], list[StrassenTreffer]] = {}

    def strassen_an_koord(self, koord_lv95: tuple[float, float],
                          tolerance: int = 15) -> list[StrassenTreffer]:
        """Liefert alle Strassen-Features im Umkreis 'tolerance' Meter.

        Args:
            koord_lv95: (east, north)
            tolerance: Toleranz in Metern. 10-15m = wirklich auf Strasse,
                       50m = "in der Naehe einer Strasse".

        Returns:
            Liste von StrassenTreffer. Leer wenn nichts in der Naehe.
        """
        cache_key = (round(koord_lv95[0], 0), round(koord_lv95[1], 0), tolerance)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            features = self._identify(koord_lv95, LAYER_STRASSEN, tolerance=tolerance)
        except TlmFehler as fehler:
            logger.warning(f"TLM-Strassen-Abfrage fehlgeschlagen: {fehler}")
            return []

        treffer: list[StrassenTreffer] = []
        for f in features:
            p = f.get("properties") or {}
            treffer.append(StrassenTreffer(
                strassenname=p.get("strassenname"),
                objektart=p.get("objektart"),
                belagsart=p.get("belagsart"),
                verkehrsbedeutung=p.get("verkehrsbedeutung"),
                eigentuemer=p.get("eigentuemer"),
            ))

        self._cache[cache_key] = treffer
        return treffer

    def ist_auf_strasse(self, koord_lv95: tuple[float, float],
                        tolerance: int = 15) -> bool:
        """True wenn TLM3D an dieser Koordinate eine Strasse hat (in Tolerance)."""
        return len(self.strassen_an_koord(koord_lv95, tolerance=tolerance)) > 0


# ---------------------------------------------------------------------------
# ArealstatistikQuelle
# ---------------------------------------------------------------------------

class ArealstatistikQuelle(_MapServerIdentifyBasis):
    """Fragt BFS-Arealstatistik (Bodenbedeckung NOLC04) ab.

    ACHTUNG: Daten sind alt (1979/85) und in einem 100x100m-Raster, also
    nur als grobe Heuristik geeignet. Bei Ufer-Parzellen oft "Wasser"-Treffer.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache: dict[tuple[float, float], list[ArealstatistikTreffer]] = {}

    def bodenbedeckung(self, koord_lv95: tuple[float, float],
                       tolerance: int = 50) -> list[ArealstatistikTreffer]:
        """Liefert alle Bodenbedeckungs-Eintraege am Punkt.

        Die Arealstatistik liefert Eintraege fuer mehrere Erhebungs-Jahre
        (1979/85, 1992/97, 2004/09, etc.). Wir geben alle zurueck - der
        Aufrufer entscheidet welche relevant sind.
        """
        cache_key = (round(koord_lv95[0], 0), round(koord_lv95[1], 0))
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            features = self._identify(koord_lv95, LAYER_AREALSTATISTIK, tolerance=tolerance)
        except TlmFehler as fehler:
            logger.warning(f"Arealstatistik-Abfrage fehlgeschlagen: {fehler}")
            return []

        treffer: list[ArealstatistikTreffer] = []
        for f in features:
            p = f.get("properties") or {}
            code = p.get("lc09r_27")
            if code is None:
                continue
            try:
                code_int = int(code)
            except (ValueError, TypeError):
                continue
            treffer.append(ArealstatistikTreffer(
                code=code_int,
                beschreibung=p.get("desc_lc09r_27_de") or "?",
                jahr=p.get("year"),
            ))

        self._cache[cache_key] = treffer
        return treffer

    def neueste_klassifikation(self, koord_lv95: tuple[float, float]) -> ArealstatistikTreffer | None:
        """Liefert den neuesten Bodenbedeckungs-Eintrag (groesstes Jahr)."""
        eintraege = self.bodenbedeckung(koord_lv95)
        if not eintraege:
            return None
        return max(eintraege, key=lambda t: t.jahr or 0)

    def ist_wald(self, koord_lv95: tuple[float, float]) -> bool:
        """True wenn die neueste Bodenbedeckung Wald ist."""
        neueste = self.neueste_klassifikation(koord_lv95)
        return neueste is not None and neueste.ist_wald


# ---------------------------------------------------------------------------
# CLI-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    print("Test: TlmStrassenQuelle")
    tlm = TlmStrassenQuelle()
    parz1 = (2618457, 1174925)  # Strasse
    parz677 = (2617435, 1176417)  # Wald
    parz100 = (2617469, 1175135)  # bebaut

    print(f"  Parz 1   ist_auf_strasse (tol=15): {tlm.ist_auf_strasse(parz1, 15)}")
    print(f"  Parz 677 ist_auf_strasse (tol=15): {tlm.ist_auf_strasse(parz677, 15)}")
    print(f"  Parz 100 ist_auf_strasse (tol=15): {tlm.ist_auf_strasse(parz100, 15)}")

    print()
    print("Test: ArealstatistikQuelle")
    areal = ArealstatistikQuelle()
    for label, koord in [("Parz 1", parz1), ("Parz 677", parz677), ("Parz 100", parz100)]:
        neueste = areal.neueste_klassifikation(koord)
        if neueste:
            print(f"  {label}: code={neueste.code}, {neueste.beschreibung} ({neueste.jahr})  ist_wald={neueste.ist_wald}")
        else:
            print(f"  {label}: keine Daten")
