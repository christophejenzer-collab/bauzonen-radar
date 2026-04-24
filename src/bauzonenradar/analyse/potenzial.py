"""
Potenzialberechnung fuer Schweizer Grundstuecke.

Kombiniert eine Parzelle (mit ihren OEREB-Daten) und ein Baureglement
(mit AZ, GFZo oder Hoehen+GZ) zu einer Potenzialabschaetzung.

Der Berechner unterstuetzt alle drei Bemessungssysteme des Kantons Bern:

  - AZ   (klassische Ausnuetzungsziffer, altes Recht)
  - GFZo (Geschossflaechenziffer oberirdisch, IVHB-konform)
  - hoehen_und_gz (Hoehen + Gruenflaechenziffer, Thun-Stil)

Bei AZ und GFZo rechnet die Formel:
    Zulaessige Geschossflaeche = Parzellenflaeche x Kennzahl

Bei hoehen_und_gz gibt es keine einzelne Kennzahl; die Potenzialaussage
beschraenkt sich dann auf qualitative Hinweise (Volumetrie, freizuhaltende
Flaeche, Ist-Bebauung im Kontext).

Die Ist-Bebauung ist derzeit ein Platzhalter und wird in einer kuenftigen
Version aus swissBUILDINGS3D bezogen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from modelle import Parzelle, Restriction
from baureglement import Baureglement, Bauparameter, BemessungsSystem


class PotenzialStatus(Enum):
    """Ergebnis-Kategorien der Potenzialberechnung."""
    HOCH = "hoch"                            # viel ungenutzte Reserve
    MITTEL = "mittel"                        # moderate Reserve
    GERING = "gering"                        # weitgehend ausgeschoepft
    AUSGESCHOEPFT = "ausgeschoepft"          # vollstaendig bebaut
    NICHT_BERECHENBAR = "nicht_berechenbar"  # keine Kennzahl verfuegbar


@dataclass
class PotenzialErgebnis:
    """Strukturiertes Ergebnis einer Potenzialanalyse."""
    parzellenflaeche_m2: float
    anrechenbare_flaeche_m2: float
    zonen_betrachtet: list[str] = field(default_factory=list)
    verwendetes_system: str | None = None            # "AZ", "GFZo", oder "hoehen_und_gz"
    verwendete_kennzahl: float | None = None         # Der Wert der Kennzahl
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
        zeilen.append(f"Parzellenflaeche:       {self.parzellenflaeche_m2:.0f} m^2")

        if self.anrechenbare_flaeche_m2 != self.parzellenflaeche_m2:
            zeilen.append(
                f"Anrechenbare Flaeche:   {self.anrechenbare_flaeche_m2:.0f} m^2"
            )

        if self.zonen_betrachtet:
            zeilen.append(f"Zone(n):                {', '.join(self.zonen_betrachtet)}")

        if self.verwendetes_system:
            zeilen.append(f"Verwendetes System:     {self.verwendetes_system}")

        if self.verwendete_kennzahl is not None:
            zeilen.append(
                f"Kennzahl:               {self.verwendetes_system} = "
                f"{self.verwendete_kennzahl}"
            )

        if self.theoretisch_zulaessig_m2 is not None:
            zeilen.append(
                f"Theoretisch zulaessig:  {self.theoretisch_zulaessig_m2:.0f} m^2 "
                f"Geschossflaeche"
            )

        if self.geschaetzt_realisiert_m2 is not None:
            kennz = " (PLATZHALTER)" if self.realisiert_ist_platzhalter else ""
            zeilen.append(
                f"Realisiert (geschaetzt):{self.geschaetzt_realisiert_m2:.0f} m^2{kennz}"
            )

        if self.reserve_m2 is not None:
            zeilen.append(f"Reserve:                {self.reserve_m2:.0f} m^2")

        if self.ausschoepfungsgrad_prozent is not None:
            zeilen.append(
                f"Ausschoepfungsgrad:     {self.ausschoepfungsgrad_prozent:.0f}%"
            )

        zeilen.append(f"Status:                 {self.status.value.upper()}")

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
    Erkennt das jeweilige Bemessungssystem (AZ, GFZo, Hoehen+GZ) und
    waehlt die passende Berechnungslogik.
    """

    def berechne(self, parzelle: Parzelle,
                 reglement: Baureglement | None) -> PotenzialErgebnis:
        """
        Fuehrt die Potenzialanalyse durch.

        Ablauf:
          1. Parameter aus Reglement holen (alle betroffenen Zonen)
          2. Ersten Parameter mit berechenbarer Kennzahl auswaehlen
          3. Mit AZ oder GFZo rechnen, oder qualitative Hinweise geben
          4. Warnhinweise zu OEREB-Einschraenkungen anhaengen
        """
        ergebnis = PotenzialErgebnis(
            parzellenflaeche_m2=parzelle.flaeche_m2,
            anrechenbare_flaeche_m2=parzelle.flaeche_m2,
        )

        # Kein Reglement -> nur Parzellen-Infos und Warnhinweise
        if reglement is None:
            ergebnis.bemerkungen.append(
                "Kein Baureglement fuer diese Gemeinde verfuegbar."
            )
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # Parameter aus dem Reglement holen
        parameter_liste = reglement.finde_bauparameter(parzelle)
        if not parameter_liste:
            ergebnis.bemerkungen.append(
                "Keine Zonenparameter gefunden. Zone ist im Reglement "
                "noch nicht erfasst."
            )
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # Zonen und Systeme notieren
        ergebnis.zonen_betrachtet = [
            f"{p.quelle_eintrag} [{p.system.value}]" for p in parameter_liste
        ]

        # Ersten berechenbaren Parameter suchen (GFZo bevorzugt, dann AZ)
        berechenbare = [p for p in parameter_liste if p.ist_berechenbar]

        if not berechenbare:
            # Kein Parameter hat AZ oder GFZo - qualitative Analyse
            self._behandle_nicht_berechenbar(parameter_liste, parzelle, ergebnis)
            return ergebnis

        # Berechnung mit dem ersten berechenbaren Parameter
        parameter = berechenbare[0]
        hauptkennzahl = parameter.hauptkennzahl()

        if hauptkennzahl is None:
            # System ist Hoehen+GZ - keine direkte Kennzahl
            self._behandle_hoehen_und_gz(parameter, parzelle, ergebnis)
            return ergebnis

        # AZ oder GFZo verwenden
        system_code, kennzahl = hauptkennzahl
        ergebnis.verwendetes_system = system_code
        ergebnis.verwendete_kennzahl = kennzahl

        if len(berechenbare) > 1:
            ergebnis.bemerkungen.append(
                f"Mehrere berechenbare Zonen gefunden. Berechnung basiert auf "
                f"'{parameter.quelle_eintrag}'. Bei flaechenmaessiger Teilung "
                f"ist eine gewichtete Berechnung genauer."
            )

        # Berechnung
        ergebnis.theoretisch_zulaessig_m2 = (
            ergebnis.anrechenbare_flaeche_m2 * kennzahl
        )

        # Ist-Bebauung schaetzen
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

        # Hinweis zum Systemwechsel anhaengen
        if parameter.system == BemessungsSystem.DUALITAET:
            ergebnis.bemerkungen.append(
                "Diese Zone steht in einer Uebergangsphase (Dualitaet). "
                "Baugesuche werden nach altem und neuem Recht geprueft - "
                "das Ergebnis ist eine Naeherung."
            )

        # Status ableiten
        ergebnis.status = self._bestimme_status(ergebnis.ausschoepfungsgrad_prozent)

        # Fachliche Hinweise aus dem Reglement
        if parameter.hinweise:
            ergebnis.bemerkungen.append(
                f"Zone '{parameter.quelle_eintrag}': {parameter.hinweise}"
            )

        # Warnhinweise aus OEREB-Einschraenkungen
        ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))

        return ergebnis

    # ----- Spezialfaelle ------------------------------------------------

    @staticmethod
    def _behandle_nicht_berechenbar(parameter_liste: list[Bauparameter],
                                    parzelle: Parzelle,
                                    ergebnis: PotenzialErgebnis) -> None:
        """Fuellt das Ergebnis, wenn keine Zone eine berechenbare Kennzahl hat."""
        ergebnis.bemerkungen.append(
            "In keiner der Zonen ist eine Kennzahl (AZ oder GFZo) zur "
            "Potenzialberechnung hinterlegt."
        )
        for p in parameter_liste:
            if p.hinweise:
                ergebnis.bemerkungen.append(
                    f"Zone '{p.quelle_eintrag}' [{p.system.value}]: {p.hinweise}"
                )
        ergebnis.bemerkungen.extend(
            PotenzialBerechner._sammle_warnhinweise(parzelle)
        )

    @staticmethod
    def _behandle_hoehen_und_gz(parameter: Bauparameter,
                                parzelle: Parzelle,
                                ergebnis: PotenzialErgebnis) -> None:
        """Fuellt das Ergebnis, wenn die Zone ueber Hoehen+GZ gesteuert wird."""
        ergebnis.verwendetes_system = parameter.system.value
        ergebnis.bemerkungen.append(
            f"Zone '{parameter.quelle_eintrag}' wird nicht ueber eine "
            f"Ausnuetzungs- oder Geschossflaechenziffer geregelt. Die "
            f"bauliche Dichte ergibt sich aus Gebaeudehoehen, "
            f"Grenzabstaenden und Gruenflaechenziffer."
        )

        if parameter.max_gebaeudehoehe_m is not None:
            ergebnis.bemerkungen.append(
                f"Maximale Gebaeudehoehe: {parameter.max_gebaeudehoehe_m} m"
            )
        if parameter.max_fassadenhoehe_m is not None:
            ergebnis.bemerkungen.append(
                f"Maximale Fassadenhoehe: {parameter.max_fassadenhoehe_m} m"
            )
        if parameter.gruenflaechenziffer is not None:
            ergebnis.bemerkungen.append(
                f"Gruenflaechenziffer: {parameter.gruenflaechenziffer}"
            )
        if parameter.grenzabstand_gross_m is not None:
            ergebnis.bemerkungen.append(
                f"Grosser Grenzabstand: {parameter.grenzabstand_gross_m} m"
            )

        if parameter.hinweise:
            ergebnis.bemerkungen.append(
                f"Zone '{parameter.quelle_eintrag}': {parameter.hinweise}"
            )

        ergebnis.bemerkungen.extend(
            PotenzialBerechner._sammle_warnhinweise(parzelle)
        )

    # ----- Interne Hilfsmethoden ---------------------------------------

    @staticmethod
    def _schaetze_ist_bebauung(parzelle: Parzelle) -> float:
        """
        Platzhalter fuer die Ist-Bebauung.

        Heuristik: 40% der Parzellenflaeche als grobe Naeherung.
        Wird durch swissBUILDINGS3D-Abfrage ersetzt.
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
                "Baulinien auf der Parzelle - effektive Bauflaeche ist "
                "kleiner als die Gesamtflaeche."
            )

        if parzelle.laufende_aenderungen():
            hinweise.append(
                "LAUFENDE ZONENPLANAENDERUNG - kuenftige Bauvorschriften "
                "koennen abweichen."
            )

        return hinweise
