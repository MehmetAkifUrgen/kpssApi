import requests
from bs4 import BeautifulSoup
import json
import time
import urllib.parse

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# List of La Liga players (top 60 for demo, you can expand as needed)
LA_LIGA_PLAYERS = [
    "Kylian Mbappé", "Vinícius Júnior", "Erling Haaland", "Rodrygo", "Federico Valverde", "Jude Bellingham", "Robert Lewandowski", "Pedri", "Lamine Yamal", "Álex Baena",
    "Marcos Llorente", "Yeremy Pino", "Dani Ceballos", "Fabián Ruiz", "Robin Le Normand", "Iago Aspas", "Aleix García", "Mikel Merino", "Lucas Vázquez", "Nacho Vidal",
    "Álvaro Odriozola", "Óscar de Marcos", "Jon Moncayola", "Aihen Muñoz", "Iñaki Williams", "Unai Núñez", "Dani García", "Ander Capa", "Raúl García", "Iker Muniain"
]


def get_wikipedia_image(player_name):
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": player_name
    }
    resp = requests.get(WIKIPEDIA_API_URL, params=params, headers=HEADERS)
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "original" in page:
            return page["original"]["source"]
    return ""

def main():
    players_with_images = []
    for name in LA_LIGA_PLAYERS:
        print(f"Fetching image for {name}...")
        image_url = get_wikipedia_image(name)
        players_with_images.append({"name": name, "image": image_url})
        time.sleep(0.5)
    # Categorize
    easy = players_with_images[:10]
    medium = players_with_images[10:20]
    hard = players_with_images[20:30]
    categorized = {"easy": easy, "medium": medium, "hard": hard}
    # Update football.json
    with open("../football.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        if "players" not in data:
            data["players"] = {}
        data["players"]["La Liga"] = categorized
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

if __name__ == "__main__":
    main()
