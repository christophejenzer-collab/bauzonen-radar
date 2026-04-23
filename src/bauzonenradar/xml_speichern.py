"""Hilfsskript: Speichert das OEREB-XML einer Adresse lokal zur Analyse.

Aufruf:
    python xml_speichern.py "Adresse" ausgabe.xml

Wenn keine Argumente gegeben werden, wird Kramgasse 49 nach extract_test.xml
gespeichert.
"""

import sys
from bern import BernOerebQuelle


def main() -> int:
    adresse = sys.argv[1] if len(sys.argv) > 1 else "Kramgasse 49, 3011 Bern"
    ausgabe = sys.argv[2] if len(sys.argv) > 2 else "extract_test.xml"

    print(f"Adresse:  {adresse}")
    print(f"Ausgabe:  {ausgabe}")
    print()

    quelle = BernOerebQuelle()

    koord = quelle.geocode(adresse)
    if not koord:
        print("FEHLER: Geocoding fehlgeschlagen")
        return 1
    print(f"Koordinaten: E={koord[0]:.1f}, N={koord[1]:.1f}")

    egrid = quelle.getegrid(*koord)
    if not egrid:
        print("FEHLER: Kein EGRID gefunden")
        return 1
    print(f"EGRID: {egrid}")

    xml = quelle.get_extract_xml(egrid)
    if not xml:
        print("FEHLER: Extract fehlgeschlagen")
        return 1

    with open(ausgabe, "wb") as f:
        f.write(xml)
    print(f"Gespeichert: {ausgabe} ({len(xml)} Bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
