import csv
import requests

API_KEY = "b07f1923393d0311948f6fb29a279dc3"

# Liste de compétitions courantes
SPORTS = [
    "soccer_france_ligue_one",
    "soccer_epl",
    "soccer_uefa_champs_league",
    "soccer_spain_la_liga"
]

resultats = []

for sport in SPORTS:
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "api_key": API_KEY,
        "regions": "eu",
        "markets": "h2h"
    }
    
    res = requests.get(url, params=params)
    if res.status_code != 200:
        continue
        
    matches = res.json()
    
    for match in matches:
        equipe_dom = match.get("home_team")
        equipe_ext = match.get("away_team")
        match_str = f"{equipe_dom} - {equipe_ext}"
        date_str = match.get("commence_time", "").replace("T", " ").replace("Z", "")
        
        # Recherche du premier bookmaker disponible (priorité à Winamax si présent)
        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            continue
            
        cible = next((b for b in bookmakers if "winamax" in b.get("key", "").lower()), bookmakers[0])
        bookmaker_nom = cible.get("title", "")
        
        c1, cn, c2 = "-", "-", "-"
        for market in cible.get("markets", []):
            if market.get("key") == "h2h":
                for out in market.get("outcomes", []):
                    if out.get("name") == equipe_dom:
                        c1 = out.get("price")
                    elif out.get("name") == equipe_ext:
                        c2 = out.get("price")
                    elif out.get("name") == "Draw":
                        cn = out.get("price")
                        
        resultats.append({
            "Date": date_str,
            "Match": match_str,
            "Bookmaker": bookmaker_nom,
            "Cote 1": c1,
            "Cote N": cn,
            "Cote 2": c2
        })

with open("cotes_winamax.csv", mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["Date", "Match", "Bookmaker", "Cote 1", "Cote N", "Cote 2"], delimiter=";")
    writer.writeheader()
    writer.writerows(resultats)

print(f"Total : {len(resultats)} matchs enregistrés.")
