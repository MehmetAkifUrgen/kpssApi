import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QPushButton, 
                            QTextEdit, QSpinBox, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
import openai
import random
import json

class SoruUreticiGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soru Üretici")
        self.setGeometry(100, 100, 800, 600)
        
        # Sınav türleri ve dersleri
        self.sinavlar = {
            "TYT": ["Türkçe", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe"],
            "AYT": ["Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe"],
            "KPSS": ["Türkçe", "Matematik", "Tarih", "Coğrafya", "Vatandaşlık"],
            "ALES": ["Sözel", "Sayısal"],
            "DGS": ["Sözel", "Sayısal", "Mantık"]
        }
        
        # Dersler ve konuları
        self.konular = {
            "Türkçe": ["Paragraf", "Dil Bilgisi", "Anlatım Bozukluğu", "Sözcükte Anlam", "Cümlede Anlam"],
            "Matematik": ["Temel Kavramlar", "Sayılar", "Cebir", "Geometri", "Trigonometri"],
            "Fizik": ["Mekanik", "Elektrik", "Optik", "Dalgalar", "Modern Fizik"],
            "Kimya": ["Temel Kavramlar", "Atom Yapısı", "Periyodik Sistem", "Kimyasal Bağlar", "Reaksiyonlar"],
            "Biyoloji": ["Hücre", "Canlılar", "Genetik", "Ekosistem", "İnsan Fizyolojisi"],
            "Tarih": ["İlk Çağ", "Orta Çağ", "Yeni Çağ", "Yakın Çağ", "İnkılap Tarihi"],
            "Coğrafya": ["Fiziki Coğrafya", "Beşeri Coğrafya", "Ekonomik Coğrafya", "Türkiye Coğrafyası"],
            "Felsefe": ["Felsefeye Giriş", "Bilgi Felsefesi", "Varlık Felsefesi", "Ahlak Felsefesi"],
            "Türk Dili ve Edebiyatı": ["Edebiyat Akımları", "Şiir Bilgisi", "Düz Yazı Türleri", "Edebi Sanatlar"],
            "Vatandaşlık": ["Temel Haklar", "Devlet Yönetimi", "Anayasa", "Güncel Olaylar"],
            "Sözel": ["Sözel Mantık", "Sözel Yetenek", "Sözel Akıl Yürütme"],
            "Sayısal": ["Sayısal Mantık", "Sayısal Yetenek", "Sayısal Akıl Yürütme"],
            "Mantık": ["Mantık Kuralları", "Çıkarım", "Akıl Yürütme", "Problem Çözme"]
        }
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # API Key girişi
        api_layout = QHBoxLayout()
        api_label = QLabel("OpenAI API Key:")
        self.api_input = QLineEdit()
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        layout.addLayout(api_layout)
        
        # Sınav türü seçimi
        sinav_layout = QHBoxLayout()
        sinav_label = QLabel("Sınav Türü:")
        self.sinav_combo = QComboBox()
        self.sinav_combo.addItems(self.sinavlar.keys())
        sinav_layout.addWidget(sinav_label)
        sinav_layout.addWidget(self.sinav_combo)
        layout.addLayout(sinav_layout)
        
        # Ders seçimi
        ders_layout = QHBoxLayout()
        ders_label = QLabel("Ders:")
        self.ders_combo = QComboBox()
        ders_layout.addWidget(ders_label)
        ders_layout.addWidget(self.ders_combo)
        layout.addLayout(ders_layout)
        
        # Konu seçimi
        konu_layout = QHBoxLayout()
        konu_label = QLabel("Konu:")
        self.konu_combo = QComboBox()
        konu_layout.addWidget(konu_label)
        konu_layout.addWidget(self.konu_combo)
        layout.addLayout(konu_layout)
        
        # Zorluk seviyesi
        zorluk_layout = QHBoxLayout()
        zorluk_label = QLabel("Zorluk (1-5):")
        self.zorluk_spin = QSpinBox()
        self.zorluk_spin.setRange(1, 5)
        zorluk_layout.addWidget(zorluk_label)
        zorluk_layout.addWidget(self.zorluk_spin)
        layout.addLayout(zorluk_layout)
        
        # Soru üret butonu
        self.uret_button = QPushButton("Soru Üret")
        self.uret_button.clicked.connect(self.soru_uret)
        layout.addWidget(self.uret_button)
        
        # Soru ve cevap alanı
        self.soru_text = QTextEdit()
        self.soru_text.setReadOnly(True)
        layout.addWidget(self.soru_text)
        
        # Cevabı göster butonu
        self.cevap_button = QPushButton("Cevabı Göster")
        self.cevap_button.clicked.connect(self.cevap_goster)
        layout.addWidget(self.cevap_button)
        
        # Sinyal bağlantıları
        self.sinav_combo.currentIndexChanged.connect(self.sinav_degisti)
        self.ders_combo.currentIndexChanged.connect(self.ders_degisti)
        
        # İlk sınavın derslerini yükle
        self.sinav_degisti()
        
    def sinav_degisti(self):
        sinav = self.sinav_combo.currentText()
        self.ders_combo.clear()
        self.ders_combo.addItems(self.sinavlar[sinav])
        
    def ders_degisti(self):
        ders = self.ders_combo.currentText()
        self.konu_combo.clear()
        if ders in self.konular:
            self.konu_combo.addItems(self.konular[ders])
            
    def soru_uret(self):
        try:
            # API anahtarını al ve ayarla
            api_key = self.api_input.text()
            if not api_key:
                QMessageBox.warning(self, "Hata", "Lütfen OpenAI API anahtarınızı girin.")
                return
                
            openai.api_key = api_key
            
            sinav = self.sinav_combo.currentText()
            ders = self.ders_combo.currentText()
            konu = self.konu_combo.currentText()
            zorluk = self.zorluk_spin.value()
            
            prompt = f"""
            {sinav} sınavı için {ders} dersinden {konu} konusunda zorluk seviyesi {zorluk} olan bir soru oluştur.
            Soru çoktan seçmeli olmalı ve 5 seçenek içermeli (A, B, C, D, E).
            Sorunun sonunda doğru cevabı ve detaylı açıklamasını da ekle.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir sınav sorusu hazırlama uzmanısın."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            soru_metni = response.choices[0].message.content
            self.soru_text.setText(soru_metni)
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Soru üretilirken hata oluştu: {str(e)}")
            
    def cevap_goster(self):
        current_text = self.soru_text.toPlainText()
        if "Doğru cevap:" not in current_text:
            QMessageBox.information(self, "Bilgi", "Önce bir soru üretmelisiniz.")
        else:
            # Cevap zaten görünür durumda
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoruUreticiGUI()
    window.show()
    sys.exit(app.exec_()) 