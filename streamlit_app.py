"""Streamlit Cloud Entry-Point.

Loest das Pfad-Problem fuer Streamlit Community Cloud.
frontend.py erwartet 'src/bauzonenradar' im sys.path - diese Datei
absoluten Pfad ein und delegiert dann.
"""
import sys
from pathlib import Path

# Absoluter Pfad zu src/bauzonenradar (egal von wo gestartet)
REPO_ROOT = Path(__file__).parent.absolute()
MODUL_PFAD = REPO_ROOT / "src" / "bauzonenradar"

# Beide Pfade einfuegen
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
if str(MODUL_PFAD) not in sys.path:
    sys.path.insert(0, str(MODUL_PFAD))

# Frontend-Code ausfuehren
FRONTEND_PFAD = MODUL_PFAD / "gui" / "frontend.py"
with open(FRONTEND_PFAD, encoding="utf-8") as f:
    code = f.read()
exec(code)