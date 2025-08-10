import requests
from bs4 import BeautifulSoup
import json
import time

# Transfermarkt La Liga teams page
BASE_URL = "https://www.transfermarkt.com"
LA_LIGA_URL = "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

def get_team_links():
    resp = requests.get(LA_LIGA_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    teams = []
    for row in soup.select('table.items tbody tr'):  # Each team row
        link = row.find('a', class_='vereinprofil_tooltip')
        if link:
            teams.append(BASE_URL + link['href'])
    return teams

def get_players_from_team(team_url):
    resp = requests.get(team_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    players = []
    for row in soup.select('table.items tbody tr'):  # Each player row
        name_tag = row.find('td', class_='hauptlink')
        img_tag = row.find('img', class_='bilderrahmen-fixed')
        if name_tag and img_tag:
            name = name_tag.text.strip()
            image = img_tag['data-src'] if img_tag.has_attr('data-src') else img_tag['src']
            if image.startswith('//'):
                image = 'https:' + image
            players.append({"name": name, "image": image})
    return players

def main():
    all_players = []
    team_links = get_team_links()
    for team_url in team_links:
        all_players.extend(get_players_from_team(team_url))
        time.sleep(1)
    # Remove duplicates by name
    seen = set()
    unique_players = []
    for p in all_players:
        if p['name'] not in seen and p['image']:
            seen.add(p['name'])
            unique_players.append(p)
    # Categorize
    easy = unique_players[:20]
    medium = unique_players[20:40]
    hard = unique_players[40:60]
    categorized = {"easy": easy, "medium": medium, "hard": hard}
    # Update football.json
    with open("/Users/a./github/kpssApi/football.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        if "players" not in data:
            data["players"] = {}
        data["players"]["La Liga"] = categorized
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

if __name__ == "__main__":
    main()
