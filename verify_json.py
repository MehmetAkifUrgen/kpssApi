
import json

def verify_json():
    file_path = '/Users/a./github/kpssApi/genel_trivia.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        kv = data['categories']['Kurtlar Vadisi']
        print(f"Kurtlar Vadisi Questions: {len(kv)}")
        
        # Check for duplicates by question text
        seen = set()
        duplicates = []
        for q in kv:
            txt = q['question']
            if txt in seen:
                duplicates.append(txt)
            seen.add(txt)
            
        if duplicates:
            print(f"FOUND DUPLICATES ({len(duplicates)}):")
            for d in duplicates:
                print(d)
        else:
            print("No text duplicate found.")
            
        print("JSON is valid.")
        
    except Exception as e:
        print(f"Invalid JSON: {e}")

if __name__ == "__main__":
    verify_json()
