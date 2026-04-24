"""
Baureglement-Lade-Modul.

Laedt die gemeindespezifischen Baureglemente aus JSON-Dateien und bietet
eine einheitliche Schnittstelle, um fuer eine Parzelle die passenden
Bauparameter zu finden.

Systemwechsel im Kanton Bern:
-----------------------------
Der Kanton Bern hat die klassische Ausnuetzungsziffer (AZ) durch die
Geschossflaechenziffer oberirdisch (GFZo) ersetzt (BMBV-Verordnung,
basierend auf der IVHB-Vereinbarung). Gemeinden muessen ihre Baureglemente
schrittweise anpassen. Solange das nicht geschehen ist, gelten die alten
AZ-Bestimmungen (BauV Art. 93-98) weiter.

Einige Gemeinden (Beispiel Thun, BR 2022 ab Februar 2025) gehen noch
einen Schritt weiter und verzichten auch auf die GFZo: Die bauliche
Dichte wird dort primaer ueber Gebaeudehoehen und die Gruenflaechenziffer
gesteuert.

Das Datenmodell unterstuetzt alle drei Bemessungssysteme:
  - AZ            : Klassische Ausnuetzungsziffer (alt, immer noch gueltig
                    wo Revision fehlt)
  - GFZo          : Geschossflaechenziffer oberirdisch (IVHB-konform)
  - hoehen_und_gz : Steuerung ueber Gebaeudehoehen + Gruenflaechenziffer
                    (Thun-Stil)

Dualitaet: In Uebergangsphasen (z.B. Thun seit Maerz 2022) gelten beide
Regelwerke parallel. In dem Fall werden beide Kennzahlen im JSON gepflegt;
der Berechner waehlt die jeweils relevante aus.

Strukturvarianten der JSON-Dateien:
  - "bauklassen"  - Stadt-Bern-Stil mit getrennten Eintraegen fuer
                    Nutzungszone und Bauklasse. Parameter typischerweise
                    auf der Bauklasse.
  - "kombiniert"  - Land-Stil (Thun, Koeniz), Zone und Bauklasse in einem
                    Eintrag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from modelle import Parzelle, Restriction


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BemessungsSystem(Enum):
    """
    Welches Regelwerk steuert die Bebauungsdichte dieser Zone?

    AZ            - Klassische Ausnuetzungsziffer (altes Recht, BauV Art. 93-98)
    GFZo          - Geschossflaechenziffer oberirdisch (IVHB-konform)
    HOEHEN_UND_GZ - Steuerung primaer durch Gebaeudehoehen und Gruenflaechenziffer
    DUALITAET     - Uebergangsphase: altes und neues Recht gelten parallel
    UNBEKANNT     - System nicht im Reglement erfasst
    """
    AZ = "AZ"
    GFZO = "GFZo"
    HOEHEN_UND_GZ = "hoehen_und_gz"
    DUALITAET = "dualitaet"
    UNBEKANNT = "unbekannt"

    @classmethod
    def from_string(cls, text: str | None) -> "BemessungsSystem":
        """Parst einen JSON-String in das Enum. Toleriert verschiedene Schreibweisen."""
        if not text:
            return cls.UNBEKANNT
        norm = text.strip().lower().replace("-", "_")
        mapping = {
            "az": cls.AZ,
            "gfzo": cls.GFZO,
            "geschossflaechenziffer": cls.GFZO,
            "geschossflächenziffer": cls.GFZO,
            "hoehen_und_gz": cls.HOEHEN_UND_GZ,
            "höhen_und_gz": cls.HOEHEN_UND_GZ,
            "hoehen": cls.HOEHEN_UND_GZ,
            "dualitaet": cls.DUALITAET,
            "dualität": cls.DUALITAET,
            "uebergang": cls.DUALITAET,
        }
        return mapping.get(norm, cls.UNBEKANNT)


# ---------------------------------------------------------------------------
# Bauparameter
# ---------------------------------------------------------------------------

@dataclass
class Bauparameter:
    """
    Die konkreten Reglement-Eckwerte einer Zone.

    Kann Werte fuer AZ, GFZo und/oder Hoehen+GZ enthalten, je nachdem
    welches System die Gemeinde verwendet. Bei Uebergangsphasen (Dualitaet)
    sind alte und neue Werte gleichzeitig gepflegt.

    Alle Zahlen-Felder sind optional, damit die Klasse mit Reglementen
    in unterschiedlichem Revisions-Stand umgehen kann.
    """
    quelle_eintrag: str                              # z.B. "Bauklasse E" oder "Wohnzone W2"
    system: BemessungsSystem = BemessungsSystem.UNBEKANNT

    # Klassische AZ (altes Recht)
    ausnuetzungsziffer: float | None = None

    # GFZo (neues Recht nach IVHB)
    geschossflaechenziffer_oberirdisch: float | None = None

    # Hoehen-basierte Steuerung
    max_gebaeudehoehe_m: float | None = None
    max_fassadenhoehe_m: float | None = None
    max_geschosse: int | None = None

    # Gruenflaechenziffer (wie viel der Parzelle unversiegelt bleibt)
    gruenflaechenziffer: float | None = None

    # Abstaende
    grenzabstand_klein_m: float | None = None
    grenzabstand_gross_m: float | None = None

    # Meta
    rechtsgrundlage: str = ""        # z.B. "BR 2022 Art. 23" oder "BR 2002 Art. 15"
    hinweise: str = ""
    gueltig_ab: str | None = None    # z.B. "2025-02-01" bei neuem Recht

    # ----- Abgeleitete Eigenschaften -----

    @property
    def ist_berechenbar(self) -> bool:
        """
        True, wenn irgendein Wert zur Potenzialberechnung verfuegbar ist.

        Eine AZ, eine GFZo oder Gebaeudehoehe+Gruenflaechenziffer genuegt.
        """
        if self.ausnuetzungsziffer is not None:
            return True
        if self.geschossflaechenziffer_oberirdisch is not None:
            return True
        if self.max_gebaeudehoehe_m is not None and self.gruenflaechenziffer is not None:
            return True
        return False

    def hauptkennzahl(self) -> tuple[str, float] | None:
        """
        Gibt die fuer die Potenzialberechnung relevante Kennzahl zurueck.

        Prioritaet:
          1. GFZo (neues Recht)
          2. AZ (altes Recht)
          3. None (muss via Hoehen+GZ berechnet werden)
        """
        if self.geschossflaechenziffer_oberirdisch is not None:
            return ("GFZo", self.geschossflaechenziffer_oberirdisch)
        if self.ausnuetzungsziffer is not None:
            return ("AZ", self.ausnuetzungsziffer)
        return None

    # ----- Textausgabe -----

    def zusammenfassung(self) -> str:
        """Kurze Textuebersicht fuer Debugging und Ausgabe."""
        teile = [f"{self.quelle_eintrag} [{self.system.value}]:"]

        if self.ausnuetzungsziffer is not None:
            teile.append(f"AZ={self.ausnuetzungsziffer}")
        if self.geschossflaechenziffer_oberirdisch is not None:
            teile.append(f"GFZo={self.geschossflaechenziffer_oberirdisch}")
        if self.max_gebaeudehoehe_m is not None:
            teile.append(f"max. {self.max_gebaeudehoehe_m} m Hoehe")
        if self.max_geschosse is not None:
            teile.append(f"max. {self.max_geschosse} Gesch.")
        if self.gruenflaechenziffer is not None:
            teile.append(f"GZ={self.gruenflaechenziffer}")

        if not self.ist_berechenbar:
            teile.append("(keine Kennzahlen - Potenzialberechnung nicht moeglich)")

        return " ".join(teile)


# ---------------------------------------------------------------------------
# Baureglement
# ---------------------------------------------------------------------------

@dataclass
class Baureglement:
    """
    Reglement einer Gemeinde. Wird aus einer JSON-Datei geladen.

    Struktur-Varianten:
      - struktur="bauklassen"  -> Parameter aus dem 'bauklassen'-Block
      - struktur="kombiniert"  -> Parameter aus dem 'nutzungszonen'-Block
    """
    gemeinde: str
    bfs_nr: int
    kanton: str
    stand: str
    quelle: str
    struktur: str
    system_default: BemessungsSystem = BemessungsSystem.UNBEKANNT
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

        Umlaute werden fuer den Dateinamen zu ae/oe/ue umgewandelt.

        Raises: FileNotFoundError, wenn die Datei fehlt.
        """
        if basis_pfad is None:
            hier = Path(__file__).resolve().parent
            basis_pfad = hier.parent.parent / "daten" / "baureglemente"
        else:
            basis_pfad = Path(basis_pfad)

        # Umlaute fuer dateisystem-sichere Namen ersetzen
        umlaute = {"ä": "ae", "ö": "oe", "ü": "ue",
                   "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
        name = gemeinde
        for alt, neu in umlaute.items():
            name = name.replace(alt, neu)
        dateiname = name.lower().replace(" ", "_") + ".json"
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
            system_default=BemessungsSystem.from_string(daten.get("system_default")),
            bauklassen=daten.get("bauklassen", {}),
            nutzungszonen=daten.get("nutzungszonen", {}),
        )

    # ----- Matching -----

    def finde_bauparameter(self, parzelle: Parzelle) -> list[Bauparameter]:
        """
        Findet fuer eine Parzelle die passenden Bauparameter.

        Gibt eine Liste zurueck, weil eine Parzelle in mehreren Zonen
        liegen kann. Wenn kein Match gefunden wird, ist die Liste leer.
        """
        if self.struktur == "bauklassen":
            return self._match_bauklassen(parzelle)
        return self._match_kombiniert(parzelle)

    def _match_bauklassen(self, parzelle: Parzelle) -> list[Bauparameter]:
        """
        Stadt-Bern-Stil: Bauklasse bestimmt die Parameter.
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
        Land-Stil: Grundnutzung-Eintrag liefert Zone+Bauklasse in einem.
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

        Match-Strategien in Reihenfolge:
          1. Exakte Uebereinstimmung
          2. Suchtext ist Teilstring eines Schluessels
          3. Schluessel ist Teilstring des Suchtexts
        """
        if not quelle or not suchtext:
            return None

        # Interne Platzhalter ignorieren
        effektiv = {k: v for k, v in quelle.items()
                    if not k.startswith("_")}

        # 1. Exakte Uebereinstimmung
        if suchtext in effektiv:
            return self._baue_parameter(suchtext, effektiv[suchtext])

        # 2. Suchtext ist Teil des Schluessels
        for key, value in effektiv.items():
            if suchtext in key:
                return self._baue_parameter(key, value)

        # 3. Schluessel ist Teil des Suchtexts
        for key, value in effektiv.items():
            if key in suchtext:
                return self._baue_parameter(key, value)

        return None

    def _baue_parameter(self, quelle_eintrag: str,
                        daten: dict) -> Bauparameter:
        """
        Erstellt ein Bauparameter-Objekt aus einem JSON-Dict.

        Verwendet das System aus dem Eintrag oder faellt auf den
        Gemeinde-Default zurueck.
        """
        system_text = daten.get("system")
        system = (BemessungsSystem.from_string(system_text)
                  if system_text else self.system_default)

        return Bauparameter(
            quelle_eintrag=quelle_eintrag,
            system=system,
            ausnuetzungsziffer=daten.get("ausnuetzungsziffer"),
            geschossflaechenziffer_oberirdisch=daten.get(
                "geschossflaechenziffer_oberirdisch"
            ),
            max_gebaeudehoehe_m=daten.get("max_gebaeudehoehe_m"),
            max_fassadenhoehe_m=daten.get("max_fassadenhoehe_m"),
            max_geschosse=daten.get("max_geschosse"),
            gruenflaechenziffer=daten.get("gruenflaechenziffer"),
            grenzabstand_klein_m=daten.get("grenzabstand_klein_m"),
            grenzabstand_gross_m=daten.get("grenzabstand_gross_m"),
            rechtsgrundlage=daten.get("rechtsgrundlage", ""),
            hinweise=daten.get("hinweise", ""),
            gueltig_ab=daten.get("gueltig_ab"),
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

    quelle = BernOerebQuelle()
    parzelle = quelle.adresse_zu_parzelle(adresse)
    if not parzelle:
        print("Keine Parzelle gefunden.")
        sys.exit(1)

    print(f"Parzelle: {parzelle.nummer} ({parzelle.gemeinde})")
    print(f"Flaeche:  {parzelle.flaeche_m2:.0f} m^2")
    print()

    try:
        reglement = Baureglement.laden(parzelle.gemeinde)
        print(f"Reglement geladen: {reglement.gemeinde}")
        print(f"  Stand:          {reglement.stand}")
        print(f"  Struktur:       {reglement.struktur}")
        print(f"  Default-System: {reglement.system_default.value}")
    except FileNotFoundError as e:
        print(f"Kein Reglement verfuegbar: {e}")
        sys.exit(1)

    print()

    parameter_liste = reglement.finde_bauparameter(parzelle)

    if not parameter_liste:
        print("Keine Bauparameter gefunden.")
        print("Zone ist im Reglement noch nicht erfasst.")
        print()
        print("Zonen der Parzelle:")
        for r in parzelle.grundnutzungen():
            print(f"  - {r.legende}")
        sys.exit(0)

    print(f"Gefundene Bauparameter ({len(parameter_liste)}):")
    for p in parameter_liste:
        print(f"  - {p.zusammenfassung()}")
        if p.rechtsgrundlage:
            print(f"    Rechtsgrundlage: {p.rechtsgrundlage}")
        if p.hinweise:
            print(f"    Hinweis:         {p.hinweise}")
        if p.gueltig_ab:
            print(f"    Gueltig ab:      {p.gueltig_ab}")
