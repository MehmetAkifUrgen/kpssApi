import requests
import json
import time

def fetch_la_liga_players():
    api_url = "https://api.football-data.org/v4/competitions/PD/teams"
    headers = {
        "X-Auth-Token": "7ead6eb7972641aa8c682a3d1fbab181"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch teams from Football Data API")
        return []
    data = response.json()
    players = []
    for team in data.get("teams", []):
        team_id = team["id"]
        squad_url = f"https://api.football-data.org/v4/teams/{team_id}"
        squad_response = requests.get(squad_url, headers=headers)
        if squad_response.status_code == 200:
            squad_data = squad_response.json()
            for player in squad_data.get("squad", []):
                name = player.get("name")
                # Football Data API does not provide player images, so use Transfermarkt as fallback
                image = f"https://img.a.transfermarkt.technology/portrait/header/{player.get('id', 0)}.jpg" if player.get('id') else ""
                if name and image:
                    players.append({"name": name, "image": image})
        time.sleep(1)  # Respect API rate limits
    return players

def categorize_players(players):
    easy = players[:20]
    medium = players[20:40]
    hard = players[40:60]
    return {"easy": easy, "medium": medium, "hard": hard}

def main():
    players = fetch_la_liga_players()
    if not players:
        print("No players found.")
        return
    categorized_players = categorize_players(players)
    with open("/Users/a./github/kpssApi/football.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        if "players" not in data:
            data["players"] = {}
        data["players"]["La Liga"] = categorized_players
        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.truncate()

if __name__ == "__main__":
    main()
