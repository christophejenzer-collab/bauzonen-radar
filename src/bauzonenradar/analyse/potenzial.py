"""
Potenzialberechnung fuer Schweizer Grundstuecke.

Kombiniert eine Parzelle (mit ihren OEREB-Daten) und ein Baureglement
zu einer Potenzialabschaetzung.

Drei Datenqualitaeten werden klar unterschieden:
  - VERBINDLICH    : AZ oder GFZo vorhanden, exakte Berechnung
  - GROBSCHAETZUNG : Hoehen-System, Berechnung mit konservativen Annahmen
  - NICHT_MOEGLICH : Keine Werte verfuegbar

Drei Bemessungssysteme werden unterstuetzt:
  - AZ            : Klassische Ausnuetzungsziffer
                    Berechnung: Flaeche x AZ
  - GFZo          : Geschossflaechenziffer oberirdisch
                    Berechnung: Flaeche x GFZo
  - hoehen_und_gz : Steuerung ueber Hoehen + Geometrie + (optional GZ)
                    GROBSCHAETZUNG: max. Gebaeudegrundflaeche x Vollgeschosse
                    + anteiliges Dachgeschoss

Empfehlung-System (visuell):
  - Bauland-Reserve in Prozent als zentrale Lagebeurteilung
  - ASCII-Fortschrittsbalken zur sofortigen visuellen Erfassung
  - Bei Schaetzungen klar als "geschaetzt" markiert
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from modelle import Parzelle, Restriction
from baureglement import Baureglement, Bauparameter, BemessungsSystem


# Default-Annahmen fuer die Schaetz-Berechnung im Hoehen-System
DEFAULT_GEBAEUDEBREITE_M = 12.0
DACHGESCHOSS_ANRECHNUNG_SCHRAEGDACH = 0.6
DACHGESCHOSS_ANRECHNUNG_FLACHDACH = 0.0

# Visualisierung
BALKEN_BREITE = 20  # Anzahl Zeichen im ASCII-Fortschrittsbalken


class PotenzialStatus(Enum):
    HOCH = "hoch"
    MITTEL = "mittel"
    GERING = "gering"
    AUSGESCHOEPFT = "ausgeschoepft"
    NICHT_BERECHENBAR = "nicht_berechenbar"
    SCHAETZWERT = "schaetzwert"


class Datenqualitaet(Enum):
    """Qualitaetsstufen der Potenzialberechnung."""
    VERBINDLICH = "verbindlich"
    GROBSCHAETZUNG = "grobschaetzung"
    NICHT_MOEGLICH = "nicht_moeglich"


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
    reserve_prozent: float | None = None
    ausschoepfungsgrad_prozent: float | None = None
    datenqualitaet: Datenqualitaet = Datenqualitaet.NICHT_MOEGLICH
    status: PotenzialStatus = PotenzialStatus.NICHT_BERECHENBAR
    bemerkungen: list[str] = field(default_factory=list)
    arealbonus_anwendbar: bool = False

    def textbericht(self) -> str:
        """Lesbare Textausgabe des Ergebnisses mit klarer Datenqualitaets-Markierung."""
        zeilen: list[str] = []

        # Header mit Datenqualitaet
        if self.datenqualitaet == Datenqualitaet.VERBINDLICH:
            zeilen.append("Potenzialanalyse - Datenqualitaet: VERBINDLICH")
        elif self.datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
            zeilen.append("Potenzialanalyse - Datenqualitaet: GROBSCHAETZUNG")
            zeilen.append("!!! Werte sind konservativ geschaetzt - keine Investitionsentscheidung darauf basieren !!!")
        else:
            zeilen.append("Potenzialanalyse - Datenqualitaet: KEINE BERECHNUNG MOEGLICH")

        zeilen.append("-" * 70)
        zeilen.append(f"Parzellenflaeche:       {self.parzellenflaeche_m2:.0f} m^2")

        if self.anrechenbare_flaeche_m2 != self.parzellenflaeche_m2:
            zeilen.append(f"Anrechenbare Flaeche:   {self.anrechenbare_flaeche_m2:.0f} m^2")

        if self.zonen_betrachtet:
            zeilen.append(f"Zone(n):                {', '.join(self.zonen_betrachtet)}")

        if self.verwendetes_system:
            zeilen.append(f"Verwendetes System:     {self.verwendetes_system}")

        if self.verwendete_kennzahl is not None:
            zeilen.append(
                f"Kennzahl:               {self.verwendetes_system} = {self.verwendete_kennzahl}"
            )

        # Theoretischer Wert mit deutlicher Markierung
        if self.theoretisch_zulaessig_m2 is not None:
            if self.datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
                zeilen.append(
                    f"GROBSCHAETZUNG zulaessig: ca. {self.theoretisch_zulaessig_m2:.0f} m^2"
                )
            else:
                zeilen.append(
                    f"Theoretisch zulaessig:  {self.theoretisch_zulaessig_m2:.0f} m^2"
                )

        if self.geschaetzt_realisiert_m2 is not None:
            kennz = " (PLATZHALTER)" if self.realisiert_ist_platzhalter else ""
            if self.datenqualitaet == Datenqualitaet.VERBINDLICH:
                zeilen.append(
                    f"Realisiert (geschaetzt):{self.geschaetzt_realisiert_m2:.0f} m^2{kennz}"
                )

        # Reserve und Ausschoepfung nur bei verbindlicher Berechnung
        if self.datenqualitaet == Datenqualitaet.VERBINDLICH:
            if self.reserve_m2 is not None:
                zeilen.append(f"Reserve:                {self.reserve_m2:.0f} m^2")
            if self.ausschoepfungsgrad_prozent is not None:
                zeilen.append(f"Ausschoepfungsgrad:     {self.ausschoepfungsgrad_prozent:.0f}%")

        # Status mit Schaetzwert-Variante
        if self.datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
            zeilen.append("Status:                 SCHAETZWERT - keine Investitionsentscheidung darauf basieren")
        else:
            zeilen.append(f"Status:                 {self.status.value.upper()}")

        # ===== EMPFEHLUNG mit visuellem Balken =====
        empfehlung_block = self._formatiere_empfehlung()
        if empfehlung_block:
            zeilen.append("")
            zeilen.extend(empfehlung_block)

        if self.arealbonus_anwendbar:
            zeilen.append("")
            zeilen.append("AREALBONUS MOEGLICH: zusaetzliches Geschoss bewilligungsfaehig")

        if self.bemerkungen:
            zeilen.append("")
            zeilen.append("Bemerkungen:")
            for b in self.bemerkungen:
                zeilen.append(f"  - {b}")

        return "\n".join(zeilen)

    def _formatiere_empfehlung(self) -> list[str]:
        """Erstellt den Empfehlungs-Block mit Reserve-Prozent und Balken."""
        if self.ausschoepfungsgrad_prozent is None:
            return []

        zeilen = []
        zeilen.append("=" * 70)

        # Header je nach Datenqualitaet
        if self.datenqualitaet == Datenqualitaet.VERBINDLICH:
            zeilen.append("EMPFEHLUNG (verbindliche Berechnung)")
        else:
            zeilen.append("EMPFEHLUNG (Grobschaetzung - nur als Orientierung)")
        zeilen.append("=" * 70)

        # Ehrliche Anzeige: bei Ueber-100% wird das gezeigt mit Warnung
        ausschoepfung_echt = max(0.0, self.ausschoepfungsgrad_prozent)
        ueberzeichnet = ausschoepfung_echt > 100.0
        # Fuer den Balken: auf 100 deckeln, damit er nicht ueberlaeuft
        ausschoepfung = min(100.0, ausschoepfung_echt)
        reserve = max(0.0, 100.0 - ausschoepfung)
        if self.reserve_prozent is not None:
            reserve = max(0.0, min(100.0, self.reserve_prozent))

        # Balken Ausschoepfung (ehrlich, mit Warnung wenn >100%)
        balken_ausschoepfung = self._zeichne_balken(ausschoepfung)
        if ueberzeichnet:
            zeilen.append(
                f"  Ausschoepfung:    {balken_ausschoepfung} {ausschoepfung_echt:5.1f}% (!! Ist > Soll - Schaetzung versagt)"
            )
        else:
            zeilen.append(
                f"  Ausschoepfung:    {balken_ausschoepfung} {ausschoepfung:5.1f}%"
            )

        # Balken Reserve
        balken_reserve = self._zeichne_balken(reserve)
        zeilen.append(
            f"  Bauland-Reserve: {balken_reserve} {reserve:5.1f}%"
        )

        # Lagebeurteilung
        zeilen.append("")
        beurteilung = self._lagebeurteilung(reserve)
        if self.datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
            zeilen.append(f"  -> {beurteilung} (geschaetzt)")
        else:
            zeilen.append(f"  -> {beurteilung}")

        zeilen.append("=" * 70)
        return zeilen

    @staticmethod
    def _zeichne_balken(prozent: float) -> str:
        """Zeichnet einen ASCII-Fortschrittsbalken.

        Beispiel: 80% -> '[################----]'
        """
        anzahl_voll = int(round(prozent / 100.0 * BALKEN_BREITE))
        anzahl_leer = BALKEN_BREITE - anzahl_voll
        return "[" + "#" * anzahl_voll + "-" * anzahl_leer + "]"

    @staticmethod
    def _lagebeurteilung(reserve_prozent: float) -> str:
        """Verbale Lagebeurteilung anhand der Bauland-Reserve."""
        if reserve_prozent >= 60:
            return "HOHES Verdichtungs-Potenzial - attraktive Bauland-Reserve"
        if reserve_prozent >= 30:
            return "MITTLERES Verdichtungs-Potenzial - lohnt Detailpruefung"
        if reserve_prozent >= 10:
            return "GERINGES Verdichtungs-Potenzial - primaer Bestandsoptimierung"
        return "PRAKTISCH AUSGESCHOEPFT - kein nennenswertes Verdichtungs-Potenzial"


class PotenzialBerechner:
    """Berechnet das Bebauungspotenzial einer Parzelle."""

    def berechne(self, parzelle: Parzelle,
                 reglement: Baureglement | None,
                 bkp_quelle=None) -> PotenzialErgebnis:
        """Fuehrt die Potenzialanalyse durch.

        Args:
            parzelle: OEREB-Parzelle mit Geometrie und Restrictions.
            reglement: Geladenes Baureglement der Gemeinde, oder None.
            bkp_quelle: Optionale BernBkpQuelle. Wenn vorhanden, werden
                fuer Bern die parzellenscharfen BKP-Daten geholt und in
                die Bauparameter eingespeist (echte Gebaeudelaenge,
                Bauweise statt Default-Annahmen).
        """
        ergebnis = PotenzialErgebnis(
            parzellenflaeche_m2=parzelle.flaeche_m2,
            anrechenbare_flaeche_m2=parzelle.flaeche_m2,
        )

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
            # Wenn BKP-Daten verfuegbar sind, sind die Codes potenziell
            # neu fuer das Reglement - geben einen konkreten Hinweis
            bkp_hinweis = self._bkp_zone_hinweis(parzelle, bkp_quelle)
            if bkp_hinweis:
                ergebnis.bemerkungen.append(
                    "ZONE IM REGLEMENT NICHT ERFASST: " + bkp_hinweis
                )
            else:
                ergebnis.bemerkungen.append(
                    "ZONE IM REGLEMENT NICHT ERFASST: Die OEREB-Auskunft "
                    "liefert eine Bauklasse oder Nutzungszone, die in der "
                    "JSON-Datei der Gemeinde noch nicht erfasst ist. "
                    "Pruefen Sie die OEREB-Bezeichnung und ergaenzen Sie "
                    "die Zone in der Reglement-JSON."
                )
            ergebnis.datenqualitaet = Datenqualitaet.NICHT_MOEGLICH
            ergebnis.status = PotenzialStatus.NICHT_BERECHENBAR
            ergebnis.bemerkungen.append(
                "EMPFEHLUNG: Direkter Kontakt mit der Bauverwaltung der "
                "Gemeinde. Bei Sonderzonen (UeO/UeP) gelten projekt"
                "spezifische Vorschriften statt der Standard-Bauordnung."
            )
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.append(strukturgebiet_warnung)
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # BKP-Anreicherung fuer Stadt Bern
        if bkp_quelle is not None:
            parameter_liste = self._reichere_mit_bkp_an(
                parameter_liste, parzelle, bkp_quelle, ergebnis
            )

        # Zonen notieren
        ergebnis.zonen_betrachtet = [
            f"{p.quelle_eintrag} [{p.system.value}]" for p in parameter_liste
        ]

        # NICHT_MOEGLICH: Zone gibt explizit zu erkennen, dass keine
        # quantitative Berechnung sinnvoll ist (z.B. Altstadt, Schutzzonen)
        nicht_moeglich = [p for p in parameter_liste
                          if p.system == BemessungsSystem.NICHT_MOEGLICH]
        if nicht_moeglich and len(nicht_moeglich) == len(parameter_liste):
            self._behandle_nicht_moeglich(nicht_moeglich, parzelle, ergebnis)
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
            return ergebnis

        # Berechenbare Parameter finden (NICHT_MOEGLICH ausgeschlossen)
        berechenbare = [p for p in parameter_liste
                        if p.ist_berechenbar
                        and p.system != BemessungsSystem.NICHT_MOEGLICH]

        if not berechenbare:
            self._behandle_nicht_berechenbar(parameter_liste, parzelle, ergebnis)
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
            return ergebnis

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

        # Direkte Kennzahl (AZ/GFZo)?
        hauptkennzahl = parameter.hauptkennzahl()

        if hauptkennzahl is None:
            # Hoehen-System mit GROBSCHAETZUNG
            self._behandle_hoehen_und_gz(parameter, parzelle, ergebnis)
            if strukturgebiet_warnung:
                ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
            ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
            return ergebnis

        # AZ oder GFZo - VERBINDLICHE Berechnung
        self._behandle_verbindliche_berechnung(
            parameter, hauptkennzahl, parzelle, ergebnis, berechenbare
        )

        if strukturgebiet_warnung:
            ergebnis.bemerkungen.insert(0, strukturgebiet_warnung)
        ergebnis.bemerkungen.extend(self._sammle_warnhinweise(parzelle))
        return ergebnis

    # ----- BKP-Anreicherung (Stadt Bern) --------------------------------

    @staticmethod
    def _bkp_zone_hinweis(parzelle: Parzelle, bkp_quelle) -> str | None:
        """Erstellt einen Text, der die im BKP gefundenen Codes nennt.

        Wird bei 'Zone im Reglement nicht erfasst' verwendet, um dem
        Benutzer konkret zu sagen welche Codes ergaenzt werden muessten.
        """
        if bkp_quelle is None:
            return None

        # Versuche, eine LV95-Koordinate aus der Parzelle zu bekommen
        koordinate = None
        for feldname in ("koordinate_lv95", "koordinaten", "lv95"):
            if hasattr(parzelle, feldname):
                wert = getattr(parzelle, feldname)
                if wert and len(wert) == 2:
                    koordinate = (float(wert[0]), float(wert[1]))
                    break
        if koordinate is None:
            return None

        try:
            auskunft = bkp_quelle.hole_auskunft(koordinate[0], koordinate[1])
        except Exception:
            return None

        if not auskunft.gefunden:
            return None

        teile = []
        if auskunft.grundzone:
            g = auskunft.grundzone
            teile.append(
                f"Der Bauklassenplan liefert Bauklasse '{g.bauklasse_kuerzel}' "
                f"({g.bauklasse_beschrieb}) und Nutzungszone "
                f"'{g.nutzungszone_kuerzel}' ({g.nutzungszone_beschrieb})."
            )

        teile.append(
            "Die Bezeichnung aus der OEREB-Auskunft passt jedoch zu keinem "
            "Eintrag im Reglement. Moegliche Ursachen: (1) Die Zone ist eine "
            "Sonderzone mit eigener Ueberbauungsordnung (UeO), oder (2) das "
            "Reglement-JSON sollte um diesen Eintrag ergaenzt werden."
        )
        return " ".join(teile)

    def _reichere_mit_bkp_an(self, parameter_liste: list[Bauparameter],
                             parzelle: Parzelle,
                             bkp_quelle,
                             ergebnis: PotenzialErgebnis) -> list[Bauparameter]:
        """Reichert Bauparameter mit parzellenscharfen BKP-Daten an.

        Holt fuer die Parzellen-Koordinate die BKP-Auskunft und ergaenzt
        Gebaeudelaenge/Bauweise in den Parametern. Falls die Parzelle
        keine Koordinate hat oder die BKP-Anfrage fehlschlaegt, bleibt
        die Liste unveraendert.
        """
        # Versuche, eine LV95-Koordinate aus der Parzelle zu bekommen
        koordinate = None
        for feldname in ("koordinate_lv95", "koordinaten", "lv95"):
            if hasattr(parzelle, feldname):
                wert = getattr(parzelle, feldname)
                if wert and len(wert) == 2:
                    koordinate = (float(wert[0]), float(wert[1]))
                    break

        if koordinate is None:
            return parameter_liste

        try:
            auskunft = bkp_quelle.hole_auskunft(koordinate[0], koordinate[1])
        except Exception as fehler:
            ergebnis.bemerkungen.append(
                f"BKP-Anfrage fehlgeschlagen: {fehler}. "
                f"Berechnung mit Default-Werten."
            )
            return parameter_liste

        if not auskunft.gefunden:
            return parameter_liste

        # Reichere alle Parameter mit den BKP-Daten an
        angereichert = [p.mit_bkp_daten(auskunft) for p in parameter_liste]

        if auskunft.bauweise:
            b = auskunft.bauweise
            laenge = ("unbeschr." if b.gebaeudelaenge_unbeschraenkt
                      else f"{b.gebaeudelaenge} m")
            tiefe = ("unbeschr." if b.gebaeudetiefe_unbeschraenkt
                     else f"{b.gebaeudetiefe} m")
            ergebnis.bemerkungen.append(
                f"BKP-Daten Stadt Bern uebernommen: Bauweise "
                f"'{b.bauweise_beschrieb}', Gebaeudelaenge {laenge}, "
                f"Gebaeudetiefe {tiefe} (parzellenscharf aus Bauklassenplan)."
            )

        return angereichert

    # ----- NICHT_MOEGLICH-Pfad -----------------------------------------

    @staticmethod
    def _behandle_nicht_moeglich(parameter_liste: list[Bauparameter],
                                 parzelle: Parzelle,
                                 ergebnis: PotenzialErgebnis) -> None:
        """Wenn die Zone explizit als 'nicht_moeglich' markiert ist.

        Beispiele: Altstadt-Zonen (UNESCO-Schutz), Schutzzonen, Zonen mit
        Planungspflicht ohne UeO. Hier ist eine quantitative
        Potenzialberechnung nicht sinnvoll - die Aussage muss klar sein:
        'Keine Berechnung moeglich, individuelle Pruefung noetig'.
        """
        ergebnis.datenqualitaet = Datenqualitaet.NICHT_MOEGLICH
        ergebnis.verwendetes_system = "Spezialregime (keine Standard-Berechnung)"
        ergebnis.status = PotenzialStatus.NICHT_BERECHENBAR

        ergebnis.bemerkungen.append(
            "QUANTITATIVE POTENZIALBERECHNUNG NICHT MOEGLICH:"
        )
        ergebnis.bemerkungen.append(
            "Diese Zone unterliegt einem Spezialregime (z.B. UNESCO-Schutz, "
            "Altstadt, Schutzzone, Planungspflicht). Eine Standard-Berechnung "
            "anhand von AZ/GFZo oder Hoehenmassen waere irrefuehrend."
        )

        for p in parameter_liste:
            if p.hinweise:
                ergebnis.bemerkungen.append("")
                ergebnis.bemerkungen.append(
                    f"Zone '{p.quelle_eintrag}': {p.hinweise}"
                )
            if p.rechtsgrundlage:
                ergebnis.bemerkungen.append(
                    f"  Rechtsgrundlage: {p.rechtsgrundlage}"
                )

        ergebnis.bemerkungen.append("")
        ergebnis.bemerkungen.append(
            "EMPFEHLUNG: Direkter Kontakt mit Bauverwaltung und ggf. "
            "Denkmalpflege der Gemeinde. Vor jedem Bauvorhaben ist eine "
            "individuelle Vorabklaerung noetig."
        )

        ergebnis.bemerkungen.extend(
            PotenzialBerechner._sammle_warnhinweise(parzelle)
        )

    # ----- Verbindliche Berechnung (AZ/GFZo) ----------------------------

    def _behandle_verbindliche_berechnung(self, parameter: Bauparameter,
                                          hauptkennzahl: tuple[str, float],
                                          parzelle: Parzelle,
                                          ergebnis: PotenzialErgebnis,
                                          berechenbare: list[Bauparameter]) -> None:
        """Echte m^2-Berechnung mit AZ oder GFZo."""
        system_code, kennzahl = hauptkennzahl
        ergebnis.verwendetes_system = system_code
        ergebnis.verwendete_kennzahl = kennzahl
        ergebnis.datenqualitaet = Datenqualitaet.VERBINDLICH

        if len(berechenbare) > 1:
            ergebnis.bemerkungen.append(
                f"Mehrere berechenbare Zonen gefunden. Berechnung basiert auf "
                f"'{parameter.quelle_eintrag}'."
            )

        ergebnis.theoretisch_zulaessig_m2 = (
            ergebnis.anrechenbare_flaeche_m2 * kennzahl
        )

        ergebnis.geschaetzt_realisiert_m2 = self._schaetze_ist_bebauung(parzelle)
        ergebnis.realisiert_ist_platzhalter = True
        ergebnis.bemerkungen.append(
            "Ist-Bebauung ist derzeit ein Platzhalter (25% der Parzelle). "
            "Der echte Wert kommt in einer kuenftigen Version aus swissBUILDINGS3D."
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
            ergebnis.reserve_prozent = 100.0 - ergebnis.ausschoepfungsgrad_prozent

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

    # ----- Spezialfaelle ------------------------------------------------

    @staticmethod
    def _behandle_nicht_berechenbar(parameter_liste: list[Bauparameter],
                                    parzelle: Parzelle,
                                    ergebnis: PotenzialErgebnis) -> None:
        """Wenn KEIN einziger Wert hinterlegt ist (alles None)."""
        ergebnis.datenqualitaet = Datenqualitaet.NICHT_MOEGLICH
        ergebnis.bemerkungen.append(
            "DATEN NICHT VERFUEGBAR: In keiner der Zonen ist eine Kennzahl "
            "oder Hoehenangabe zur Potenzialberechnung hinterlegt."
        )
        for p in parameter_liste:
            if p.hinweise:
                ergebnis.bemerkungen.append(
                    f"Zone '{p.quelle_eintrag}' [{p.system.value}]: {p.hinweise}"
                )
        ergebnis.bemerkungen.extend(
            PotenzialBerechner._sammle_warnhinweise(parzelle)
        )

    def _behandle_hoehen_und_gz(self, parameter: Bauparameter,
                                parzelle: Parzelle,
                                ergebnis: PotenzialErgebnis) -> None:
        """Hoehen-System mit GROBSCHAETZUNG und klarer Markierung."""
        ergebnis.verwendetes_system = parameter.system.value
        ergebnis.datenqualitaet = Datenqualitaet.GROBSCHAETZUNG

        # Klare Einleitung mit Datenlage
        if parameter.gruenflaechenziffer is not None:
            ergebnis.bemerkungen.append(
                f"DATENLAGE: Zone '{parameter.quelle_eintrag}' wird ueber "
                f"Gebaeudemasse und Gruenflaechenziffer gesteuert. Es existiert "
                f"keine flaechen-bezogene Kennzahl (AZ/GFZo). Eine exakte "
                f"Geschossflaechen-Berechnung ist nicht moeglich - nur eine "
                f"konservative Schaetzung anhand der zulaessigen Gebaeudemasse."
            )
        else:
            ergebnis.bemerkungen.append(
                f"DATENLAGE: Zone '{parameter.quelle_eintrag}' wird ueber "
                f"Vollgeschosse und Gebaeudemasse gesteuert. Es existiert weder "
                f"eine flaechen-bezogene Kennzahl noch eine Gruenflaechenziffer. "
                f"Eine exakte Geschossflaechen-Berechnung ist nicht moeglich - "
                f"nur eine konservative Schaetzung."
            )

        # Reglement-Werte ausgeben
        self._gib_hoehen_werte_aus(parameter, parzelle, ergebnis)

        # GROBSCHAETZUNG durchfuehren
        schaetzung = self._schaetze_geschossflaeche_hoehen(parameter, parzelle)

        if schaetzung is not None:
            ergebnis.theoretisch_zulaessig_m2 = schaetzung["geschossflaeche_m2"]
            ergebnis.status = PotenzialStatus.SCHAETZWERT

            ist_schaetzung = self._schaetze_ist_bebauung(parzelle)
            ergebnis.geschaetzt_realisiert_m2 = ist_schaetzung
            ergebnis.realisiert_ist_platzhalter = True

            # Auch bei Schaetzung Reserve/Ausschoepfung berechnen,
            # damit der Empfehlungs-Block angezeigt wird
            if ergebnis.theoretisch_zulaessig_m2 > 0:
                ergebnis.ausschoepfungsgrad_prozent = (
                    ist_schaetzung / ergebnis.theoretisch_zulaessig_m2 * 100
                )
                ergebnis.reserve_prozent = max(0.0, 100.0 - ergebnis.ausschoepfungsgrad_prozent)
                ergebnis.reserve_m2 = max(0.0, ergebnis.theoretisch_zulaessig_m2 - ist_schaetzung)

            ergebnis.bemerkungen.append("")
            ergebnis.bemerkungen.append(
                "BERECHNUNGSBASIS DER SCHAETZUNG:"
            )

            # Drei moegliche Begrenzer transparent zeigen
            ergebnis.bemerkungen.append(
                f"  Drei Begrenzer der Grundflaeche werden geprueft - "
                f"der kleinste gewinnt:"
            )
            geo_marker = " <- aktiv" if schaetzung["begrenzer"] == "geometrie" else ""
            if schaetzung["grundflaeche_geometrie_m2"] == float("inf"):
                ergebnis.bemerkungen.append(
                    f"    1. Gebaeudemasse: unbegrenzt "
                    f"(Gebaeudelaenge unbeschraenkt){geo_marker}"
                )
            else:
                ergebnis.bemerkungen.append(
                    f"    1. Gebaeudemasse: {schaetzung['grundflaeche_geometrie_m2']:.0f} m^2 "
                    f"({parameter.max_gebaeudelaenge_m} m x {schaetzung['breite_m']:.1f} m "
                    f"aus {schaetzung['breite_quelle']}){geo_marker}"
                )
            parz_marker = " <- aktiv" if schaetzung["begrenzer"] == "parzelle" else ""
            ergebnis.bemerkungen.append(
                f"    2. Parzelle minus Grenzabstaende: "
                f"{schaetzung['grundflaeche_parzelle_m2']:.0f} m^2 "
                f"(quadratische Naeherung){parz_marker}"
            )
            if schaetzung["grundflaeche_gz_m2"] is not None:
                gz_marker = " <- aktiv" if schaetzung["begrenzer"] == "gz" else ""
                ergebnis.bemerkungen.append(
                    f"    3. Gruenflaechenziffer: "
                    f"{schaetzung['grundflaeche_gz_m2']:.0f} m^2 (versiegelbar){gz_marker}"
                )
            else:
                ergebnis.bemerkungen.append(
                    f"    3. Gruenflaechenziffer: nicht definiert (entfaellt)"
                )

            ergebnis.bemerkungen.append(
                f"  -> Massgebende Grundflaeche: {schaetzung['grundflaeche_m2']:.0f} m^2"
            )
            ergebnis.bemerkungen.append(
                f"  Vollgeschosse:         {schaetzung['vollgeschosse']}"
            )
            if schaetzung["mit_dachgeschoss"]:
                ergebnis.bemerkungen.append(
                    f"  Dachgeschoss-Bonus:    +{DACHGESCHOSS_ANRECHNUNG_SCHRAEGDACH * 100:.0f}% "
                    f"(Schraegdach moeglich)"
                )
            ergebnis.bemerkungen.append(
                f"  = GROBSCHAETZUNG zulaessig: {schaetzung['geschossflaeche_m2']:.0f} m^2"
            )
            ergebnis.bemerkungen.append(
                f"  Vergleich Ist (Platzhalter 25% der Parzelle): {ist_schaetzung:.0f} m^2 "
                f"(beide Werte sind Schaetzungen - direkter Vergleich nur grob aussagekraeftig)"
            )

            ergebnis.bemerkungen.append("")
            ergebnis.bemerkungen.append(
                "ANNAHMEN UND UNSICHERHEIT:"
            )
            if schaetzung["breite_quelle"] == "BKP":
                ergebnis.bemerkungen.append(
                    f"  - Gebaeudebreite {schaetzung['breite_m']:.1f} m stammt "
                    f"aus dem parzellenscharfen Bauklassenplan (verbindlich)."
                )
            else:
                ergebnis.bemerkungen.append(
                    f"  - Gebaeudebreite-Annahme {DEFAULT_GEBAEUDEBREITE_M:.0f} m "
                    f"(Default) kann je nach Parzellen-Geometrie zu hoch oder "
                    f"zu niedrig sein."
                )
            ergebnis.bemerkungen.append(
                f"  - Grenzabstaende werden quadratisch approximiert "
                f"(reale Parzelle ist meist nicht quadratisch)."
            )
            ergebnis.bemerkungen.append(
                "  - Der echte Wert haengt vom Volumen-Konzept eines "
                "Architekten ab und kann deutlich ueber oder unter der "
                "Schaetzung liegen."
            )

            # Plausibilitaetscheck gegen alten AZ
            if parameter.vergleichswert_az_alt is not None:
                az_referenz = parzelle.flaeche_m2 * parameter.vergleichswert_az_alt
                faktor = schaetzung['geschossflaeche_m2'] / az_referenz if az_referenz > 0 else 0
                ergebnis.bemerkungen.append("")
                ergebnis.bemerkungen.append(
                    f"PLAUSIBILITAETSCHECK gegen altes Recht:"
                )
                ergebnis.bemerkungen.append(
                    f"  Altes BR: AZ={parameter.vergleichswert_az_alt} -> "
                    f"{az_referenz:.0f} m^2 erlaubt"
                )
                ergebnis.bemerkungen.append(
                    f"  Schaetzung: {schaetzung['geschossflaeche_m2']:.0f} m^2 "
                    f"(Faktor {faktor:.2f}x gegenueber altem AZ-Recht)"
                )
                if faktor < 0.7:
                    ergebnis.bemerkungen.append(
                        f"  ! Schaetzung deutlich UNTER altem Recht. "
                        f"Wahrscheinlich ist die Annahme Gebaeudebreite zu klein "
                        f"oder die Parzellen-Geometrie ist ungewoehnlich."
                    )
                elif faktor > 1.8:
                    ergebnis.bemerkungen.append(
                        f"  ! Schaetzung deutlich UEBER altem Recht. Wahrscheinlich "
                        f"ist die maximale Gebaeudegrundflaeche in Praxis durch "
                        f"andere Faktoren begrenzt."
                    )
                else:
                    ergebnis.bemerkungen.append(
                        f"  Plausibel: Faktor {faktor:.2f}x liegt im erwartbaren "
                        f"Bereich der Verdichtungs-Reform."
                    )
        else:
            ergebnis.bemerkungen.append(
                "GROBSCHAETZUNG nicht moeglich: Es fehlen Vollgeschosse "
                "oder Geometrie-Werte (kA, gA, GL)."
            )

        # Zonen-Hinweis aus Reglement
        if parameter.hinweise:
            ergebnis.bemerkungen.append("")
            ergebnis.bemerkungen.append(
                f"Reglement-Hinweis Zone '{parameter.quelle_eintrag}': "
                f"{parameter.hinweise}"
            )

    @staticmethod
    def _gib_hoehen_werte_aus(parameter: Bauparameter,
                              parzelle: Parzelle,
                              ergebnis: PotenzialErgebnis) -> None:
        """Schreibt die Reglement-Werte als Bemerkungen ins Ergebnis."""
        ergebnis.bemerkungen.append("")
        ergebnis.bemerkungen.append("REGLEMENT-EINGANGSWERTE:")
        if parameter.max_geschosse is not None:
            ergebnis.bemerkungen.append(
                f"  Maximale Vollgeschosse:  {parameter.max_geschosse}"
            )
        if parameter.max_fassadenhoehe_traufseitig_m is not None:
            ergebnis.bemerkungen.append(
                f"  Fassadenhoehe traufseitig (Schraegdach): "
                f"max. {parameter.max_fassadenhoehe_traufseitig_m} m"
            )
        if parameter.max_fassadenhoehe_giebelseitig_m is not None:
            ergebnis.bemerkungen.append(
                f"  Fassadenhoehe giebelseitig (Schraegdach): "
                f"max. {parameter.max_fassadenhoehe_giebelseitig_m} m"
            )
        if parameter.max_fassadenhoehe_anderes_dach_m is not None:
            ergebnis.bemerkungen.append(
                f"  Fassadenhoehe (Flachdach o.ae.): "
                f"max. {parameter.max_fassadenhoehe_anderes_dach_m} m"
            )
        if parameter.max_gebaeudehoehe_m is not None:
            ergebnis.bemerkungen.append(
                f"  Maximale Gebaeudehoehe:  {parameter.max_gebaeudehoehe_m} m"
            )
        if parameter.max_gebaeudelaenge_m is not None:
            ergebnis.bemerkungen.append(
                f"  Maximale Gebaeudelaenge: {parameter.max_gebaeudelaenge_m} m"
            )
        if parameter.grenzabstand_klein_m is not None:
            ergebnis.bemerkungen.append(
                f"  Kleiner Grenzabstand:    {parameter.grenzabstand_klein_m} m"
            )
        if parameter.grenzabstand_gross_m is not None:
            ergebnis.bemerkungen.append(
                f"  Grosser Grenzabstand:    {parameter.grenzabstand_gross_m} m"
            )
        if parameter.gruenflaechenziffer is not None:
            min_gruen_m2 = parzelle.flaeche_m2 * parameter.gruenflaechenziffer
            ergebnis.bemerkungen.append(
                f"  Gruenflaechenziffer:     {parameter.gruenflaechenziffer} "
                f"(min. {min_gruen_m2:.0f} m^2 unversiegelt)"
            )

    # ----- Schaetz-Berechnung im Hoehen-System --------------------------

    @staticmethod
    def _schaetze_geschossflaeche_hoehen(parameter: Bauparameter,
                                         parzelle: Parzelle) -> dict | None:
        """Schaetzt die zulaessige Geschossflaeche im Hoehen-System."""
        if parameter.max_geschosse is None:
            return None
        # Bei unbeschraenkter Gebaeudelaenge (z.B. BK_5 geschlossen) ist
        # der Geometrie-Begrenzer "kein Begrenzer". Wir ueberspringen ihn
        # und nutzen die anderen zwei (Parzelle, GZ).
        gebaeudelaenge_unbeschraenkt = parameter.max_gebaeudelaenge_m is None

        # Breite-Annahme: Wenn der BKP eine echte Gebaeudetiefe geliefert
        # hat, nutzen wir die statt des pauschalen Defaults. Sonst Default.
        if gebaeudelaenge_unbeschraenkt:
            # Bei unbegrenzter Laenge ist die Geometrie kein Begrenzer.
            # Setze inf, damit min() in der Begrenzer-Auswahl ihn ignoriert.
            breite_m = (parameter.bkp_gebaeudetiefe_m
                        if parameter.bkp_gebaeudetiefe_m is not None
                        else DEFAULT_GEBAEUDEBREITE_M)
            breite_quelle = "BKP" if parameter.bkp_gebaeudetiefe_m is not None else "Default"
            grundflaeche_geometrie = float("inf")
        elif parameter.bkp_gebaeudetiefe_m is not None:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           parameter.bkp_gebaeudetiefe_m)
            breite_quelle = "BKP"
            grundflaeche_geometrie = parameter.max_gebaeudelaenge_m * breite_m
        else:
            breite_m = min(parameter.max_gebaeudelaenge_m,
                           DEFAULT_GEBAEUDEBREITE_M)
            breite_quelle = "Default"
            grundflaeche_geometrie = parameter.max_gebaeudelaenge_m * breite_m

        grundflaeche_parzelle = grundflaeche_geometrie
        if (parameter.grenzabstand_klein_m is not None
                and parameter.grenzabstand_gross_m is not None):
            # Annahme: typische Parzelle ist nicht quadratisch sondern
            # eher rechteckig im Verhaeltnis 1:1.5 (laengere Seite zur
            # Strasse hin). Das ist realistischer als die quadratische
            # Naeherung und verhindert Ausreisser bei kleinen Parzellen.
            verhaeltnis = 1.5
            kurze_seite = (parzelle.flaeche_m2 / verhaeltnis) ** 0.5
            lange_seite = kurze_seite * verhaeltnis
            # Kleiner Grenzabstand auf den kurzen Seiten,
            # grosser Grenzabstand auf den langen Seiten
            nutzbare_kurz = max(0, kurze_seite - 2 * parameter.grenzabstand_klein_m)
            nutzbare_lang = max(0, lange_seite - 2 * parameter.grenzabstand_gross_m)
            grundflaeche_parzelle = nutzbare_kurz * nutzbare_lang

        grundflaeche_gz = float("inf")
        if parameter.gruenflaechenziffer is not None:
            max_versiegelt = parzelle.flaeche_m2 * (1 - parameter.gruenflaechenziffer)
            grundflaeche_gz = max_versiegelt

        grundflaeche = min(
            grundflaeche_geometrie,
            grundflaeche_parzelle,
            grundflaeche_gz,
        )

        # Welcher Faktor ist der Begrenzer?
        if grundflaeche == grundflaeche_geometrie:
            begrenzer = "geometrie"
        elif grundflaeche == grundflaeche_parzelle:
            begrenzer = "parzelle"
        else:
            begrenzer = "gz"

        geschossflaeche = grundflaeche * parameter.max_geschosse

        mit_dachgeschoss = (
            parameter.max_fassadenhoehe_traufseitig_m is not None
            and parameter.max_fassadenhoehe_giebelseitig_m is not None
        )
        if mit_dachgeschoss:
            geschossflaeche += grundflaeche * DACHGESCHOSS_ANRECHNUNG_SCHRAEGDACH

        return {
            "grundflaeche_m2": grundflaeche,
            "vollgeschosse": parameter.max_geschosse,
            "geschossflaeche_m2": geschossflaeche,
            "breite_m": breite_m,
            "breite_quelle": breite_quelle,
            "mit_dachgeschoss": mit_dachgeschoss,
            "grundflaeche_geometrie_m2": grundflaeche_geometrie,
            "grundflaeche_parzelle_m2": grundflaeche_parzelle,
            "grundflaeche_gz_m2": (
                grundflaeche_gz if grundflaeche_gz != float("inf") else None
            ),
            "begrenzer": begrenzer,
        }

    # ----- Strukturgebiet-Erkennung ------------------------------------

    @staticmethod
    def _pruefe_strukturgebiet(parzelle: Parzelle) -> str | None:
        """Prueft, ob die Parzelle im Strukturgebiet liegt (Thun-Spezial)."""
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
        """Platzhalter: 25% der Parzellenflaeche (realistischer als 40%)."""
        return parzelle.flaeche_m2 * 0.25

    @staticmethod
    def _bestimme_status(ausschoepfung: float | None) -> PotenzialStatus:
        """Klassifiziert den Ausschoepfungsgrad in einen Status."""
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
