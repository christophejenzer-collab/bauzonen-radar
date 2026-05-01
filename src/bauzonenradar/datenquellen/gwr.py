"""
Datenquelle: GWR (Eidgenoessisches Gebaeude- und Wohnungsregister).

Holt parzellenscharfe Ist-Werte fuer bestehende Gebaeude:
  - Grundflaeche (garea)
  - Anzahl Vollgeschosse (gastw)
  - Anzahl Wohnungen (ganzwhg)
  - Baujahr / Bauperiode
  - Heizungs-System und Sanierungsdatum

Damit kann das Tool die echte Geschossflaeche eines Gebaeudes
berechnen statt mit dem 25%-Platzhalter zu arbeiten:

    Ist-Geschossflaeche = garea x gastw

Verwendung:
-----------
Einzelabfrage einer Adresse:

    quelle = GwrQuelle()
    gebaeude_liste = quelle.gebaeude_zu_adresse("Frutigenstrasse 25, 3604 Thun")
    for g in gebaeude_liste:
        print(g.label, g.geschossflaeche_m2)

Aggregation pro Parzelle (mehrere Gebaeude moeglich):

    summe = quelle.geschossflaeche_pro_parzelle("CH394601433582")
    print(f"Total Ist-Geschossflaeche: {summe} m^2")

Architektur:
------------
Zwei-Stufen-Workflow ueber api3.geo.admin.ch:

  Stufe 1: SearchAPI mit type=address liefert featureId(s)
           -> /SearchServer?type=locations&origins=address&searchText=...

  Stufe 2: MapServer mit featureId liefert Gebaeudedaten
           -> /MapServer/ch.bfs.gebaeude_wohnungs_register/{featureId}

Beide Stufen sind cache-faehig, beide werden bei Fehler retry-t.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

SEARCH_API = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
MAP_SERVER = (
    "https://api3.geo.admin.ch/rest/services/ech/MapServer/"
    "ch.bfs.gebaeude_wohnungs_register"
)

DEFAULT_TIMEOUT_SEK = 10.0
DEFAULT_RETRIES = 2
DEFAULT_RETRY_DELAY_SEK = 1.5
DEFAULT_THROTTLE_SEK = 0.0  # zwischen Anfragen, fuer Massen-Abfragen sinnvoll

# Maximale Cache-Groesse (verhindert unbegrenzten Speicherverbrauch
# bei langen Sessions / Massen-Analyse)
MAX_CACHE_SIZE = 5000


# ---------------------------------------------------------------------------
# Datenklasse: ein einzelnes Gebaeude aus dem GWR
# ---------------------------------------------------------------------------

@dataclass
class GwrGebaeude:
    """
    Ein einzelnes Gebaeude aus dem GWR.

    Felder spiegeln direkt die echte API-Response von api3.geo.admin.ch
    fuer den Layer ch.bfs.gebaeude_wohnungs_register.

    Beispiel (Frutigenstrasse 25, 3604 Thun):
        egid:           "1435137"
        egrid:          "CH394601433582"
        parzellennummer: "324"
        gemeinde:       "Thun"
        bfs_gemeinde:   942
        grundflaeche_m2: 304
        geschosse:      5
        anzahl_wohnungen: 7
        baujahr:        None
        bauperiode_code: 8016
    """
    egid: str                            # eindeutige Gebaeude-ID
    egrid: str                           # zugehoerige Parzelle (zur Aggregation)
    parzellennummer: str | None          # lparz
    gemeinde: str | None                 # ggdename
    bfs_gemeinde: int | None             # ggdenr
    adresse: str | None                  # strname_deinr
    grundflaeche_m2: int | None          # garea
    geschosse: int | None                # gastw
    anzahl_wohnungen: int | None         # ganzwhg
    baujahr: int | None                  # gbauj
    bauperiode_code: int | None          # gbaup (Fallback wenn baujahr fehlt)
    heizung_saniert_datum: str | None    # gwaerdath1 (Datum-String)
    denkmalschutz: bool                  # gschutzr is not None
    koordinate_lv95: tuple[float, float] | None  # (gkode, gkodn)

    @property
    def geschossflaeche_m2(self) -> int | None:
        """Ist-Geschossflaeche = Grundflaeche x Geschosse.

        Returns None wenn Grundflaeche oder Geschosse fehlen.
        """
        if self.grundflaeche_m2 is None or self.geschosse is None:
            return None
        return self.grundflaeche_m2 * self.geschosse

    @property
    def label(self) -> str:
        """Kurzbeschreibung fuer die Anzeige."""
        teile = []
        if self.adresse:
            teile.append(self.adresse)
        teile.append(f"EGID {self.egid}")
        return " - ".join(teile)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GwrFehler(Exception):
    """Basisklasse fuer GWR-spezifische Fehler."""


class GwrApiFehler(GwrFehler):
    """Fehler bei der API-Kommunikation (Netzwerk, Timeout, HTTP-Status)."""


class GwrParseFehler(GwrFehler):
    """Fehler beim Parsen der API-Antwort (unerwartetes Format)."""


# ---------------------------------------------------------------------------
# Hauptklasse: GwrQuelle
# ---------------------------------------------------------------------------

class GwrQuelle:
    """
    Zugriff auf das GWR ueber api3.geo.admin.ch.

    Verwendet einen In-Memory-Cache (Dict), um wiederholte Abfragen der
    gleichen Adresse oder featureId zu vermeiden. Der Cache lebt nur
    innerhalb einer Instanz - persistierendes Caching (z.B. SQLite)
    waere eine spaetere Erweiterung fuer die Massen-Analyse.

    Der Cache hat eine harte Obergrenze (MAX_CACHE_SIZE), bei deren
    Ueberschreitung er beim naechsten put() geleert wird. Das
    funktioniert fuer eine Session mit ein paar tausend Adressen
    problemlos.
    """

    def __init__(
        self,
        timeout_sek: float = DEFAULT_TIMEOUT_SEK,
        retries: int = DEFAULT_RETRIES,
        retry_delay_sek: float = DEFAULT_RETRY_DELAY_SEK,
        throttle_sek: float = DEFAULT_THROTTLE_SEK,
    ) -> None:
        """
        Args:
            timeout_sek:     Timeout pro HTTP-Request.
            retries:         Anzahl Wiederholungen bei transienten Fehlern.
            retry_delay_sek: Wartezeit zwischen Wiederholungen.
            throttle_sek:    Pause vor jedem Request (fuer Massenabfragen).
        """
        self.timeout = timeout_sek
        self.retries = retries
        self.retry_delay = retry_delay_sek
        self.throttle = throttle_sek

        self._cache_adresse: dict[str, list[GwrGebaeude]] = {}
        self._cache_feature: dict[str, GwrGebaeude] = {}

    # ----- Oeffentliche API ---------------------------------------------

    def gebaeude_zu_adresse(self, adresse: str) -> list[GwrGebaeude]:
        """
        Holt alle Gebaeude die zu einer Adresse gehoeren.

        Wichtig: Eine Adresse kann mehrere Gebaeude haben, oder die
        Hausnummer kann Treffer fuer 25 + 25a liefern. Die Aggregation
        pro Parzelle erfolgt ueber die Methode geschossflaeche_pro_parzelle().

        Args:
            adresse: Strasse + Nummer + Ort, z.B. "Frutigenstrasse 25, 3604 Thun"

        Returns:
            Liste von GwrGebaeude. Leer wenn keine Treffer.

        Raises:
            GwrApiFehler:   bei wiederholten API-Problemen
            GwrParseFehler: bei unerwartetem Antwort-Format
        """
        adresse_norm = adresse.strip()
        if adresse_norm in self._cache_adresse:
            return self._cache_adresse[adresse_norm]

        feature_ids = self._suche_feature_ids(adresse_norm)
        gebaeude: list[GwrGebaeude] = []
        for fid in feature_ids:
            try:
                g = self._hole_gebaeude(fid)
                if g is not None:
                    gebaeude.append(g)
            except GwrFehler:
                # Einzelner Treffer schlaegt fehl - wir machen weiter
                # mit den anderen statt die ganze Adresse abzubrechen.
                continue

        self._cache_put(self._cache_adresse, adresse_norm, gebaeude)
        return gebaeude

    def gebaeude_pro_parzelle(self, egrid: str) -> list[GwrGebaeude]:
        """
        Filtert aus dem Cache alle Gebaeude die zu einem bestimmten
        EGRID gehoeren.

        Vorbedingung: gebaeude_zu_adresse() wurde fuer mindestens eine
        Adresse der Parzelle aufgerufen. Sonst leer.

        Fuer Iteration 5 wird das anders implementiert (z.B. via
        Geometrie-Suche ueber Bbox), heute reicht der Cache-Filter.
        """
        ergebnis: list[GwrGebaeude] = []
        for liste in self._cache_adresse.values():
            for g in liste:
                if g.egrid == egrid:
                    ergebnis.append(g)
        # Duplikate entfernen (gleicher EGID kann mehrfach vorkommen)
        gesehen: set[str] = set()
        eindeutig: list[GwrGebaeude] = []
        for g in ergebnis:
            if g.egid not in gesehen:
                gesehen.add(g.egid)
                eindeutig.append(g)
        return eindeutig

    def geschossflaeche_pro_parzelle(self, egrid: str) -> int | None:
        """
        Aggregiert die Ist-Geschossflaeche aller Gebaeude einer Parzelle.

        Returns:
            Summe von garea x gastw ueber alle Gebaeude des EGRID,
            oder None wenn keine Gebaeude oder keine vollstaendigen
            Daten vorhanden sind.
        """
        gebaeude = self.gebaeude_pro_parzelle(egrid)
        if not gebaeude:
            return None
        summe = 0
        hat_daten = False
        for g in gebaeude:
            gf = g.geschossflaeche_m2
            if gf is not None:
                summe += gf
                hat_daten = True
        return summe if hat_daten else None

    def cache_leeren(self) -> None:
        """Leert beide internen Caches. Nuetzlich fuer Tests."""
        self._cache_adresse.clear()
        self._cache_feature.clear()

    # ----- Stufe 1: SearchAPI -> featureIds -----------------------------

    def _suche_feature_ids(self, adresse: str) -> list[str]:
        """Holt featureId(s) zur Adresse via SearchAPI."""
        params = {
            "searchText": adresse,
            "type": "locations",
            "origins": "address",
            "limit": "10",
            "sr": "2056",
        }
        url = f"{SEARCH_API}?{urllib.parse.urlencode(params)}"
        daten = self._http_get_json(url)

        results = daten.get("results")
        if not isinstance(results, list):
            raise GwrParseFehler(
                f"Unerwartete SearchAPI-Antwort fuer '{adresse}': "
                f"'results' fehlt oder ist keine Liste."
            )

        feature_ids: list[str] = []
        for treffer in results:
            attrs = treffer.get("attrs") if isinstance(treffer, dict) else None
            if not isinstance(attrs, dict):
                continue
            fid = attrs.get("featureId")
            if isinstance(fid, str) and fid:
                feature_ids.append(fid)
        return feature_ids

    # ----- Stufe 2: MapServer -> Gebaeudedaten --------------------------

    def _hole_gebaeude(self, feature_id: str) -> GwrGebaeude | None:
        """Holt Gebaeudedaten fuer eine featureId via MapServer."""
        if feature_id in self._cache_feature:
            return self._cache_feature[feature_id]

        url = f"{MAP_SERVER}/{feature_id}"
        daten = self._http_get_json(url)

        feature = daten.get("feature")
        if not isinstance(feature, dict):
            return None
        attrs = feature.get("attributes")
        if not isinstance(attrs, dict):
            return None

        gebaeude = self._parse_attrs(attrs)
        self._cache_put(self._cache_feature, feature_id, gebaeude)
        return gebaeude

    @staticmethod
    def _parse_attrs(attrs: dict[str, Any]) -> GwrGebaeude:
        """Wandelt das attributes-Dict in eine GwrGebaeude-Instanz."""
        def _str(key: str) -> str | None:
            wert = attrs.get(key)
            if wert is None or wert == "":
                return None
            return str(wert)

        def _int(key: str) -> int | None:
            wert = attrs.get(key)
            if wert is None:
                return None
            try:
                return int(wert)
            except (ValueError, TypeError):
                return None

        koordinate: tuple[float, float] | None = None
        gkode = attrs.get("gkode")
        gkodn = attrs.get("gkodn")
        if gkode is not None and gkodn is not None:
            try:
                koordinate = (float(gkode), float(gkodn))
            except (ValueError, TypeError):
                koordinate = None

        return GwrGebaeude(
            egid=_str("egid") or "",
            egrid=_str("egrid") or "",
            parzellennummer=_str("lparz"),
            gemeinde=_str("ggdename"),
            bfs_gemeinde=_int("ggdenr"),
            adresse=_str("strname_deinr"),
            grundflaeche_m2=_int("garea"),
            geschosse=_int("gastw"),
            anzahl_wohnungen=_int("ganzwhg"),
            baujahr=_int("gbauj"),
            bauperiode_code=_int("gbaup"),
            heizung_saniert_datum=_str("gwaerdath1"),
            denkmalschutz=attrs.get("gschutzr") is not None,
            koordinate_lv95=koordinate,
        )

    # ----- HTTP-Hilfsmethode mit Retry und Throttle ---------------------

    def _http_get_json(self, url: str) -> dict[str, Any]:
        """
        Fuehrt einen GET aus und liefert geparste JSON-Antwort zurueck.

        Implementiert:
        - Throttling vor dem Request (falls konfiguriert)
        - Retry-Logic mit exponentialem Backoff bei transienten Fehlern
        - Saubere Exception-Klassen
        """
        if self.throttle > 0:
            time.sleep(self.throttle)

        letzter_fehler: Exception | None = None
        delay = self.retry_delay

        for versuch in range(self.retries + 1):
            try:
                with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                try:
                    return json.loads(body)
                except json.JSONDecodeError as fehler:
                    raise GwrParseFehler(
                        f"Ungueltige JSON-Antwort von {url}"
                    ) from fehler
            except urllib.error.HTTPError as fehler:
                # 4xx: Client-Fehler, kein Retry
                if 400 <= fehler.code < 500:
                    raise GwrApiFehler(
                        f"HTTP {fehler.code} fuer {url}: {fehler.reason}"
                    ) from fehler
                letzter_fehler = fehler
            except (urllib.error.URLError, TimeoutError, OSError) as fehler:
                letzter_fehler = fehler

            if versuch < self.retries:
                time.sleep(delay)
                delay *= 2

        # Alle Versuche fehlgeschlagen
        raise GwrApiFehler(
            f"GWR-API nicht erreichbar nach {self.retries + 1} Versuchen: {url}"
        ) from letzter_fehler

    # ----- Cache-Verwaltung ---------------------------------------------

    @staticmethod
    def _cache_put(cache: dict, schluessel: str, wert: Any) -> None:
        """Legt einen Eintrag in den Cache, leert ihn bei Ueberlaufen."""
        if len(cache) >= MAX_CACHE_SIZE:
            cache.clear()
        cache[schluessel] = wert
