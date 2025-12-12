import json
import random
import os

file_path = '/Users/a./github/kpssApi/genel_trivia.json'

def randomize_trivia():
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('categories', {})
        target_category = "Muhteşem Yüzyıl"
        
        if target_category not in categories:
            print(f"Category '{target_category}' not found.")
            return

        questions = categories[target_category]
        print(f"Found {len(questions)} questions in '{target_category}'. Randomizing...")

        for q in questions:
            options = q['options']
            correct_index = q['correct_answer']
            
            # Get the actual correct answer text
            correct_answer_text = options[correct_index]
            
            # Shuffle options
            random.shuffle(options)
            
            # Find the new index of the correct answer
            new_correct_index = options.index(correct_answer_text)
            
            # Update the question object
            q['options'] = options
            q['correct_answer'] = new_correct_index

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("Successfully randomized options.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    randomize_trivia()
