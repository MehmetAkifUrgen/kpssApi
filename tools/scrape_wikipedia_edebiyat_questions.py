import requests
from bs4 import BeautifulSoup
import json
import random
import re
from typing import List, Dict, Optional, Tuple

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}

WIKI_BASE = "https://tr.wikipedia.org"

# Kişiler (yazar/şair) için kategori sayfaları
AUTHOR_CATEGORY_URLS = [
    f"{WIKI_BASE}/wiki/Kategori:T%C3%BCrk_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:T%C3%BCrk_%C5%9Fairler",
]

# Eserler için kategori ve liste sayfaları
WORK_CATEGORY_URLS = [
    f"{WIKI_BASE}/wiki/Kategori:T%C3%BCrk_romanlar%C4%B1",
]
WORK_LIST_PAGES = [
    f"{WIKI_BASE}/wiki/T%C3%BCrk_romanlar%C4%B1_listesi",
]

DIGIT_RE = re.compile(r"\d")
BRACKET_REF_RE = re.compile(r"\[\d+\]")
WS_RE = re.compile(r"\s+")

ROLE_KEYWORDS = [
    ("şair", "Şair"),
    ("yazar", "Yazar"),
    ("oyun yazarı", "Oyun yazarı"),
    ("eleştirmen", "Eleştirmen"),
    ("denemeci", "Denemeci"),
    ("gazeteci", "Gazeteci"),
    ("romancı", "Yazar"),
    ("öykücü", "Yazar"),
    ("senarist", "Senarist"),
    ("edebiyat", "Edebiyatçı"),
]


def fetch(url: str) -> Optional[BeautifulSoup]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return None
    return None


def clean_text(s: str) -> str:
    if not s:
        return ""
    s = BRACKET_REF_RE.sub("", s)
    # Parantez içi yıllar/ek açıklamaları sadeleştir
    s = re.sub(r"\([^)]*\)", "", s)
    s = s.replace("—", " ")
    s = WS_RE.sub(" ", s).strip()
    return s


def get_category_members(url: str, max_members: int = 150) -> List[str]:
    names: List[str] = []
    soup = fetch(url)
    if not soup:
        return names
    pages_div = soup.find(id="mw-pages")
    if not pages_div:
        pages_div = soup
    for a in pages_div.select("a"):
        title = a.get("title")
        href = a.get("href", "")
        if not title or not href.startswith("/wiki/"):
            continue
        if title.startswith("Kategori:") or title.startswith("Dosya:"):
            continue
        if ":" in href[6:]:
            continue
        # Çok kelimeli başlıklar da olabilir (eser isimleri)
        names.append(title)
        if len(names) >= max_members:
            break
    # benzersiz sırayı koru
    return list(dict.fromkeys(names))


def get_links_from_list_page(url: str, max_links: int = 300) -> List[str]:
    titles: List[str] = []
    soup = fetch(url)
    if not soup:
        return titles
    content = soup.select_one("div.mw-parser-output")
    if not content:
        return titles
    for a in content.select("a"):
        title = a.get("title")
        href = a.get("href", "")
        if not title or not href.startswith("/wiki/"):
            continue
        if title.startswith("Kategori:") or title.startswith("Dosya:"):
            continue
        if ":" in href[6:]:
            continue
        titles.append(title)
        if len(titles) >= max_links:
            break
    return list(dict.fromkeys(titles))


def extract_short_desc(soup: BeautifulSoup) -> str:
    sd = soup.select_one("div.shortdescription")
    if sd and sd.get_text(strip=True):
        return sd.get_text(strip=True)
    p = soup.select_one("div.mw-parser-output > p")
    if p and p.get_text(strip=True):
        return p.get_text(strip=True)
    infobox = soup.find("table", class_=re.compile("infobox"))
    if infobox:
        cap = infobox.find("caption")
        if cap and cap.get_text(strip=True):
            return cap.get_text(strip=True)
    return ""


def sanitize_label(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r"\d+", "", text)
    return text.strip(" ,.;:•-–—")


def extract_roles_from_infobox(soup: BeautifulSoup) -> List[str]:
    roles: List[str] = []
    infobox = soup.find("table", class_=re.compile("infobox"))
    if not infobox:
        return roles
    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if not th or not td:
            continue
        key = th.get_text(" ", strip=True).lower()
        if any(k in key for k in ["meslek", "mesleği", "occupation", "görev", "görevi", "görevleri"]):
            raw = td.get_text(", ", strip=True)
            raw = re.sub(r"\([^)]*\)", "", raw)
            parts = [sanitize_label(p) for p in raw.split(",")]
            for p in parts:
                low = p.lower()
                canon = None
                for kw, label in ROLE_KEYWORDS:
                    if kw in low:
                        canon = label
                        break
                if canon:
                    roles.append(canon)
    # benzersiz ilk birkaç
    out: List[str] = []
    for r in roles:
        if r and r not in out:
            out.append(r)
    return out[:3]


def extract_author_of_work(soup: BeautifulSoup) -> Optional[str]:
    infobox = soup.find("table", class_=re.compile("infobox"))
    if not infobox:
        return None
    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if not th or not td:
            continue
        key = th.get_text(" ", strip=True).lower()
        if any(k in key for k in ["yazar", "author", "yazan"]):
            author = td.get_text(" ", strip=True)
            author = clean_text(author)
            # Birden fazla isim virgülle ayrılmış olabilir
            author = author.split(",")[0]
            # Çok uzun olmasın
            if 2 <= len(author) <= 80:
                return author
    return None


def build_person_role_questions(names: List[str], max_q: int = 100) -> List[Dict]:
    questions: List[Dict] = []
    random.shuffle(names)
    for name in names:
        url = f"{WIKI_BASE}/wiki/{name.replace(' ', '_')}"
        soup = fetch(url)
        if not soup:
            continue
        roles = extract_roles_from_infobox(soup)
        if not roles:
            # özet üzerinden anahtar kelime yakala
            desc = extract_short_desc(soup)
            low = desc.lower()
            found = None
            for kw, label in ROLE_KEYWORDS:
                if kw in low:
                    found = label
                    break
            if found:
                roles = [found]
        if not roles:
            continue
        correct = roles[0]
        # Çeldiriciler rol etiketlerinden üret
        role_pool = list({lab for _, lab in ROLE_KEYWORDS})
        random.shuffle(role_pool)
        distractors = [r for r in role_pool if r != correct][:3]
        if len(distractors) < 3:
            continue
        options = [correct] + distractors
        random.shuffle(options)
        q = {
            "question": f"{name} kimdir?",
            "options": options,
            "correct_answer": options.index(correct),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions


def build_work_author_questions(work_titles: List[str], author_pool: List[str], max_q: int = 120) -> List[Dict]:
    questions: List[Dict] = []
    random.shuffle(work_titles)
    # Destek havuzu olarak yazar isimlerini temizle
    author_pool_clean = [w for w in author_pool if 2 <= len(w) <= 80]
    for title in work_titles:
        url = f"{WIKI_BASE}/wiki/{title.replace(' ', '_')}"
        soup = fetch(url)
        if not soup:
            continue
        author = extract_author_of_work(soup)
        if not author:
            continue
        # Çeldiriciler: havuzdan farklı yazarlar
        pool = [a for a in author_pool_clean if a != author]
        if len(pool) < 3:
            continue
        distractors = random.sample(pool, 3)
        options = [author] + distractors
        random.shuffle(options)
        q = {
            "question": f"{title} adlı eserin yazarı kimdir?",
            "options": options,
            "correct_answer": options.index(author),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions

# Yeni: Eser-yazar çiftlerini tek seferde topla

def collect_work_author_pairs(work_titles: List[str], max_items: int = 500) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    count = 0
    for title in work_titles:
        if count >= max_items:
            break
        url = f"{WIKI_BASE}/wiki/{title.replace(' ', '_')}"
        soup = fetch(url)
        if not soup:
            continue
        author = extract_author_of_work(soup)
        if author:
            pairs[title] = author
            count += 1
    return pairs

# Yeni: Eser -> Yazar soruları (çiftlerden)

def build_work_author_questions_from_pairs(pairs: Dict[str, str], max_q: int = 120) -> List[Dict]:
    questions: List[Dict] = []
    items = list(pairs.items())
    random.shuffle(items)
    authors = list({a for a in pairs.values() if 2 <= len(a) <= 80})
    for title, author in items:
        pool = [a for a in authors if a != author]
        if len(pool) < 3:
            continue
        distractors = random.sample(pool, 3)
        options = [author] + distractors
        random.shuffle(options)
        q = {
            "question": f"{title} adlı eserin yazarı aşağıdakilerden hangisidir?",
            "options": options,
            "correct_answer": options.index(author),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions

# Yeni: Yazar -> Eser soruları

def build_author_work_questions_from_pairs(pairs: Dict[str, str], max_q: int = 120) -> List[Dict]:
    questions: List[Dict] = []
    # Yazar -> eserler listesi
    author_to_works: Dict[str, List[str]] = {}
    for work, author in pairs.items():
        author_to_works.setdefault(author, []).append(work)
    authors = [a for a, ws in author_to_works.items() if len(ws) >= 1]
    all_works = list(pairs.keys())
    random.shuffle(authors)
    for author in authors:
        works = author_to_works.get(author, [])
        if not works:
            continue
        correct_work = random.choice(works)
        # Çeldirici eserler: farklı yazarlara ait farklı eserler
        pool = [w for w in all_works if w not in works]
        if len(pool) < 3:
            continue
        distractors = random.sample(pool, 3)
        options = [correct_work] + distractors
        random.shuffle(options)
        q = {
            "question": f"Aşağıdakilerden hangisi {author}’ın eseridir?",
            "options": options,
            "correct_answer": options.index(correct_work),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions

# Yeni: Yazar sayfasından ‘Eserleri/Yapıtları’ başlıklarından eserleri çek

def extract_author_works(soup: BeautifulSoup) -> List[str]:
    titles: List[str] = []
    content = soup.select_one("div.mw-parser-output")
    if not content:
        return titles
    keywords = ["Eserleri", "Yapıtları", "Bibliyografya", "Seçilmiş eserler", "Kitapları", "Eserler"]
    for header in content.find_all(["h2", "h3"]):
        heading_text = header.get_text(" ", strip=True)
        if any(k.lower() in heading_text.lower() for k in keywords):
            # Başlıktan sonra gelen listeleri topla, bir sonraki başlığa kadar
            for sib in header.find_all_next():
                if sib.name in ["h2", "h3"]:
                    break
                if sib.name == "ul":
                    for li in sib.find_all("li", recursive=False):
                        a = li.find("a")
                        t = a.get("title") if a and a.get("title") else li.get_text(" ", strip=True)
                        t = clean_text(t)
                        if t and not t.startswith("Liste") and len(t) <= 120:
                            titles.append(t)
            break
    # benzersiz ve sınırlı
    return list(dict.fromkeys(titles))[:30]

# Yeni: Yazar listelerinden eser–yazar çiftlerini üret

def collect_pairs_from_authors(author_names: List[str], max_authors: int = 250) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    processed = 0
    for name in author_names:
        if processed >= max_authors:
            break
        url = f"{WIKI_BASE}/wiki/{name.replace(' ', '_')}"
        soup = fetch(url)
        if not soup:
            continue
        works = extract_author_works(soup)
        if works:
            for w in works:
                pairs.setdefault(w, name)
            processed += 1
    return pairs


def collect_authors() -> Tuple[List[str], Dict[str, List[str]]]:
    # Tüm kişi isimleri ve kategori bazlı isimler (Şair/Yazar)
    all_persons: List[str] = []
    cat_persons: Dict[str, List[str]] = {"Türk yazar": [], "Türk şair": []}
    for url in AUTHOR_CATEGORY_URLS:
        names = get_category_members(url, max_members=200)
        all_persons.extend(names)
        if "T%C3%BCrk_yazarlar" in url:
            cat_persons["Türk yazar"].extend(names)
        elif "%C5%9Fairler" in url:
            cat_persons["Türk şair"].extend(names)
    # benzersiz
    all_persons = list(dict.fromkeys(all_persons))
    for k in list(cat_persons.keys()):
        cat_persons[k] = list(dict.fromkeys(cat_persons[k]))
    return all_persons, cat_persons


# Dünya edebiyatı: yazar ve roman kategorileri (seçki, trwiki’de mevcut olanlar toplanır, bulunamazsa boş döner)
WORLD_AUTHOR_CATEGORY_URLS = [
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0ngiliz_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:Amerikal%C4%B1_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:Frans%C4%B1z_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:Rus_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:Alman_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0spanyol_yazarlar",
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0talyan_yazarlar",
]

WORLD_WORK_CATEGORY_URLS = [
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0ngiliz_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:Amerikan_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:Frans%C4%B1z_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:Rus_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:Alman_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0spanyol_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:%C4%B0talyan_romanlar%C4%B1",
    f"{WIKI_BASE}/wiki/Kategori:Klasik_romanlar",
]


def collect_world_authors() -> List[str]:
    names: List[str] = []
    for url in WORLD_AUTHOR_CATEGORY_URLS:
        names.extend(get_category_members(url, max_members=200))
    return list(dict.fromkeys(names))

# collect_works’i dünya kategorilerini de kapsayacak şekilde genişlet

def collect_works() -> List[str]:
    works: List[str] = []
    for url in WORK_CATEGORY_URLS:
        works.extend(get_category_members(url, max_members=300))
    # Dünya roman kategorileri
    for url in WORLD_WORK_CATEGORY_URLS:
        works.extend(get_category_members(url, max_members=300))
    for url in WORK_LIST_PAGES:
        works.extend(get_links_from_list_page(url, max_links=500))
    # Temizlik: çok genel veya kişi sayfalarını eleme denemesi
    out: List[str] = []
    for w in works:
        ww = clean_text(w)
        if not ww:
            continue
        if ww.startswith("Liste"):
            continue
        if len(ww) > 120:
            continue
        out.append(ww)
    return list(dict.fromkeys(out))

# --- Popülerlik skoru: sayfa metin uzunluğu, iç link sayısı, infobox, kaynak sayısı, kategori sayısı ---
_soup_cache: Dict[str, BeautifulSoup] = {}

def fetch_title_soup(title: str) -> Optional[BeautifulSoup]:
    if title in _soup_cache:
        return _soup_cache[title]
    url = f"{WIKI_BASE}/wiki/{title.replace(' ', '_')}"
    soup = fetch(url)
    if soup:
        _soup_cache[title] = soup
    return soup


def compute_popularity_from_soup(soup: BeautifulSoup) -> float:
    try:
        text_len = len(soup.get_text(" ", strip=True))
        links = soup.select('div.mw-parser-output a[href^="/wiki/"]')
        link_count = len(links)
        infobox = 1.0 if soup.find("table", class_=re.compile("infobox")) else 0.0
        refs = len(soup.select("ol.references li"))
        cats = len(soup.select("#mw-normal-catlinks li"))
        # Ağırlıklar deneysel
        score = 0.0004 * text_len + 0.004 * link_count + 0.5 * infobox + 0.02 * refs + 0.01 * cats
        return float(score)
    except Exception:
        return 0.0


def compute_popularity_for_title(title: str) -> float:
    soup = fetch_title_soup(title)
    if not soup:
        return 0.0
    return compute_popularity_from_soup(soup)

# Sıralı (popülerliğe göre) pair listesi üret

def rank_pairs_by_popularity(pairs: Dict[str, str], max_items: int = 2500) -> Tuple[List[Tuple[str, str, float]], List[Tuple[str, float]], List[Tuple[str, float]]]:
    ranked_pairs: List[Tuple[str, str, float]] = []
    work_scores: Dict[str, float] = {}
    author_scores: Dict[str, float] = {}
    items = list(pairs.items())[:max_items]
    for work, author in items:
        if work not in work_scores:
            work_scores[work] = compute_popularity_for_title(work)
        if author not in author_scores:
            author_scores[author] = compute_popularity_for_title(author)
        score = 0.6 * work_scores[work] + 0.4 * author_scores[author]
        ranked_pairs.append((work, author, score))
    ranked_pairs.sort(key=lambda x: x[2], reverse=True)
    ranked_authors = sorted(author_scores.items(), key=lambda x: x[1], reverse=True)
    ranked_works = sorted(work_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_pairs, ranked_authors, ranked_works

# Popülerlik sıralı pairlerden soru üreticiler

def build_work_author_questions_ranked(ranked_pairs: List[Tuple[str, str, float]], ranked_authors: List[Tuple[str, float]], max_q: int = 200) -> List[Dict]:
    questions: List[Dict] = []
    author_order = [a for a, _ in ranked_authors]
    for work, author, _ in ranked_pairs:
        pool = [a for a in author_order if a != author]
        if len(pool) < 3:
            continue
        distractors = pool[:3] if len(pool) >= 3 else pool
        distractors = random.sample(pool[:50] if len(pool) > 50 else pool, 3)
        options = [author] + distractors
        random.shuffle(options)
        q = {
            "question": f"{work} adlı eserin yazarı aşağıdakilerden hangisidir?",
            "options": options,
            "correct_answer": options.index(author),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions


def build_author_work_questions_ranked(ranked_pairs: List[Tuple[str, str, float]], ranked_works: List[Tuple[str, float]], max_q: int = 200) -> List[Dict]:
    questions: List[Dict] = []
    # yazar -> popüler eserler (ranked_pairs’ten)
    author_to_works: Dict[str, List[str]] = {}
    for work, author, _ in ranked_pairs:
        author_to_works.setdefault(author, []).append(work)
    work_order = [w for w, _ in ranked_works]
    # yazarları popüler pair’lerden sırayla dolaş
    seen_authors: set = set()
    for work, author, _ in ranked_pairs:
        if author in seen_authors:
            continue
        seen_authors.add(author)
        works = author_to_works.get(author, [])
        if not works:
            continue
        correct_work = works[0]
        pool = [w for w in work_order if w not in works]
        if len(pool) < 3:
            continue
        distractors = random.sample(pool[:60] if len(pool) > 60 else pool, 3)
        options = [correct_work] + distractors
        random.shuffle(options)
        q = {
            "question": f"Aşağıdakilerden hangisi {author}’ın eseridir?",
            "options": options,
            "correct_answer": options.index(correct_work),
            "category": "Edebiyat",
            "source_id": "internet_wikipedia",
        }
        questions.append(q)
        if len(questions) >= max_q:
            break
    return questions


def build_category_membership_questions(cat_persons: Dict[str, List[str]], max_q: int = 80) -> List[Dict]:
    qs: List[Dict] = []
    labels = list(cat_persons.keys())
    # Her etiket için karşı havuz
    other_pools: Dict[str, List[str]] = {}
    for lbl in labels:
        others: List[str] = []
        for lbl2, names2 in cat_persons.items():
            if lbl2 == lbl:
                continue
            others.extend(names2)
        other_pools[lbl] = list(dict.fromkeys(others))

    round_guard = 0
    while len(qs) < max_q and round_guard < max_q * 5:
        round_guard += 1
        progress = False
        for lbl in labels:
            names = cat_persons.get(lbl, [])
            o_pool = other_pools.get(lbl, [])
            if len(names) < 1 or len(o_pool) < 3:
                continue
            correct = random.choice(names)
            distractors = random.sample(o_pool, 3)
            options = [correct] + distractors
            random.shuffle(options)
            q = {
                "question": f"Aşağıdakilerden hangisi bir {lbl}dir?",
                "options": options,
                "correct_answer": options.index(correct),
                "category": "Edebiyat",
                "source_id": "internet_wikipedia",
            }
            qs.append(q)
            progress = True
            if len(qs) >= max_q:
                break
        if not progress:
            break
    return qs


def main():
    # 1) Kişileri ve kişi kategorilerini topla
    persons, cat_persons = collect_authors()
    world_authors = collect_world_authors()
    persons_all = list(dict.fromkeys(persons + world_authors))
    print(f"[Bilgi] Kişi toplamı: {len(persons_all)} (TR+Dünya)")

    # 2) Eserleri topla (TR + Dünya)
    works_all = collect_works()
    print(f"[Bilgi] Eser toplamı: {len(works_all)} (TR+Dünya)")

    # 2.1) Eser–yazar eşleşmeleri
    pairs_from_works = collect_work_author_pairs(works_all)
    print(f"[Bilgi] Eser–yazar eşleşmesi (eser sayfası): {len(pairs_from_works)}")

    # 2.2) Yazar sayfalarından genişlet
    pairs_from_authors_all = collect_pairs_from_authors(persons_all, max_authors=350)
    print(f"[Bilgi] Eser–yazar eşleşmesi (yazar sayfası): {len(pairs_from_authors_all)}")

    # Türkiye/Dünya ayrımı: basit kural — Türk ş, ç, ğ, ı, ö, ü harfli yazar veya AUTHOR_CATEGORY_URLS’te bulunan kişi adları TR say, aksi Dünya say
    turkish_person_set = set(persons)  # Türk kategorilerinden gelenler
    turkish_chars = set("çğıöşüÇĞİÖŞÜ")

    def is_turkish_author(name: str) -> bool:
        if name in turkish_person_set:
            return True
        return any(ch in name for ch in turkish_chars)

    # Birleşik eşleşmeler
    pairs_all: Dict[str, str] = {}
    pairs_all.update(pairs_from_works)
    pairs_all.update(pairs_from_authors_all)
    print(f"[Bilgi] Birleşik eşleşme: {len(pairs_all)}")

    # TR ve Dünya olarak böl
    pairs_tr: Dict[str, str] = {}
    pairs_world: Dict[str, str] = {}
    for work, author in pairs_all.items():
        if is_turkish_author(author):
            pairs_tr[work] = author
        else:
            pairs_world[work] = author

    print(f"[Bilgi] TR pair: {len(pairs_tr)} | Dünya pair: {len(pairs_world)}")

    # 3) Her grup için popülerliğe göre sıralama
    ranked_pairs_tr, ranked_authors_tr, ranked_works_tr = rank_pairs_by_popularity(pairs_tr, max_items=2500)
    ranked_pairs_world, ranked_authors_world, ranked_works_world = rank_pairs_by_popularity(pairs_world, max_items=2500)

    # 4) Her gruptan 150’şer soru: her grupta 75 eser→yazar + 75 yazar→eser
    tr_work_qs = build_work_author_questions_ranked(ranked_pairs_tr, ranked_authors_tr, max_q=75)
    tr_author_work_qs = build_author_work_questions_ranked(ranked_pairs_tr, ranked_works_tr, max_q=75)

    world_work_qs = build_work_author_questions_ranked(ranked_pairs_world, ranked_authors_world, max_q=75)
    world_author_work_qs = build_author_work_questions_ranked(ranked_pairs_world, ranked_works_world, max_q=75)

    questions: List[Dict] = []
    questions.extend(tr_work_qs)
    questions.extend(tr_author_work_qs)
    questions.extend(world_work_qs)
    questions.extend(world_author_work_qs)

    # Mükerrerleri temizle
    def qkey(q: Dict) -> str:
        return q.get("question", "") + "||" + "||".join(q.get("options", []))
    uniq: Dict[str, Dict] = {}
    for q in questions:
        uniq[qkey(q)] = q
    questions = list(uniq.values())

    # 5) 150+150 = 300 hedef
    target = 300
    if len(questions) >= target:
        # Karışık sıraya koy
        random.shuffle(questions)
        questions = questions[:target]
    else:
        random.shuffle(questions)

    out_path = "edebiyat_sorular_internet.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    # Özet ve örnekler
    print(f"Toplam oluşturulan soru: {len(questions)}")
    print(f"[Özet] TR soruları: {len(tr_work_qs) + len(tr_author_work_qs)} | Dünya soruları: {len(world_work_qs) + len(world_author_work_qs)}")
    for q in random.sample(questions, min(5, len(questions))):
        print(q["question"])
        print("Seçenekler:", q["options"]) 
        print("Doğru şık:", q["options"][q["correct_answer"]])
        print("-")


if __name__ == "__main__":
    main()