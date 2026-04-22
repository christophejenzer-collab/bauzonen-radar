"""
Proof-of-Concept v3 fuer Bauzonen-Radar.

Nutzt den offiziellen OEREB-Webservice des Kantons Bern.
Basis-URL: https://www.oereb2.apps.be.ch/

Stufen:
  1. swisstopo Geocoding (Adresse -> LV95-Koordinaten)
  2. OEREB GetEGRID (Koordinaten -> EGRID)
  3. OEREB Extract (EGRID -> vollstaendiger OEREB-Auszug als XML)
  4. Zonen-Informationen aus dem XML extrahieren

Aufruf:
    python proof_of_concept.py
"""

import requests
import sys
from xml.etree import ElementTree as ET


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

OEREB_BASE = "https://www.oereb2.apps.be.ch"


# ---------------------------------------------------------------------------
# Stufe 1: Geocoding
# ---------------------------------------------------------------------------

def stufe_1_geocoding(adresse: str) -> dict | None:
    """Adresse -> LV95-Koordinaten via swisstopo SearchServer."""
    print(f"\n[Stufe 1] Geocoding: {adresse}")

    url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
    params = {
        "searchText": adresse,
        "type": "locations",
        "sr": 2056,
        "limit": 1,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not data.get("results"):
            print("  -> Keine Treffer.")
            return None

        attrs = data["results"][0]["attrs"]
        result = {
            "east": attrs["y"],
            "north": attrs["x"],
            "label": attrs.get("label", "").replace("<b>", "").replace("</b>", ""),
        }
        print(f"  -> {result['label']}")
        print(f"  -> LV95: E={result['east']:.1f}, N={result['north']:.1f}")
        return result

    except Exception as e:
        print(f"  -> FEHLER: {e}")
        return None


# ---------------------------------------------------------------------------
# Stufe 2: GetEGRID (XML, weil Bern primaer XML liefert)
# ---------------------------------------------------------------------------

def stufe_2_getegrid(east: float, north: float) -> str | None:
    """Koordinaten -> EGRID via OEREB-Webservice des Kantons Bern."""
    print(f"\n[Stufe 2] GetEGRID an E={east:.1f}, N={north:.1f}")

    url = f"{OEREB_BASE}/getegrid/xml/"
    params = {"EN": f"{east},{north}"}

    try:
        r = requests.get(url, params=params, timeout=15)
        print(f"  -> Status: {r.status_code}")

        if r.status_code != 200:
            print(f"  -> Antwort: {r.text[:200]}")
            return None

        # XML parsen - der Namespace ist Teil der OEREB-Spezifikation
        root = ET.fromstring(r.content)

        # Alle Elemente durchsuchen, die "egrid" im Tag-Namen haben
        # (Namespace-agnostisch)
        egrids = []
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]  # Namespace entfernen
            if tag.lower() == "egrid" and elem.text:
                egrids.append(elem.text.strip())

        if not egrids:
            print("  -> Keine EGRID im XML gefunden.")
            print(f"  -> Erste 500 Zeichen der Antwort:\n{r.text[:500]}")
            return None

        print(f"  -> EGRID: {egrids[0]}")
        if len(egrids) > 1:
            print(f"  -> Weitere gefundene EGRIDs: {egrids[1:]}")
        return egrids[0]

    except ET.ParseError as e:
        print(f"  -> XML-Parse-Fehler: {e}")
        print(f"  -> Rohe Antwort:\n{r.text[:500]}")
        return None
    except Exception as e:
        print(f"  -> FEHLER: {e}")
        return None


# ---------------------------------------------------------------------------
# Stufe 3: Extract
# ---------------------------------------------------------------------------

def stufe_3_extract(egrid: str) -> bytes | None:
    """EGRID -> vollstaendiger OEREB-Auszug als XML."""
    print(f"\n[Stufe 3] Extract fuer EGRID {egrid}")

    url = f"{OEREB_BASE}/extract/xml/"
    params = {"EGRID": egrid}

    try:
        r = requests.get(url, params=params, timeout=30)
        print(f"  -> Status: {r.status_code}")
        print(f"  -> Groesse der Antwort: {len(r.content)} Bytes")

        if r.status_code != 200:
            print(f"  -> Antwort: {r.text[:300]}")
            return None

        return r.content

    except Exception as e:
        print(f"  -> FEHLER: {e}")
        return None


# ---------------------------------------------------------------------------
# Stufe 4: Zonen-Informationen extrahieren
# ---------------------------------------------------------------------------

def stufe_4_zonen_auswerten(xml_content: bytes) -> None:
    """
    Sucht im OEREB-Extract nach der Nutzungsplanung (Bauzone)
    und gibt die gefundenen Informationen aus.
    """
    print(f"\n[Stufe 4] Zonen aus dem Extract auslesen")

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"  -> XML-Parse-Fehler: {e}")
        return

    # Grundstuecks-Grunddaten
    for tag_name in ["MunicipalityName", "CantonCode", "LandRegistryArea",
                     "Number", "IdentDN"]:
        for elem in root.iter():
            if elem.tag.split("}")[-1] == tag_name and elem.text:
                print(f"  -> {tag_name}: {elem.text.strip()}")
                break

    # RestrictionOnLandownership = die einzelnen OEREB-Themen
    themen_gefunden = []
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        if tag == "RestrictionOnLandownership":
            # Thema-Code und ggf. Zonen-Bezeichnung sammeln
            theme_code = None
            legend_text = None
            type_code = None

            for child in elem.iter():
                ctag = child.tag.split("}")[-1]
                if ctag == "Theme":
                    # Sub-Element "Code"
                    for sub in child.iter():
                        if sub.tag.split("}")[-1] == "Code" and sub.text:
                            theme_code = sub.text.strip()
                            break
                elif ctag == "LegendText" and child.text and not legend_text:
                    legend_text = child.text.strip()
                elif ctag == "TypeCode" and child.text and not type_code:
                    type_code = child.text.strip()
                elif ctag == "Information" and child.text and not legend_text:
                    legend_text = child.text.strip()

            if theme_code:
                themen_gefunden.append({
                    "theme": theme_code,
                    "legend": legend_text,
                    "type": type_code,
                })

    if not themen_gefunden:
        print("  -> Keine Restrictions im XML gefunden.")
        return

    print(f"\n  -> {len(themen_gefunden)} OEREB-Eintraege auf dieser Parzelle:")

    # Eindeutige Themen anzeigen
    themen_uniq = {}
    for t in themen_gefunden:
        key = t["theme"]
        if key not in themen_uniq:
            themen_uniq[key] = []
        if t["legend"]:
            themen_uniq[key].append(t["legend"])

    for theme, legenden in sorted(themen_uniq.items()):
        print(f"\n     Thema: {theme}")
        unique_legs = list(dict.fromkeys(legenden))  # unique, erhalte Reihenfolge
        for leg in unique_legs[:5]:  # max 5 pro Thema
            print(f"       - {leg}")

    # Besonders die Nutzungsplanung hervorheben
    nutzungsplanung = [t for t in themen_gefunden
                       if "landuseplans" in t["theme"].lower()
                       or "nutzungsplanung" in t["theme"].lower()]
    if nutzungsplanung:
        print(f"\n  >> BAUZONE/NUTZUNGSPLANUNG gefunden:")
        for t in nutzungsplanung[:3]:
            print(f"     {t['legend']} (Type: {t['type']})")


# ---------------------------------------------------------------------------
# Hauptablauf
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Bauzonen-Radar - Proof of Concept v3 (OEREB Kanton Bern)")
    print("=" * 70)
    print(f"OEREB-Service: {OEREB_BASE}")

    # Testadressen im Kanton Bern
    test_adressen = [
        "Kramgasse 49, 3011 Bern",
        "Laupenstrasse 7, 3008 Bern",
        "Thunstrasse 100, 3006 Bern",
    ]

    erfolg = False

    for adresse in test_adressen:
        print("\n" + "#" * 70)
        print(f"# TEST: {adresse}")
        print("#" * 70)

        geocode = stufe_1_geocoding(adresse)
        if not geocode:
            continue

        egrid = stufe_2_getegrid(geocode["east"], geocode["north"])
        if not egrid:
            continue

        xml_content = stufe_3_extract(egrid)
        if not xml_content:
            continue

        stufe_4_zonen_auswerten(xml_content)
        erfolg = True

        # Bei erstem Erfolg das XML lokal speichern fuer spaetere Analyse
        with open("extract_beispiel.xml", "wb") as f:
            f.write(xml_content)
        print(f"\n  -> XML-Auszug gespeichert in extract_beispiel.xml")
        break  # Ein Erfolg reicht zum Beweisen

    print("\n" + "=" * 70)
    if erfolg:
        print("TECHNISCHER DURCHSTICH GESCHAFFT!")
        print("Adresse -> Koordinaten -> EGRID -> OEREB-Auszug -> Zonen funktioniert.")
        print("Ihr koennt mit dem Modul-Aufbau beginnen.")
    else:
        print("Keine Adresse ist komplett durchgelaufen.")
        print("Details in der Ausgabe oben.")
    print("=" * 70)


if __name__ == "__main__":
    main()
