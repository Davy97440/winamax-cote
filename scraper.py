import csv
from datetime import datetime
from curl_cffi import requests

SPORT_ID = 1  # 1 = Football
URL = f"https://www.winamax.fr/paris-sportifs/api/bets/matches/sports/{SPORT_ID}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.winamax.fr/paris-sportifs",
}

response = requests.get(URL, headers=headers, impersonate="chrome120")
if response.status_code != 200:
    print(f"Erreur : {response.status_code}")
    exit(1)

data = response.json()
matches = data.get("matches", {})
bets = data.get("bets", {})
outcomes = data.get("outcomes", {})

resultats = []

for match_id, match in matches.items():
    titre = match.get("title", "")
    match_start = match.get("matchStart", 0)
    date_str = datetime.fromtimestamp(match_start).strftime("%Y-%m-%d %H:%M") if match_start else ""
    
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
        resultats.append({"Date": date_str, "Match": titre, "Cote 1": cotes[0], "Cote N": cotes[1], "Cote 2": cotes[2]})
    elif len(cotes) == 2:
        resultats.append({"Date": date_str, "Match": titre, "Cote 1": cotes[0], "Cote N": "-", "Cote 2": cotes[1]})

with open("cotes_winamax.csv", mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Date", "Match", "Cote 1", "Cote N", "Cote 2"], delimiter=";")
    writer.writeheader()
    writer.writerows(resultats)

print(f"Succès : {len(resultats)} matchs enregistrés.")
