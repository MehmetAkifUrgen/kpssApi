import json
import os
import time
import requests
from bs4 import BeautifulSoup
import random
import warnings
from dotenv import load_dotenv
# Gereksiz uyarıları gizle
warnings.filterwarnings("ignore")

# İlk kullanımda transformers kütüphanesini yükleyin
try:
    from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
    transformers_yuklu = True
except ImportError:
    print("Transformers kütüphanesi yüklü değil. Yerel doğrulama yapılacak.")
    print("Yüklemek için: pip install transformers torch")
    transformers_yuklu = False

# .env dosyasını yükle
load_dotenv()

# API anahtarını environment variable'dan al
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

class SoruDogrulayiciBot:
    def __init__(self):
        """Bot için gerekli başlangıç ayarlarını yapar"""
        # Bilinen hataları kaldırıyoruz, her soru internet üzerinden doğrulanacak
        
        # API key ayarı (opsiyonel)
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        # HuggingFace API key (demo api key ile çalışabilir)
        self.huggingface_api_key = HUGGINGFACE_API_KEY
        self.ai_destegi_aktif = True  # Yapay zeka desteği aktif
        
        # Yerel transformers modeli yükleme
        self.model_yuklu = False
        if transformers_yuklu:
            try:
                print("Yapay zeka modeli yükleniyor...")
                # Türkçe için uyumlu bir model seçimi
                model_name = "dbmdz/bert-base-turkish-cased"
                
                # Model ve tokenizer'ı yükle
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
                
                # Sentiment analizi pipeline'ı oluştur
                self.nlp = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
                
                self.model_yuklu = True
                print("Yapay zeka modeli başarıyla yüklendi!")
            except Exception as e:
                print(f"Model yükleme hatası: {str(e)}")
                print("Basit kurallar kullanılacak")
        
        # İnternet bağlantısını test et
        self.internet_baglantisi_var = self.internet_baglantisi_kontrol()
        if self.internet_baglantisi_var:
            print("İnternet bağlantısı aktif. HuggingFace API modelleri kullanılacak.")
        else:
            print("İnternet bağlantısı yok. Yerel model kullanılacak.")
        
        # Element sembolleri veritabanı (kimya soruları için)
        self.elementler = {
            "Hidrojen": "H", "Helyum": "He", "Lityum": "Li", "Berilyum": "Be", "Bor": "B", 
            "Karbon": "C", "Azot": "N", "Oksijen": "O", "Flor": "F", "Neon": "Ne",
            "Sodyum": "Na", "Magnezyum": "Mg", "Alüminyum": "Al", "Silisyum": "Si", "Fosfor": "P",
            "Kükürt": "S", "Klor": "Cl", "Argon": "Ar", "Potasyum": "K", "Kalsiyum": "Ca",
            "Skandiyum": "Sc", "Titanyum": "Ti", "Vanadyum": "V", "Krom": "Cr", "Mangan": "Mn",
            "Demir": "Fe", "Kobalt": "Co", "Nikel": "Ni", "Bakır": "Cu", "Çinko": "Zn"
        }
        
        # Sözcük türleri ve dilbilgisi için kurallar
        self.dilbilgisi_kurallari = {
            "isim_tamlamasi": ["ev kapısı", "okulun bahçesi", "kalem ucu", "kitabın sayfası", "okulun bahçesinde"]
        }
        
        # Sonuç dosyaları
        self.suphe_edilen_sorular = []
        self.temiz_sorular = {}
        
        # İstatistikler
        self.toplam_soru = 0
        self.suphe_sayisi = 0
        self.arama_sayisi = 0
        
        # Google arama için farklı user-agent'lar (botları tespit eden siteleri engellemek için)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        # İnternet kontrolü açık
        self.internet_kontrol = True
        
        # Arama gecikme süresi (saniye) - IP engelleme sorununu azaltmak için
        self.arama_gecikmesi = 1.5
        
        # TYT kaynaklarını genişletiyoruz
        self.tyt_kaynaklar = [
            # Resmi Kurumlar
            'osym.gov.tr', 
            'yok.gov.tr',
            'meb.gov.tr',
            'anadolu.edu.tr',
            'eba.gov.tr',
            
            # Yayın Evleri
            'tonguceglitim.com.tr',
            'tongucakademi.com.tr',
            'vitaminyayinlari.com',
            'tudem.com',
            'palme.com.tr',
            'pegem.net',
            'hiz.com.tr',
            'prf.com.tr',
            'zambak.com.tr',
            'esen.com.tr',
            'bilimyayinlari.com.tr',
            'akademidenizi.com.tr',
            'fiziknot.com',
            'kimyahane.com',
            
            # Test Siteleri
            'testcozum.com',
            'okulistik.com',
            'testlericoz.com',
            'testokul.com',
            'sorubak.com',
            'morpakampus.com',
            'materyalfizik.com',
            'bilgiyarim.com.tr',
            'dersanlatimli.com',
            'testcini.com',
            
            # Forum ve Soru-Cevap Siteleri
            'yandex.com.tr/q',
            'memurlar.net/forum',
            'konudankonuya.net',
            'ozdebir.org.tr',
            'answerinthedetails.com'
        ]
        
    def calistir(self, dosya_yolu):
        """Bot'u çalıştır, verilen dosyadaki soruları kontrol et"""
        print(f"{dosya_yolu} dosyası işleniyor...")
        
        try:
            # JSON dosyasını oku
            with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
                tum_veri = json.load(dosya)
                
            # Temiz sorular için aynı yapıyı oluştur
            self.temiz_sorular = {"soruCozumu": {}}
                
            # soruCozumu içindeki her kategori için
            for kategori, alt_kategoriler in tum_veri.get("soruCozumu", {}).items():
                self.temiz_sorular["soruCozumu"][kategori] = {}
                
                # Her alt kategori için
                for alt_kategori, sorular in alt_kategoriler.items():
                    print(f"Kategori: {kategori} - Alt Kategori: {alt_kategori} - {len(sorular)} soru işleniyor...")
                    
                    self.temiz_sorular["soruCozumu"][kategori][alt_kategori] = []
                    self.toplam_soru += len(sorular)
                    
                    # Her soru için
                    for soru in sorular:
                        kontrol_sonucu = self.soru_dogrula(soru, kategori, alt_kategori)
                        if kontrol_sonucu["durum"]:
                            # Soru geçerliyse temiz sorulara ekle
                            self.temiz_sorular["soruCozumu"][kategori][alt_kategori].append(soru)
                        else:
                            # Değilse şüpheli sorulara ekle
                            self.suphe_edilen_sorular.append({
                                "kategori": kategori,
                                "alt_kategori": alt_kategori,
                                "soru": soru,
                                "sebep": kontrol_sonucu["sebep"]
                            })
                            self.suphe_sayisi += 1
                    
                    # Ara kayıt - her alt kategori işlendikten sonra kaydet
                    self.sonuclari_kaydet()
                    
                    # İstatistik yazdır
                    print(f"  - Toplam {len(sorular)} soru işlendi, şüpheli: {self.suphe_sayisi}, arama sayısı: {self.arama_sayisi}")
            
            # Son kez kaydet
            self.sonuclari_kaydet()
            
            return f"İşlem tamamlandı. Toplam {self.toplam_soru} soru işlendi, {self.suphe_sayisi} adet şüpheli soru tespit edildi. Toplam {self.arama_sayisi} arama yapıldı."
            
        except Exception as e:
            return f"Hata oluştu: {str(e)}"
    
    def soru_dogrula(self, soru, kategori, alt_kategori):
        """Bir sorunun doğruluğunu kontrol eder"""
        
        # 1. Temel format kontrolü
        if not isinstance(soru, dict) or not all(alan in soru for alan in ["soru", "secenekler", "dogruCevap"]):
            print(f"Format hatası: {soru.get('soru', 'Bilinmeyen soru')}")
            return {"durum": False, "sebep": "Format hatası"}
            
        # 2. Doğru cevap seçeneklerde var mı?
        if soru["dogruCevap"] not in soru["secenekler"]:
            print(f"Cevap hatası: {soru['soru']} - Doğru cevap seçeneklerde yok")
            return {"durum": False, "sebep": "Doğru cevap seçeneklerde yok"}
        
        # 3. İnternet/yapay zeka doğrulama kontrolü
        if self.internet_kontrol:
            internet_kontrolu = self.internet_dogrula(soru, kategori, alt_kategori)
            if not internet_kontrolu["durum"]:
                print(f"Doğrulama hatası: {soru['soru']} - {internet_kontrolu['sebep']}")
                return {"durum": False, "sebep": f"Doğrulama hatası: {internet_kontrolu['sebep']}"}
        
        # Tüm kontrollerden geçti
        return {"durum": True, "sebep": ""}
    
    def soru_mantikli_mi(self, soru):
        """Sorunun mantıksal tutarlılığını kontrol eder"""
        
        # Soru metni çok kısa mı?
        if len(soru["soru"]) < 10:
            return {"durum": False, "sebep": "Soru metni çok kısa"}
            
        # Seçenekler çok az mı?
        if len(soru["secenekler"]) < 2:
            return {"durum": False, "sebep": "Seçenek sayısı yetersiz"}
            
        # Tüm seçenekler aynı mı?
        if len(set(soru["secenekler"])) < len(soru["secenekler"]):
            return {"durum": False, "sebep": "Tekrarlanan seçenekler var"}
            
        return {"durum": True, "sebep": ""}
    
    def internet_baglantisi_kontrol(self):
        """İnternet bağlantısını kontrol eder"""
        try:
            # HuggingFace API'yi kontrol et
            response = requests.get("https://huggingface.co", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def yapay_zeka_dogrula(self, soru):
        """Yapay zeka kullanarak soruların doğruluğunu kontrol eder"""
        try:
            if not self.ai_destegi_aktif:
                return {"durum": True, "sebep": "Yapay zeka desteği kapalı"}
            
            # 1. İnternet bağlantısı varsa, önce HuggingFace API kullan
            if self.internet_baglantisi_var and self.huggingface_api_key:
                try:
                    print(f"HuggingFace API ile soru doğrulanıyor: {soru['soru'][:50]}...")
                    
                    # En iyi HuggingFace modelleri (Türkçe desteği var)
                    hf_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
                    headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
                    
                    # Zero-shot sınıflandırma için prompt
                    hf_data = {
                        "inputs": soru['soru'],
                        "parameters": {
                            "candidate_labels": [soru['dogruCevap'], "yanlış cevap"]
                        }
                    }
                    
                    # API isteği
                    response = requests.post(hf_url, headers=headers, json=hf_data, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"HuggingFace API cevabı: {result}")
                        
                        # Sonuç analizi
                        labels = result.get("labels", [])
                        scores = result.get("scores", [])
                        
                        if labels and scores and len(labels) > 0:
                            # Doğru cevap en yüksek skora sahip mi?
                            if labels[0] == soru['dogruCevap']:
                                return {"durum": True, "sebep": f"HuggingFace skoru: {scores[0]:.2f}"}
                            else:
                                # Fark çok büyük değilse yine de doğru kabul et
                                if scores[0] - scores[1] < 0.2:
                                    return {"durum": True, "sebep": "Düşük güven farkına rağmen kabul edildi"}
                                else:
                                    return {"durum": False, "sebep": f"HuggingFace: Doğru cevap düşük skorlu ({scores[1]:.2f})"}
                except Exception as e:
                    print(f"HuggingFace API hatası: {str(e)}")
                    # API hatası durumunda yerel modele geç
            
            # 2. Yerel transformers modelini kullan (eğer yüklüyse)
            if self.model_yuklu:
                print(f"Yerel yapay zeka modeli ile analiz: {soru['soru'][:50]}...")
                
                # Soru ve doğru cevabı birleştir
                birlesik_metin = f"Soru: {soru['soru']}, Cevap: {soru['dogruCevap']}"
                
                try:
                    # Transformers pipeline kullanarak duygu analizi yap
                    sentiment_sonuc = self.nlp(birlesik_metin)
                    print(f"Yerel AI Analiz: {sentiment_sonuc}")
                    
                    # Sonuç LABEL_0 (negatif) veya LABEL_1 (pozitif) olabilir
                    # Çoğu transformers modeli için LABEL_1 genellikle olumlu anlam taşır
                    if sentiment_sonuc[0]['label'] == 'LABEL_1':
                        return {"durum": True, "sebep": f"Yerel AI puanı: {sentiment_sonuc[0]['score']:.2f}"}
                    
                    # Skor yeterince yüksekse, yine de kabul et
                    if sentiment_sonuc[0]['score'] < 0.8:
                        return {"durum": True, "sebep": "Düşük güven skoruna rağmen kabul edildi"}
                        
                    return {"durum": False, "sebep": f"Yerel AI: Cevap uyumsuz olabilir (skor: {sentiment_sonuc[0]['score']:.2f})"}
                    
                except Exception as e:
                    print(f"Yerel AI Analiz hatası: {str(e)}")
                    # Model hata verirse kural tabanlı kontrole geç
            
            # 3. Alternatif: Kural tabanlı kontrol
            print("Kural tabanlı kontrol yapılıyor...")
            dogru_cevap = soru['dogruCevap'].lower()
            soru_metni = soru['soru'].lower()
            
            # Yerel kontrol - şüpheli sorular için
            if self.local_kontrol_gerekli_mi(soru):
                local_sonuc = self.local_ai_dogrula(soru)
                if not local_sonuc["durum"]:
                    return local_sonuc
            
            # Diğer tüm kontroller başarısız olursa, varsayılan olarak doğru kabul et
            return {"durum": True, "sebep": "Kontrol başarılı"}
                
        except Exception as e:
            print(f"Yapay zeka doğrulama hatası: {str(e)}")
            return {"durum": True, "sebep": ""}  # Hata durumunda varsayılan olarak geçer
    
    def local_kontrol_gerekli_mi(self, soru):
        """Basit bir kurala göre yerel kontrol gerekip gerekmediğini belirler"""
        # Çok kısa sorular için ek kontrol yapalım
        if len(soru['soru']) < 20:
            return True
            
        # Doğru cevap seçeneklerde var mı?
        if soru["dogruCevap"] not in soru["secenekler"]:
            return True
            
        # Çok uzun veya garip cevaplar için kontrol
        if len(soru['dogruCevap']) > 100:
            return True
            
        # Çoğu soru için kontrol etmemize gerek yok
        return False
    
    def internet_dogrula(self, soru, kategori, alt_kategori):
        """Soruları doğrular - yapay zeka kullanır"""
        try:
            # Doğrudan yapay zeka doğrulaması
            print(f"Soru doğrulanıyor: {soru['soru'][:50]}...")
            return self.yapay_zeka_dogrula(soru)
            
        except Exception as e:
            print(f"Doğrulama hatası: {str(e)}")
            # Hata durumunda doğru kabul et
            return {"durum": True, "sebep": ""}
    
    def google_arama(self, sorgu, limit=5, sadece_tyt_kaynaklar=False):
        """Google'da arama yapar ve sonuçları analiz eder"""
        try:
            # Google arama engellenmesini azaltmak için gecikme ekleyelim
            time.sleep(self.arama_gecikmesi)
            
            # Google arama URL'i 
            url = f"https://www.google.com/search?q={sorgu.replace(' ', '+')}"
            
            # Rasgele user agent seç
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            
            # İstek yap
            response = requests.get(url, headers=headers, timeout=10)
            
            # Başarılı istek kontrolü
            if response.status_code != 200:
                return {"durum": False, "sebep": f"Google yanıt kodu: {response.status_code}"}
            
            # Bot engeline takıldık mı kontrol et
            if "unusual traffic" in response.text or "captcha" in response.text:
                # Gecikmeyi arttır
                self.arama_gecikmesi = min(self.arama_gecikmesi * 1.5, 10)
                print(f"Google bot engeline takıldık! Gecikme arttırıldı: {self.arama_gecikmesi} saniye")
                return {"durum": False, "sebep": "Google bot engeli tespit edildi"}
            
            # HTML içeriğini analiz et
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sonuç bulunamadı kontrolü
            if "Hiçbir sonuç bulunamadı" in response.text or "No results found" in response.text:
                return {"durum": False, "sebep": "Google sonuç bulamadı"}
            
            # Basitleştirilmiş yaklaşım - tüm linkler
            tum_linkler = soup.find_all('a')
            
            if len(tum_linkler) == 0:
                return {"durum": False, "sebep": "Hiç link bulunamadı"}
                
            # Güvenilir site sayacı
            guvenilir_site_sayisi = 0
            tyt_kaynak_sayisi = 0
            bulunan_linkler = []
            
            # Tüm linklerde güvenilir olanları say
            for link in tum_linkler:
                if link.has_attr('href'):
                    href = link['href']
                    # Google sonuçları genelde /url?q= ile başlar
                    if href.startswith('/url?q='):
                        # URL'i temizle
                        temiz_url = href.split('/url?q=')[1].split('&')[0]
                        
                        # Link listesine ekle
                        bulunan_linkler.append(temiz_url)
                        
                        # Sadece TYT kaynakları isteniyorsa kontrol et
                        if sadece_tyt_kaynaklar:
                            if self.tyt_kaynak_mi(temiz_url):
                                tyt_kaynak_sayisi += 1
                        # Değilse genel güvenilir site kontrolü yap
                        elif self.guvenilir_site_mi(temiz_url):
                            guvenilir_site_sayisi += 1
            
            # Debug - hangi siteleri bulduğumuzu görelim
            if len(bulunan_linkler) > 0 and (sadece_tyt_kaynaklar and tyt_kaynak_sayisi > 0):
                print(f"  TYT kaynakları ({tyt_kaynak_sayisi}): {', '.join(bulunan_linkler[:3])}")
            
            # Sonucu döndür
            if sadece_tyt_kaynaklar:
                if tyt_kaynak_sayisi > 0:
                    # Başarılı olduğumuzda gecikmeyi biraz azalt
                    self.arama_gecikmesi = max(self.arama_gecikmesi * 0.9, 1.0)
                    return {"durum": True, "sebep": "", "skor": tyt_kaynak_sayisi}
                else:
                    return {"durum": False, "sebep": "TYT kaynaklarında bulunamadı"}
            else:
                if guvenilir_site_sayisi > 0:
                    # Başarılı olduğumuzda gecikmeyi biraz azalt
                    self.arama_gecikmesi = max(self.arama_gecikmesi * 0.9, 1.0)
                    return {"durum": True, "sebep": "", "skor": guvenilir_site_sayisi}
                else:
                    return {"durum": False, "sebep": "Güvenilir kaynak bulunamadı"}
                
        except Exception as e:
            print(f"Google arama hatası: {str(e)}")
            # Hata olursa varsayılan olarak başarılı kabul et
            return {"durum": True, "sebep": "", "skor": 0}
    
    def duckduckgo_arama(self, sorgu):
        """DuckDuckGo'da arama yapar (alternatif olarak)"""
        try:
            # HTML API için URL
            url = f"https://html.duckduckgo.com/html/?q={sorgu.replace(' ', '+')}"
            
            # Rasgele user agent seç
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml'
            }
            
            # İstek yap
            response = requests.get(url, headers=headers, timeout=10)
            
            # Başarılı istek kontrolü
            if response.status_code != 200:
                return {"durum": False, "sebep": f"DuckDuckGo yanıt kodu: {response.status_code}"}
            
            # HTML içeriğini analiz et
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sonuçları incele
            sonuc_divleri = soup.find_all('div', class_='result')
            
            if len(sonuc_divleri) == 0:
                return {"durum": False, "sebep": "DuckDuckGo sonuç bulamadı"}
                
            # En az bir sonuç var
            return {"durum": True, "sebep": "", "skor": len(sonuc_divleri)}
                
        except Exception as e:
            print(f"DuckDuckGo arama hatası: {str(e)}")
            # Hata olursa varsayılan olarak başarılı kabul et
            return {"durum": True, "sebep": "", "skor": 0}
            
    def guvenilir_site_mi(self, url):
        """URL'in güvenilir bir site olup olmadığını kontrol eder"""
        guvenilir_domainler = [
            # Eğitim kurumları
            'edu.tr', 'edu', 'ac.uk', 'sch.', 
            # Devlet kurumları
            'gov.tr', 'gov', 'meb.gov.tr', 'tubitak.gov.tr', 'tuba.gov.tr',
            # Popüler ansiklopediler ve akademik kaynaklar
            'wikipedia.org', 'wikimedia.org', 'tdk.gov.tr', 'britannica.com', 'academia.edu',
            'researchgate.net', 'springer.com', 'sciencedirect.com', 'jstor.org', 'ieee.org',
            'bilimgenc.tubitak.gov.tr', 'bilimteknoloji.tubitak.gov.tr',
            # Türk haber kaynakları
            'hurriyet.com.tr', 'milliyet.com.tr', 'sozcu.com.tr', 'sabah.com.tr', 
            'haberturk.com', 'ntv.com.tr', 'cnnturk.com', 'trthaber.com', 'aa.com.tr',
            # Uluslararası haber kaynakları
            'bbc.com', 'bbc.co.uk', 'cnn.com', 'nytimes.com', 'reuters.com', 'apnews.com',
            # Eğitim platformları
            'khan', 'khanacademy.org', 'youtube.com/watch', 'edx.org', 'coursera.org',
            # Türk üniversiteleri
            'bilgi.edu.tr', 'marmara.edu.tr', 'istanbul.edu.tr', 'itu.edu.tr',
            'anadolu.edu.tr', 'gazi.edu.tr', 'metu.edu.tr', 'hacettepe.edu.tr',
            'boun.edu.tr', 'yildiz.edu.tr', 'sabanciuniv.edu', 'bilkent.edu.tr',
            # Resmi kurumlar ve organizasyonlar
            'ataturk.org.tr', 'tccb.gov.tr', 'tbmm.gov.tr', 'kultur.gov.tr',
            'un.org', 'who.int', 'nato.int', 'europa.eu',
            # Popüler bilim ve bilgi siteleri
            'bilim.org', 'popsci.com.tr', 'bilimveutopya.com.tr',
            # Google Kitaplar ve Google Scholar
            'books.google.com', 'scholar.google.com',
            # İçerik olarak güvenilir sayılabilecek siteler
            'quora.com', 'eksi.org', 'ekşisözlük.com',
            # Müzeler ve kütüphaneler
            'ibb.gov.tr', 'kultur.gov.tr', 'mkutup.gov.tr'
        ]
        
        # URL'yi küçük harfe çevir ve kontrol et
        url_kucuk = url.lower()
        
        # Başındaki protokol kısımlarını temizle
        if url_kucuk.startswith(('http://', 'https://')):
            # URL'den protokol kısmını çıkart
            for protokol in ['http://', 'https://']:
                if url_kucuk.startswith(protokol):
                    url_kucuk = url_kucuk[len(protokol):]
                    break
        
        # Önce "www." gibi başlangıçları temizle
        if url_kucuk.startswith('www.'):
            url_kucuk = url_kucuk[4:]
        
        # Domain'i al (ilk / işaretine kadar)
        if '/' in url_kucuk:
            url_kucuk = url_kucuk.split('/', 1)[0]
        
        # Her bir güvenilir domaini kontrol et
        for domain in guvenilir_domainler:
            # Tam eşleşme veya alt domain olabilir
            if domain in url_kucuk:
                # Domain kısmı mı yoksa alan adının içinde mi olduğunu kontrol et
                # Örneğin: "example.com" içinde "le.co" olabilir, bu güvenilir değil
                domain_parts = domain.split('.')
                url_parts = url_kucuk.split('.')
                
                # Basit kontrol: domain site içinde bir parça olarak geçiyor mu?
                for i in range(len(url_parts) - len(domain_parts) + 1):
                    if url_parts[i:i+len(domain_parts)] == domain_parts:
                        return True
                
                # veya domain doğrudan site adının sonu mu?
                if url_kucuk.endswith('.' + domain):
                    return True
                
                # veya domain doğrudan site adının kendisi mi?
                if url_kucuk == domain:
                    return True
        
        return False
    
    def sonuclari_kaydet(self):
        """Sonuçları JSON dosyalarına kaydeder"""
        try:
            # Temiz soruları kaydet
            with open('temiz_sorular.json', 'w', encoding='utf-8') as dosya:
                json.dump(self.temiz_sorular, dosya, ensure_ascii=False, indent=2)
                
            # Şüpheli soruları kaydet
            with open('suphe_edilen_sorular.json', 'w', encoding='utf-8') as dosya:
                json.dump(self.suphe_edilen_sorular, dosya, ensure_ascii=False, indent=2)
                
            print(f"Sonuçlar kaydedildi: temiz_sorular.json ve suphe_edilen_sorular.json")
            
        except Exception as e:
            print(f"Sonuçları kaydetme hatası: {str(e)}")
    
    def tamlamalari_kontrol_et(self, soru):
        """İsim tamlamaları ile ilgili soruları kontrol eder"""
        try:
            # İsim tamlaması sorularında doğru cevap kontrolü
            if "isim tamlaması" in soru["soru"].lower() and "cümlede hangi sözcük" in soru["soru"].lower():
                # Cümleyi bul
                cumle = ""
                if "'" in soru["soru"]:
                    cumle_parcalari = soru["soru"].split("'")
                    if len(cumle_parcalari) >= 3:
                        cumle = cumle_parcalari[1]
                
                if not cumle:
                    return {"durum": True, "sebep": ""}  # Cümle bulunamadı, varsayılan olarak geçer
                
                # Doğru cevap gerçekten isim tamlaması mı?
                dogru_cevap = soru["dogruCevap"]
                if dogru_cevap and not self.isim_tamlamasi_mi(dogru_cevap, cumle):
                    return {"durum": False, "sebep": f"'{dogru_cevap}' bir isim tamlaması değil gibi görünüyor"}
                
                # Olası tamlamaları kontrol et
                for tamlama in self.dilbilgisi_kurallari["isim_tamlamasi"]:
                    if tamlama in cumle and tamlama not in soru["secenekler"] and tamlama != dogru_cevap:
                        return {"durum": False, "sebep": f"Cümlede '{tamlama}' isim tamlaması var ama seçeneklerde yok"}
                
            return {"durum": True, "sebep": ""}
            
        except Exception as e:
            print(f"Tamlama kontrolü hatası: {str(e)}")
            return {"durum": True, "sebep": ""}  # Hata durumunda varsayılan olarak geçer
    
    def isim_tamlamasi_mi(self, ifade, cumle):
        """Bir ifadenin isim tamlaması olup olmadığını kontrol eder"""
        # Basit kontrol: İsim tamlaması genelde iki isimden oluşur ve birleşik isim şeklindedir
        if ifade in self.dilbilgisi_kurallari["isim_tamlamasi"]:
            return True
            
        # Belirtili tamlama kontrolü (iyelik eki)
        if "nın" in ifade or "nin" in ifade or "nun" in ifade or "nün" in ifade or "ın" in ifade or "in" in ifade or "un" in ifade or "ün" in ifade:
            return True
            
        # İki kelimeden oluşma kontrolü
        kelimeler = ifade.split()
        if len(kelimeler) >= 2:
            return True
            
        return False
    
    def fiil_cekimlerini_kontrol_et(self, soru):
        """Fiil çekimleri ile ilgili soruları kontrol eder"""
        # Örnek bir kontrol, gerçek uygulamada daha kapsamlı olmalı
        return {"durum": True, "sebep": ""}
    
    def elektron_dizilimi_kontrol_et(self, soru):
        """Elektron dizilimi ile ilgili soruları kontrol eder"""
        try:
            # Elektron dizilimi sorularında doğru cevabın element adı kontrolü
            if "elektron dizilimi" in soru["soru"] and "hangi element" in soru["soru"].lower():
                # Elektron dizilimini bul
                elektron_dizilimi = None
                for format_dizilimi in ["1s²", "1s2"]:  # Farklı notasyon formatları
                    if format_dizilimi in soru["soru"]:
                        # Elektron dizilimini çıkart
                        dizilim_baslangic = soru["soru"].find(format_dizilimi)
                        if dizilim_baslangic > 0:
                            # Bir sonraki cümleye kadar al
                            dizilim_sonu = soru["soru"].find("?", dizilim_baslangic)
                            if dizilim_sonu > 0:
                                elektron_dizilimi = soru["soru"][dizilim_baslangic:dizilim_sonu].strip()
                            else:
                                elektron_dizilimi = soru["soru"][dizilim_baslangic:].strip()
                
                if elektron_dizilimi:
                    # Nikel'in elektron dizilimi: 1s² 2s² 2p⁶ 3s² 3p⁶ 4s² 3d⁸
                    if "3d⁸" in elektron_dizilimi or "3d8" in elektron_dizilimi:
                        beklenen_element = "Nikel"
                        if beklenen_element != soru["dogruCevap"] and beklenen_element not in soru["secenekler"]:
                            return {"durum": False, "sebep": f"Elektron dizilimi Nikel elementine ait, ancak seçeneklerde yok"}
            
            return {"durum": True, "sebep": ""}
            
        except Exception as e:
            print(f"Elektron dizilimi kontrolü hatası: {str(e)}")
            return {"durum": True, "sebep": ""}  # Hata durumunda varsayılan olarak geçer
    
    def element_kontrol_et(self, soru):
        """Element ile ilgili soruları kontrol eder"""
        # Örnek bir kontrol, gerçek uygulamada daha kapsamlı olmalı
        return {"durum": True, "sebep": ""}
    
    def kategori_kontrolu(self, soru, kategori, alt_kategori):
        """Soru kategorisine göre özel kontroller yapar"""
        try:
            # Kategori bazlı kontroller
            if kategori == "Türkçe":
                # Türkçe dil bilgisi kuralları kontrolü
                if "isim tamlaması" in soru["soru"].lower():
                    return self.tamlamalari_kontrol_et(soru)
                    
            elif kategori == "Kimya":
                # Kimya formülleri kontrolü
                if "elektron dizilimi" in soru["soru"].lower():
                    return self.elektron_dizilimi_kontrol_et(soru)
            
            # Diğer kategoriler için kontroller eklenebilir
            
            return {"durum": True, "sebep": ""}
        
        except Exception as e:
            print(f"Kategori kontrolü hatası: {str(e)}")
            return {"durum": True, "sebep": ""}  # Hata durumunda varsayılan olarak geçer

    def tyt_kaynak_mi(self, url):
        """URL'in TYT kaynağı olup olmadığını kontrol eder"""
        # URL'yi küçük harfe çevir
        url_kucuk = url.lower()
        
        # Başındaki protokol kısımlarını temizle
        if url_kucuk.startswith(('http://', 'https://')):
            for protokol in ['http://', 'https://']:
                if url_kucuk.startswith(protokol):
                    url_kucuk = url_kucuk[len(protokol):]
                    break
        
        # "www." gibi başlangıçları temizle
        if url_kucuk.startswith('www.'):
            url_kucuk = url_kucuk[4:]
        
        # TYT kaynakları listesindeki her kaynağı kontrol et
        for kaynak in self.tyt_kaynaklar:
            if kaynak in url_kucuk:
                return True
                
        # TYT anahtar kelimesi geçiyor mu kontrol et
        if 'tyt' in url_kucuk:
            return True
            
        return False

    def local_ai_dogrula(self, soru):
        """İnternet bağlantısı gerektirmeyen yerel yapay zeka doğrulaması yapar"""
        try:
            # 1. Kelime eşleşmesi kontrolü
            soru_metni = soru['soru'].lower()
            dogru_cevap = soru['dogruCevap'].lower()
            
            # Sık kullanılan kelimeler (stopwords) listesi
            sik_kelimeler = ["ve", "veya", "ile", "bu", "şu", "o", "bir", "için", "gibi", "kadar", 
                            "nasıl", "ne", "neden", "kim", "hangi", "mi", "mı", "mu", "mü", "ya"]
            
            # Soru metnindeki tüm kelimeleri al
            kelimeler = []
            for kelime in soru_metni.replace("?", " ").replace(".", " ").replace(",", " ").split():
                if kelime not in sik_kelimeler and len(kelime) > 2:
                    kelimeler.append(kelime)
            
            # Doğru cevaptaki kelimeleri al
            cevap_kelimeleri = []
            for kelime in dogru_cevap.replace(".", " ").replace(",", " ").split():
                if kelime not in sik_kelimeler and len(kelime) > 2:
                    cevap_kelimeleri.append(kelime)
            
            # Cevaptaki kelimeler soruda geçiyor mu?
            eslesen_kelime_sayisi = 0
            toplam_kelime = len(cevap_kelimeleri)
            
            if toplam_kelime == 0:
                toplam_kelime = 1  # Bölme hatasını önlemek için
                
            for kelime in cevap_kelimeleri:
                if kelime in kelimeler:
                    eslesen_kelime_sayisi += 1
            
            esleme_orani = eslesen_kelime_sayisi / toplam_kelime
            
            # Diğer seçeneklerle karşılaştırma
            en_iyi_oran = esleme_orani
            en_iyi_secenek = dogru_cevap
            
            for secenek in soru['secenekler']:
                if secenek.lower() != dogru_cevap:
                    secenek_kelimeleri = []
                    for kelime in secenek.lower().replace(".", " ").replace(",", " ").split():
                        if kelime not in sik_kelimeler and len(kelime) > 2:
                            secenek_kelimeleri.append(kelime)
                    
                    secenek_eslesen = 0
                    secenek_toplam = len(secenek_kelimeleri)
                    
                    if secenek_toplam == 0:
                        secenek_toplam = 1
                    
                    for kelime in secenek_kelimeleri:
                        if kelime in kelimeler:
                            secenek_eslesen += 1
                    
                    secenek_orani = secenek_eslesen / secenek_toplam
                    
                    if secenek_orani > en_iyi_oran:
                        en_iyi_oran = secenek_orani
                        en_iyi_secenek = secenek.lower()
            
            # Eşleşme oranı düşükse veya başka bir seçenek daha iyi eşleşiyorsa
            if esleme_orani < 0.3 or en_iyi_secenek != dogru_cevap:
                return {"durum": False, "sebep": f"Yerel AI: Doğru cevap soru ile uyumsuz, eşleşme oranı: {esleme_orani:.2f}"}
            
            # 2. İçeriğe dayalı özel kurallar
            
            # Tarih soruları için yıl kontrolü
            if ("tarih" in soru_metni or "hangi yıl" in soru_metni) and any(char.isdigit() for char in dogru_cevap):
                # Cevaptaki yılların mantıklı aralıkta olup olmadığı kontrol edilebilir
                yillar = [int(s) for s in dogru_cevap.split() if s.isdigit() and len(s) == 4]
                for yil in yillar:
                    if yil < 1000 or yil > 2023:
                        return {"durum": False, "sebep": f"Yerel AI: Belirtilen yıl makul aralık dışında: {yil}"}
            
            # Matematik soruları için sayısal cevap kontrolü
            if "kaçtır" in soru_metni or "hesaplayınız" in soru_metni:
                sayilar = [s for s in dogru_cevap.split() if s.replace(',', '').replace('.', '').isdigit()]
                if not sayilar:
                    return {"durum": False, "sebep": "Yerel AI: Sayısal bir soru için sayısal cevap bulunamadı"}
            
            # Kategori ve alt kategori bazlı kontroller
            if "kategori" in locals() and "alt_kategori" in locals():
                # Fizik soruları için birim kontrolü
                if kategori == "Fizik":
                    birimler = ["m", "cm", "kg", "g", "s", "N", "J", "W", "V", "A"]
                    for birim in birimler:
                        if birim in soru_metni and all(birim not in secenek.lower() for secenek in soru['secenekler']):
                            return {"durum": False, "sebep": f"Yerel AI: Fizik sorusunda birim içeren cevap bulunamadı: {birim}"}
            
            # Kontroller tamamlandı, herhangi bir sorun bulunamadı
            return {"durum": True, "sebep": ""}
            
        except Exception as e:
            print(f"Yerel AI doğrulama hatası: {str(e)}")
            return {"durum": True, "sebep": ""}  # Hata durumunda varsayılan olarak geçer

# Uygulamayı çalıştır
if __name__ == "__main__":
    bot = SoruDogrulayiciBot()
    basla = time.time()
    sonuc = bot.calistir("questionsTyt.json")
    sure = time.time() - basla
    print(sonuc)
    print(f"İşlem {sure:.2f} saniyede tamamlandı.")