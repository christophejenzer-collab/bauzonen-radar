"""
Potenzialberechnung fuer Schweizer Grundstuecke.

Kombiniert eine Parzelle (mit ihren OEREB-Daten) und ein Baureglement
(mit den Ausnuetzungsziffern) zu einer Potenzialabschaetzung.

Kernformel:
    Theoretisch zulaessige Geschossflaeche = Parzellenflaeche x AZ

Die Ist-Bebauung kommt spaeter aus swissBUILDINGS3D. Bis dahin wird
sie als Platzhalter behandelt und klar als solche markiert.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from modelle import Parzelle, Restriction
from baureglement import Baureglement, Bauparameter


class PotenzialStatus(Enum):
    """Ergebnis-Kategorien der Potenzialberechnung."""
    HOCH = "hoch"                    # viel ungenutzte Reserve
    MITTEL = "mittel"                # moderate Reserve
    GERING = "gering"                # weitgehend ausgeschoepft
    AUSGESCHOEPFT = "ausgeschoepft"  # vollstaendig bebaut
    NICHT_BERECHENBAR = "nicht_berechenbar"  # AZ oder Istwerte fehlen


@dataclass
class PotenzialErgebnis:
    """Strukturiertes Ergebnis einer Potenzialanalyse fuer eine Parzelle."""
    parzellenflaeche_m2: float
    anrechenbare_flaeche_m2: float
    zonen_betrachtet: list[str] = field(default_factory=list)
    ausnuetzungsziffer: float | None = None
    theoretisch_zulaessig_m2: float | None = None
    geschaetzt_realisiert_m2: float | None = None
    realisiert_ist_platzhalter: bool = True
    reserve_m2: float | None = None
    ausschoepfungsgrad_prozent: float | None = None
    status: PotenzialStatus = PotenzialStatus.NICHT_BERECHENBAR
    bemerkungen: list[str] = field(default_factory=list)

    def textbericht(self) -> str:
        """Lesbare Textausgabe des Ergebnisses."""
        zeilen = ["Potenzialanalyse"]
        zeilen.append("-" * 40)
        zeilen.append(f"Parzellenflaeche:      {self.parzellenflaeche_m2:.0f} m^2")

        if self.anrechenbare_flaeche_m2 != self.parzellenflaeche_m2:
            zeilen.append(
                f"Anrechenbare Flaeche:  {self.anrechenbare_flaeche_m2:.0f} m^2"
            )

        if self.zonen_betrachtet:
            zeilen.append(f"Zone(n):               {', '.join(self.zonen_betrachtet)}")

        if self.ausnuetzungsziffer is not None:
            zeilen.append(f"Ausnuetzungsziffer:    {self.ausnuetzungsziffer}")

        if self.theoretisch_zulaessig_m2 is not None:
            zeilen.append(
                f"Theoretisch zulaessig: {self.theoretisch_zulaessig_m2:.0f} m^2 Geschossflaeche"
            )

        if self.geschaetzt_realisiert_m2 is not None:
            kennz = " (PLATZHALTER)" if self.realisiert_ist_platzhalter else ""
            zeilen.append(
                f"Realisiert (geschaetzt):{self.geschaetzt_realisiert_m2:.0f} m^2{kennz}"
            )

        if self.reserve_m2 is not None:
            zeilen.append(f"Reserve:               {self.reserve_m2:.0f} m^2")

        if self.ausschoepfungsgrad_prozent is not None:
            zeilen.append(
                f"Ausschoepfungsgrad:    {self.ausschoepfungsgrad_prozent:.0f}%"
            )

        zeilen.append(f"Status:                {self.status.value.upper()}")

        if self.bemerkungen:
            zeilen.append("")
            zeilen.append("Bemerkungen:")
            for b in self.bemerkungen:
                zeilen.append(f"  - {b}")

        return "\n".join(zeilen)


class PotenzialBerechner:
    """
    Berechnet das Bebauungspotenzial einer Parzelle.

    Arbeitet mit einer Parzelle (OEREB-Daten) und einem Baureglement.
    Falls fuer eine Zone keine AZ hinterlegt ist, gibt der Berechner
    ein Ergebnis mit Status NICHT_BERECHENBAR zurueck - kein Crash.
    """

    def berechne(self, parzelle: Parzelle,
                 reglement: Baureglement | None) -> PotenzialErgebnis:
        """
        Fuehrt die Potenzialanalyse durch.

        Ablauf:
          1. Parameter aus dem Reglement holen
          2. Erste gefundene AZ verwenden (oder: None)
          3. Theoretisch zulaessige Geschossflaeche berechnen
          4. Ist-Bebauung schaetzen (Platzhalter)
          5. Reserve und Ausschoepfungsgrad ableiten
          6. Status kategorisieren
        """
        ergebnis = PotenzialErgebnis(
            parzellenflaeche_m2=parzelle.flaeche_m2,
            anrechenbare_flaeche_m2=parzelle.flaeche_m2,
        )

        # Kein Reglement -> direkt mit Grund zurueckgeben
        if reglement is None:
            ergebnis.bemerkungen.append(
                "Kein Baureglement fuer diese Gemeinde verfuegbar."
            )
            return ergebnis

        # Parameter aus dem Reglement holen
        parameter_liste = reglement.finde_bauparameter(parzelle)
        if not parameter_liste:
            ergebnis.bemerkungen.append(
                "Keine Zonenparameter gefunden. Zone ist im Reglement "
                "noch nicht erfasst."
            )
            return ergebnis

        # Alle betrachteten Zonen notieren
        ergebnis.zonen_betrachtet = [p.quelle_eintrag for p in parameter_liste]

        # Die erste Parameter-Entsprechung mit gesetzter AZ verwenden
        parameter_mit_az = [p for p in parameter_liste
                            if p.ausnuetzungsziffer is not None]

        if not parameter_mit_az:
            ergebnis.bemerkungen.append(
                "Ausnuetzungsziffer nicht im Reglement hinterlegt. "
                "Potenzial kann nicht berechnet werden."
            )
            ergebnis.bemerkungen.extend(
                f"Zone '{p.quelle_eintrag}': {p.hinweise}"
                for p in parameter_liste if p.hinweise
            )
            # Auch ohne AZ sind die Warnhinweise wertvoll
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # Wenn mehrere Zonen mit AZ, nehmen wir die erste.
        # Verbesserungsmoeglichkeit: gewichteter Durchschnitt nach Flaechenanteil.
        parameter = parameter_mit_az[0]
        ergebnis.ausnuetzungsziffer = parameter.ausnuetzungsziffer

        if len(parameter_mit_az) > 1:
            ergebnis.bemerkungen.append(
                f"Mehrere Zonen mit AZ gefunden. Berechnung basiert auf "
                f"'{parameter.quelle_eintrag}'. Genauere Analyse moeglich."
            )

        # Berechnung
        ergebnis.theoretisch_zulaessig_m2 = (
            ergebnis.anrechenbare_flaeche_m2 * parameter.ausnuetzungsziffer
        )

        # Ist-Bebauung schaetzen - derzeit Platzhalter
        ergebnis.geschaetzt_realisiert_m2 = self._schaetze_ist_bebauung(parzelle)
        ergebnis.realisiert_ist_platzhalter = True
        ergebnis.bemerkungen.append(
            "Ist-Bebauung ist derzeit ein Platzhalter. Der echte Wert "
            "kommt in einer kuenftigen Version aus swissBUILDINGS3D."
        )

        # Reserve und Ausschoepfungsgrad
        ergebnis.reserve_m2 = (
            ergebnis.theoretisch_zulaessig_m2 - ergebnis.geschaetzt_realisiert_m2
        )
        if ergebnis.theoretisch_zulaessig_m2 > 0:
            ergebnis.ausschoepfungsgrad_prozent = (
                ergebnis.geschaetzt_realisiert_m2
                / ergebnis.theoretisch_zulaessig_m2
                * 100
            )

        # Status ableiten
        ergebnis.status = self._bestimme_status(ergebnis.ausschoepfungsgrad_prozent)

        # Warnhinweise bei relevanten Ueberlagerungen
        warnhinweise = self._sammle_warnhinweise(parzelle)
        ergebnis.bemerkungen.extend(warnhinweise)

        return ergebnis

    # ----- Interne Hilfsmethoden -----

    @staticmethod
    def _schaetze_ist_bebauung(parzelle: Parzelle) -> float:
        """
        Platzhalter fuer die Ist-Bebauung.

        Derzeit eine grobe Heuristik: wir nehmen an, dass die Parzelle
        zu 40% bebaut ist (typischer Wert fuer Schweizer Wohnzonen).
        Wird spaeter durch swissBUILDINGS3D-Abfrage ersetzt.
        """
        return parzelle.flaeche_m2 * 0.4

    @staticmethod
    def _bestimme_status(ausschoepfung: float | None) -> PotenzialStatus:
        """Kategorisiert den Ausschoepfungsgrad in Stufen."""
        if ausschoepfung is None:
            return PotenzialStatus.NICHT_BERECHENBAR
        if ausschoepfung >= 95:
            return PotenzialStatus.AUSGESCHOEPFT
        if ausschoepfung >= 75:
            return PotenzialStatus.GERING
        if ausschoepfung >= 40:
            return PotenzialStatus.MITTEL
        return PotenzialStatus.HOCH

    @staticmethod
    def _sammle_warnhinweise(parzelle: Parzelle) -> list[str]:
        """
        Sammelt relevante Warnhinweise zu Ueberlagerungen, Gefahrengebieten
        und Baulinien, die das theoretische Potenzial einschraenken.
        """
        hinweise: list[str] = []

        if parzelle.ueberlagerungen():
            hinweise.append(
                "Parzelle hat Ueberlagerungen (z.B. Ortsbildschutz). "
                "Das theoretische Potenzial kann in der Praxis stark "
                "eingeschraenkt sein."
            )

        gefahren = parzelle.gefahrengebiete()
        if gefahren:
            hinweise.append(
                f"Parzelle liegt in {len(gefahren)} Naturgefahrengebiet(en). "
                "Bebaubarkeit muss im Detail geprueft werden."
            )

        if parzelle.linien():
            hinweise.append(
                "Baulinien auf der Parzelle - effektive Bauflaeche ist kleiner "
                "als die Gesamtflaeche."
            )

        if parzelle.laufende_aenderungen():
            hinweise.append(
                "LAUFENDE ZONENPLANAENDERUNG - kuenftige Bauvorschriften "
                "koennen abweichen."
            )

        return hinweise
