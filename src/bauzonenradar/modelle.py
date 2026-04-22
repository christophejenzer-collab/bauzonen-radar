"""
Datenmodell fuer den Bauzonen-Radar.

Definiert die zentralen Klassen, die Parzellen und ihre OEREB-Informationen
strukturiert halten. Alle Datenquellen (Bern, spaeter Zuerich, etc.)
liefern ihre Resultate in Form dieser Klassen.

Wir nutzen dataclasses, weil sie wenig Boilerplate haben und automatisch
eine huebsche Textausgabe produzieren (nuetzlich fuer Debugging).
"""

from dataclasses import dataclass, field
from enum import Enum


class Lawstatus(Enum):
    """
    Rechtsstatus einer OEREB-Beschraenkung gemaess OEREB-Schema V2.0.

    IN_FORCE ist der Normalfall (rechtskraeftig).
    Die anderen drei Werte sind euer 'Zukunfts-Layer':
    Parzellen mit diesem Status haben laufende oder projektierte Aenderungen.
    """
    IN_FORCE = "inForce"                            # rechtskraeftig
    CHANGE_WITH_PRE_EFFECT = "changeWithPreEffect"  # Aenderung mit Vorwirkung
    CHANGE_WITHOUT_PRE_EFFECT = "changeWithoutPreEffect"  # Aenderung ohne Vorwirkung
    RUNNING_MODIFICATIONS = "runningModifications"  # laufende Verfahren

    @classmethod
    def from_string(cls, code: str) -> "Lawstatus":
        """Erstellt Lawstatus aus XML-Code. Faellt auf IN_FORCE zurueck."""
        for status in cls:
            if status.value == code:
                return status
        return cls.IN_FORCE


@dataclass
class Restriction:
    """
    Eine einzelne OEREB-Beschraenkung auf der Parzelle.

    Beispiel: 'Altstadtperimeter BO.06' (Nutzungsplanung) -
    Rechtskraeftig, betrifft 236 m^2 (100% der Parzelle).
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

    @property
    def ist_nutzungsplanung(self) -> bool:
        """True, wenn dies eine Bauzone (Grundnutzung) ist."""
        if not self.sub_code:
            return False
        return "Grundnutzung" in self.sub_code or "Nutzungszonen" in self.sub_code

    @property
    def ist_in_aenderung(self) -> bool:
        """True, wenn diese Beschraenkung nicht mehr den aktuellen Stand hat."""
        return self.lawstatus != Lawstatus.IN_FORCE


@dataclass
class Parzelle:
    """
    Eine Schweizer Parzelle mit allen relevanten OEREB-Informationen.

    Das ist das zentrale Datenobjekt eures Tools. Datenquellen
    liefern Parzelle-Objekte, die Analyse-Module rechnen darauf,
    Ausgabe-Module formatieren sie.
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

    def bauzonen(self) -> list[Restriction]:
        """Gibt nur die Nutzungsplanung-Eintraege (Grundnutzung) zurueck."""
        return [r for r in self.restrictions if r.ist_nutzungsplanung]

    def laufende_aenderungen(self) -> list[Restriction]:
        """
        Gibt alle Beschraenkungen zurueck, die NICHT mehr den aktuellen
        Rechtsstand haben. Das ist der Zukunfts-Layer fuer euer Tool.
        """
        return [r for r in self.restrictions if r.ist_in_aenderung]

    def themen_uebersicht(self) -> dict[str, int]:
        """Zaehlt Beschraenkungen pro Thema."""
        zaehler: dict[str, int] = {}
        for r in self.restrictions:
            zaehler[r.thema_code] = zaehler.get(r.thema_code, 0) + 1
        return zaehler

    def kurzbericht(self) -> str:
        """Erzeugt eine kurze Textuebersicht der Parzelle."""
        zeilen = [
            f"Parzelle {self.nummer} ({self.gemeinde}, {self.kanton})",
            f"EGRID:    {self.egrid}",
            f"Flaeche:  {self.flaeche_m2:.0f} m^2",
        ]

        if self.adresse:
            zeilen.append(f"Adresse:  {self.adresse}")

        bauzonen = self.bauzonen()
        if bauzonen:
            zeilen.append("")
            zeilen.append("Bauzone(n):")
            for b in bauzonen:
                zeile = f"  - {b.legende}"
                if b.prozent_anteil is not None:
                    zeile += f" ({b.prozent_anteil:.0f}%, {b.flaeche_m2:.0f} m^2)"
                zeilen.append(zeile)

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
