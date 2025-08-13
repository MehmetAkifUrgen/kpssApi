import requests
import json
import time
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

WIKIPEDIA_BASE = "https://en.wikipedia.org"

# Wikipedia'da hayvan adını arar ve ilk görselin url'sini döndürür

def get_animal_image(animal_name):
    search_url = f"https://en.wikipedia.org/w/index.php?search={animal_name.replace(' ', '+')}"
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    # İlk arama sonucu sayfasına git
    first_link = soup.select_one('.mw-search-result-heading a')
    if first_link:
        page_url = WIKIPEDIA_BASE + first_link['href']
    else:
        # Direkt sayfa varsa
        page_url = f"https://en.wikipedia.org/wiki/{animal_name.replace(' ', '_')}"
    resp = requests.get(page_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    infobox = soup.find('table', class_=re.compile('infobox'))
    if infobox:
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
    with open("../animals.json", "r", encoding="utf-8") as f:
        animals = json.load(f)
    for animal in animals:
        name = animal["animal_name"]
        print(f"Fetching image for {name}...")
        image_url = get_animal_image(name)
        animal["image"] = image_url
        time.sleep(0.5)
    with open("../animals.json", "w", encoding="utf-8") as f:
        json.dump(animals, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
