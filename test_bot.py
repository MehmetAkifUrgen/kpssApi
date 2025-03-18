from soru_dogrulayici import SoruDogrulayiciBot
import json
import time

def test_tek_soru():
    """Tek bir soruyla testi gerçekleştir"""
    print("Tek soru testi başlatılıyor...")
    
    # Test için örnek bir soru
    test_soru = {
        "soru": "Türk adı ilk defa hangi kaynakta geçmiştir?",
        "secenekler": [
            "Bizans",
            "Kaşgarlı Mahmut",
            "Çin",
            "Ziya Gökalp"
        ],
        "dogruCevap": "Çin"
    }
    
    # Bot oluştur
    bot = SoruDogrulayiciBot()
    
    # Internet kontrolünü açık tut
    bot.internet_kontrol = True
    
    # Zamanı ölç
    basla = time.time()
    
    # Soruyu doğrula
    sonuc = bot.soru_dogrula(test_soru, "Test", "Deneme")
    
    # Sonuçları yazdır
    sure = time.time() - basla
    print(f"Test tamamlandı: {sonuc}")
    print(f"Geçen süre: {sure:.2f} saniye")
    
    return sonuc

def test_hata_tespiti():
    """Hatalı bir soru ile testi gerçekleştir"""
    print("\nHata tespiti testi başlatılıyor...")
    
    # Test için hatalı bir soru
    test_soru = {
        "soru": "Türklerin bilinen ilk topluluğu hangisidir?",
        "secenekler": [
            "İskitler",
            "Uygurlar",
            "Hunlar",
            "Köktürkler"
        ],
        "dogruCevap": "İskitler"  # Bilinen hatalar veritabanında "Hunlar" olması gerekir
    }
    
    # Bot oluştur
    bot = SoruDogrulayiciBot()
    
    # Internet kontrolünü kapat (sadece bilinen hata kontrolü yap)
    bot.internet_kontrol = False
    
    # Zamanı ölç
    basla = time.time()
    
    # Soruyu doğrula
    sonuc = bot.soru_dogrula(test_soru, "Test", "Deneme")
    
    # Sonuçları yazdır
    sure = time.time() - basla
    print(f"Test tamamlandı: {sonuc}")
    print(f"Geçen süre: {sure:.2f} saniye")
    
    return sonuc

def test_google_arama():
    """Google araması test et"""
    print("\nGoogle arama testi başlatılıyor...")
    
    bot = SoruDogrulayiciBot()
    sorgu = "Türk adı ilk defa Çin kaynaklarında geçmiştir doğru mu"
    
    basla = time.time()
    sonuc = bot.google_arama(sorgu)
    sure = time.time() - basla
    
    print(f"Google arama sonucu: {sonuc}")
    print(f"Geçen süre: {sure:.2f} saniye")
    
    return sonuc

if __name__ == "__main__":
    print("Soru Doğrulayıcı Bot Test Programı")
    print("================================\n")
    
    # Testleri çalıştır
    test_tek_soru()
    test_hata_tespiti()
    test_google_arama() 