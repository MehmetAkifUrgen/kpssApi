// questionsAgs.json dosyasındaki soru sayısını hesaplayan düzeltilmiş bot

const fs = require('fs');

// JSON dosyasını oku
fs.readFile('questionsAgs.json', 'utf8', (err, data) => {
  if (err) {
    console.error('Dosya okuma hatası:', err);
    return;
  }
  
  try {
    // JSON verisini parse et
    const jsonData = JSON.parse(data);
    
    let totalQuestions = 0;
    
    // Tüm JSON nesnesindeki soru alanlarını bul ve say
    function countQuestions(obj) {
      if (!obj) return;
      
      // Doğrudan bir soru nesnesi mi kontrol et
      if (obj.soru && obj.secenekler && obj.dogruCevap) {
        totalQuestions++;
        return;
      }
      
      // Array ise her elemanı kontrol et
      if (Array.isArray(obj)) {
        obj.forEach(item => countQuestions(item));
        return;
      }
      
      // Object ise her bir değeri kontrol et
      if (typeof obj === 'object') {
        Object.values(obj).forEach(value => countQuestions(value));
      }
    }
    
    countQuestions(jsonData);
    
    console.log(`Toplam Soru Sayısı: ${totalQuestions}`);
    
  } catch (error) {
    console.error('JSON parse hatası:', error);
    console.error(error.stack);
  }
});