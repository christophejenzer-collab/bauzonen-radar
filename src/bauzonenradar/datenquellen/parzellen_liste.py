"""
parzellen_liste.py - Liefert die Liste aller Parzellen einer Gemeinde.

Eingangspunkt fuer Iteration 5 (Gemeinde-Massen-Analyse).

Strategie: Praefix-Baum-Traversal
    Die swisstopo SearchAPI macht **Prefix-Matching** auf Parzellennummern:
        "Oberhofen 30" -> liefert Parzellen 30, 301, 302, ..., 309
        "Oberhofen 1"  -> liefert Parzellen 1, 10-19, 100-199, 1000-1999
    Plus: API limitiert auf 50 Treffer pro Anfrage.

    Daraus ergibt sich die Strategie:
    1. Starte mit der Wildcard-Suche (nur Gemeindename) -> erste 50 Treffer
    2. Iteriere Praefixe "0".."9" -> jeweils alle Parzellen mit diesem Praefix
    3. Falls ein Praefix >= 50 Treffer liefert: rekursiv subdividieren
       ("1" -> "10".."19" -> "100".."109" usw.)
    4. Deduplizierung via EGRID-Set

    Damit klappern wir systematisch alle moeglichen Nummern ab, ohne
    bei jeder einzelnen Parzelle anzufragen.

API-Beispiel:
    GET https://api3.geo.admin.ch/rest/services/api/SearchServer
        ?type=locations&origins=parcel&searchText=Oberhofen+1&sr=2056

API-Response-Format (verifiziert 11.05.2026):
    {
      "results": [
        {
          "attrs": {
            "label": "<b>Oberhofen am Thunersee</b> 1 (CH 5501 4696 3519)",
            "detail": "1 oberhofen am thunersee 934 ch550146963519",
            "origin": "parcel",
            "y": 2618457.0,        # east in LV95
            "x": 1174925.125,      # north in LV95
            "lat": 46.7252...,
            "lon": 7.6800...
          }
        }
      ]
    }

Wichtige API-Eigenschaften:
    - 'detail'-Feld: "<nummer> <gemeinde> <bfs> <egrid>"
    - 'label' enthaelt formatierte Anzeige mit HTML
    - EGRID NICHT in eigenem Feld, nur in detail/label
    - Maximal 50 Treffer pro Anfrage (Standard)
    - Prefix-Matching auf Nummern

CLI-Aufruf:
    python -m bauzonenradar.datenquellen.parzellen_liste "Oberhofen am Thunersee"
    python parzellen_liste.py "Thun" --verbose

Iteration 5 | Stand: 11. Mai 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

SEARCH_API_URL = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

# Throttling: 0.7 Sekunden Pause zwischen Calls
THROTTLE_SEKUNDEN = 0.7

# SearchAPI Limit pro Anfrage
TREFFER_PRO_ANFRAGE = 50

# Maximale Rekursionstiefe fuer Praefix-Baum
# 5 Ebenen = bis zu 9-stellige Parzellennummern (mehr als realistisch)
MAX_PRAEFIX_TIEFE = 5

# Maximale Anzahl API-Calls als Sicherheitsnetz
# 10^1 + 10^2 + 10^3 + 10^4 + 10^5 = 111'110 theoretisches Max
# In der Praxis: ca. 100-200 Calls pro Gemeinde
MAX_API_CALLS = 500

# User-Agent
USER_AGENT = "Bauzonen-Radar/1.0 (Iter5 Massenanalyse)"

# HTTP-Timeout
HTTP_TIMEOUT_SEKUNDEN = 30

# Regex fuer EGRID-Extraktion
EGRID_PATTERN = re.compile(r"\b(ch[0-9a-f]{12,16})\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Datenklasse
# ---------------------------------------------------------------------------

@dataclass
class ParzellenRef:
    """Minimal-Referenz auf eine Parzelle - Eintrittspunkt fuer Detail-Analyse."""

    gemeinde: str
    parzellen_nummer: str
    egrid: str
    koordinate_lv95: tuple[float, float]
    koordinate_wgs84: Optional[tuple[float, float]] = None
    bfs_nummer: Optional[int] = None
    label: str = ""

    def __repr__(self) -> str:
        return f"<Parzelle {self.gemeinde} {self.parzellen_nummer} EGRID={self.egrid}>"


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ParzellenListeFehler(Exception):
    """Basis-Exception fuer dieses Modul."""


class ParzellenListeApiFehler(ParzellenListeFehler):
    """Fehler beim API-Call."""


class ParzellenListeParseFehler(ParzellenListeFehler):
    """Fehler beim Parsen der API-Antwort."""


# ---------------------------------------------------------------------------
# Helper: HTTP-Call
# ---------------------------------------------------------------------------

def _fetch_search_api(search_text: str) -> dict:
    """Ruft die swisstopo SearchAPI mit origins=parcel auf."""
    params = {
        "type": "locations",
        "origins": "parcel",
        "searchText": search_text,
        "sr": "2056",
    }
    url = f"{SEARCH_API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SEKUNDEN) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise ParzellenListeApiFehler(
            f"HTTP-Fehler {e.code} bei Suche '{search_text}': {e.reason}"
        ) from e
    except urllib.error.URLError as e:
        raise ParzellenListeApiFehler(
            f"Netzwerk-Fehler bei Suche '{search_text}': {e.reason}"
        ) from e
    except TimeoutError as e:
        raise ParzellenListeApiFehler(
            f"Timeout bei Suche '{search_text}'"
        ) from e

    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise ParzellenListeParseFehler(
            f"JSON-Parse-Fehler: {e.msg}"
        ) from e


# ---------------------------------------------------------------------------
# Helper: Parsen eines API-Treffers
# ---------------------------------------------------------------------------

def _parse_parzellen_treffer(treffer: dict, gemeinde: str) -> Optional[ParzellenRef]:
    """Wandelt einen SearchAPI-Treffer in eine ParzellenRef um.

    Format detail-Feld: "<nummer> <gemeinde> <bfs> <egrid>"
    Beispiel: "309 oberhofen am thunersee 934 ch382046359635"
    """
    attrs = treffer.get("attrs", {})

    if attrs.get("origin") != "parcel":
        return None

    detail = attrs.get("detail", "")
    if not detail:
        return None

    # EGRID via Regex
    egrid_match = EGRID_PATTERN.search(detail)
    if not egrid_match:
        return None
    egrid = egrid_match.group(1).upper()

    # Parzellennummer = erstes Token
    detail_tokens = detail.split()
    if not detail_tokens:
        return None
    parzellen_nummer = detail_tokens[0]

    # BFS-Nummer = letztes numerisches Token vor EGRID
    bfs_nummer: Optional[int] = None
    try:
        egrid_index = detail_tokens.index(egrid_match.group(1))
        if egrid_index > 0:
            bfs_kandidat = detail_tokens[egrid_index - 1]
            if bfs_kandidat.isdigit():
                bfs_nummer = int(bfs_kandidat)
    except (ValueError, IndexError):
        pass

    # Koordinaten LV95
    east = attrs.get("y")
    north = attrs.get("x")
    if east is None or north is None:
        return None
    koordinate_lv95 = (float(east), float(north))

    # WGS84
    koordinate_wgs84 = None
    lat = attrs.get("lat")
    lon = attrs.get("lon")
    if lat is not None and lon is not None:
        koordinate_wgs84 = (float(lat), float(lon))

    label = attrs.get("label", "")

    return ParzellenRef(
        gemeinde=gemeinde,
        parzellen_nummer=parzellen_nummer,
        egrid=egrid,
        koordinate_lv95=koordinate_lv95,
        koordinate_wgs84=koordinate_wgs84,
        bfs_nummer=bfs_nummer,
        label=label,
    )


# ---------------------------------------------------------------------------
# Praefix-Baum-Traversal: rekursive Suche
# ---------------------------------------------------------------------------

def _sammle_praefix(
    gemeinde: str,
    praefix: str,
    tiefe: int,
    gesehene_egrids: set[str],
    parzellen: list[ParzellenRef],
    call_counter: list[int],
    throttle_sekunden: float,
) -> None:
    """Rekursive Helper-Funktion fuer Praefix-Baum-Traversal.

    Args:
        gemeinde: Ziel-Gemeinde
        praefix: Aktueller Nummern-Praefix (leer fuer Wildcard)
        tiefe: Aktuelle Rekursionstiefe (Sicherheits-Stopp)
        gesehene_egrids: Set fuer Deduplizierung (mutiert)
        parzellen: Liste der bisher gefundenen Parzellen (mutiert)
        call_counter: List mit einem Element zum Mitzaehlen (mutiert)
        throttle_sekunden: Pause zwischen Calls
    """
    if call_counter[0] >= MAX_API_CALLS:
        logger.warning(f"MAX_API_CALLS={MAX_API_CALLS} erreicht - breche ab")
        return

    if tiefe > MAX_PRAEFIX_TIEFE:
        logger.warning(f"MAX_PRAEFIX_TIEFE={MAX_PRAEFIX_TIEFE} erreicht bei Praefix '{praefix}'")
        return

    # Such-Text bauen
    if praefix:
        search_text = f"{gemeinde} {praefix}"
    else:
        search_text = gemeinde

    logger.info(
        f"Praefix '{praefix}' (Tiefe {tiefe}): searchText='{search_text}' "
        f"(bisher {len(parzellen)} Parzellen, {call_counter[0]} API-Calls)"
    )

    # API-Call mit einfacher Retry-Logic
    try:
        response = _fetch_search_api(search_text)
    except ParzellenListeApiFehler as e:
        logger.warning(f"API-Fehler bei Praefix '{praefix}': {e}")
        time.sleep(throttle_sekunden * 2)
        try:
            response = _fetch_search_api(search_text)
        except ParzellenListeApiFehler as e2:
            logger.error(f"Retry fehlgeschlagen: {e2}. Praefix '{praefix}' uebersprungen.")
            return

    call_counter[0] += 1
    treffer_liste = response.get("results", [])

    # Treffer einsammeln
    neue_in_praefix = 0
    for treffer in treffer_liste:
        parzelle = _parse_parzellen_treffer(treffer, gemeinde)
        if parzelle is None:
            continue
        if parzelle.egrid not in gesehene_egrids:
            gesehene_egrids.add(parzelle.egrid)
            parzellen.append(parzelle)
            neue_in_praefix += 1

    logger.info(
        f"  -> {len(treffer_liste)} Treffer, {neue_in_praefix} neue, "
        f"{len(treffer_liste) - neue_in_praefix} Duplikate"
    )

    # Throttling
    time.sleep(throttle_sekunden)

    # Rekursion: wenn Treffer-Limit erreicht, subdivide
    # ABER: bei leerem Praefix immer subdividen (Wildcard-Suche)
    treffer_limit_erreicht = len(treffer_liste) >= TREFFER_PRO_ANFRAGE
    ist_wildcard = (praefix == "")

    if treffer_limit_erreicht or ist_wildcard:
        # Subdivide: hange "0".."9" an den Praefix
        for ziffer in "0123456789":
            neuer_praefix = praefix + ziffer
            _sammle_praefix(
                gemeinde=gemeinde,
                praefix=neuer_praefix,
                tiefe=tiefe + 1,
                gesehene_egrids=gesehene_egrids,
                parzellen=parzellen,
                call_counter=call_counter,
                throttle_sekunden=throttle_sekunden,
            )


# ---------------------------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------------------------

def liste_parzellen_einer_gemeinde(
    gemeinde: str,
    throttle_sekunden: float = THROTTLE_SEKUNDEN,
) -> list[ParzellenRef]:
    """Liefert alle Parzellen einer Gemeinde via Praefix-Baum-Traversal.

    Args:
        gemeinde: Gemeindename, z.B. "Oberhofen am Thunersee"
        throttle_sekunden: Pause zwischen API-Calls (default 0.7s)

    Returns:
        Liste der Parzellen-Referenzen, dedupliziert per EGRID.
        Sortiert nach Parzellen-Nummer (nummerisch wenn moeglich).

    Strategie:
        1. Wildcard-Anfrage ("<gemeinde>") -> erste 50 Treffer
        2. Praefix "0", "1", ... "9" -> jeweils mehr Treffer
        3. Bei >= 50 Treffer pro Praefix: rekursiv subdividieren
        4. Deduplizierung via EGRID
    """
    if not gemeinde or not gemeinde.strip():
        raise ValueError("Gemeinde darf nicht leer sein")

    gemeinde = gemeinde.strip()
    gesehene_egrids: set[str] = set()
    parzellen: list[ParzellenRef] = []
    call_counter = [0]  # Liste fuer Mutation in Rekursion

    logger.info(f"Starte Parzellen-Liste fuer Gemeinde '{gemeinde}'")
    start = time.time()

    # Start mit leerem Praefix (Wildcard) - das triggert die initiale
    # Suche plus Subdivision auf "0".."9"
    _sammle_praefix(
        gemeinde=gemeinde,
        praefix="",
        tiefe=0,
        gesehene_egrids=gesehene_egrids,
        parzellen=parzellen,
        call_counter=call_counter,
        throttle_sekunden=throttle_sekunden,
    )

    laufzeit = time.time() - start
    logger.info(
        f"Fertig: {len(parzellen)} Parzellen fuer '{gemeinde}' gesammelt "
        f"({call_counter[0]} API-Calls, {laufzeit:.1f}s)"
    )

    # Sortierung: nummerisch wenn moeglich
    def sortier_key(p: ParzellenRef):
        try:
            return (0, int(p.parzellen_nummer))
        except (ValueError, TypeError):
            return (1, p.parzellen_nummer)

    parzellen.sort(key=sortier_key)
    return parzellen


# ---------------------------------------------------------------------------
# CLI-Eintrittspunkt
# ---------------------------------------------------------------------------

def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="Listet alle Parzellen einer Gemeinde via Praefix-Baum-Traversal"
    )
    parser.add_argument(
        "gemeinde",
        help='Gemeinde-Name, z.B. "Oberhofen am Thunersee"',
    )
    parser.add_argument(
        "--throttle",
        type=float,
        default=THROTTLE_SEKUNDEN,
        help=f"Pause zwischen API-Calls in Sekunden (default {THROTTLE_SEKUNDEN})",
    )
    parser.add_argument(
        "--limit-output",
        type=int,
        default=30,
        help="Anzahl Parzellen die im Output gezeigt werden (default 30)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detailliertes Logging anzeigen",
    )

    args = parser.parse_args()

    # Logging
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    print(f"Suche Parzellen fuer Gemeinde: {args.gemeinde}")
    print(f"  Throttling: {args.throttle}s")
    print()

    start_zeit = time.time()
    try:
        parzellen = liste_parzellen_einer_gemeinde(
            args.gemeinde,
            throttle_sekunden=args.throttle,
        )
    except ParzellenListeFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1

    laufzeit = time.time() - start_zeit
    print(f"Laufzeit: {laufzeit:.1f}s")
    print(f"Anzahl Parzellen: {len(parzellen)}")
    print()

    if len(parzellen) == 0:
        print("Keine Parzellen gefunden. Pruefe Gemeinde-Name.")
        return 1

    # BFS
    bfs_set = {p.bfs_nummer for p in parzellen if p.bfs_nummer is not None}
    if bfs_set:
        print(f"BFS-Gemeindenummer(n): {sorted(bfs_set)}")
        print()

    # Nummer-Statistik
    nummern_int = []
    for p in parzellen:
        try:
            nummern_int.append(int(p.parzellen_nummer))
        except (ValueError, TypeError):
            pass
    if nummern_int:
        print(f"Nummern-Bereich: {min(nummern_int)} bis {max(nummern_int)}")
        print()

    print(f"Erste {min(args.limit_output, len(parzellen))} Parzellen:")
    print(f"{'Nr.':>8}  {'EGRID':<20}  {'Koord LV95':<22}  Label")
    print("-" * 90)
    for p in parzellen[: args.limit_output]:
        koord_str = f"{p.koordinate_lv95[0]:.0f}, {p.koordinate_lv95[1]:.0f}"
        label_clean = re.sub(r"<[^>]+>", "", p.label).strip()
        print(f"{p.parzellen_nummer:>8}  {p.egrid:<20}  {koord_str:<22}  {label_clean[:40]}")

    if len(parzellen) > args.limit_output:
        print(f"... und {len(parzellen) - args.limit_output} weitere")

    return 0


if __name__ == "__main__":
    sys.exit(_cli())
