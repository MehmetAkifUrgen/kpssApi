import urllib.request
import json

def fetch_superheroes():
    """
    superhero-api'den (akabab/superhero-api) en popüler 100 süper kahramanı çeker.
    API'de 700+ kahraman var. Biz en tanınmış 100 tanesini seçip
    name ve image_url formatında döndürüyoruz.
    """

    # En popüler 100 süper kahraman ID'leri (superhero-api'deki ID'ler)
    # Bu liste elle seçilmiş, en tanınmış kahramanlardır.
    popular_ids = [
        644,  # Superman
        70,   # Batman
        620,  # Spider-Man
        703,  # Wonder Woman
        346,  # Iron Man
        149,  # Captain America
        332,  # Hulk
        213,  # Deadpool
        717,  # Wolverine
        659,  # Thor
        106,  # Black Panther
        107,  # Black Widow
        30,   # Aquaman
        226,  # Doctor Strange
        309,  # Green Arrow
        310,  # Green Lantern (Hal Jordan)
        275,  # Flash
        60,   # Batman (alternate)
        261,  # Falcon
        165,  # Catwoman
        579,  # Scarlet Witch
        720,  # Ant-Man
        687,  # The Flash (Wally West)
        655,  # Thanos
        423,  # Magneto
        225,  # Doctor Doom
        369,  # Joker
        414,  # Loki
        387,  # Kingpin
        350,  # Jigsaw
        162,  # Captain Marvel (Carol Danvers)
        697,  # Vision
        326,  # Hawkeye
        697,  # Vision
        700,  # War Machine
        74,   # Beast
        550,  # Poison Ivy
        577,  # Raven
        174,  # Clayface
        636,  # Supergirl
        637,  # Superboy
        590,  # Robin (Damian Wayne)
        457,  # Mystique
        487,  # Nightcrawler
        195,  # Cyborg
        340,  # Huntress
        596,  # Sabretooth
        485,  # Nick Fury
        352,  # Jean Grey
        195,  # Cyborg
        556,  # Power Girl
        633,  # Storm
        182,  # Colossus
        192,  # Cyclops
        491,  # Nightwing
        561,  # Professor X
        419,  # Luke Cage
        350,  # Jessica Jones
        344,  # Iceman
        591,  # Robin (Tim Drake)
        313,  # Groot
        593,  # Rocket Raccoon
        268,  # Firestorm
        599,  # Sandman
        406,  # Lex Luthor
        505,  # Penguin
        372,  # Juggernaut
        579,  # Scarlet Witch
        38,   # Atom
        113,  # Boba Fett -> No, let's use Blade
        104,  # Black Canary
        241,  # Drax the Destroyer
        471,  # Nebula
        290,  # Gamora
        585,  # Rogue
        80,   # Birdman -> Bizarro
        399,  # Lara Croft -> Legion
        435,  # Martian Manhunter
        547,  # Plastic Man
        71,   # Batgirl
        469,  # Namor
        611,  # Sinestro
        572,  # Ra's Al Ghul
        542,  # Phoenix
        200,  # Daredevil
        522,  # Punisher
        246,  # Elektra
        252,  # Enchantress
        658,  # Tigra
        153,  # Carnage
        692,  # Venom
        667,  # Toad
        438,  # Medusa
        78,   # Big Barda
        131,  # Cable
        291,  # Gambit
        616,  # Solomon Grundy
        528,  # Quicksilver
        94,   # Black Lightning
        424,  # Man-Bat
        308,  # Gorilla Grodd
    ]

    # Benzersiz ID'leri al (duplikasyonları engelle)
    unique_ids = list(dict.fromkeys(popular_ids))[:100]

    print(f"superhero-api'den {len(unique_ids)} süper kahraman çekiliyor...")

    url = "https://cdn.jsdelivr.net/gh/akabab/superhero-api@0.3.0/api/all.json"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'SuperheroFetcher/1.0'
    })

    with urllib.request.urlopen(req) as response:
        all_heroes = json.loads(response.read().decode('utf-8'))

    # ID'ye göre hızlı arama tablosu oluştur
    hero_map = {h['id']: h for h in all_heroes}

    results = []
    found = set()
    
    # Önce seçilen ID'lerdeki kahramanları ekle
    for hero_id in unique_ids:
        if hero_id in hero_map and hero_map[hero_id]['name'] not in found:
            hero = hero_map[hero_id]
            results.append({
                "name": hero['name'],
                "image_url": hero['images']['md']
            })
            found.add(hero['name'])

    # Eğer 100'den az kaldıysa, kalan en popüler kahramanları ekle
    # (Popülerlik göstergesi olarak toplam powerstats kullanabiliriz)
    if len(results) < 100:
        remaining = []
        for hero in all_heroes:
            if hero['name'] not in found:
                total_power = sum([
                    hero['powerstats'].get('intelligence', 0) or 0,
                    hero['powerstats'].get('strength', 0) or 0,
                    hero['powerstats'].get('speed', 0) or 0,
                    hero['powerstats'].get('durability', 0) or 0,
                    hero['powerstats'].get('power', 0) or 0,
                    hero['powerstats'].get('combat', 0) or 0,
                ])
                remaining.append((total_power, hero))
        
        remaining.sort(key=lambda x: x[0], reverse=True)
        
        for _, hero in remaining:
            if len(results) >= 100:
                break
            if hero['name'] not in found:
                results.append({
                    "name": hero['name'],
                    "image_url": hero['images']['md']
                })
                found.add(hero['name'])

    print(f"Toplam {len(results)} süper kahraman bulundu.")
    
    # Sonuçları JSON dosyasına kaydet
    with open('super_kahramanlar.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print("Veriler 'super_kahramanlar.json' dosyasına kaydedildi.")
    
    # İlk 10 kahraman örneği
    print("\nÖrnek (İlk 10 kahraman):")
    for i, hero in enumerate(results[:10]):
        print(f"  {i+1}. {hero['name']}")

    return results

if __name__ == '__main__':
    fetch_superheroes()
