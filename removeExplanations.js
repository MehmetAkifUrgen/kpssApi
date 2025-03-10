const fs = require('fs');

// JSON dosyasını oku
const jsonData = JSON.parse(fs.readFileSync('questionsAgs.json', 'utf8'));

// Tüm açıklamaları kaldırmak için recursive fonksiyon
function removeExplanations(obj) {
  if (typeof obj !== 'object' || obj === null) {
    return;
  }
  
  // Eğer bir dizi ise
  if (Array.isArray(obj)) {
    for (let i = 0; i < obj.length; i++) {
      if (typeof obj[i] === 'object') {
        // Açıklama alanını kaldır
        if (obj[i].aciklama !== undefined) {
          delete obj[i].aciklama;
        }
        // Alt nesneleri de kontrol et
        removeExplanations(obj[i]);
      }
    }
  } else {
    // Nesne ise tüm özellikleri dolaş
    for (const key in obj) {
      if (typeof obj[key] === 'object') {
        removeExplanations(obj[key]);
      }
    }
  }
}

// Tüm JSON'ı dolaş ve açıklamaları kaldır
removeExplanations(jsonData);

// Düzenlenmiş JSON'ı dosyaya yaz
fs.writeFileSync('questionsAgs.json', JSON.stringify(jsonData, null, 2), 'utf8');

console.log('Tüm açıklamalar başarıyla kaldırıldı.'); 