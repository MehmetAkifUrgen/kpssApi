
import json

def remove_questions():
    file_path = '/Users/a./github/kpssApi/genel_trivia.json'
    
    questions_to_remove_by_id = [
        "generated_kv_13", 
        "generated_kv_phase2_31", 
        "generated_kv_phase2_8"
    ]
    
    questions_to_remove_by_text = [
        "Polat Alemdar'ın sevgilisi Elif'in mesleği nedir?",
        "Memati Baş'ın, Polat Alemdar'a hitap şekli nedir?",
        "Süleyman Çakır'ın sağ kolu kimdir?",
        "Süleyman Çakır, hangi meyveyi çok sever ve sürekli yer?",
        "Memati Baş'ın geçmişte yaptığı meslek nedir?",
        "Polat Alemdar'ın estetik operasyon geçirmeden önceki adı nedir?",
        "Memati'nin oğlunun (Ali Memati) annesi kimdir?", # Too easy/soap opera style
        "Polat Alemdar'ın kız kardeşi Safiye Karahanlı dizide hangi ülkeden gelmiştir?", # Basic info
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('categories', {})
        kv_questions = categories.get("Kurtlar Vadisi", [])
        
        initial_count = len(kv_questions)
        print(f"Initial count: {initial_count}")
        
        new_kv_questions = []
        removed_count = 0
        
        for q in kv_questions:
            should_remove = False
            
            # Check ID
            if q.get('source_id') in questions_to_remove_by_id:
                should_remove = True
                print(f"Removing by ID: {q.get('source_id')}")
            
            # Check Text (exact match for now)
            if q.get('question') in questions_to_remove_by_text:
                should_remove = True
                print(f"Removing by Text: {q.get('question')}")
                
            if not should_remove:
                new_kv_questions.append(q)
            else:
                removed_count += 1
                
        categories["Kurtlar Vadisi"] = new_kv_questions
        data['categories'] = categories
        
        print(f"Removed {removed_count} questions.")
        print(f"Final count: {len(new_kv_questions)}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print("Successfully updated genel_trivia.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    remove_questions()
