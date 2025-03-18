import json
import os
import time
import requests
from bs4 import BeautifulSoup
import random
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

try:
    from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
    transformers_yuklu = True
except ImportError:
    print("Transformers kütüphanesi yüklü değil. Yerel doğrulama yapılacak.")
    print("Yüklemek için: pip install transformers torch")
    transformers_yuklu = False

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

class KpssSoruDogrulayiciBot:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.huggingface_api_key = HUGGINGFACE_API_KEY
        self.ai_destegi_aktif = True
        
        self.model_yuklu = False
        if transformers_yuklu:
            try:
                print("Yapay zeka modeli yükleniyor...")
                model_name = "dbmdz/bert-base-turkish-cased"
                
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
                
                self.nlp = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
                
                self.model_yuklu = True
                print("Yapay zeka modeli başarıyla yüklendi!")
            except Exception as e:
                print(f"Model yükleme hatası: {str(e)}")
                print("Basit kurallar kullanılacak")
        
        self.internet_baglantisi_var = self.internet_baglantisi_kontrol()
        if self.internet_baglantisi_var:
            print("İnternet bağlantısı aktif. HuggingFace API modelleri kullanılacak.")
        else:
            print("İnternet bağlantısı yok. Yerel model kullanılacak.")
        
        self.suphe_edilen_sorular = []
        self.temiz_sorular = {}
        
        self.toplam_soru = 0
        self.suphe_sayisi = 0
        self.arama_sayisi = 0
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        self.internet_kontrol = True
        self.arama_gecikmesi = 1.5
        
        # KPSS kaynakları
        self.kpss_kaynaklar = [
            # Resmi Kurumlar
            'osym.gov.tr',
            'meb.gov.tr',
            'memurlar.net',
            'dpb.gov.tr',
            'tccb.gov.tr',
            'tbmm.gov.tr',
            'resmigazete.gov.tr',
            
            # KPSS Hazırlık Siteleri
            'kpsscafe.com.tr',
            'kpssdelisi.com',
            'kpssmaster.com',
            'kpssonline.com',
            'kpssrehberi.com',
            
            # Eğitim Platformları
            'pegem.net',
            'yargiyayinevi.com',
            'benim-hocam.com',
            'kpssders.com',
            'kpssakademi.com',
            
            # Üniversiteler
            'anadolu.edu.tr',
            'ankara.edu.tr',
            'gazi.edu.tr',
            'marmara.edu.tr',
            'istanbul.edu.tr',
            
            # Akademik Kaynaklar
            'dergipark.org.tr',
            'tubitak.gov.tr',
            'tuba.gov.tr',
            'academia.edu.tr',
            
            # Haber Siteleri
            'hurriyet.com.tr',
            'milliyet.com.tr',
            'sozcu.com.tr',
            'sabah.com.tr',
            'haberturk.com'
        ]

    def calistir(self, dosya_yolu):
        print(f"{dosya_yolu} dosyası işleniyor...")
        
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
                tum_veri = json.load(dosya)
                
            self.temiz_sorular = {"soruCozumu": {}}
                
            for kategori, alt_kategoriler in tum_veri.get("soruCozumu", {}).items():
                self.temiz_sorular["soruCozumu"][kategori] = {}
                
                for alt_kategori, sorular in alt_kategoriler.items():
                    print(f"Kategori: {kategori} - Alt Kategori: {alt_kategori} - {len(sorular)} soru işleniyor...")
                    
                    self.temiz_sorular["soruCozumu"][kategori][alt_kategori] = []
                    self.toplam_soru += len(sorular)
                    
                    for soru in sorular:
                        kontrol_sonucu = self.soru_dogrula(soru, kategori, alt_kategori)
                        if kontrol_sonucu["durum"]:
                            self.temiz_sorular["soruCozumu"][kategori][alt_kategori].append(soru)
                        else:
                            self.suphe_edilen_sorular.append({
                                "kategori": kategori,
                                "alt_kategori": alt_kategori,
                                "soru": soru,
                                "sebep": kontrol_sonucu["sebep"]
                            })
                            self.suphe_sayisi += 1
                    
                    self.sonuclari_kaydet()
                    print(f"  - Toplam {len(sorular)} soru işlendi, şüpheli: {self.suphe_sayisi}, arama sayısı: {self.arama_sayisi}")
            
            self.sonuclari_kaydet()
            
            return f"İşlem tamamlandı. Toplam {self.toplam_soru} soru işlendi, {self.suphe_sayisi} adet şüpheli soru tespit edildi. Toplam {self.arama_sayisi} arama yapıldı."
            
        except Exception as e:
            return f"Hata oluştu: {str(e)}"

    def soru_dogrula(self, soru, kategori, alt_kategori):
        if not isinstance(soru, dict) or not all(alan in soru for alan in ["soru", "secenekler", "dogruCevap"]):
            print(f"Format hatası: {soru.get('soru', 'Bilinmeyen soru')}")
            return {"durum": False, "sebep": "Format hatası"}
            
        if soru["dogruCevap"] not in soru["secenekler"]:
            print(f"Cevap hatası: {soru['soru']} - Doğru cevap seçeneklerde yok")
            return {"durum": False, "sebep": "Doğru cevap seçeneklerde yok"}
        
        if self.internet_kontrol:
            internet_kontrolu = self.internet_dogrula(soru, kategori, alt_kategori)
            if not internet_kontrolu["durum"]:
                print(f"Doğrulama hatası: {soru['soru']} - {internet_kontrolu['sebep']}")
                return {"durum": False, "sebep": f"Doğrulama hatası: {internet_kontrolu['sebep']}"}
        
        return {"durum": True, "sebep": ""}

    def internet_baglantisi_kontrol(self):
        try:
            response = requests.get("https://huggingface.co", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def internet_dogrula(self, soru, kategori, alt_kategori):
        try:
            print(f"Soru doğrulanıyor: {soru['soru'][:50]}...")
            return self.yapay_zeka_dogrula(soru)
            
        except Exception as e:
            print(f"Doğrulama hatası: {str(e)}")
            return {"durum": False, "sebep": f"Doğrulama hatası: {str(e)}"}
    
    def yapay_zeka_dogrula(self, soru):
        try:
            if not self.ai_destegi_aktif:
                return {"durum": False, "sebep": "Yapay zeka desteği kapalı"}
            
            if self.internet_baglantisi_var and self.huggingface_api_key:
                try:
                    print(f"HuggingFace API ile soru doğrulanıyor: {soru['soru'][:50]}...")
                    
                    hf_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
                    headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
                    
                    hf_data = {
                        "inputs": soru['soru'],
                        "parameters": {
                            "candidate_labels": [soru['dogruCevap'], "yanlış cevap"]
                        }
                    }
                    
                    response = requests.post(hf_url, headers=headers, json=hf_data, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"HuggingFace API cevabı: {result}")
                        
                        labels = result.get("labels", [])
                        scores = result.get("scores", [])
                        
                        if labels and scores and len(labels) > 0:
                            if labels[0] == soru['dogruCevap']:
                                return {"durum": True, "sebep": f"HuggingFace skoru: {scores[0]:.2f}"}
                            else:
                                return {"durum": False, "sebep": f"HuggingFace: Doğru cevap düşük skorlu ({scores[1]:.2f})"}
                    elif response.status_code == 402:
                        print("HuggingFace API limiti doldu, yerel modele geçiliyor...")
                        if self.model_yuklu:
                            return self.yerel_model_dogrula(soru)
                        else:
                            return {"durum": False, "sebep": "HuggingFace API limiti doldu ve yerel model yüklü değil"}
                    else:
                        print(f"HuggingFace API hatası: {response.status_code}, yerel modele geçiliyor...")
                        if self.model_yuklu:
                            return self.yerel_model_dogrula(soru)
                        else:
                            return {"durum": False, "sebep": f"HuggingFace API hatası: {response.status_code}"}
                        
                except Exception as e:
                    print(f"HuggingFace API hatası: {str(e)}, yerel modele geçiliyor...")
                    if self.model_yuklu:
                        return self.yerel_model_dogrula(soru)
                    else:
                        return {"durum": False, "sebep": f"HuggingFace API hatası: {str(e)}"}
            
            if self.model_yuklu:
                return self.yerel_model_dogrula(soru)
            
            return {"durum": False, "sebep": "Yapay zeka doğrulaması yapılamadı"}
                
        except Exception as e:
            print(f"Yapay zeka doğrulama hatası: {str(e)}")
            return {"durum": False, "sebep": f"Yapay zeka doğrulama hatası: {str(e)}"}
            
    def yerel_model_dogrula(self, soru):
        try:
            print(f"Yerel yapay zeka modeli ile analiz: {soru['soru'][:50]}...")
            
            birlesik_metin = f"Soru: {soru['soru']}, Cevap: {soru['dogruCevap']}"
            
            sentiment_sonuc = self.nlp(birlesik_metin)
            print(f"Yerel AI Analiz: {sentiment_sonuc}")
            
            if sentiment_sonuc[0]['label'] == 'LABEL_1':
                return {"durum": True, "sebep": f"Yerel AI puanı: {sentiment_sonuc[0]['score']:.2f}"}
            else:
                return {"durum": False, "sebep": f"Yerel AI: Cevap uyumsuz (skor: {sentiment_sonuc[0]['score']:.2f})"}
                
        except Exception as e:
            print(f"Yerel AI Analiz hatası: {str(e)}")
            return {"durum": False, "sebep": f"Yerel AI hatası: {str(e)}"}

    def sonuclari_kaydet(self):
        try:
            with open('kpss_temiz_sorular.json', 'w', encoding='utf-8') as dosya:
                json.dump(self.temiz_sorular, dosya, ensure_ascii=False, indent=2)
                
            with open('kpss_suphe_edilen_sorular.json', 'w', encoding='utf-8') as dosya:
                json.dump(self.suphe_edilen_sorular, dosya, ensure_ascii=False, indent=2)
                
            print(f"Sonuçlar kaydedildi: kpss_temiz_sorular.json ve kpss_suphe_edilen_sorular.json")
            
        except Exception as e:
            print(f"Sonuçları kaydetme hatası: {str(e)}")

    def kpss_kaynak_mi(self, url):
        url_kucuk = url.lower()
        
        if url_kucuk.startswith(('http://', 'https://')):
            for protokol in ['http://', 'https://']:
                if url_kucuk.startswith(protokol):
                    url_kucuk = url_kucuk[len(protokol):]
                    break
        
        if url_kucuk.startswith('www.'):
            url_kucuk = url_kucuk[4:]
        
        for kaynak in self.kpss_kaynaklar:
            if kaynak in url_kucuk:
                return True
                
        if 'kpss' in url_kucuk:
            return True
            
        return False

# Uygulamayı çalıştır
if __name__ == "__main__":
    bot = KpssSoruDogrulayiciBot()
    basla = time.time()
    sonuc = bot.calistir("questions.json")
    sure = time.time() - basla
    print(sonuc)
    print(f"İşlem {sure:.2f} saniyede tamamlandı.") 