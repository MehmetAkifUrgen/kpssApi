import requests
from bs4 import BeautifulSoup
import json
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

WIKIPEDIA_BASE = "https://en.wikipedia.org"
SEASON_URL = "https://en.wikipedia.org/wiki/2025%E2%80%9326_Premier_League"

def get_premier_league_teams():
    resp = requests.get(SEASON_URL, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    teams = set()
    # 1. Tüm "Teams" veya "Clubs" başlığı altındaki bağlantıları bul
    for header in soup.find_all(['h2', 'h3']):
        if header.get_text().strip().lower().startswith('teams') or header.get_text().strip().lower().startswith('clubs'):
            ul = header.find_next_sibling(['ul', 'ol'])
            if ul:
                for li in ul.find_all('li'):
                    link = li.find('a')
                    if link and link.get('title'):
                        teams.add(link.get('title'))
    # 2. Eğer yukarıda bulunamazsa, sayfadaki tüm wikitable'lardaki ilk sütun linklerini de ekle (yedek)
    if not teams:
        for table in soup.find_all('table', class_='wikitable'):
            for row in table.find_all('tr')[1:]:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                team_cell = cells[0]
                link = team_cell.find('a')
                if link and link.get('title'):
                    teams.add(link.get('title'))
    return list(teams)

def get_team_wikipedia_url(team_name):
    search_url = f"https://en.wikipedia.org/w/index.php?search={team_name.replace(' ', '+')}"
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    first_link = soup.select_one('.mw-search-result-heading a')
    if first_link:
        return WIKIPEDIA_BASE + first_link['href']
    # Fallback: try direct page
    direct_url = f"https://en.wikipedia.org/wiki/{team_name.replace(' ', '_')}"
    resp = requests.get(direct_url, headers=HEADERS)
    if resp.status_code == 200 and 'may refer to:' not in resp.text:
        return direct_url
    return None

def get_team_logo_url(wiki_url):
    if not wiki_url:
        return ""
    resp = requests.get(wiki_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find('table', class_=re.compile('infobox'))
    if not infobox:
        return ""
    img = infobox.find('img')
    if img and img['src']:
        src = img['src']
        if src.startswith('//'):
            return 'https:' + src
        elif src.startswith('http'):
            return src
        else:
            return WIKIPEDIA_BASE + src
    return ""

def main():
    teams = get_premier_league_teams()
    teams_with_logos = []
    for name in teams:
        print(f"Fetching logo for {name}...")
        wiki_url = get_team_wikipedia_url(name)
        logo_url = get_team_logo_url(wiki_url)
        teams_with_logos.append({"name": name, "image": logo_url})
        time.sleep(0.5)
    # football.json'da teams altında Premier League olarak ekle
    with open("../football.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        if "teams" not in data:
            data["teams"] = {}
        data["teams"]["Premier League"] = teams_with_logos
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

if __name__ == "__main__":
    main()
