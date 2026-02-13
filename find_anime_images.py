"""
Script to find missing anime character images in genel_trivia.json using DuckDuckGo search.

Usage:
    pip install duckduckgo-search
    python find_anime_images.py
"""
import json
from duckduckgo_search import DDGS
import time

def find_missing_images():
    file_path = 'genel_trivia.json'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    if "categories" not in data or "Anime Karakterleri" not in data["categories"]:
        print("Error: 'Anime Karakterleri' category not found in JSON.")
        return

    anime_characters = data["categories"]["Anime Karakterleri"]
    updated_count = 0
    
    print(f"Found {len(anime_characters)} characters.")

    with DDGS() as ddgs:
        for char in anime_characters:
            if not char.get("image_url") or char["image_url"] == "":
                name = char.get("name")
                print(f"Searching image for: {name}")
                
                try:
                    results = list(ddgs.images(f"{name} anime character", max_results=1))
                    if results:
                        image_url = results[0]['image']
                        char["image_url"] = image_url
                        print(f"Found: {image_url}")
                        updated_count += 1
                    else:
                        print(f"No results for {name}")
                    
                    # Be polite to the API
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error searching for {name}: {e}")

    if updated_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully updated {updated_count} characters.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    find_missing_images()
