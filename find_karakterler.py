import json
import time
from duckduckgo_search import DDGS

def fetch_character_images():
    characters = [
        "Mario", "Luigi", "Princess Peach", "Bowser", "Yoshi", "Toad (Nintendo)", "Wario", "Donkey Kong",
        "Diddy Kong", "Link (Zelda)", "Princess Zelda", "Ganon", "Samus Aran", "Kirby", "Fox McCloud", "Pikachu",
        "Charizard", "Mewtwo", "Lucario", "Jigglypuff", "Ness (EarthBound)", "Captain Falcon", "Marth", "Roy (Fire Emblem)",
        "Ike (Fire Emblem)", "Pit (Kid Icarus)", "Palutena", "Olimar", "Isabelle (Animal Crossing)", "Tom Nook", "K.K. Slider", "Shulk",
        "Rex (Xenoblade)", "Pyra (Xenoblade)", "Mythra (Xenoblade)", "Inkling", "Min Min", "Spring Man", "Twintelle", "Sonic the Hedgehog",
        "Miles Tails Prower", "Knuckles the Echidna", "Amy Rose", "Doctor Eggman", "Shadow the Hedgehog", "Mega Man",
        "Zero (Mega Man)", "Ryu (Street Fighter)", "Ken Masters", "Chun-Li", "Guile", "M. Bison", "Akuma (Street Fighter)", "Cammy White",
        "Zangief", "Terry Bogard", "Kyo Kusanagi", "Mai Shiranui", "Iori Yagami", "Kazuya Mishima", "Heihachi Mishima",
        "Jin Kazama", "Nina Williams", "Yoshimitsu", "King (Tekken)", "Paul Phoenix", "Marshall Law (Tekken)", "Scorpion (Mortal Kombat)",
        "Sub-Zero (Mortal Kombat)", "Raiden (Mortal Kombat)", "Liu Kang", "Johnny Cage", "Sonya Blade", "Kitana", "Mileena", "Shao Kahn",
        "Solid Snake", "Big Boss", "Raiden (Metal Gear)", "Revolver Ocelot", "Cloud Strife", "Sephiroth",
        "Tifa Lockhart", "Aerith Gainsborough", "Squall Leonhart", "Zidane Tribal", "Lara Croft", "Nathan Drake",
        "Chloe Frazer", "Kratos (God of War)", "Atreus", "Master Chief", "Cortana", "Arbiter", "Marcus Fenix", "Dominic Santiago",
        "Geralt of Rivia", "Ciri", "Yennefer of Vengerberg", "Triss Merigold", "Arthur Morgan", "John Marston",
        "Dutch van der Linde", "Sadie Adler", "Tommy Vercetti", "Carl Johnson", "Niko Bellic", "Trevor Philips", 
        "Michael De Santa", "Franklin Clinton"
    ] # Total 106 characters
    
    # Take exactly 100 characters from the list
    characters = characters[:100]
    results = []
    
    print(f"{len(characters)} karakterin görseli araştırılıyor...")
    
    with DDGS() as ddgs:
        for index, char_name in enumerate(characters):
            # Clean name for the final JSON display
            display_name = char_name.split(' (')[0]
            
            search_query = f"{char_name} character transparent png"
            
            try:
                # Get the first image result
                search_results = list(ddgs.images(
                    keywords=search_query,
                    region="wt-wt",
                    safesearch="on",
                    size="Medium",
                    type_image="photo",
                    max_results=1
                ))
                
                if search_results and len(search_results) > 0:
                    image_url = search_results[0]['image']
                    
                    results.append({
                        "name": display_name,
                        "image_url": image_url
                    })
                    print(f"[{index+1}/100] Bulundu: {display_name}")
                else:
                    print(f"[{index+1}/100] Bulunamadı: {char_name}")
            except Exception as e:
                print(f"[{index+1}/100] Hata oluştu ({char_name}): {e}")
                
            # Sleep to strictly avoid being rate limited
            time.sleep(1.0)

    print(f"\nToplam {len(results)}/{len(characters)} karakter görseli bulundu.")
    
    with open('video_oyun_karakterleri.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
if __name__ == '__main__':
    fetch_character_images()
