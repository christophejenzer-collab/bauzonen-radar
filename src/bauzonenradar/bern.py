"""
Datenquelle fuer den Kanton Bern.

Kapselt den Zugriff auf den OEREB-Webservice des Kantons Bern
(https://www.oereb2.apps.be.ch/) und die swisstopo Such-API.

Hauptfunktion: adresse_zu_parzelle(adresse) -> Parzelle
"""

import requests
from xml.etree import ElementTree as ET

from modelle import Parzelle, Restriction, Lawstatus


# XML-Namespaces gemaess OEREB-Schema V2.0
NS = {
    "extract": "http://schemas.geo.admin.ch/V_D/OeREB/2.0/Extract",
    "data":    "http://schemas.geo.admin.ch/V_D/OeREB/2.0/ExtractData",
    "geometry": "http://www.interlis.ch/geometry/1.0",
}


class BernOerebQuelle:
    """Datenquelle fuer Grundstuecks- und OEREB-Informationen im Kanton Bern."""

    BASE_URL = "https://www.oereb2.apps.be.ch"
    GEOCODE_URL = "https://api3.geo.admin.ch/rest/services/api/SearchServer"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    # ----- Oeffentliche Hauptmethode -------------------------------------

    def adresse_zu_parzelle(self, adresse: str) -> Parzelle | None:
        """
        Komplette Pipeline: Adresse -> Parzelle mit OEREB-Daten.

        Returns: Parzelle-Objekt oder None bei Fehler.
        """
        koord = self._geocode(adresse)
        if not koord:
            return None

        egrid = self._getegrid(*koord)
        if not egrid:
            return None

        xml_bytes = self._get_extract(egrid)
        if not xml_bytes:
            return None

        parzelle = self._parse_extract(xml_bytes)
        if parzelle:
            parzelle.adresse = adresse
            parzelle.koordinaten_lv95 = koord
        return parzelle

    # ----- Interne Schritte ----------------------------------------------

    def _geocode(self, adresse: str) -> tuple[float, float] | None:
        """Adresse -> (east, north) in LV95 via swisstopo."""
        params = {
            "searchText": adresse,
            "type": "locations",
            "sr": 2056,
            "limit": 1,
        }
        try:
            r = requests.get(self.GEOCODE_URL, params=params, timeout=self.timeout)
            r.raise_for_status()
            results = r.json().get("results", [])
            if not results:
                return None
            attrs = results[0]["attrs"]
            return (attrs["y"], attrs["x"])  # y=East, x=North in swisstopo-API
        except (requests.RequestException, KeyError, ValueError):
            return None

    def _getegrid(self, east: float, north: float) -> str | None:
        """LV95-Koordinaten -> EGRID via OEREB-Service Bern."""
        url = f"{self.BASE_URL}/getegrid/xml/"
        params = {"EN": f"{east},{north}"}
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            if r.status_code != 200:
                return None
            root = ET.fromstring(r.content)
            for elem in root.iter():
                tag = elem.tag.split("}")[-1]
                if tag.lower() == "egrid" and elem.text:
                    return elem.text.strip()
            return None
        except (requests.RequestException, ET.ParseError):
            return None

    def _get_extract(self, egrid: str) -> bytes | None:
        """EGRID -> vollstaendiges OEREB-XML."""
        url = f"{self.BASE_URL}/extract/xml/"
        params = {"EGRID": egrid}
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            if r.status_code != 200:
                return None
            return r.content
        except requests.RequestException:
            return None

    def _parse_extract(self, xml_bytes: bytes) -> Parzelle | None:
        """Parst OEREB-XML zu einer Parzelle mit Restrictions."""
        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError:
            return None

        # RealEstate-Block finden (Grundstuecks-Basisdaten)
        realestate = self._find_first_child(root, "RealEstate")
        if realestate is None:
            return None

        parzelle = Parzelle(
            egrid=self._get_text(realestate, "EGRID") or "",
            nummer=self._get_text(realestate, "Number") or "",
            identdn=self._get_text(realestate, "IdentDN") or "",
            gemeinde=self._get_text(realestate, "MunicipalityName") or "",
            kanton=self._get_text(realestate, "Canton") or "",
            flaeche_m2=float(self._get_text(realestate, "LandRegistryArea") or 0),
        )

        # Alle RestrictionOnLandownership-Eintraege durchsuchen
        for elem in root.iter():
            if elem.tag.split("}")[-1] == "RestrictionOnLandownership":
                r = self._parse_restriction(elem)
                if r:
                    parzelle.restrictions.append(r)

        return parzelle

    def _parse_restriction(self, elem: ET.Element) -> Restriction | None:
        """Parst einen RestrictionOnLandownership-Knoten."""
        legende = self._get_localised_text(elem, "LegendText")

        # Theme-Block
        theme_elem = self._find_first_child(elem, "Theme")
        thema_code = ""
        thema_text = ""
        sub_code = None
        if theme_elem is not None:
            thema_code = self._get_text(theme_elem, "Code") or ""
            sub_code = self._get_text(theme_elem, "SubCode")
            thema_text = self._get_localised_text(theme_elem, "Text") or ""

        type_code = self._get_text(elem, "TypeCode")

        # Lawstatus: wir nehmen den der ganzen Restriction, nicht der Geometry
        lawstatus = Lawstatus.IN_FORCE
        law_elem = self._find_first_child(elem, "Lawstatus")
        if law_elem is not None:
            code = self._get_text(law_elem, "Code")
            if code:
                lawstatus = Lawstatus.from_string(code)

        # Flaeche und Prozent
        flaeche = self._get_text_as_float(elem, "AreaShare")
        prozent = self._get_text_as_float(elem, "PartInPercent")

        # Symbol-URL und WMS-URL
        symbol_url = self._get_text(elem, "SymbolRef")
        map_elem = self._find_first_child(elem, "Map")
        wms_url = None
        if map_elem is not None:
            wms_url = self._get_localised_text(map_elem, "ReferenceWMS")

        return Restriction(
            thema_code=thema_code,
            thema_text=thema_text,
            sub_code=sub_code,
            legende=legende or "(ohne Bezeichnung)",
            type_code=type_code,
            lawstatus=lawstatus,
            flaeche_m2=flaeche,
            prozent_anteil=prozent,
            symbol_url=symbol_url,
            karten_wms_url=wms_url,
        )

    # ----- XML-Helfer ----------------------------------------------------

    @staticmethod
    def _find_first_child(parent: ET.Element, tag_name: str) -> ET.Element | None:
        """Findet das erste Kind mit dem gegebenen lokalen Tag-Namen."""
        for child in parent.iter():
            if child.tag.split("}")[-1] == tag_name:
                return child
        return None

    @staticmethod
    def _get_text(parent: ET.Element, tag_name: str) -> str | None:
        """Sucht direkt unter parent nach einem Element mit diesem Namen."""
        for child in parent.iter():
            if child.tag.split("}")[-1] == tag_name and child.text:
                return child.text.strip()
        return None

    def _get_text_as_float(self, parent: ET.Element, tag_name: str) -> float | None:
        text = self._get_text(parent, tag_name)
        if text is None:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _get_localised_text(self, parent: ET.Element, tag_name: str,
                            lang: str = "de") -> str | None:
        """
        Findet einen lokalisierten Text unter parent.

        Struktur:
            <tag_name>
              <LocalisedText>
                <Language>de</Language>
                <Text>...</Text>
              </LocalisedText>
            </tag_name>
        """
        container = self._find_first_child(parent, tag_name)
        if container is None:
            return None

        # Suche nach LocalisedText mit passender Sprache
        current_lang = None
        for child in container.iter():
            t = child.tag.split("}")[-1]
            if t == "Language" and child.text:
                current_lang = child.text.strip()
            elif t == "Text" and child.text and current_lang == lang:
                return child.text.strip()

        # Fallback: erstes Text-Element, egal welche Sprache
        for child in container.iter():
            if child.tag.split("}")[-1] == "Text" and child.text:
                return child.text.strip()
        return None


# --------------------------------------------------------------------------
# Direkter Aufruf zum Testen
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    adresse = sys.argv[1] if len(sys.argv) > 1 else "Kramgasse 49, 3011 Bern"

    print(f"Suche Parzelle fuer: {adresse}")
    print("=" * 70)

    quelle = BernOerebQuelle()
    parzelle = quelle.adresse_zu_parzelle(adresse)

    if parzelle:
        print(parzelle.kurzbericht())
    else:
        print("Keine Parzelle gefunden.")
