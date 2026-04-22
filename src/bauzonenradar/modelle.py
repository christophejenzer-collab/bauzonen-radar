"""
Datenmodell fuer den Bauzonen-Radar.

Definiert die zentralen Klassen, die Parzellen und ihre OEREB-Informationen
strukturiert halten. Alle Datenquellen (Bern, spaeter Zuerich, etc.)
liefern ihre Resultate in Form dieser Klassen.

Der Parser erkennt die SubCodes gemaess OEREB-Schema V2.0:
  - ch.NutzungsplanungGrundnutzung (+ Subtypen Nutzungszonen, Bauklassen)
  - ch.NutzungsplanungUeberlagerung
  - ch.NutzungsplanungSondernutzung
  - ch.NutzungsplanungGefahrengebiete
  - ch.NutzungsplanungFlaecheAndere
  - ch.NutzungsplanungLinie

Wir nutzen dataclasses, weil sie wenig Boilerplate haben und automatisch
eine huebsche Textausgabe produzieren (nuetzlich fuer Debugging).
"""

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Lawstatus
# ---------------------------------------------------------------------------

class Lawstatus(Enum):
    """
    Rechtsstatus einer OEREB-Beschraenkung gemaess OEREB-Schema V2.0.

    IN_FORCE ist der Normalfall (rechtskraeftig).
    Die anderen drei Werte sind der 'Zukunfts-Layer':
    Parzellen mit diesem Status haben laufende oder projektierte Aenderungen.
    """
    IN_FORCE = "inForce"                                   # rechtskraeftig
    CHANGE_WITH_PRE_EFFECT = "changeWithPreEffect"         # Aenderung mit Vorwirkung
    CHANGE_WITHOUT_PRE_EFFECT = "changeWithoutPreEffect"   # Aenderung ohne Vorwirkung
    RUNNING_MODIFICATIONS = "runningModifications"         # laufende Verfahren

    @classmethod
    def from_string(cls, code: str) -> "Lawstatus":
        """Erstellt Lawstatus aus XML-Code. Faellt auf IN_FORCE zurueck."""
        for status in cls:
            if status.value == code:
                return status
        return cls.IN_FORCE


# ---------------------------------------------------------------------------
# Restriction (eine einzelne OEREB-Beschraenkung)
# ---------------------------------------------------------------------------

@dataclass
class Restriction:
    """
    Eine einzelne OEREB-Beschraenkung auf der Parzelle.

    Beispiele:
        - Altstadtperimeter BO.06 (Grundnutzung, rechtskraeftig, 236 m^2)
        - Hochwassergefahrengebiet mittel (Gefahrengebiet)
        - Baulinie Strasse (Linie)
    """
    thema_code: str              # z.B. "ch.Nutzungsplanung"
    thema_text: str              # z.B. "Kommunale Nutzungsplanung"
    sub_code: str | None         # z.B. "ch.NutzungsplanungGrundnutzungNutzungszonen"
    legende: str                 # z.B. "Altstadtperimeter BO.06"
    type_code: str | None        # z.B. "217_309" (interne Kennung)
    lawstatus: Lawstatus         # rechtskraeftig oder in Aenderung
    flaeche_m2: float | None     # AreaShare in m^2
    prozent_anteil: float | None # PartInPercent (0-100)
    symbol_url: str | None       # URL zu Legenden-Symbol
    karten_wms_url: str | None   # Vorgefertigte WMS-URL fuer Kartenansicht

    # ----- Kategorie-Properties (basierend auf sub_code) -----

    @property
    def ist_grundnutzung(self) -> bool:
        """Grundnutzung (eigentliche Bauzone). AZ wird darauf angewendet."""
        if not self.sub_code:
            return False
        return "Grundnutzung" in self.sub_code

    @property
    def ist_nutzungszone(self) -> bool:
        """Nutzungszone im Stadt-Bern-Dialekt (z.B. Wohnzone W)."""
        if not self.sub_code:
            return False
        return "GrundnutzungNutzungszonen" in self.sub_code

    @property
    def ist_bauklasse(self) -> bool:
        """Bauklasse im Stadt-Bern-Dialekt (bestimmt Dichte)."""
        if not self.sub_code:
            return False
        return "GrundnutzungBauklassen" in self.sub_code

    @property
    def ist_ueberlagerung(self) -> bool:
        """Ueberlagernde Nutzung (Ortsbildschutz, Erhaltungszone, etc.)."""
        if not self.sub_code:
            return False
        return (
            "Ueberlagerung" in self.sub_code
            or "Ueberlagernd" in self.sub_code
            or "Überlagerung" in self.sub_code
            or "Überlagernd" in self.sub_code
        )

    @property
    def ist_gefahrengebiet(self) -> bool:
        """Naturgefahren-Zone (Hochwasser, Rutschung, Sturz)."""
        if not self.sub_code:
            return False
        return "Gefahrengebiet" in self.sub_code

    @property
    def ist_flaeche_andere(self) -> bool:
        """Weitere Flaechen-Information (z.B. Gewaesser, Waldabstand)."""
        if not self.sub_code:
            return False
        return "FlaecheAndere" in self.sub_code

    @property
    def ist_linie(self) -> bool:
        """Lineare Beschraenkungen (Baulinien, Erschliessungslinien)."""
        if not self.sub_code:
            return False
        return "Linie" in self.sub_code

    @property
    def ist_sondernutzung(self) -> bool:
        """Sondernutzung (Gestaltungsplan, Ueberbauungsordnung)."""
        if not self.sub_code:
            return False
        return "Sondernutzung" in self.sub_code

    @property
    def ist_nutzungsplanung(self) -> bool:
        """True, wenn dies irgendeine Nutzungsplanung-Kategorie ist."""
        return self.thema_code == "ch.Nutzungsplanung"

    @property
    def ist_in_aenderung(self) -> bool:
        """True, wenn diese Beschraenkung nicht mehr den aktuellen Stand hat."""
        return self.lawstatus != Lawstatus.IN_FORCE


# ---------------------------------------------------------------------------
# Parzelle
# ---------------------------------------------------------------------------

@dataclass
class Parzelle:
    """
    Eine Schweizer Parzelle mit allen relevanten OEREB-Informationen.

    Zentrale Datenklasse: Datenquellen liefern Parzelle-Objekte,
    Analyse-Module rechnen darauf, Ausgabe-Module formatieren sie.
    """
    egrid: str                         # eidgenoessische Grundstuecks-ID
    nummer: str                        # lokale Parzellennummer (z.B. "575")
    identdn: str                       # lokale Gemeinde-ID (z.B. "BE0200000042")
    gemeinde: str                      # z.B. "Bern"
    kanton: str                        # z.B. "BE"
    flaeche_m2: float                  # Gesamtflaeche des Grundstuecks
    adresse: str | None = None         # Original-Adresse der Suche
    koordinaten_lv95: tuple[float, float] | None = None  # (E, N)
    restrictions: list[Restriction] = field(default_factory=list)

    # ----- Filter-Methoden nach Kategorie -----

    def nutzungszonen(self) -> list[Restriction]:
        """Nutzungszonen im Stadt-Bern-Dialekt (z.B. Wohnzone W)."""
        return [r for r in self.restrictions if r.ist_nutzungszone]

    def bauklassen(self) -> list[Restriction]:
        """Bauklassen im Stadt-Bern-Dialekt (bestimmen Ausnuetzung)."""
        return [r for r in self.restrictions if r.ist_bauklasse]

    def grundnutzungen(self) -> list[Restriction]:
        """Alle Grundnutzungen (Nutzungszone + Bauklasse + allgemein)."""
        return [r for r in self.restrictions if r.ist_grundnutzung]

    def grundnutzungen_allgemein(self) -> list[Restriction]:
        """
        Grundnutzungen ohne spezifische Unterkategorie.
        Fuer Gemeinden ohne feine Unterteilung (z.B. Koeniz, Thun).
        """
        return [
            r for r in self.restrictions
            if r.ist_grundnutzung
            and not r.ist_nutzungszone
            and not r.ist_bauklasse
        ]

    def ueberlagerungen(self) -> list[Restriction]:
        """Ueberlagernde Nutzungen (Ortsbildschutz, Erhaltungszonen)."""
        return [r for r in self.restrictions if r.ist_ueberlagerung]

    def sondernutzungen(self) -> list[Restriction]:
        """Sondernutzungen (Gestaltungsplaene, Ueberbauungsordnungen)."""
        return [r for r in self.restrictions if r.ist_sondernutzung]

    def gefahrengebiete(self) -> list[Restriction]:
        """Naturgefahren-Zonen (Hochwasser, Rutschung, Sturz)."""
        return [r for r in self.restrictions if r.ist_gefahrengebiet]

    def flaechen_andere(self) -> list[Restriction]:
        """Weitere Flaechen-Informationen."""
        return [r for r in self.restrictions if r.ist_flaeche_andere]

    def linien(self) -> list[Restriction]:
        """Lineare Einschraenkungen (Baulinien)."""
        return [r for r in self.restrictions if r.ist_linie]

    def bauzonen(self) -> list[Restriction]:
        """Alle Nutzungsplanung-Eintraege (alle Kategorien zusammen)."""
        return [r for r in self.restrictions if r.ist_nutzungsplanung]

    def laufende_aenderungen(self) -> list[Restriction]:
        """
        Alle Beschraenkungen, die NICHT mehr den aktuellen Rechtsstand
        haben. Das ist der Zukunfts-Layer fuer das Tool.
        """
        return [r for r in self.restrictions if r.ist_in_aenderung]

    # ----- Uebersicht -----

    def themen_uebersicht(self) -> dict[str, int]:
        """Zaehlt Beschraenkungen pro Thema."""
        zaehler: dict[str, int] = {}
        for r in self.restrictions:
            zaehler[r.thema_code] = zaehler.get(r.thema_code, 0) + 1
        return zaehler

    # ----- Textausgabe -----

    def kurzbericht(self) -> str:
        """Erzeugt eine strukturierte Textuebersicht der Parzelle."""
        zeilen = [
            f"Parzelle {self.nummer} ({self.gemeinde}, {self.kanton})",
            f"EGRID:    {self.egrid}",
            f"Flaeche:  {self.flaeche_m2:.0f} m^2",
        ]

        if self.adresse:
            zeilen.append(f"Adresse:  {self.adresse}")

        self._block_mit_flaeche(zeilen, "Nutzungszone(n)", self.nutzungszonen())
        self._block_einfach(zeilen, "Bauklasse(n)", self.bauklassen())
        self._block_mit_flaeche(zeilen, "Grundnutzung (Bauzone)", self.grundnutzungen_allgemein())
        self._block_einfach(zeilen, "Ueberlagerungen", self.ueberlagerungen())
        self._block_einfach(zeilen, "Sondernutzungen", self.sondernutzungen())
        self._block_einfach(zeilen, "Naturgefahren", self.gefahrengebiete(), praefix="! ")
        self._block_einfach(zeilen, "Baulinien", self.linien())
        self._block_einfach(zeilen, "Weitere Flaechen", self.flaechen_andere())

        aenderungen = self.laufende_aenderungen()
        if aenderungen:
            zeilen.append("")
            zeilen.append("LAUFENDE AENDERUNGEN:")
            for a in aenderungen:
                zeilen.append(f"  ! {a.legende} - Status: {a.lawstatus.value}")

        themen = self.themen_uebersicht()
        if themen:
            zeilen.append("")
            zeilen.append("OEREB-Themen auf dieser Parzelle:")
            for thema, anzahl in sorted(themen.items()):
                zeilen.append(f"  - {thema} ({anzahl} Eintrag/Eintraege)")

        return "\n".join(zeilen)

    # ----- Interne Hilfsmethoden fuer den Kurzbericht -----

    @staticmethod
    def _block_einfach(zeilen: list[str], titel: str,
                       items: list[Restriction], praefix: str = "") -> None:
        """Haengt einen einfachen Block 'Titel: - Item - Item' an."""
        if not items:
            return
        zeilen.append("")
        zeilen.append(f"{titel}:")
        # Duplikate entfernen (gleiche Legende), Reihenfolge behalten
        gesehen: set[str] = set()
        for item in items:
            if item.legende in gesehen:
                continue
            gesehen.add(item.legende)
            zeilen.append(f"  - {praefix}{item.legende}")

    @staticmethod
    def _block_mit_flaeche(zeilen: list[str], titel: str,
                           items: list[Restriction]) -> None:
        """Haengt einen Block mit Flaechen-/Prozent-Angabe an."""
        if not items:
            return
        zeilen.append("")
        zeilen.append(f"{titel}:")
        gesehen: set[str] = set()
        for item in items:
            if item.legende in gesehen:
                continue
            gesehen.add(item.legende)
            zeile = f"  - {item.legende}"
            if item.prozent_anteil is not None and item.flaeche_m2 is not None:
                zeile += f" ({item.prozent_anteil:.0f}%, {item.flaeche_m2:.0f} m^2)"
            zeilen.append(zeile)
