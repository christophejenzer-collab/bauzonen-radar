"""
Hauptskript: Komplette Analyse einer Adresse.

Fuehrt die gesamte Pipeline in einem einzigen Aufruf durch:

  Adresse -> OEREB-Daten -> Baureglement -> Potenzialanalyse -> Bericht

Aufruf:
    python analyse_adresse.py "Kramgasse 49, 3011 Bern"

Dies ist die Hauptschnittstelle fuer Demos und den spaeteren
Einsatz als Kommandozeilen-Tool.
"""

from __future__ import annotations

import sys

from bern import BernOerebQuelle
from baureglement import Baureglement
from analyse.potenzial import PotenzialBerechner


def analysiere(adresse: str) -> None:
    """Fuehrt die vollstaendige Analyse durch und gibt den Bericht aus."""
    print("=" * 70)
    print(f"Bauzonen-Radar - Analyse fuer: {adresse}")
    print("=" * 70)

    # Schritt 1: Parzelle laden via OEREB
    quelle = BernOerebQuelle()
    parzelle = quelle.adresse_zu_parzelle(adresse)
    if not parzelle:
        print("Keine Parzelle gefunden fuer diese Adresse.")
        return

    # Schritt 2: OEREB-Kurzbericht anzeigen
    print()
    print(parzelle.kurzbericht())
    print()
    print("=" * 70)

    # Schritt 3: Baureglement laden (falls vorhanden)
    reglement: Baureglement | None = None
    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        print(f"Baureglement geladen: {reglement.gemeinde} "
              f"(Stand: {reglement.stand}, Struktur: {reglement.struktur})")
    except FileNotFoundError:
        print(f"Kein Baureglement fuer '{parzelle.gemeinde}' verfuegbar.")
        print("Potenzialberechnung wird nicht moeglich sein.")

    print()

    # Schritt 4: Potenzialberechnung
    berechner = PotenzialBerechner()
    ergebnis = berechner.berechne(parzelle, reglement)

    print(ergebnis.textbericht())
    print()


def main() -> int:
    if len(sys.argv) < 2:
        print("Verwendung: python analyse_adresse.py \"Strasse Nr, PLZ Ort\"")
        print()
        print("Beispiele:")
        print('  python analyse_adresse.py "Kramgasse 49, 3011 Bern"')
        print('  python analyse_adresse.py "Rathausplatz 1, 3600 Thun"')
        return 1

    analysiere(sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
