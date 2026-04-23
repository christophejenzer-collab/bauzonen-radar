"""
Baureglement-Lade-Modul.

Laedt die gemeindespezifischen Baureglemente aus JSON-Dateien und bietet
eine einheitliche Schnittstelle, um fuer eine Parzelle die passenden
Bauparameter (Ausnuetzungsziffer, Gebaeudehoehe, Grenzabstaende) zu finden.

Die Reglemente liegen unter daten/baureglemente/ und sind pro Gemeinde
strukturiert. Unterstuetzt werden zwei Strukturen:

  1. "bauklassen"  - Stadt-Bern-Stil mit getrennten Eintraegen fuer
                     Nutzungszone und Bauklasse. Parameter sitzen
                     typischerweise auf der Bauklasse.

  2. "kombiniert"  - Land-Stil (z.B. Thun, Koeniz), bei dem Zone und
                     Bauklasse in einem Eintrag stehen. Parameter
                     sitzen direkt auf der Zone.

Die Matching-Logik probiert mehrere Strategien und liefert den ersten
Treffer zurueck.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from modelle import Parzelle, Restriction


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------

@dataclass
class Bauparameter:
    """
    Die konkreten Reglement-Eckwerte einer Zone/Bauklasse.

    Alle Felder sind optional - je nach Reglement-Qualitaet und
    Gemeinde-Praxis sind nicht immer alle Werte gepflegt.
    """
    quelle_eintrag: str                         # z.B. "Bauklasse E" oder "Wohnzone W2"
    ausnuetzungsziffer: float | None = None     # AZ, z.B. 0.6
    max_geschosse: int | None = None            # Maximale Geschosszahl
    max_gebaeudehoehe_m: float | None = None    # Maximale Gebaeudehoehe in Metern
    grenzabstand_klein_m: float | None = None   # Kleiner Grenzabstand
    grenzabstand_gross_m: float | None = None   # Grosser Grenzabstand
    hinweise: str = ""                          # Freitext-Hinweise

    @property
    def ist_vollstaendig(self) -> bool:
        """True, wenn die AZ als Kernwert fuer die Potenzialberechnung da ist."""
        return self.ausnuetzungsziffer is not None

    def zusammenfassung(self) -> str:
        """Kurze Textuebersicht fuer Debugging und Ausgabe."""
        teile = [f"{self.quelle_eintrag}:"]
        if self.ausnuetzungsziffer is not None:
            teile.append(f"AZ={self.ausnuetzungsziffer}")
        if self.max_geschosse is not None:
            teile.append(f"max. {self.max_geschosse} Geschosse")
        if self.max_gebaeudehoehe_m is not None:
            teile.append(f"max. {self.max_gebaeudehoehe_m} m Hoehe")
        if not self.ist_vollstaendig:
            teile.append("(AZ fehlt - Potenzialberechnung nicht moeglich)")
        return " ".join(teile)


@dataclass
class Baureglement:
    """
    Reglement einer Gemeinde. Wird aus einer JSON-Datei geladen.

    Struktur-Varianten:
      - struktur="bauklassen"  -> Parameter kommen aus dem 'bauklassen'-Block
      - struktur="kombiniert"  -> Parameter kommen aus dem 'nutzungszonen'-Block
    """
    gemeinde: str
    bfs_nr: int
    kanton: str
    stand: str
    quelle: str
    struktur: str                                    # "bauklassen" oder "kombiniert"
    bauklassen: dict[str, dict] = field(default_factory=dict)
    nutzungszonen: dict[str, dict] = field(default_factory=dict)

    # ----- Laden -----

    @classmethod
    def laden(cls, gemeinde: str,
              basis_pfad: Path | str | None = None) -> "Baureglement":
        """
        Laedt das Baureglement einer Gemeinde aus der JSON-Datei.

        Sucht standardmaessig unter ../../daten/baureglemente/<gemeinde>.json
        relativ zum Modul. Alternativer Pfad kann uebergeben werden.

        Raises: FileNotFoundError, wenn die Datei fehlt.
        """
        if basis_pfad is None:
            hier = Path(__file__).resolve().parent
            basis_pfad = hier.parent.parent / "daten" / "baureglemente"
        else:
            basis_pfad = Path(basis_pfad)

        dateiname = gemeinde.lower().replace(" ", "_") + ".json"
        pfad = basis_pfad / dateiname

        if not pfad.exists():
            raise FileNotFoundError(
                f"Baureglement fuer '{gemeinde}' nicht gefunden unter {pfad}. "
                f"Erwartete Datei: {dateiname}"
            )

        with open(pfad, "r", encoding="utf-8") as f:
            daten = json.load(f)

        return cls(
            gemeinde=daten.get("gemeinde", gemeinde),
            bfs_nr=daten.get("bfs_nr", 0),
            kanton=daten.get("kanton", ""),
            stand=daten.get("stand", ""),
            quelle=daten.get("quelle", ""),
            struktur=daten.get("struktur", "kombiniert"),
            bauklassen=daten.get("bauklassen", {}),
            nutzungszonen=daten.get("nutzungszonen", {}),
        )

    # ----- Matching -----

    def finde_bauparameter(self, parzelle: Parzelle) -> list[Bauparameter]:
        """
        Findet fuer eine Parzelle die passenden Bauparameter.

        Gibt eine Liste zurueck, weil eine Parzelle in mehreren Zonen
        liegen kann (siehe Rathausplatz Thun: Bestandeszone + Uferzone).

        Wenn kein Match gefunden wird, ist die Liste leer. Der Aufrufer
        bekommt dann keine Fehler, sondern einfach "keine Information".
        """
        treffer: list[Bauparameter] = []

        if self.struktur == "bauklassen":
            treffer.extend(self._match_bauklassen(parzelle))
        else:
            treffer.extend(self._match_kombiniert(parzelle))

        return treffer

    def _match_bauklassen(self, parzelle: Parzelle) -> list[Bauparameter]:
        """
        Stadt-Bern-Stil: Bauklasse bestimmt die Parameter.
        Wir suchen im Bauklassen-Feld der Parzelle und vergleichen mit
        den Bauklassen-Eintraegen im Reglement.
        """
        treffer: list[Bauparameter] = []
        for bauklasse_parzelle in parzelle.bauklassen():
            parameter = self._suche_in_dict(
                self.bauklassen, bauklasse_parzelle.legende
            )
            if parameter:
                treffer.append(parameter)
        return treffer

    def _match_kombiniert(self, parzelle: Parzelle) -> list[Bauparameter]:
        """
        Land-Stil (Thun, Koeniz): Grundnutzung-Eintrag liefert Zone+Bauklasse
        in einem String. Wir matchen gegen nutzungszonen-Schluessel.
        """
        treffer: list[Bauparameter] = []
        for grundnutzung in parzelle.grundnutzungen_allgemein():
            parameter = self._suche_in_dict(
                self.nutzungszonen, grundnutzung.legende
            )
            if parameter:
                treffer.append(parameter)
        return treffer

    def _suche_in_dict(self, quelle: dict[str, dict],
                       suchtext: str) -> Bauparameter | None:
        """
        Durchsucht ein Reglement-Dict nach einem passenden Eintrag.

        Match-Strategien, in Reihenfolge:
          1. Exakte Uebereinstimmung
          2. Suchtext ist Teilstring eines Schluessels
          3. Schluessel ist Teilstring des Suchtexts
        """
        if not quelle or not suchtext:
            return None

        # Ignoriere interne Platzhalter
        effektiv = {k: v for k, v in quelle.items()
                    if not k.startswith("_")}

        # 1. Exakte Uebereinstimmung
        if suchtext in effektiv:
            return self._baue_parameter(suchtext, effektiv[suchtext])

        # 2. Suchtext ist Teil des Schluessels (z.B. "Bauklasse E" findet
        #    "Bauklasse E, Erhaltung der best. Bebauungsstruktur")
        for key, value in effektiv.items():
            if suchtext in key:
                return self._baue_parameter(key, value)

        # 3. Schluessel ist Teil des Suchtexts (z.B. "Wohnzone W" findet
        #    "Wohnzone W5" - in beide Richtungen robust)
        for key, value in effektiv.items():
            if key in suchtext:
                return self._baue_parameter(key, value)

        return None

    @staticmethod
    def _baue_parameter(quelle_eintrag: str, daten: dict) -> Bauparameter:
        """Erstellt ein Bauparameter-Objekt aus einem JSON-Dict."""
        return Bauparameter(
            quelle_eintrag=quelle_eintrag,
            ausnuetzungsziffer=daten.get("ausnuetzungsziffer"),
            max_geschosse=daten.get("max_geschosse"),
            max_gebaeudehoehe_m=daten.get("max_gebaeudehoehe_m"),
            grenzabstand_klein_m=daten.get("grenzabstand_klein_m"),
            grenzabstand_gross_m=daten.get("grenzabstand_gross_m"),
            hinweise=daten.get("hinweise", ""),
        )


# ---------------------------------------------------------------------------
# Direkter Aufruf zum Testen
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from bern import BernOerebQuelle

    adresse = sys.argv[1] if len(sys.argv) > 1 else "Thunstrasse 40, 3005 Bern"

    print(f"Suche Bauparameter fuer: {adresse}")
    print("=" * 70)

    # Parzelle laden
    quelle = BernOerebQuelle()
    parzelle = quelle.adresse_zu_parzelle(adresse)
    if not parzelle:
        print("Keine Parzelle gefunden.")
        sys.exit(1)

    print(f"Parzelle: {parzelle.nummer} ({parzelle.gemeinde})")
    print(f"Flaeche:  {parzelle.flaeche_m2:.0f} m^2")
    print()

    # Baureglement der Gemeinde laden
    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        print(f"Reglement geladen: {reglement.gemeinde} "
              f"(Stand: {reglement.stand}, Struktur: {reglement.struktur})")
    except FileNotFoundError as e:
        print(f"Kein Reglement verfuegbar: {e}")
        sys.exit(1)

    print()

    # Bauparameter suchen
    parameter_liste = reglement.finde_bauparameter(parzelle)

    if not parameter_liste:
        print("Keine Bauparameter gefunden.")
        print("Vermutlich ist die Zone noch nicht im Reglement-JSON erfasst.")
        print()
        print("Zonen der Parzelle:")
        for r in parzelle.grundnutzungen():
            print(f"  - {r.legende}")
        sys.exit(0)

    print(f"Gefundene Bauparameter ({len(parameter_liste)}):")
    for p in parameter_liste:
        print(f"  - {p.zusammenfassung()}")
        if p.hinweise:
            print(f"    Hinweis: {p.hinweise}")
