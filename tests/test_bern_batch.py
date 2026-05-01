"""Batch-Test fuer den Bauklassenplan Stadt Bern.

Testet mehrere Adressen quer durch die Stadt, um zu sehen wie die echten
BKP-Daten fuer verschiedene Bauklassen aussehen.

Verwendung:
    python -m src.bauzonenradar.test_bern_batch
"""

from src.bauzonenradar.bern_bkp import BernBkpQuelle


# Test-Adressen quer durch Bern.
# Koordinaten in LV95 (siehe map.geo.admin.ch).
# Erwartete Bauklasse ist eine Vermutung - der Test zeigt die echte.
TEST_ADRESSEN = [
    {
        "adresse": "Thunstrasse 40, Bern",
        "ost": 2601810,
        "nord": 1200030,
        "vermutung": "BK_2 (W) - bekannt aus erstem Test",
    },
    {
        "adresse": "Marktgasse 25, Bern (Altstadt)",
        "ost": 2600540,  # TODO: bei map.geo.admin.ch verifizieren
        "nord": 1199730,  # TODO: bei map.geo.admin.ch verifizieren
        "vermutung": "BK_E (Erhaltung)",
    },
    {
        "adresse": "Bundesgasse 1, Bern (Bundeshaus-Naehe)",
        "ost": 2600090,  # TODO: bei map.geo.admin.ch verifizieren
        "nord": 1199500,  # TODO: bei map.geo.admin.ch verifizieren
        "vermutung": "BK_E oder BK_5/6 (innerstaedtisch)",
    },
    {
        "adresse": "Wankdorfplatz 1, Bern (Wankdorf)",
        "ost": 2602140,  # TODO: bei map.geo.admin.ch verifizieren
        "nord": 1201730,  # TODO: bei map.geo.admin.ch verifizieren
        "vermutung": "BK_5 oder BK_6 (Hochhauszone)",
    },
    {
        "adresse": "Lorrainestrasse 50, Bern (Lorraine)",
        "ost": 2600610,  # TODO: bei map.geo.admin.ch verifizieren
        "nord": 1200340,  # TODO: bei map.geo.admin.ch verifizieren
        "vermutung": "BK_3 oder BK_4 (gemischt urban)",
    },
    {
        "adresse": "Bumplitzstrasse 100, Bern (Bumplitz)",
        "ost": 2596500,  # TODO: bei map.geo.admin.ch verifizieren
        "nord": 1199500,  # TODO: bei map.geo.admin.ch verifizieren
        "vermutung": "BK_2 oder BK_3 (Aussenquartier)",
    },
]


def teste_adresse(quelle: BernBkpQuelle, eintrag: dict) -> None:
    """Testet eine einzelne Adresse und gibt das Ergebnis aus."""
    print()
    print("=" * 70)
    print(f"Adresse:    {eintrag['adresse']}")
    print(f"Koordinate: LV95 {eintrag['ost']}/{eintrag['nord']}")
    print(f"Vermutung:  {eintrag['vermutung']}")
    print("=" * 70)

    auskunft = quelle.hole_auskunft(eintrag["ost"], eintrag["nord"])

    if not auskunft.gefunden:
        print("  KEINE DATEN - Punkt liegt vermutlich ausserhalb Bern Stadtgebiet")
        return

    if auskunft.grundzone:
        g = auskunft.grundzone
        print(f"  Nutzungszone:    {g.nutzungszone_kuerzel:8} ({g.nutzungszone_beschrieb})")
        print(f"  Bauklasse:       {g.bauklasse_kuerzel:8} ({g.bauklasse_beschrieb})")
    else:
        print("  Grundzone:       (keine Daten)")

    if auskunft.bauweise:
        b = auskunft.bauweise
        laenge = "unbeschr." if b.gebaeudelaenge_unbeschraenkt else f"{b.gebaeudelaenge} m"
        tiefe = "unbeschr." if b.gebaeudetiefe_unbeschraenkt else f"{b.gebaeudetiefe} m"
        print(f"  Bauweise:        {b.bauweise_beschrieb}")
        print(f"  Gebaeudelaenge:  {laenge}")
        print(f"  Gebaeudetiefe:   {tiefe}")
    else:
        print("  Bauweise:        (keine Daten)")


def main() -> None:
    quelle = BernBkpQuelle()
    print()
    print("BKP-BATCH-TEST Stadt Bern")
    print(f"Anzahl Adressen: {len(TEST_ADRESSEN)}")

    for eintrag in TEST_ADRESSEN:
        try:
            teste_adresse(quelle, eintrag)
        except Exception as fehler:
            print(f"  FEHLER: {fehler}")

    print()
    print("=" * 70)
    print("BATCH-TEST FERTIG")
    print("=" * 70)


if __name__ == "__main__":
    main()
