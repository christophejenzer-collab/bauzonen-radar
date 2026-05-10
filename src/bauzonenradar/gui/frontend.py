"""
Bauzonen-Radar – Streamlit GUI
Iteration 4 | Stand: 03. Mai 2026

Aufruf (aus Projekt-Root):
    streamlit run src/bauzonenradar/gui/app.py

Voraussetzungen:
    pip install streamlit
    Python 3.13, venv aktiv
"""

import sys
import math
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Backend-Import
# ---------------------------------------------------------------------------
sys.path.insert(0, "src/bauzonenradar")

try:
    from analyse_adresse import analysiere
    from analyse.potenzial import Datenqualitaet, PotenzialStatus
    BACKEND_OK = True
except ImportError as e:
    BACKEND_OK = False
    BACKEND_FEHLER = str(e)

# ---------------------------------------------------------------------------
# Seitenkonfiguration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Bauzonen-Radar",
    page_icon="🏗️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS – Design orientiert an za-ag.ch
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Schrift & Grundfarben */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        color: #1A1A1A;
    }

    /* Header */
    .radar-header {
        padding: 2rem 0 1rem 0;
        border-bottom: 2px solid #1A1A1A;
        margin-bottom: 2rem;
    }
    .radar-title {
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 0.05em;
        color: #1A1A1A;
        margin: 0;
    }
    .radar-subtitle {
        font-size: 0.9rem;
        color: #757575;
        margin-top: 0.25rem;
    }

    /* Sektions-Trennlinie */
    .sektion {
        border-top: 1px solid #E0E0E0;
        margin-top: 2rem;
        padding-top: 1.5rem;
    }
    .sektion-titel {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #757575;
        margin-bottom: 1rem;
    }

    /* Datenqualitäts-Badge */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 2px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .badge-verbindlich   { background: #E8F5E9; color: #2E7D32; border: 1px solid #2E7D32; }
    .badge-grobschaetzung { background: #FFF3E0; color: #E65100; border: 1px solid #E65100; }
    .badge-nicht-moeglich { background: #F5F5F5; color: #757575; border: 1px solid #757575; }

    /* Warnung */
    .warnung-box {
        background: #FFF8E1;
        border-left: 3px solid #E65100;
        padding: 0.8rem 1rem;
        margin: 1rem 0;
        font-size: 0.85rem;
    }

    /* Konflikt-Box GWR */
    .konflikt-box {
        background: #FFF3E0;
        border-left: 3px solid #FF6F00;
        padding: 0.8rem 1rem;
        margin: 1rem 0;
        font-size: 0.85rem;
    }

    /* Lagebeurteilung */
    .lage-hoch        { color: #2E7D32; font-weight: 600; font-size: 1.05rem; }
    .lage-mittel      { color: #1565C0; font-weight: 600; font-size: 1.05rem; }
    .lage-gering      { color: #E65100; font-weight: 600; font-size: 1.05rem; }
    .lage-ausgeschoepft { color: #757575; font-weight: 600; font-size: 1.05rem; }
    .lage-unbekannt   { color: #1A1A1A; font-weight: 600; font-size: 1.05rem; }

    /* Kennzahlen-Grid */
    .kennzahl-label {
        font-size: 0.75rem;
        color: #757575;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .kennzahl-wert {
        font-size: 1.4rem;
        font-weight: 300;
        color: #1A1A1A;
    }
    .kennzahl-einheit {
        font-size: 0.8rem;
        color: #757575;
    }

    /* Footer */
    .radar-footer {
        border-top: 1px solid #E0E0E0;
        margin-top: 3rem;
        padding-top: 1rem;
        font-size: 0.75rem;
        color: #BDBDBD;
        text-align: center;
    }

    /* Streamlit-Defaults überschreiben */
    .stButton > button {
        background: #1A1A1A;
        color: white;
        border: none;
        border-radius: 2px;
        padding: 0.5rem 2rem;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: #8B1A1A;
        color: white;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 2px;
        border: 1px solid #BDBDBD;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def lv95_zu_wgs84(ost: float, nord: float) -> tuple[float, float]:
    """
    Näherungskonvertierung LV95 → WGS84.
    Quelle: swisstopo Näherungsformeln (±1m Genauigkeit, ausreichend für st.map)
    """
    x = (ost  - 2_600_000) / 1_000_000
    y = (nord - 1_200_000) / 1_000_000

    lon = (2.6779094
           + 4.728982 * x
           + 0.791484 * x * y
           + 0.1306   * x * y * y
           - 0.0436   * x * x * x)
    lat = (16.9023892
           + 3.238272 * y
           - 0.270978 * x * x
           - 0.002528 * y * y
           - 0.0447   * x * x * y
           - 0.0140   * y * y * y)

    lon = lon * 100 / 36
    lat = lat * 100 / 36
    return lat, lon


def badge_html(datenqualitaet: "Datenqualitaet") -> str:
    if datenqualitaet == Datenqualitaet.VERBINDLICH:
        return '<span class="badge badge-verbindlich">✓ Verbindlich</span>'
    elif datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
        return '<span class="badge badge-grobschaetzung">~ Grobschätzung</span>'
    else:
        return '<span class="badge badge-nicht-moeglich">– Nicht möglich</span>'


def lage_html(status: "PotenzialStatus", reserve: float | None) -> str:
    if reserve is None:
        return '<span class="lage-unbekannt">Keine Berechnung möglich</span>'
    if reserve >= 60:
        return f'<span class="lage-hoch">▲ Hohes Verdichtungs-Potenzial</span>'
    elif reserve >= 30:
        return f'<span class="lage-mittel">◆ Mittleres Verdichtungs-Potenzial</span>'
    elif reserve >= 10:
        return f'<span class="lage-gering">▼ Geringes Verdichtungs-Potenzial</span>'
    else:
        return f'<span class="lage-ausgeschoepft">● Praktisch ausgeschöpft</span>'


def zeige_progress_bar(label: str, prozent: float | None, farbe: str = "#1A1A1A") -> None:
    if prozent is None:
        return
    prozent_clean = max(0.0, min(100.0, prozent))
    st.markdown(f"""
    <div style="margin-bottom: 0.8rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.2rem;">
            <span style="font-size:0.8rem; color:#757575; text-transform:uppercase;
                         letter-spacing:0.08em;">{label}</span>
            <span style="font-size:0.9rem; font-weight:500;">{prozent:.1f}%</span>
        </div>
        <div style="background:#F0F0F0; height:6px; border-radius:1px;">
            <div style="background:{farbe}; width:{prozent_clean}%; height:6px;
                        border-radius:1px; transition:width 0.4s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="radar-header">
    <p class="radar-title">Bauzonen-Radar</p>
    <p class="radar-subtitle">
        Analysewerkzeug für ungenutztes Bebauungspotenzial – Kanton Bern
    </p>
</div>
""", unsafe_allow_html=True)

# Backend-Fehler abfangen
if not BACKEND_OK:
    st.error(f"Backend konnte nicht geladen werden: {BACKEND_FEHLER}")
    st.info("Stelle sicher, dass du die App aus dem Projekt-Root ausführst:\n"
            "`streamlit run src/bauzonenradar/gui/app.py`")
    st.stop()

# ---------------------------------------------------------------------------
# Eingabe
# ---------------------------------------------------------------------------
with st.form("analyse_form"):
    adresse = st.text_input(
        "Adresse",
        placeholder="z.B. Frutigenstrasse 25, 3604 Thun",
        label_visibility="collapsed",
    )
    abschicken = st.form_submit_button("Analysieren")

# ---------------------------------------------------------------------------
# Analyse
# ---------------------------------------------------------------------------
if abschicken:
    if not adresse.strip():
        st.warning("Bitte eine Adresse eingeben.")
        st.stop()

    with st.spinner("Analyse läuft – OEREB, BKP und GWR werden abgefragt…"):
        try:
            resultat = analysiere(adresse.strip())
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {e}")
            st.stop()

    if resultat is None:
        st.error("Adresse nicht gefunden. Bitte Schreibweise prüfen "
                 "(z.B. «Frutigenstrasse 25, 3604 Thun»).")
        st.stop()

    # Ergebnis-Objekt entpacken
    # Erwartetes Interface nach Backend-Vorbereitung Christophe:
    # resultat.parzelle        → Parzelle-Objekt
    # resultat.ergebnis        → PotenzialErgebnis-Objekt
    # resultat.gwr_gebaeude    → list[GwrGebaeude] | None
    # Falls analysiere() direkt PotenzialErgebnis zurückgibt (Variante B):
    if hasattr(resultat, "datenqualitaet"):
        # Variante B: analysiere() gibt PotenzialErgebnis direkt zurück
        ergebnis = resultat
        parzelle = None
        gwr_gebaeude = None
    else:
        # Variante A: analysiere() gibt ein zusammengesetztes Objekt zurück
        ergebnis   = getattr(resultat, "ergebnis", None)
        parzelle   = getattr(resultat, "parzelle", None)
        gwr_gebaeude = getattr(resultat, "gwr_gebaeude", None)

    # -----------------------------------------------------------------------
    # Sektion: Karte
    # -----------------------------------------------------------------------
    koordinate = None
    if parzelle is not None:
        for feldname in ("koordinate_lv95", "koordinaten", "lv95"):
            if hasattr(parzelle, feldname):
                wert = getattr(parzelle, feldname)
                if wert and len(wert) == 2:
                    koordinate = (float(wert[0]), float(wert[1]))
                    break

    if koordinate:
        lat, lon = lv95_zu_wgs84(koordinate[0], koordinate[1])
        st.markdown('<div class="sektion"><p class="sektion-titel">Lage</p></div>',
                    unsafe_allow_html=True)
        df_karte = pd.DataFrame({"lat": [lat], "lon": [lon]})
        st.map(df_karte, zoom=15)

    # -----------------------------------------------------------------------
    # Sektion: Parzellen-Info + Datenqualität
    # -----------------------------------------------------------------------
    st.markdown('<div class="sektion"><p class="sektion-titel">Parzelle</p></div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        gemeinde = (parzelle.gemeinde if parzelle and hasattr(parzelle, "gemeinde")
                    else "–")
        st.markdown(f'<p class="kennzahl-label">Gemeinde</p>'
                    f'<p class="kennzahl-wert">{gemeinde}</p>', unsafe_allow_html=True)

    with col2:
        flaeche = (f"{parzelle.flaeche_m2:.0f}"
                   if parzelle and hasattr(parzelle, "flaeche_m2")
                   else (f"{ergebnis.parzellenflaeche_m2:.0f}"
                         if ergebnis else "–"))
        st.markdown(f'<p class="kennzahl-label">Fläche</p>'
                    f'<p class="kennzahl-wert">{flaeche} '
                    f'<span class="kennzahl-einheit">m²</span></p>',
                    unsafe_allow_html=True)

    with col3:
        zonen_text = (", ".join(ergebnis.zonen_betrachtet)
                      if ergebnis and ergebnis.zonen_betrachtet else "–")
        # Kürzen falls zu lang
        if len(zonen_text) > 40:
            zonen_text = zonen_text[:40] + "…"
        st.markdown(f'<p class="kennzahl-label">Zone(n)</p>'
                    f'<p class="kennzahl-wert" style="font-size:0.95rem;">'
                    f'{zonen_text}</p>', unsafe_allow_html=True)

    # Datenqualitäts-Badge
    st.markdown("<br>", unsafe_allow_html=True)
    if ergebnis:
        st.markdown(badge_html(ergebnis.datenqualitaet), unsafe_allow_html=True)
        if ergebnis.datenqualitaet == Datenqualitaet.GROBSCHAETZUNG:
            st.markdown(
                '<div class="warnung-box">⚠ Werte sind konservativ geschätzt – '
                'keine Investitionsentscheidung darauf basieren.</div>',
                unsafe_allow_html=True
            )

    # -----------------------------------------------------------------------
    # Sektion: Potenzial
    # -----------------------------------------------------------------------
    st.markdown('<div class="sektion"><p class="sektion-titel">Bebauungspotenzial</p></div>',
                unsafe_allow_html=True)

    if ergebnis and ergebnis.datenqualitaet != Datenqualitaet.NICHT_MOEGLICH:

        # Kennzahlen-Row
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            soll = (f"{ergebnis.theoretisch_zulaessig_m2:.0f}"
                    if ergebnis.theoretisch_zulaessig_m2 is not None else "–")
            st.markdown(f'<p class="kennzahl-label">Theoretisch zulässig</p>'
                        f'<p class="kennzahl-wert">{soll} '
                        f'<span class="kennzahl-einheit">m²</span></p>',
                        unsafe_allow_html=True)
        with col_b:
            aussch = (f"{ergebnis.ausschoepfungsgrad_prozent:.1f}"
                      if ergebnis.ausschoepfungsgrad_prozent is not None else "–")
            st.markdown(f'<p class="kennzahl-label">Ausschöpfung</p>'
                        f'<p class="kennzahl-wert">{aussch} '
                        f'<span class="kennzahl-einheit">%</span></p>',
                        unsafe_allow_html=True)
        with col_c:
            res = (f"{ergebnis.reserve_prozent:.1f}"
                   if ergebnis.reserve_prozent is not None else "–")
            st.markdown(f'<p class="kennzahl-label">Bauland-Reserve</p>'
                        f'<p class="kennzahl-wert">{res} '
                        f'<span class="kennzahl-einheit">%</span></p>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Progress-Bars
        zeige_progress_bar(
            "Ausschöpfung",
            ergebnis.ausschoepfungsgrad_prozent,
            farbe="#8B1A1A"
        )
        zeige_progress_bar(
            "Bauland-Reserve",
            ergebnis.reserve_prozent,
            farbe="#2E7D32"
        )

        # Lagebeurteilung
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(lage_html(ergebnis.status, ergebnis.reserve_prozent),
                    unsafe_allow_html=True)

        # Arealbonus
        if ergebnis.arealbonus_anwendbar:
            st.info("🏗 Arealbonus möglich: Zusätzliches Geschoss bewilligungsfähig.")

    elif ergebnis:
        st.markdown(
            '<div class="warnung-box">Quantitative Potenzialberechnung nicht möglich. '
            'Diese Zone unterliegt einem Spezialregime (z.B. Altstadt, Schutzzone). '
            'Bitte Bauverwaltung kontaktieren.</div>',
            unsafe_allow_html=True
        )

    # -----------------------------------------------------------------------
    # Sektion: GWR – Soll vs. Ist
    # -----------------------------------------------------------------------
    if gwr_gebaeude:
        st.markdown(
            '<div class="sektion"><p class="sektion-titel">GWR – Bestehende Bebauung (Ist)</p></div>',
            unsafe_allow_html=True
        )

        summe_ist = 0.0
        hat_konflikt = False
        gwr_zeilen = []

        for g in gwr_gebaeude:
            gf  = getattr(g, "grundflaeche_m2", None)
            ges = getattr(g, "geschosse", None)
            wohnungen = getattr(g, "anzahl_wohnungen", None)
            baujahr   = getattr(g, "baujahr", None) or getattr(g, "bauperiode_code", "–")
            label     = getattr(g, "label", "Gebäude")
            gf_total  = getattr(g, "geschossflaeche_m2", None)

            if gf is not None and ges is not None and gf_total is not None:
                summe_ist += gf_total
                gwr_zeilen.append({
                    "Gebäude":         label,
                    "Grundfläche m²":  f"{gf:.0f}",
                    "Geschosse":       str(ges),
                    "Geschossfläche m²": f"{gf_total:.0f}",
                    "Wohnungen":       str(wohnungen or "–"),
                    "Baujahr":         str(baujahr),
                })
            else:
                gwr_zeilen.append({
                    "Gebäude":         label,
                    "Grundfläche m²":  "–",
                    "Geschosse":       "–",
                    "Geschossfläche m²": "Daten unvollständig",
                    "Wohnungen":       "–",
                    "Baujahr":         str(baujahr),
                })

        if gwr_zeilen:
            st.dataframe(
                pd.DataFrame(gwr_zeilen),
                use_container_width=True,
                hide_index=True
            )

        # Plausibilitäts-Konflikt
        if (ergebnis
                and ergebnis.theoretisch_zulaessig_m2 is not None
                and summe_ist > ergebnis.theoretisch_zulaessig_m2 * 1.05):
            hat_konflikt = True
            st.markdown(
                f'<div class="konflikt-box">'
                f'⚡ <strong>Plausibilitäts-Konflikt:</strong> '
                f'GWR-Ist ({summe_ist:.0f} m²) übersteigt den berechneten Soll-Wert '
                f'({ergebnis.theoretisch_zulaessig_m2:.0f} m²). '
                f'Die Schätzung unterschätzt die reale Bebauung – '
                f'manuelle Prüfung empfohlen.'
                f'</div>',
                unsafe_allow_html=True
            )

    # -----------------------------------------------------------------------
    # Sektion: Bemerkungen & Spezialfälle
    # -----------------------------------------------------------------------
    if ergebnis and ergebnis.bemerkungen:
        # Nur wirklich relevante Bemerkungen anzeigen (Warnhinweise, Spezialfälle)
        wichtige = [b for b in ergebnis.bemerkungen
                    if any(kw in b.upper() for kw in [
                        "NATURGE", "BAULINI", "STRUKTURGEBIET", "ÜBERLAGER",
                        "LAUFEND", "AREALBONUS", "SPEZIAL", "ALTSTADT",
                        "UNESCO", "DUALIT", "NICHT MÖGLICH", "EMPFEHLUNG"
                    ])]
        if wichtige:
            st.markdown(
                '<div class="sektion"><p class="sektion-titel">Hinweise & Spezialfälle</p></div>',
                unsafe_allow_html=True
            )
            for b in wichtige:
                st.markdown(f"- {b}")

    # -----------------------------------------------------------------------
    # Haftungsausschluss
    # -----------------------------------------------------------------------
    st.markdown(
        '<div class="radar-footer">'
        'Bauzonen-Radar – Hochschulprojekt, nicht zur kommerziellen Nutzung. '
        'Keine rechtsverbindliche Auskunft der Bauverwaltung. '
        'Grobschätzungen sind keine Grundlage für Investitionsentscheide.'
        '</div>',
        unsafe_allow_html=True
    )
