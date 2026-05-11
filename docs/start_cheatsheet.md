# Quick-Start Cheat-Sheet

Persoenliche Befehls-Sammlung fuer den Tag-Anfang.

# START Tool

BACKEND
cd C:\Tools\bauzonen-radar
.\start.ps1

FRONTEND
streamlit run src\bauzonenradar\gui\frontend.py


## Abfragen

# Eintrittspunkte
python -m bauzonenradar.analyse_adresse "Hauptstrasse 30, 3653 Oberhofen"  
python -m bauzonenradar.analyse_parzelle --gemeinde "Oberhofen" --nr 309   
python -m bauzonenradar.analyse_parzelle --egrid CH382046359635

python analyse_adresse.py "Kramgasse 1, 3000 Bern"
python analyse_adresse.py "Thunstrasse 40, 3005 Bern"
python analyse_adresse.py "Untere Sadelstrasse 1, 3653 Oberhofen"
python analyse_adresse.py "Hirschweg 7, 3604 Thun"
python analyse_adresse.py "Junkerngasse 47, 3011 Bern"
python analyse_adresse.py "Marktgasse 1, 3011 Bern"
python analyse_adresse.py "Bundesgasse 26, 3011 Bern"

## DEMO 10 Adressen
cd C:\Tools\bauzonen-radar
.\start.ps1
.\demo.ps1


##Test Start

cd C:\Tools\bauzonen-radar
Unblock-File .\tests\test_zwoelf_adressen.ps1
.\tests\test_zwoelf_adressen.ps1
