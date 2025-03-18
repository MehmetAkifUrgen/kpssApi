import json

# Şüpheli soruları yükle
with open('suphe_edilen_sorular.json', 'r', encoding='utf-8') as f:
    suphe_edilen = json.load(f)

# Temiz soruları yükle
with open('temiz_sorular.json', 'r', encoding='utf-8') as f:
    temiz = json.load(f)

# Temiz soru sayısı
temiz_sayisi = 0
for kategori, alt_kategoriler in temiz.get('soruCozumu', {}).items():
    for alt_kategori, sorular in alt_kategoriler.items():
        temiz_sayisi += len(sorular)

print(f"Toplam şüpheli soru sayısı: {len(suphe_edilen)}")
print(f"Toplam temiz soru sayısı: {temiz_sayisi}")
print(f"Toplam soru sayısı: {len(suphe_edilen) + temiz_sayisi}")

# Şüpheli soru detayları
print("\nŞüpheli sorular:")
for i, soru in enumerate(suphe_edilen, 1):
    print(f"{i}. {soru['kategori']} - {soru['alt_kategori']}: {soru['soru']['soru']}")
    print(f"   Doğru cevap: {soru['soru']['dogruCevap']}")
    print() 