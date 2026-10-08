import csv
import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests

URL = "https://www.winamax.fr/paris-sportifs/sports/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

print("Connexion à Winamax...")
res = requests.get(URL, headers=headers, impersonate="chrome120")

if res.status_code != 200:
    print(f"Erreur HTTP : {res.status_code}")
    exit(1)

# Recherche de l'état initial injecté dans la page
match_json = re.search(r"var PRELOADED_STATE = ({.*?});</script>", res.text)

if not match_json:
    # Alternative si la variable a un autre nom
    soup = BeautifulSoup(res.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        data = json.loads(script_tag.string)
    else:
        print("Structure introuvable ou blocage du serveur.")
        exit(1)
else:
    data = json.loads(match_json.group(1))

matches = data.get("matches", {})
bets = data.get("bets", {})
outcomes = data.get("outcomes", {})

resultats = []

for match_id, match in matches.items():
    titre = match.get("title", "")
    main_bet_id = match.get("mainBetId")
    if not main_bet_id or str(main_bet_id) not in bets:
        continue

    bet = bets[str(main_bet_id)]
    outcome_ids = bet.get("outcomes", [])
    
    cotes = []
    for o_id in outcome_ids:
        outcome = outcomes.get(str(o_id), {})
        cote_val = outcome.get("odds")
        if cote_val:
            cote_decimale = cote_val if cote_val < 50 else cote_val / 100
            cotes.append(round(cote_decimale, 2))

    if len(cotes) == 3:
        resultats.append({"Match": titre, "Cote 1": cotes[0], "Cote N": cotes[1], "Cote 2": cotes[2]})
    elif len(cotes) == 2:
        resultats.append({"Match": titre, "Cote 1": cotes[0], "Cote N": "-", "Cote 2": cotes[1]})

with open("cotes_winamax.csv", mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Match", "Cote 1", "Cote N", "Cote 2"], delimiter=";")
    writer.writeheader()
    writer.writerows(resultats)

print(f"Succès : {len(resultats)} matchs enregistrés.")
