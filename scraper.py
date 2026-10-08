import csv
import requests

API_KEY = "b07f1923393d0311948f6fb29a279dc3"
SPORT = "soccer_france_ligue_one"
URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"

params = {
    "api_key": API_KEY,
    "regions": "eu",
    "markets": "h2h",
    "bookmakers": "winamax"
}

print("Récupération des cotes Winamax via l'API...")
response = requests.get(URL, params=params)

if response.status_code != 200:
    print(f"Erreur API : {response.status_code} - {response.text}")
    exit(1)

data = response.json()
resultats = []

for match in data:
    equipe_dom = match.get("home_team")
    equipe_ext = match.get("away_team")
    match_str = f"{equipe_dom} - {equipe_ext}"
    date_str = match.get("commence_time", "").replace("T", " ").replace("Z", "")

    for bookmaker in match.get("bookmakers", []):
        if bookmaker.get("key") == "winamax":
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    outcomes = market.get("outcomes", [])
                    c1, cn, c2 = "-", "-", "-"
                    for out in outcomes:
                        if out.get("name") == equipe_dom:
                            c1 = out.get("price")
                        elif out.get("name") == equipe_ext:
                            c2 = out.get("price")
                        elif out.get("name") == "Draw":
                            cn = out.get("price")
                    resultats.append({
                        "Date": date_str,
                        "Match": match_str,
                        "Cote 1": c1,
                        "Cote N": cn,
                        "Cote 2": c2
                    })

with open("cotes_winamax.csv", mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Date", "Match", "Cote 1", "Cote N", "Cote 2"], delimiter=";")
    writer.writeheader()
    writer.writerows(resultats)

print(f"Succès : {len(resultats)} matchs enregistrés.")
