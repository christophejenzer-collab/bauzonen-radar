"""
gemeinde_analyse.py - Haupt-Pipeline fuer Iter-5-Massen-Analyse.

Workflow:
    1. parzellen_liste: alle Parzellen einer Gemeinde holen
    2. Pro Parzelle:
       a. Cache pruefen (wenn aktiviert)
       b. Sonst: analysiere_per_egrid()
       c. klassifiziere_parzelle()
       d. In Cache speichern
    3. Statistik bauen

CLI-Aufruf:
    python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee"
    python -m bauzonenradar.gemeinde_analyse "Thun" --limit 10
    python -m bauzonenradar.gemeinde_analyse "Bern" --no-cache
    python -m bauzonenradar.gemeinde_analyse "Bern" --refresh-aelter-als 7

Iter 5 | Stand: 12. Mai 2026
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

DEFAULT_THROTTLING_SEKUNDEN = 0.7
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SEKUNDEN = 2.0
DEFAULT_KANTON = "be"
DEFAULT_MAX_ALTER_TAGE = 30
PROGRESS_INTERVALL = 25  # Progress-Log alle N Parzellen

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------

@dataclass
class AnalyseOptionen:
    """Konfiguration fuer einen Massen-Lauf."""
    gemeinde: str
    kanton: str = DEFAULT_KANTON
    use_cache: bool = True
    refresh_aelter_als_tage: Optional[int] = None  # None = nicht refreshen
    throttling_sekunden: float = DEFAULT_THROTTLING_SEKUNDEN
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay_sekunden: float = DEFAULT_RETRY_DELAY_SEKUNDEN
    limit: Optional[int] = None  # Nur N Parzellen fuer Test


@dataclass
class GemeindeStatistik:
    """Ergebnis-Statistik eines Massen-Laufs."""
    gemeinde: str
    kanton: str
    start_zeit: datetime.datetime
    ende_zeit: Optional[datetime.datetime] = None
    total_parzellen: int = 0
    analysiert_live: int = 0
    aus_cache: int = 0
    fehler: int = 0
    pro_klassifikation: dict = field(default_factory=dict)

    @property
    def dauer_sekunden(self) -> Optional[float]:
        if self.ende_zeit is None:
            return None
        return (self.ende_zeit - self.start_zeit).total_seconds()

    def drucke_bericht(self) -> None:
        """Druckt eine ausfuehrliche Statistik auf stdout."""
        print()
        print("=" * 70)
        print(f"  Massen-Analyse: {self.gemeinde} (Kanton {self.kanton.upper()})")
        print("=" * 70)
        print(f"  Start:           {self.start_zeit.strftime('%H:%M:%S')}")
        if self.ende_zeit:
            print(f"  Ende:            {self.ende_zeit.strftime('%H:%M:%S')}")
            print(f"  Dauer:           {self.dauer_sekunden:.1f} Sekunden")
        print()
        print(f"  Total Parzellen: {self.total_parzellen}")
        print(f"  Live analysiert: {self.analysiert_live}")
        print(f"  Aus Cache:       {self.aus_cache}")
        print(f"  Fehler:          {self.fehler}")
        print()
        print(f"  Klassifikation:")
        if not self.pro_klassifikation:
            print(f"    (leer)")
        else:
            # Sortiere nach Geschaeftswert
            reihenfolge = [
                "VERDICHTUNG", "NEUGESCHAEFT", "ERSATZNEUBAU",
                "UNAUFFAELLIG", "AUSGEREIZT",
                "AUSSCHLUSS_REGLEMENT", "AUSSCHLUSS_ZU_KLEIN", "AUSSCHLUSS_FEHLER",
            ]
            for kat in reihenfolge:
                anzahl = self.pro_klassifikation.get(kat, 0)
                if anzahl:
                    print(f"    {kat:.<30}{anzahl:>5}")
            # Restliche (falls neue Kategorien dazukamen)
            for kat, anzahl in self.pro_klassifikation.items():
                if kat not in reihenfolge:
                    print(f"    {kat:.<30}{anzahl:>5}")
        print("=" * 70)


# ---------------------------------------------------------------------------
# Pro-Parzelle-Logik
# ---------------------------------------------------------------------------

def _analysiere_eine_parzelle(parz_ref, cache, opts: AnalyseOptionen):
    """Analysiert eine einzelne Parzelle - mit Cache-Check, Retry, Klassifikation.

    Args:
        parz_ref: ParzellenRef-Objekt aus parzellen_liste
        cache: KantonsCache oder None
        opts: AnalyseOptionen

    Returns:
        tuple (ergebnis, klassifikation, aus_cache: bool)
        ergebnis kann None sein bei totalem Fehler.
    """
    from klassifikation import klassifiziere

    egrid = parz_ref.egrid

    # 1. Cache-Check
    if cache and opts.use_cache and cache.hat_eintrag(egrid):
        # Wenn refresh_aelter_als_tage gesetzt, pruefe Alter
        if opts.refresh_aelter_als_tage is not None:
            if not cache.ist_aktuell(egrid, max_alter_tage=opts.refresh_aelter_als_tage):
                logger.debug(f"  {egrid}: Cache vorhanden aber zu alt, refreshe")
            else:
                ergebnis = cache.lade(egrid)
                if ergebnis is not None:
                    kategorie = klassifiziere(ergebnis)
                    return (ergebnis, kategorie, True)
        else:
            ergebnis = cache.lade(egrid)
            if ergebnis is not None:
                kategorie = klassifiziere(ergebnis)
                return (ergebnis, kategorie, True)

    # 2. Live-Analyse mit Retry
    from analyse_adresse import analysiere_per_egrid

    label = f"{parz_ref.gemeinde} Parz. {parz_ref.parzellen_nummer}"
    ergebnis = None
    letzter_fehler = None

    for versuch in range(1, opts.max_retries + 1):
        try:
            ergebnis = analysiere_per_egrid(
                egrid,
                koordinate_lv95=parz_ref.koordinate_lv95,
                adresse_label=label,
            )
            break  # Erfolg
        except Exception as e:
            letzter_fehler = e
            if versuch < opts.max_retries:
                logger.warning(
                    f"  {egrid}: Versuch {versuch}/{opts.max_retries} fehlgeschlagen ({e}), "
                    f"retry in {opts.retry_delay_sekunden}s"
                )
                time.sleep(opts.retry_delay_sekunden)
            else:
                logger.error(f"  {egrid}: Alle {opts.max_retries} Versuche fehlgeschlagen: {e}")

    if ergebnis is None:
        # Totaler Fehler nach allen Retries
        return (None, None, False)

    # 3. Klassifikation
    kategorie = klassifiziere(ergebnis)

    # 4. In Cache speichern
    if cache and opts.use_cache:
        try:
            cache.speichere(ergebnis, klassifikation=kategorie)
        except Exception as e:
            logger.warning(f"  {egrid}: Cache-Speichern fehlgeschlagen: {e}")

    return (ergebnis, kategorie, False)


# ---------------------------------------------------------------------------
# Haupt-Funktion: analysiere_gemeinde
# ---------------------------------------------------------------------------

def analysiere_gemeinde(opts: AnalyseOptionen) -> tuple[GemeindeStatistik, list]:
    """Fuehrt eine vollstaendige Massen-Analyse einer Gemeinde durch.

    Args:
        opts: AnalyseOptionen

    Returns:
        tuple (statistik, ergebnisse: list[AnalyseErgebnis])
    """
    from datenquellen.parzellen_liste import liste_parzellen_einer_gemeinde
    from gemeinde_cache import KantonsCache

    statistik = GemeindeStatistik(
        gemeinde=opts.gemeinde,
        kanton=opts.kanton,
        start_zeit=datetime.datetime.now(),
    )

    logger.info(f"=== Massen-Analyse {opts.gemeinde} (Kanton {opts.kanton.upper()}) ===")
    logger.info(f"Optionen: cache={opts.use_cache}, throttling={opts.throttling_sekunden}s, "
                f"retries={opts.max_retries}")

    # 1. Parzellen-Liste holen
    logger.info(f"Schritt 1: Parzellen-Liste holen...")
    try:
        parzellen_refs = liste_parzellen_einer_gemeinde(opts.gemeinde)
    except Exception as e:
        logger.error(f"Parzellen-Liste fehlgeschlagen: {e}")
        statistik.ende_zeit = datetime.datetime.now()
        return (statistik, [])

    if opts.limit:
        parzellen_refs = parzellen_refs[: opts.limit]
        logger.info(f"  Limit angewendet: {opts.limit} Parzellen")

    statistik.total_parzellen = len(parzellen_refs)
    logger.info(f"  {len(parzellen_refs)} Parzellen gefunden")

    if not parzellen_refs:
        logger.warning("Keine Parzellen - Abbruch")
        statistik.ende_zeit = datetime.datetime.now()
        return (statistik, [])

    # 2. Cache oeffnen
    cache = None
    if opts.use_cache:
        cache = KantonsCache(kanton=opts.kanton)
        logger.info(f"Cache aktiviert: {cache.db_pfad}")
    else:
        logger.info("Cache DEAKTIVIERT (--no-cache)")

    # 3. Pro Parzelle analysieren
    logger.info(f"Schritt 2: Parzellen analysieren...")
    ergebnisse = []
    letzter_progress = time.monotonic()

    for i, parz_ref in enumerate(parzellen_refs, 1):
        ergebnis, kategorie, aus_cache = _analysiere_eine_parzelle(parz_ref, cache, opts)

        if ergebnis is None:
            statistik.fehler += 1
            # Trotzdem in Klassifikations-Stats als FEHLER
            statistik.pro_klassifikation["AUSSCHLUSS_FEHLER"] = (
                statistik.pro_klassifikation.get("AUSSCHLUSS_FEHLER", 0) + 1
            )
        else:
            ergebnisse.append(ergebnis)
            if aus_cache:
                statistik.aus_cache += 1
            else:
                statistik.analysiert_live += 1

            if kategorie:
                statistik.pro_klassifikation[kategorie] = (
                    statistik.pro_klassifikation.get(kategorie, 0) + 1
                )

        # Progress-Log
        if i % PROGRESS_INTERVALL == 0 or i == len(parzellen_refs):
            jetzt = time.monotonic()
            seit_letzt = jetzt - letzter_progress
            rate = PROGRESS_INTERVALL / seit_letzt if seit_letzt > 0 else 0
            verbleibend = len(parzellen_refs) - i
            eta_min = (verbleibend / rate / 60) if rate > 0 else 0
            logger.info(
                f"  [{i}/{len(parzellen_refs)}] live={statistik.analysiert_live} "
                f"cache={statistik.aus_cache} fehler={statistik.fehler} "
                f"({rate:.1f} Parz/s, ETA {eta_min:.1f} min)"
            )
            letzter_progress = jetzt

        # Throttling nur bei Live-Analyse (nicht bei Cache-Hits)
        if not aus_cache and i < len(parzellen_refs):
            time.sleep(opts.throttling_sekunden)

    # 4. Cache schliessen
    if cache:
        cache.close()

    statistik.ende_zeit = datetime.datetime.now()
    logger.info(f"=== Massen-Analyse fertig in {statistik.dauer_sekunden:.1f}s ===")

    return (statistik, ergebnisse)


# ---------------------------------------------------------------------------
# CLI-Eintrittspunkt
# ---------------------------------------------------------------------------

def main() -> int:
    """CLI-Eintrittspunkt."""
    parser = argparse.ArgumentParser(
        description="Iter-5-Massen-Analyse einer Gemeinde",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Beispiele:
    python -m bauzonenradar.gemeinde_analyse "Oberhofen am Thunersee"
    python -m bauzonenradar.gemeinde_analyse "Thun" --limit 10
    python -m bauzonenradar.gemeinde_analyse "Bern" --no-cache
    python -m bauzonenradar.gemeinde_analyse "Bern" --refresh-aelter-als 7

Cache liegt in cache/cache_<kanton>.db pro Kanton.
""",
    )
    parser.add_argument(
        "gemeinde",
        help='Gemeinde-Name, z.B. "Oberhofen am Thunersee"',
    )
    parser.add_argument(
        "--kanton",
        default=DEFAULT_KANTON,
        help=f"Kanton-Kuerzel klein (default: {DEFAULT_KANTON})",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Cache deaktivieren (alles live abfragen)",
    )
    parser.add_argument(
        "--refresh-aelter-als",
        type=int,
        default=None,
        metavar="TAGE",
        help="Cache-Eintraege aelter als X Tage neu abfragen",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Nur erste N Parzellen analysieren (fuer Tests)",
    )
    parser.add_argument(
        "--throttling",
        type=float,
        default=DEFAULT_THROTTLING_SEKUNDEN,
        metavar="SEKUNDEN",
        help=f"Wartezeit zwischen API-Calls (default: {DEFAULT_THROTTLING_SEKUNDEN})",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mehr Log-Ausgabe (DEBUG-Level)",
    )

    args = parser.parse_args()

    # Logging einrichten
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    opts = AnalyseOptionen(
        gemeinde=args.gemeinde,
        kanton=args.kanton,
        use_cache=not args.no_cache,
        refresh_aelter_als_tage=args.refresh_aelter_als,
        throttling_sekunden=args.throttling,
        limit=args.limit,
    )

    try:
        statistik, ergebnisse = analysiere_gemeinde(opts)
        statistik.drucke_bericht()
        return 0
    except KeyboardInterrupt:
        print("\n*** Abbruch durch User (Strg+C). Cache-Eintraege sind gespeichert. ***")
        return 1
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler: {e}")
        return 2


if __name__ == "__main__":
    # Pfad-Setup fuer direkten Aufruf
    sys.path.insert(0, str(Path(__file__).parent))
    sys.exit(main())
