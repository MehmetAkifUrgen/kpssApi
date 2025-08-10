import requests
import json
import time

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

SUPER_LIG_PLAYERS = [
    # easy
    "Victor Osimhen", "Leroy Sané", "Barış Alper Yılmaz", "Youssef En-Nesyri", "Jhon Durán", "Sofyan Amrabat", "Sebastian Szymański", "Davinson Sánchez", "Lucas Torreira",
    # medium
    "Fred", "Cengiz Ünder", "İrfan Can Kahveci", "Uğurcan Çakır", "Ernest Muci", "Wilfred Ndidi", "Danylo Sikan", "Talisca", "Oğuz Aydın",
    # hard
    "Çağlar Söyüncü", "Edin Visca", "Cenk Tosun", "Milot Rashica", "Okay Yokuşlu", "Batista Mendy"
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
    for name in SUPER_LIG_PLAYERS:
        print(f"Fetching image for {name}...")
        image_url = get_wikipedia_image(name)
        players_with_images.append({"name": name, "image": image_url})
        time.sleep(0.5)
    easy = players_with_images[:9]
    medium = players_with_images[9:18]
    hard = players_with_images[18:]
    categorized = {"easy": easy, "medium": medium, "hard": hard}
    with open("../football.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
        if "players" not in data:
            data["players"] = {}
        data["players"]["Süper Lig"] = categorized
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.truncate()

if __name__ == "__main__":
    main()
