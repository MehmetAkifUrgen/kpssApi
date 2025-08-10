
import requests
from bs4 import BeautifulSoup
import json
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

CHAMPIONSHIP_TEAMS = [
    "Leeds United", "Leicester City", "Southampton", "Norwich City", "West Bromwich Albion", "Watford", "Middlesbrough", "Coventry City", "Sunderland", "Stoke City", "Bristol City", "Hull City", "Preston North End", "Millwall", "Cardiff City", "Blackburn Rovers", "Plymouth Argyle", "Queens Park Rangers", "Sheffield Wednesday", "Birmingham City", "Huddersfield Town", "Rotherham United", "Swansea City", "Ipswich Town"
]

WIKIPEDIA_BASE = "https://en.wikipedia.org"

# Try to find the correct Wikipedia page for the football club
def get_team_wikipedia_url(team_name):
    search_url = f"https://en.wikipedia.org/w/index.php?search={team_name.replace(' ', '+')}+F.C."
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Try to get the first search result link
    first_link = soup.select_one('.mw-search-result-heading a')
    if first_link:
        return WIKIPEDIA_BASE + first_link['href']
    # Fallback: try direct page
    direct_url = f"https://en.wikipedia.org/wiki/{team_name.replace(' ', '_')}_F.C."
    resp = requests.get(direct_url, headers=HEADERS)
    if resp.status_code == 200 and 'may refer to:' not in resp.text:
        return direct_url
    # Try without F.C.
    direct_url = f"https://en.wikipedia.org/wiki/{team_name.replace(' ', '_')}"
    resp = requests.get(direct_url, headers=HEADERS)
    if resp.status_code == 200 and 'may refer to:' not in resp.text:
        return direct_url
    return None

# Parse the infobox and get the logo image url
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
    teams_with_logos = []
    for name in CHAMPIONSHIP_TEAMS:
        print(f"Fetching logo for {name}...")
        wiki_url = get_team_wikipedia_url(name)
        logo_url = get_team_logo_url(wiki_url)
        teams_with_logos.append({"name": name, "image": logo_url})
        time.sleep(0.5)
    # football.json'da teams altında Championship olarak ekle
    with open("../football.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        if "teams" not in data:
            data["teams"] = {}
        data["teams"]["Championship"] = teams_with_logos
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

if __name__ == "__main__":
    main()
