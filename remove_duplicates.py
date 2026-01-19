import json

file_path = '/Users/a./github/kpssApi/genel_trivia.json'

def remove_duplicates():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "categories" in data and "Genel Kültür" in data["categories"]:
            questions = data["categories"]["Genel Kültür"]
            initial_count = len(questions)
            print(f"Initial question count: {initial_count}")
            
            seen_questions = set()
            unique_questions = []
            duplicates_removed = 0
            
            for q in questions:
                # Normalize question text for comparison (strip whitespace, lowercase)
                q_text = q.get("question", "").strip()
                q_text_lower = q_text.lower()
                
                if q_text_lower in seen_questions:
                    duplicates_removed += 1
                    # print(f"Removing duplicate: {q_text[:50]}...")
                else:
                    seen_questions.add(q_text_lower)
                    unique_questions.append(q)
            
            data["categories"]["Genel Kültür"] = unique_questions
            final_count = len(unique_questions)
            
            print(f"Final question count: {final_count}")
            print(f"Duplicates removed: {duplicates_removed}")
            
            if duplicates_removed > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("Successfully updated file.")
            else:
                print("No duplicates found. File not modified.")
                
        else:
            print("Category 'Genel Kültür' not found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    remove_duplicates()
