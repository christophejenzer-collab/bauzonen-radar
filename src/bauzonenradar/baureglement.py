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
schrittweise anpassen.

Einige Gemeinden gehen noch einen Schritt weiter und verzichten auch
auf die GFZo: Die bauliche Dichte wird dort primaer ueber Gebaeudehoehen,
Grenzabstaende, Gebaeudelaenge und (optional) Gruenflaechenziffer
gesteuert.

Beispiele:
  - Stadt Bern: Bauklassen 2-6 mit GFZo (parzellenscharf im BKP)
  - Stadt Thun (BR 2022): Hoehen + Gruenflaechenziffer
  - Oberhofen (BR 2012/2024): Hoehen + Vollgeschosse (ohne GZ)

Das Datenmodell unterstuetzt drei Bemessungssysteme:
  - AZ            : Klassische Ausnuetzungsziffer
  - GFZo          : Geschossflaechenziffer oberirdisch
  - hoehen_und_gz : Steuerung ueber Hoehen (+ optional GZ)

Spezialeffekte:
  - Arealbonus: Bei grossen Parzellen oder Parzellen-Zusammenlegungen
                kann ein zusaetzliches Geschoss bewilligt werden
                (Thun: Schwellenwert 3000 m^2)
  - Strukturgebiet: Beirat Stadtbild kann das Baureglement teilweise
                    aushebeln und gestalterische Vorgaben machen
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
    """Welches Regelwerk steuert die Bebauungsdichte dieser Zone?"""
    AZ = "AZ"
    GFZO = "GFZo"
    HOEHEN_UND_GZ = "hoehen_und_gz"
    DUALITAET = "dualitaet"
    UNBEKANNT = "unbekannt"

    @classmethod
    def from_string(cls, text: str | None) -> "BemessungsSystem":
        """Parst einen JSON-String in das Enum."""
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

    Felder folgen dem Berner Baurecht und der Thun BR-2022-Tabelle:
    - Grenzabstaende klein/gross (kA, gA)
    - Gebaeudelaenge (GL)
    - Fassadenhoehen differenziert nach Dachform:
        * traufseitig bei Schraegdach (Fh tr)
        * giebelseitig bei Schraegdach (Fh gi)
        * andere Dachformen wie Flachdach (Fh)
    - Gruenflaechenziffer (GZ) - optional
    - AZ und GFZo als Kennzahlen
    """
    quelle_eintrag: str
    system: BemessungsSystem = BemessungsSystem.UNBEKANNT

    # Klassische Kennzahlen
    ausnuetzungsziffer: float | None = None
    geschossflaechenziffer_oberirdisch: float | None = None

    # Hoehen-Steuerung
    max_geschosse: int | None = None
    max_gebaeudehoehe_m: float | None = None
    max_fassadenhoehe_traufseitig_m: float | None = None      # Fh tr (Schraegdach)
    max_fassadenhoehe_giebelseitig_m: float | None = None     # Fh gi (Schraegdach)
    max_fassadenhoehe_anderes_dach_m: float | None = None     # Fh (Flachdach etc.)

    # Geometrie
    max_gebaeudelaenge_m: float | None = None                 # GL
    grenzabstand_klein_m: float | None = None                 # kA
    grenzabstand_gross_m: float | None = None                 # gA

    # Gruenflaechen (optional - nicht alle Gemeinden haben das)
    gruenflaechenziffer: float | None = None                  # GZ

    # Arealbonus (zusaetzliches Geschoss bei grossen Parzellen)
    arealbonus_ab_flaeche_m2: float | None = None             # Schwellenwert
    arealbonus_zusaetzliche_geschosse: int | None = None      # Bonus

    # Meta
    rechtsgrundlage: str = ""
    hinweise: str = ""
    gueltig_ab: str | None = None

    # ----- Abgeleitete Eigenschaften -----

    @property
    def ist_berechenbar(self) -> bool:
        """
        True, wenn irgendein Wert zur qualifizierten Beurteilung verfuegbar ist.

        Drei Stufen der Berechenbarkeit (von strikt zu locker):
        1. AZ oder GFZo: ergibt direkte Quadratmeter-Berechnung
        2. Hoehen mit GZ: qualifizierte Berechnung mit unversiegelter Flaeche (Thun-Stil)
        3. Nur Hoehen: qualitative Beschreibung mit Reglement-Werten (Oberhofen-Stil)

        Wichtig: Ein Reglement ohne Gruenflaechenziffer (z.B. Oberhofen) ist
        trotzdem 'berechenbar' im Sinne dieser Methode - es gibt fachlich
        relevante Werte aus, auch wenn keine direkte m^2-Berechnung moeglich ist.
        """
        if self.ausnuetzungsziffer is not None:
            return True
        if self.geschossflaechenziffer_oberirdisch is not None:
            return True
        # Hoehen-System: schon eine Hoehenangabe genuegt
        if self.max_fassadenhoehe_traufseitig_m is not None:
            return True
        if self.max_gebaeudehoehe_m is not None:
            return True
        if self.max_fassadenhoehe_anderes_dach_m is not None:
            return True
        return False

    def hauptkennzahl(self) -> tuple[str, float] | None:
        """
        Gibt die fuer die direkte Quadratmeter-Berechnung relevante Kennzahl zurueck.

        Nur AZ oder GFZo liefern eine Hauptkennzahl. Hoehen-Systeme geben
        None zurueck und werden im PotenzialBerechner ueber die Hoehen-Pfad
        behandelt.
        """
        if self.geschossflaechenziffer_oberirdisch is not None:
            return ("GFZo", self.geschossflaechenziffer_oberirdisch)
        if self.ausnuetzungsziffer is not None:
            return ("AZ", self.ausnuetzungsziffer)
        return None

    def hat_arealbonus(self, parzellenflaeche_m2: float) -> bool:
        """Prueft, ob die Parzelle Anspruch auf einen Arealbonus hat."""
        if self.arealbonus_ab_flaeche_m2 is None:
            return False
        return parzellenflaeche_m2 >= self.arealbonus_ab_flaeche_m2

    def zusammenfassung(self) -> str:
        """Kurze Textuebersicht."""
        teile = [f"{self.quelle_eintrag} [{self.system.value}]:"]

        if self.ausnuetzungsziffer is not None:
            teile.append(f"AZ={self.ausnuetzungsziffer}")
        if self.geschossflaechenziffer_oberirdisch is not None:
            teile.append(f"GFZo={self.geschossflaechenziffer_oberirdisch}")
        if self.max_geschosse is not None:
            teile.append(f"VG={self.max_geschosse}")
        if self.max_fassadenhoehe_traufseitig_m is not None:
            teile.append(f"Fh tr={self.max_fassadenhoehe_traufseitig_m}m")
        if self.max_fassadenhoehe_giebelseitig_m is not None:
            teile.append(f"Fh gi={self.max_fassadenhoehe_giebelseitig_m}m")
        if self.max_fassadenhoehe_anderes_dach_m is not None:
            teile.append(f"Fh={self.max_fassadenhoehe_anderes_dach_m}m")
        if self.max_gebaeudelaenge_m is not None:
            teile.append(f"GL={self.max_gebaeudelaenge_m}m")
        if self.gruenflaechenziffer is not None:
            teile.append(f"GZ={self.gruenflaechenziffer}")
        if self.grenzabstand_klein_m is not None:
            teile.append(f"kA={self.grenzabstand_klein_m}m")
        if self.grenzabstand_gross_m is not None:
            teile.append(f"gA={self.grenzabstand_gross_m}m")

        if not self.ist_berechenbar:
            teile.append("(keine Kennzahlen)")

        return " ".join(teile)


# ---------------------------------------------------------------------------
# Baureglement
# ---------------------------------------------------------------------------

@dataclass
class Baureglement:
    """Reglement einer Gemeinde, geladen aus JSON."""
    gemeinde: str
    bfs_nr: int
    kanton: str
    stand: str
    quelle: str
    struktur: str
    system_default: BemessungsSystem = BemessungsSystem.UNBEKANNT
    bauklassen: dict[str, dict] = field(default_factory=dict)
    nutzungszonen: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def laden(cls, gemeinde: str,
              basis_pfad: Path | str | None = None) -> "Baureglement":
        """Laedt das Baureglement einer Gemeinde aus der JSON-Datei.

        Konvertiert Umlaute (ae/oe/ue), schreibt Kleinbuchstaben und
        ersetzt Leerzeichen durch Unterstriche. So wird aus
        'Oberhofen am Thunersee' der Dateiname 'oberhofen_am_thunersee.json'.
        """
        if basis_pfad is None:
            hier = Path(__file__).resolve().parent
            basis_pfad = hier.parent.parent / "daten" / "baureglemente"
        else:
            basis_pfad = Path(basis_pfad)

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
        """Findet fuer eine Parzelle die passenden Bauparameter."""
        if self.struktur == "bauklassen":
            return self._match_bauklassen(parzelle)
        return self._match_kombiniert(parzelle)

    def _match_bauklassen(self, parzelle: Parzelle) -> list[Bauparameter]:
        """Stadt-Bern-Stil: Bauklasse bestimmt die Parameter."""
        treffer: list[Bauparameter] = []
        for bauklasse_parzelle in parzelle.bauklassen():
            parameter = self._suche_in_dict(
                self.bauklassen, bauklasse_parzelle.legende
            )
            if parameter:
                treffer.append(parameter)
        return treffer

    def _match_kombiniert(self, parzelle: Parzelle) -> list[Bauparameter]:
        """Land-Stil: Grundnutzung-Eintrag liefert Zone+Bauklasse in einem."""
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
        """Drei-Stufen-Matching: exakt, Suchtext-in-Schluessel, Schluessel-in-Suchtext.

        Eintraege mit '_' am Anfang werden ignoriert (Kommentare/Metadaten).
        """
        if not quelle or not suchtext:
            return None

        effektiv = {k: v for k, v in quelle.items() if not k.startswith("_")}

        # Stufe 1: exakter Match
        if suchtext in effektiv:
            return self._baue_parameter(suchtext, effektiv[suchtext])

        # Stufe 2: Suchtext ist Teil eines Schluessels
        for key, value in effektiv.items():
            if suchtext in key:
                return self._baue_parameter(key, value)

        # Stufe 3: Schluessel ist Teil des Suchtexts
        for key, value in effektiv.items():
            if key in suchtext:
                return self._baue_parameter(key, value)

        return None

    def _baue_parameter(self, quelle_eintrag: str,
                        daten: dict) -> Bauparameter:
        """Erstellt ein Bauparameter-Objekt aus einem JSON-Dict."""
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
            max_geschosse=daten.get("max_geschosse"),
            max_gebaeudehoehe_m=daten.get("max_gebaeudehoehe_m"),
            max_fassadenhoehe_traufseitig_m=daten.get("max_fassadenhoehe_traufseitig_m"),
            max_fassadenhoehe_giebelseitig_m=daten.get("max_fassadenhoehe_giebelseitig_m"),
            max_fassadenhoehe_anderes_dach_m=daten.get("max_fassadenhoehe_anderes_dach_m"),
            max_gebaeudelaenge_m=daten.get("max_gebaeudelaenge_m"),
            grenzabstand_klein_m=daten.get("grenzabstand_klein_m"),
            grenzabstand_gross_m=daten.get("grenzabstand_gross_m"),
            gruenflaechenziffer=daten.get("gruenflaechenziffer"),
            arealbonus_ab_flaeche_m2=daten.get("arealbonus_ab_flaeche_m2"),
            arealbonus_zusaetzliche_geschosse=daten.get("arealbonus_zusaetzliche_geschosse"),
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

    adresse = sys.argv[1] if len(sys.argv) > 1 else "Hirschweg 7, 3604 Thun"

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
        sys.exit(0)

    print(f"Gefundene Bauparameter ({len(parameter_liste)}):")
    for p in parameter_liste:
        print(f"  - {p.zusammenfassung()}")
        if p.rechtsgrundlage:
            print(f"    Rechtsgrundlage: {p.rechtsgrundlage}")
        if p.hat_arealbonus(parzelle.flaeche_m2):
            print(f"    !!! Arealbonus: +{p.arealbonus_zusaetzliche_geschosse} "
                  f"Geschoss(e) ab {p.arealbonus_ab_flaeche_m2:.0f} m^2")
        if p.hinweise:
            print(f"    Hinweis: {p.hinweise}")
