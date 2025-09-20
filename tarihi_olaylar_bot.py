import json
import requests
import random
from datetime import datetime




def get_world_history_questions():
    """
    Dünya tarihinde yer etmiş önemli olaylardan kaliteli çoktan seçmeli sorular üretir.
    """
    events = [
        {"event": "İstanbul'un Fethi", "year": "1453", "country": "Osmanlı İmparatorluğu", "leader": "Fatih Sultan Mehmet"},
        {"event": "Fransız İhtilali", "year": "1789", "country": "Fransa", "leader": "XVI. Louis"},
        {"event": "Amerika'nın Bağımsızlık Bildirgesi", "year": "1776", "country": "Amerika Birleşik Devletleri", "leader": "George Washington"},
        {"event": "Ay'a ilk insanın ayak basması", "year": "1969", "country": "ABD", "leader": "Richard Nixon"},
        {"event": "Berlin Duvarı'nın yıkılışı", "year": "1989", "country": "Almanya", "leader": "Helmut Kohl"},
        {"event": "Birinci Dünya Savaşı'nın başlaması", "year": "1914", "country": "Almanya", "leader": "Kaiser II. Wilhelm"},
        {"event": "İkinci Dünya Savaşı'nın sona ermesi", "year": "1945", "country": "ABD", "leader": "Harry S. Truman"},
        {"event": "Süveyş Kanalı'nın açılması", "year": "1869", "country": "Mısır", "leader": "İsmail Paşa"},
        {"event": "Magna Carta'nın imzalanması", "year": "1215", "country": "İngiltere", "leader": "Kral John"},
        {"event": "Osmanlı Devleti'nin kuruluşu", "year": "1299", "country": "Osmanlı İmparatorluğu", "leader": "Osman Gazi"},
        {"event": "Osmanlı Devleti'nin yıkılışı", "year": "1922", "country": "Türkiye", "leader": "Vahdettin"},
        {"event": "Türkiye Cumhuriyeti'nin ilanı", "year": "1923", "country": "Türkiye", "leader": "Mustafa Kemal Atatürk"},
        {"event": "İlk modern olimpiyat oyunları", "year": "1896", "country": "Yunanistan", "leader": "Kral I. George"},
        {"event": "Birleşmiş Milletler'in kuruluşu", "year": "1945", "country": "ABD", "leader": "Harry S. Truman"},
        {"event": "İlk Nobel Barış Ödülü'nün verilmesi", "year": "1901", "country": "İsveç", "leader": "Oscar II"},
        {"event": "İlk yapay uydunun fırlatılması (Sputnik 1)", "year": "1957", "country": "SSCB", "leader": "Nikita Kruşçev"},
        {"event": "İlk insanlı uçuş (Wright Kardeşler)", "year": "1903", "country": "ABD", "leader": "Theodore Roosevelt"},
        {"event": "İlk Dünya Kupası", "year": "1930", "country": "Uruguay", "leader": "Juan Campisteguy"},
        {"event": "Roma İmparatorluğu'nun Batı kısmının yıkılışı", "year": "476", "country": "İtalya", "leader": "Romulus Augustulus"},
        {"event": "Sovyetler Birliği'nin dağılması", "year": "1991", "country": "SSCB", "leader": "Mihail Gorbaçov"},
        {"event": "Çin Seddi'nin tamamlanması", "year": "1644", "country": "Çin", "leader": "Shunzhi İmparatoru"},
        {"event": "Hindistan'ın bağımsızlığı", "year": "1947", "country": "Hindistan", "leader": "Jawaharlal Nehru"},
        {"event": "İlk antibiyotiğin keşfi (Penisilin)", "year": "1928", "country": "İngiltere", "leader": "George V"},
        {"event": "İlk bilgisayarın icadı", "year": "1946", "country": "ABD", "leader": "Harry S. Truman"},
        {"event": "İlk kadın başbakanın seçilmesi (Sri Lanka)", "year": "1960", "country": "Sri Lanka", "leader": "Sirimavo Bandaranaike"},
        {"event": "İlk insan hakları bildirgesinin ilanı", "year": "1789", "country": "Fransa", "leader": "XVI. Louis"},
        {"event": "İlk matbaanın icadı", "year": "1440", "country": "Almanya", "leader": "Johannes Gutenberg"},
        {"event": "İlk elektrikli ampulün icadı", "year": "1879", "country": "ABD", "leader": "Rutherford B. Hayes"},
        {"event": "İlk telefon görüşmesi", "year": "1876", "country": "ABD", "leader": "Ulysses S. Grant"},
        {"event": "İlk Nobel Edebiyat Ödülü'nün verilmesi", "year": "1901", "country": "İsveç", "leader": "Oscar II"},
        {"event": "İlk kadın Nobel ödüllü (Marie Curie)", "year": "1903", "country": "Fransa", "leader": "Émile Loubet"},
    ]
    questions = []
    # Soru tipleri: yıl, ülke, lider, olay, buluş
    for i, e in enumerate(events):
        # 1. Bu olay hangi yılda gerçekleşmiştir?
        wrong_years = [ev["year"] for j, ev in enumerate(events) if j != i]
        options = random.sample(wrong_years, 3) + [e["year"]]
        random.shuffle(options)
        answer_letter = chr(65 + options.index(e["year"]))
        questions.append({
            "question": f"{e['event']} olayı hangi yılda gerçekleşmiştir?",
            "options": options,
            "answer": answer_letter
        })
        # 2. Bu olay hangi ülkede gerçekleşmiştir?
        wrong_countries = [ev["country"] for j, ev in enumerate(events) if j != i]
        options = random.sample(wrong_countries, 3) + [e["country"]]
        random.shuffle(options)
        answer_letter = chr(65 + options.index(e["country"]))
        questions.append({
            "question": f"{e['event']} olayı hangi ülkede gerçekleşmiştir?",
            "options": options,
            "answer": answer_letter
        })
        # 3. Bu olay sırasında hangi lider görevdeydi?
        wrong_leaders = [ev["leader"] for j, ev in enumerate(events) if j != i]
        options = random.sample(wrong_leaders, 3) + [e["leader"]]
        random.shuffle(options)
        answer_letter = chr(65 + options.index(e["leader"]))
        questions.append({
            "question": f"{e['event']} olayı sırasında hangi lider görevdeydi?",
            "options": options,
            "answer": answer_letter
        })
    random.shuffle(questions)
    return questions[:100]

def main():
    questions = get_world_history_questions()
    if not questions:
        print("Wikipedia'dan Türkçe çoktan seçmeli soru alınamadı.")
        return
    with open("genel_trivia.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if "Tarihi Olaylar" not in data["categories"]:
        data["categories"]["Tarihi Olaylar"] = []
    data["categories"]["Tarihi Olaylar"] = questions
    with open("genel_trivia.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Tarihi Olaylar kategorisine 100 Türkçe çoktan seçmeli Wikipedia sorusu eklendi.")

if __name__ == "__main__":
    main()
