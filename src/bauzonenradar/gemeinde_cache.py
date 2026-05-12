"""
gemeinde_cache.py - SQLite-Cache pro Kanton fuer Iter-5-Massen-Analyse.

Persistiert vollstaendige AnalyseErgebnis-Objekte (Strategie A:
vollstaendige Serialisierung) sodass spaetere Lauefe die OEREB-Pipeline
nicht erneut durchspielen muessen.

Datei-Layout:
    cache/
    +-- cache_be.db        # Kanton Bern (Default)
    +-- cache_zh.db        # spaeter
    +-- cache_lu.db        # spaeter

Schema (Version 1):
    parzellen-Tabelle mit flachen Feldern (fuer schnelle Queries):
        egrid                PRIMARY KEY
        gemeinde             fuer Filter
        bfs_nummer           BFS-Gemeindenummer
        abfrage_datum        ISO-Timestamp fuer Aktualitaets-Pruefung
        schema_version       fuer Migration spaeter
        ...sowie flache Statistik-Felder fuer Ranglisten...
    plus daten_json: vollstaendiges AnalyseErgebnis als JSON

Serialisierungs-Strategie:
    - dataclasses.asdict() rekursiv
    - Custom Encoder fuer Enums (Lawstatus, Datenqualitaet, PotenzialStatus)
    - Tupel werden zu Listen (JSON kann nichts anderes)
    - Beim Laden: Rekonstruktion via __init__ der Datenklassen

Iter 5 | Stand: 11. Mai 2026
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import logging
import sqlite3
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1
DEFAULT_KANTON = "be"
CACHE_VERZEICHNIS = Path("cache")
DEFAULT_MAX_ALTER_TAGE = 30

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Serialisierung
# ---------------------------------------------------------------------------

class CacheEncoder(json.JSONEncoder):
    """Custom JSON-Encoder fuer Enums und sonstige Spezialfaelle."""

    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return {"__enum__": o.__class__.__name__, "value": o.value}
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        # Bytes (kommt vor bei OEREB-XML-Cache)
        if isinstance(o, bytes):
            return None  # nicht cachen, zu gross
        return super().default(o)


def serialisiere_ergebnis(ergebnis) -> str:
    """Serialisiert ein AnalyseErgebnis als JSON-String.

    Strategie: rekursive dataclass-Konvertierung via asdict(), mit
    Custom-Encoder fuer Enums.

    Felder die NICHT serialisiert werden:
    - reglement: Baureglement (laden aus JSON, nicht Cache-relevant)
    - parzelle.restrictions[].karten_wms_url (URLs sind lang, nicht noetig)
    """
    # AnalyseErgebnis hat ein 'reglement'-Feld das auf eine Baureglement-
    # Instanz zeigt - das wollen wir NICHT serialisieren
    daten = dataclasses.asdict(ergebnis)

    # Entferne nicht-serialisierbare oder unerwuenschte Felder
    daten.pop("reglement", None)

    return json.dumps(daten, cls=CacheEncoder, ensure_ascii=False)


def _rekonstruiere_enum(klassen_name: str, wert: str):
    """Rekonstruiert ein Enum aus dem Cache-Format."""
    # Import lokal um zirkulare Imports zu vermeiden
    from analyse.potenzial import Datenqualitaet, PotenzialStatus
    from modelle import Lawstatus

    enum_map = {
        "Lawstatus": Lawstatus,
        "Datenqualitaet": Datenqualitaet,
        "PotenzialStatus": PotenzialStatus,
    }
    enum_klasse = enum_map.get(klassen_name)
    if enum_klasse:
        return enum_klasse(wert)
    return wert


def _wandle_enum_dicts_zurueck(obj: Any) -> Any:
    """Rekursiv: wandelt {'__enum__': '...', 'value': '...'} zurueck."""
    if isinstance(obj, dict):
        if "__enum__" in obj and "value" in obj:
            return _rekonstruiere_enum(obj["__enum__"], obj["value"])
        return {k: _wandle_enum_dicts_zurueck(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_wandle_enum_dicts_zurueck(item) for item in obj]
    return obj


def deserialisiere_ergebnis(json_str: str):
    """Deserialisiert ein AnalyseErgebnis aus JSON.

    Rekonstruiert:
    - Enums (Lawstatus, Datenqualitaet, PotenzialStatus)
    - AnalyseErgebnis-Wrapper
    - Verschachtelte Parzelle, Restriction-Liste, PotenzialErgebnis, GwrGebaeude-Liste

    Returns:
        AnalyseErgebnis-Objekt
    """
    # Imports lokal
    from analyse_adresse import AnalyseErgebnis
    from analyse.potenzial import PotenzialErgebnis
    from datenquellen.gwr import GwrGebaeude
    from modelle import Parzelle, Restriction

    daten = json.loads(json_str)
    daten = _wandle_enum_dicts_zurueck(daten)

    # Rekonstruktion von tiefen Strukturen
    # 1. Parzelle und ihre Restrictions
    parzelle_dict = daten.pop("parzelle", None)
    if parzelle_dict:
        restrictions_data = parzelle_dict.pop("restrictions", []) or []
        restrictions = []
        for r_dict in restrictions_data:
            try:
                restrictions.append(Restriction(**r_dict))
            except TypeError as e:
                logger.warning(f"Konnte Restriction nicht rekonstruieren: {e}")
        parzelle_dict["restrictions"] = restrictions

        # Tupel-Felder rekonstruieren (json macht aus tupeln listen)
        if isinstance(parzelle_dict.get("koordinaten_lv95"), list):
            parzelle_dict["koordinaten_lv95"] = tuple(parzelle_dict["koordinaten_lv95"])

        try:
            parzelle = Parzelle(**parzelle_dict)
        except TypeError as e:
            logger.warning(f"Konnte Parzelle nicht rekonstruieren: {e}")
            parzelle = None
    else:
        parzelle = None

    # 2. PotenzialErgebnis
    pot_dict = daten.pop("potenzial_ergebnis", None)
    if pot_dict:
        try:
            potenzial = PotenzialErgebnis(**pot_dict)
        except TypeError as e:
            logger.warning(f"Konnte PotenzialErgebnis nicht rekonstruieren: {e}")
            potenzial = None
    else:
        potenzial = None

    # 3. GwrGebaeude-Liste
    gwr_data = daten.pop("gwr_gebaeude", []) or []
    gwr_liste = []
    for g_dict in gwr_data:
        try:
            gwr_liste.append(GwrGebaeude(**g_dict))
        except TypeError as e:
            logger.warning(f"Konnte GwrGebaeude nicht rekonstruieren: {e}")

    # 4. Tupel-Felder am Top-Level
    if isinstance(daten.get("koordinate_lv95"), list):
        daten["koordinate_lv95"] = tuple(daten["koordinate_lv95"])
    if isinstance(daten.get("koordinate_wgs84"), list):
        daten["koordinate_wgs84"] = tuple(daten["koordinate_wgs84"])

    # AnalyseErgebnis konstruieren - aber unbekannte Felder filtern
    # (falls sich Schema aendert)
    valid_felder = {f.name for f in dataclasses.fields(AnalyseErgebnis)}
    daten_gefiltert = {k: v for k, v in daten.items() if k in valid_felder}

    ergebnis = AnalyseErgebnis(**daten_gefiltert)
    ergebnis.parzelle = parzelle
    ergebnis.potenzial_ergebnis = potenzial
    ergebnis.gwr_gebaeude = gwr_liste

    return ergebnis


# ---------------------------------------------------------------------------
# KantonsCache-Klasse
# ---------------------------------------------------------------------------

class KantonsCache:
    """SQLite-Cache pro Kanton fuer Iter-5-Massen-Analyse.

    Args:
        kanton: Kanton-Kuerzel klein, z.B. "be", "zh"
        cache_verzeichnis: Optional - alternativer Pfad (Default: ./cache/)
    """

    def __init__(
        self,
        kanton: str = DEFAULT_KANTON,
        cache_verzeichnis: Path | None = None,
    ):
        self.kanton = kanton.lower().strip()
        verzeichnis = cache_verzeichnis or CACHE_VERZEICHNIS
        verzeichnis.mkdir(parents=True, exist_ok=True)
        self.db_pfad = verzeichnis / f"cache_{self.kanton}.db"
        self.conn = sqlite3.connect(str(self.db_pfad))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        logger.info(f"KantonsCache initialisiert: {self.db_pfad}")

    def _init_schema(self) -> None:
        """Erstellt Tabelle wenn noch nicht vorhanden."""
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parzellen (
                egrid TEXT PRIMARY KEY,
                gemeinde TEXT NOT NULL,
                bfs_nummer INTEGER,
                schema_version INTEGER NOT NULL,
                abfrage_datum TEXT NOT NULL,

                -- Flache Felder fuer schnelle Queries
                parzellen_nummer TEXT,
                parzellen_flaeche_m2 REAL,
                datenqualitaet TEXT,
                zone TEXT,
                theoretisch_zulaessig_m2 REAL,
                gwr_summe_geschossflaeche_m2 REAL,
                reserve_m2 REAL,
                reserve_prozent REAL,
                ausschoepfungsgrad_prozent REAL,
                anzahl_gebaeude INTEGER,
                klassifikation TEXT,
                fehler TEXT,

                -- Vollstaendige Daten
                daten_json TEXT NOT NULL
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_gemeinde ON parzellen(gemeinde)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_klassifikation ON parzellen(klassifikation)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_reserve_m2 ON parzellen(reserve_m2)")
        self.conn.commit()

    def speichere(self, ergebnis, klassifikation: str | None = None) -> None:
        """Speichert ein AnalyseErgebnis im Cache.

        Args:
            ergebnis: AnalyseErgebnis-Instanz
            klassifikation: Optional - VERDICHTUNG/NEUGESCHAEFT/...
                            (wird spaeter von klassifiziere() berechnet)
        """
        if not ergebnis.egrid:
            logger.warning(f"speichere: Ergebnis ohne EGRID - skip")
            return

        # Reserve berechnen (falls moeglich)
        reserve_m2 = None
        if (ergebnis.theoretisch_zulaessig_m2 is not None
                and ergebnis.gwr_summe_geschossflaeche_m2 is not None):
            reserve_m2 = (
                ergebnis.theoretisch_zulaessig_m2
                - ergebnis.gwr_summe_geschossflaeche_m2
            )
        elif ergebnis.theoretisch_zulaessig_m2 is not None:
            # Leere Parzelle: reserve = zulaessig
            reserve_m2 = ergebnis.theoretisch_zulaessig_m2

        json_str = serialisiere_ergebnis(ergebnis)

        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO parzellen (
                egrid, gemeinde, bfs_nummer, schema_version, abfrage_datum,
                parzellen_nummer, parzellen_flaeche_m2,
                datenqualitaet, zone, theoretisch_zulaessig_m2,
                gwr_summe_geschossflaeche_m2, reserve_m2, reserve_prozent,
                ausschoepfungsgrad_prozent, anzahl_gebaeude,
                klassifikation, fehler, daten_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ergebnis.egrid,
            ergebnis.gemeinde or "",
            None,  # bfs_nummer setzen wir spaeter aus ParzellenRef
            SCHEMA_VERSION,
            datetime.datetime.now().isoformat(),
            ergebnis.parzellen_nummer,
            ergebnis.parzellen_flaeche_m2,
            ergebnis.datenqualitaet,
            ergebnis.zone,
            ergebnis.theoretisch_zulaessig_m2,
            ergebnis.gwr_summe_geschossflaeche_m2,
            reserve_m2,
            ergebnis.reserve_prozent,
            ergebnis.ausschoepfungsgrad_prozent,
            len(ergebnis.gwr_gebaeude or []),
            klassifikation,
            ergebnis.fehler,
            json_str,
        ))
        self.conn.commit()

    def lade(self, egrid: str):
        """Laedt ein AnalyseErgebnis aus dem Cache.

        Returns:
            AnalyseErgebnis oder None wenn nicht im Cache.
        """
        cur = self.conn.cursor()
        cur.execute(
            "SELECT daten_json FROM parzellen WHERE egrid = ? AND schema_version = ?",
            (egrid, SCHEMA_VERSION),
        )
        row = cur.fetchone()
        if not row:
            return None
        try:
            return deserialisiere_ergebnis(row["daten_json"])
        except Exception as e:
            logger.warning(f"Deserialisierung fuer {egrid} fehlgeschlagen: {e}")
            return None

    def hat_eintrag(self, egrid: str) -> bool:
        """Schneller Existenz-Check ohne Deserialisierung."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM parzellen WHERE egrid = ? AND schema_version = ?",
            (egrid, SCHEMA_VERSION),
        )
        return cur.fetchone() is not None

    def ist_aktuell(self, egrid: str, max_alter_tage: int = DEFAULT_MAX_ALTER_TAGE) -> bool:
        """Prueft ob Cache-Eintrag juenger als max_alter_tage ist."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT abfrage_datum FROM parzellen WHERE egrid = ?",
            (egrid,),
        )
        row = cur.fetchone()
        if not row:
            return False
        try:
            datum = datetime.datetime.fromisoformat(row["abfrage_datum"])
            alter = datetime.datetime.now() - datum
            return alter.days < max_alter_tage
        except (ValueError, TypeError):
            return False

    def statistik(self, gemeinde: str | None = None) -> dict:
        """Liefert Statistik ueber den Cache.

        Args:
            gemeinde: Optional - Filter auf bestimmte Gemeinde

        Returns:
            dict mit total, pro_klassifikation, pro_datenqualitaet
        """
        cur = self.conn.cursor()
        where = ""
        params: tuple = ()
        if gemeinde:
            where = "WHERE gemeinde = ?"
            params = (gemeinde,)

        cur.execute(f"SELECT COUNT(*) as n FROM parzellen {where}", params)
        total = cur.fetchone()["n"]

        cur.execute(
            f"SELECT klassifikation, COUNT(*) as n FROM parzellen {where} "
            f"GROUP BY klassifikation",
            params,
        )
        pro_klassifikation = {row["klassifikation"]: row["n"] for row in cur.fetchall()}

        cur.execute(
            f"SELECT datenqualitaet, COUNT(*) as n FROM parzellen {where} "
            f"GROUP BY datenqualitaet",
            params,
        )
        pro_datenqualitaet = {row["datenqualitaet"]: row["n"] for row in cur.fetchall()}

        return {
            "total": total,
            "gemeinde": gemeinde,
            "pro_klassifikation": pro_klassifikation,
            "pro_datenqualitaet": pro_datenqualitaet,
        }

    def loesche_gemeinde(self, gemeinde: str) -> int:
        """Loescht alle Eintraege einer Gemeinde. Returns Anzahl geloeschter Eintraege."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM parzellen WHERE gemeinde = ?", (gemeinde,))
        anzahl = cur.rowcount
        self.conn.commit()
        return anzahl

    def alle_egrids_einer_gemeinde(self, gemeinde: str) -> list[str]:
        """Liefert alle EGRIDs einer Gemeinde aus dem Cache."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT egrid FROM parzellen WHERE gemeinde = ? ORDER BY parzellen_nummer",
            (gemeinde,),
        )
        return [row["egrid"] for row in cur.fetchall()]

    def close(self) -> None:
        """Schliesst die DB-Verbindung."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ---------------------------------------------------------------------------
# Smoke-Test (Modul-direkter Aufruf)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    print("Smoke-Test fuer KantonsCache:")
    print()

    # Test-Cache anlegen (oder oeffnen)
    cache = KantonsCache(kanton="be_test", cache_verzeichnis=Path("cache"))
    print(f"Cache-Datei: {cache.db_pfad}")
    print(f"Schema-Version: {SCHEMA_VERSION}")
    print()

    # Statistik leer
    stats = cache.statistik()
    print(f"Statistik (leer): {stats}")
    print()

    # Live-Test: Oberhofen Parzelle 1 analysieren und cachen
    print("Live-Test mit Oberhofen Parzelle 1...")
    from analyse_adresse import analysiere_per_egrid
    ergebnis = analysiere_per_egrid(
        "CH550146963519",
        koordinate_lv95=(2618457, 1174925),
        adresse_label="Oberhofen Parzelle 1",
    )
    print(f"  Live-Analyse: {ergebnis.gemeinde}, {ergebnis.datenqualitaet}")
    print(f"  Restrictions: {len(ergebnis.parzelle.restrictions) if ergebnis.parzelle else 0}")
    print()

    print("Speichere im Cache...")
    cache.speichere(ergebnis, klassifikation="TEST")
    print(f"  Eintrag vorhanden: {cache.hat_eintrag('CH550146963519')}")
    print(f"  Aktuell: {cache.ist_aktuell('CH550146963519')}")
    print()

    print("Lade aus Cache...")
    aus_cache = cache.lade("CH550146963519")
    if aus_cache:
        print(f"  Geladenes Ergebnis: {aus_cache.gemeinde}, {aus_cache.datenqualitaet}")
        print(f"  Restrictions: {len(aus_cache.parzelle.restrictions) if aus_cache.parzelle else 0}")
        print(f"  Zone: {aus_cache.zone}")
        print(f"  Theoretisch zulaessig: {aus_cache.theoretisch_zulaessig_m2}")
    else:
        print(f"  FEHLER: nichts geladen!")
    print()

    # Statistik nach Speichern
    stats = cache.statistik()
    print(f"Statistik nach Speichern: {stats}")
    print()

    print("===== SMOKE-TEST OK =====")
    cache.close()
