"""
Externe Datenquellen fuer den Bauzonen-Radar.

Module:
  - gwr: Eidgenoessisches Gebaeude- und Wohnungsregister (Ist-Werte)

Geplant fuer Iteration 5:
  - parzellen_liste: Alle Parzellen einer Gemeinde
"""

from .gwr import GwrQuelle, GwrGebaeude, GwrFehler, GwrApiFehler, GwrParseFehler

__all__ = [
    "GwrQuelle",
    "GwrGebaeude",
    "GwrFehler",
    "GwrApiFehler",
    "GwrParseFehler",
]
