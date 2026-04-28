"""
Potenzialberechnung fuer Schweizer Grundstuecke.

Kombiniert eine Parzelle (mit ihren OEREB-Daten) und ein Baureglement
zu einer Potenzialabschaetzung.

Drei Bemessungssysteme werden unterstuetzt:
  - AZ            : Klassische Ausnuetzungsziffer
  - GFZo          : Geschossflaechenziffer oberirdisch
  - hoehen_und_gz : Steuerung ueber Hoehen + Gruenflaechenziffer

Spezialeffekte:
  - Arealbonus: Bei grossen Parzellen kann ein zusaetzliches Geschoss
                bewilligt werden (Thun: Schwelle 3000 m^2)
  - Strukturgebiet: Beirat Stadtbild kann Vorgaben aushebeln
                    (Thun-spezifisches Konzept)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from modelle import Parzelle, Restriction
from baureglement import Baureglement, Bauparameter, BemessungsSystem


class PotenzialStatus(Enum):
    HOCH = "hoch"
    MITTEL = "mittel"
    GERING = "gering"
    AUSGESCHOEPFT = "ausgeschoepft"
    NICHT_BERECHENBAR = "nicht_berechenbar"


@dataclass
class PotenzialErgebnis:
    """Strukturiertes Ergebnis einer Potenzialanalyse."""
    parzellenflaeche_m2: float
    anrechenbare_flaeche_m2: float
    zonen_betrachtet: list[str] = field(default_factory=list)
    verwendetes_system: str | None = None
    verwendete_kennzahl: float | None = None
    theoretisch_zulaessig_m2: float | None = None
    geschaetzt_realisiert_m2: float | None = None
    realisiert_ist_platzhalter: bool = True
    reserve_m2: float | None = None
    ausschoepfungsgrad_prozent: float | None = None
    status: PotenzialStatus = PotenzialStatus.NICHT_BERECHENBAR
    bemerkungen: list[str] = field(default_factory=list)
    arealbonus_anwendbar: bool = False

    def textbericht(self) -> str:
        """Lesbare Textausgabe des Ergebnisses."""
        zeilen = ["Potenzialanalyse"]
        zeilen.append("-" * 40)
        zeilen.append(f"Parzellenflaeche:       {self.parzellenflaeche_m2:.0f} m^2")

        if self.anrechenbare_flaeche_m2 != self.parzellenflaeche_m2:
            zeilen.append(f"Anrechenbare Flaeche:   {self.anrechenbare_flaeche_m2:.0f} m^2")

        if self.zonen_betrachtet:
            zeilen.append(f"Zone(n):                {', '.join(self.zonen_betrachtet)}")

        if self.verwendetes_system:
            zeilen.append(f"Verwendetes System:     {self.verwendetes_system}")

        if self.verwendete_kennzahl is not None:
            zeilen.append(f"Kennzahl:               {self.verwendetes_system} = {self.verwendete_kennzahl}")

        if self.theoretisch_zulaessig_m2 is not None:
            zeilen.append(f"Theoretisch zulaessig:  {self.theoretisch_zulaessig_m2:.0f} m^2")

        if self.geschaetzt_realisiert_m2 is not None:
            kennz = " (PLATZHALTER)" if self.realisiert_ist_platzhalter else ""
            zeilen.append(f"Realisiert (geschaetzt):{self.geschaetzt_realisiert_m2:.0f} m^2{kennz}")

        if self.reserve_m2 is not None:
            zeilen.append(f"Reserve:                {self.reserve_m2:.0f} m^2")

        if self.ausschoepfungsgrad_prozent is not None:
            zeilen.append(f"Ausschoepfungsgrad:     {self.ausschoepfungsgrad_prozent:.0f}%")

        zeilen.append(f"Status:                 {self.status.value.upper()}")

        if self.arealbonus_anwendbar:
            zeilen.append("")
            zeilen.append("AREALBONUS MOEGLICH: zusaetzliches Geschoss bewilligungsfaehig")

        if self.bemerkungen:
            zeilen.append("")
            zeilen.append("Bemerkungen:")
            for b in self.bemerkungen:
                zeilen.append(f"  - {b}")

        return "\n".join(zeilen)


class PotenzialBerechner:
    """Berechnet das Bebauungspotenzial einer Parzelle."""

    def berechne(self, parzelle: Parzelle,
                 reglement: Baureglement | None) -> PotenzialErgebnis:
        """Fuehrt die Potenzialanalyse durch."""
        ergebnis = PotenzialErgebnis(
            parzellenflaeche_m2=parzelle.flaeche_m2,
            anrechenbare_flaeche_m2=parzelle.flaeche_m2,
        )

        # Strukturgebiet-Pruefung schon hier - betrifft alle weiteren Schritte
        strukturgebiet_warnung = self._pruefe_strukturgebiet(parzelle)

        # Kein Reglement
        if reglement is None:
            ergebnis.bemerkungen.append("Kein Baureglement fuer diese Gemeinde verfuegbar.")
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.append(strukturgebiet_warnung)
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # Parameter aus Reglement
        parameter_liste = reglement.finde_bauparameter(parzelle)
        if not parameter_liste:
            ergebnis.bemerkungen.append(
                "Keine Zonenparameter gefunden. Zone ist im Reglement noch nicht erfasst."
            )
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.append(strukturgebiet_warnung)
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # Zonen notieren
        ergebnis.zonen_betrachtet = [
            f"{p.quelle_eintrag} [{p.system.value}]" for p in parameter_liste
        ]

        # Berechenbare Parameter finden
        berechenbare = [p for p in parameter_liste if p.ist_berechenbar]

        if not berechenbare:
            self._behandle_nicht_berechenbar(parameter_liste, parzelle, ergebnis)
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
            return ergebnis

        # Ersten berechenbaren Parameter waehlen
        parameter = berechenbare[0]

        # Arealbonus pruefen
        if parameter.hat_arealbonus(parzelle.flaeche_m2):
            ergebnis.arealbonus_anwendbar = True
            ergebnis.bemerkungen.append(
                f"Parzelle ueberschreitet Arealbonus-Schwelle "
                f"({parameter.arealbonus_ab_flaeche_m2:.0f} m^2). "
                f"+{parameter.arealbonus_zusaetzliche_geschosse} Geschoss(e) "
                f"koennten bewilligt werden."
            )

        hauptkennzahl = parameter.hauptkennzahl()

        if hauptkennzahl is None:
            # Hoehen+GZ-System
            self._behandle_hoehen_und_gz(parameter, parzelle, ergebnis)
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
            return ergebnis

        # AZ oder GFZo
        system_code, kennzahl = hauptkennzahl
        ergebnis.verwendetes_system = system_code
        ergebnis.verwendete_kennzahl = kennzahl

        if len(berechenbare) > 1:
            ergebnis.bemerkungen.append(
                f"Mehrere berechenbare Zonen gefunden. Berechnung basiert auf "
                f"'{parameter.quelle_eintrag}'."
            )

        # Berechnung
        ergebnis.theoretisch_zulaessig_m2 = (
            ergebnis.anrechenbare_flaeche_m2 * kennzahl
        )

        ergebnis.geschaetzt_realisiert_m2 = self._schaetze_ist_bebauung(parzelle)
        ergebnis.realisiert_ist_platzhalter = True
        ergebnis.bemerkungen.append(
            "Ist-Bebauung ist derzeit ein Platzhalter. Der echte Wert "
            "kommt in einer kuenftigen Version aus swissBUILDINGS3D."
        )

        ergebnis.reserve_m2 = (
            ergebnis.theoretisch_zulaessig_m2 - ergebnis.geschaetzt_realisiert_m2
        )
        if ergebnis.theoretisch_zulaessig_m2 > 0:
            ergebnis.ausschoepfungsgrad_prozent = (
                ergebnis.geschaetzt_realisiert_m2
                / ergebnis.theoretisch_zulaessig_m2
                * 100
            )

        if parameter.system == BemessungsSystem.DUALITAET:
            ergebnis.bemerkungen.append(
                "Diese Zone steht in einer Uebergangsphase (Dualitaet). "
                "Baugesuche werden nach altem und neuem Recht geprueft."
            )

        ergebnis.status = self._bestimme_status(ergebnis.ausschoepfungsgrad_prozent)

        if parameter.hinweise:
            ergebnis.bemerkungen.append(
                f"Zone '{parameter.quelle_eintrag}': {parameter.hinweise}"
            )

        # Strukturgebiet-Warnung an den Anfang
        if strukturgebiet_warnung:
            ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)

        ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
        return ergebnis

    # ----- Spezialfaelle ------------------------------------------------

    @staticmethod
    def _behandle_nicht_berechenbar(parameter_liste: list[Bauparameter],
                                    parzelle: Parzelle,
                                    ergebnis: PotenzialErgebnis) -> None:
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
        """Fuellt das Ergebnis bei Hoehen+GZ-System (z.B. Thun BR 2022)."""
        ergebnis.verwendetes_system = parameter.system.value

        ergebnis.bemerkungen.append(
            f"Zone '{parameter.quelle_eintrag}' wird ueber Gebaeudemasse "
            f"und Gruenflaechenziffer gesteuert (kein AZ/GFZo)."
        )

        # Hoehen-Werte
        if parameter.max_fassadenhoehe_traufseitig_m is not None:
            ergebnis.bemerkungen.append(
                f"Fassadenhoehe traufseitig (Schraegdach): "
                f"max. {parameter.max_fassadenhoehe_traufseitig_m} m"
            )
        if parameter.max_fassadenhoehe_giebelseitig_m is not None:
            ergebnis.bemerkungen.append(
                f"Fassadenhoehe giebelseitig (Schraegdach): "
                f"max. {parameter.max_fassadenhoehe_giebelseitig_m} m"
            )
        if parameter.max_fassadenhoehe_anderes_dach_m is not None:
            ergebnis.bemerkungen.append(
                f"Fassadenhoehe (Flachdach o.ae.): "
                f"max. {parameter.max_fassadenhoehe_anderes_dach_m} m"
            )

        # Gebaeudegeometrie
        if parameter.max_gebaeudelaenge_m is not None:
            ergebnis.bemerkungen.append(
                f"Maximale Gebaeudelaenge: {parameter.max_gebaeudelaenge_m} m"
            )
        if parameter.grenzabstand_klein_m is not None:
            ergebnis.bemerkungen.append(
                f"Kleiner Grenzabstand: {parameter.grenzabstand_klein_m} m"
            )
        if parameter.grenzabstand_gross_m is not None:
            ergebnis.bemerkungen.append(
                f"Grosser Grenzabstand: {parameter.grenzabstand_gross_m} m"
            )

        # Gruenflaechen
        if parameter.gruenflaechenziffer is not None:
            min_gruen_m2 = parzelle.flaeche_m2 * parameter.gruenflaechenziffer
            ergebnis.bemerkungen.append(
                f"Gruenflaechenziffer: {parameter.gruenflaechenziffer} "
                f"(min. {min_gruen_m2:.0f} m^2 unversiegelt zu halten)"
            )

        if parameter.hinweise:
            ergebnis.bemerkungen.append(
                f"Zone '{parameter.quelle_eintrag}': {parameter.hinweise}"
            )

        ergebnis.bemerkungen.extend(
            PotenzialBerechner._sammle_warnhinweise(parzelle)
        )

    # ----- Strukturgebiet-Erkennung ------------------------------------

    @staticmethod
    def _pruefe_strukturgebiet(parzelle: Parzelle) -> str | None:
        """
        Prueft, ob die Parzelle im Strukturgebiet liegt (Thun-Spezial).
        Strukturgebiet liegt typischerweise als 'FlaecheAndere' oder
        'Ueberlagerung' vor.
        """
        # Suche in allen Restrictions nach 'Strukturgebiet'
        for r in parzelle.restrictions:
            if r.legende and "strukturgebiet" in r.legende.lower():
                return (
                    "STRUKTURGEBIET-UEBERLAGERUNG: Beirat Stadtbild der Stadt "
                    "Thun kann gestalterische Vorgaben machen, die das "
                    "Baureglement teilweise aushebeln. Konkrete Bebauung "
                    "muss mit der Stadt abgestimmt werden."
                )
        return None

    # ----- Hilfsmethoden -----------------------------------------------

    @staticmethod
    def _schaetze_ist_bebauung(parzelle: Parzelle) -> float:
        """Platzhalter: 40% der Parzellenflaeche."""
        return parzelle.flaeche_m2 * 0.4

    @staticmethod
    def _bestimme_status(ausschoepfung: float | None) -> PotenzialStatus:
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
        """Warnhinweise zu Ueberlagerungen, Gefahrengebieten, Baulinien."""
        hinweise: list[str] = []

        if parzelle.ueberlagerungen():
            hinweise.append(
                "Parzelle hat Ueberlagerungen (z.B. Ortsbildschutz). "
                "Theoretisches Potenzial in der Praxis stark eingeschraenkt."
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
