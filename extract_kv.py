
import json

def extract_kv_questions():
    file_path = '/Users/a./github/kpssApi/genel_trivia.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        kv_questions = data.get("Kurtlar Vadisi", [])
        
        print(f"Found {len(kv_questions)} questions in 'Kurtlar Vadisi'")
        
        with open('kv_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(kv_questions, f, indent=2, ensure_ascii=False)
            
        print("Questions saved to kv_analysis.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_kv_questions()
