import json

# Bu script, birden fazla tekrar eden ve 'image' alanı olmayan hayvanları siler.
def main():
    with open("../animals.json", "r", encoding="utf-8") as f:
        animals = json.load(f)

    seen = set()
    unique_animals = []
    for animal in animals:
        key = animal["animal_name"].strip().lower()
        has_image = bool(animal.get("image"))
        if key not in seen:
            if has_image or not has_image:
                unique_animals.append(animal)
            seen.add(key)
        else:
            # Eğer tekrar eden ve image yoksa ekleme
            if has_image:
                # Eğer tekrar edenin image'ı varsa, eskiyi silip yeniyi ekle
                for i, a in enumerate(unique_animals):
                    if a["animal_name"].strip().lower() == key and not a.get("image"):
                        unique_animals[i] = animal
                        break

    # Sonra tekrar eden ve image'ı olmayanları sil
    filtered = [a for a in unique_animals if a.get("image")]

    with open("../animals.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
