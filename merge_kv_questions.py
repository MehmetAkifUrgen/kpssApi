
import json

def merge_questions():
    main_file = '/Users/a./github/kpssApi/genel_trivia.json'
    new_questions_file = 'new_hard_kv_questions.json'
    
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            main_data = json.load(f)
            
        with open(new_questions_file, 'r', encoding='utf-8') as f:
            new_questions = json.load(f)
            
        categories = main_data.get('categories', {})
        current_kv = categories.get("Kurtlar Vadisi", [])
        
        print(f"Current KV count: {len(current_kv)}")
        print(f"Adding {len(new_questions)} new questions")
        
        # Verify unique IDs in new questions against existing
        existing_ids = {q.get('source_id') for q in current_kv if 'source_id' in q}
        
        final_list = current_kv
        added_count = 0
        
        for q in new_questions:
            if q.get('source_id') not in existing_ids:
                final_list.append(q)
                added_count += 1
            else:
                print(f"Skipping duplicate ID: {q.get('source_id')}")
        
        categories["Kurtlar Vadisi"] = final_list
        main_data['categories'] = categories
        
        print(f"Total KV count after merge: {len(final_list)}")
        
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(main_data, f, indent=2, ensure_ascii=False)
            
        print("Successfully merged questions.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    merge_questions()
