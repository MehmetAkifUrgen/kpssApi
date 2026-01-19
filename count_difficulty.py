import json
from collections import Counter

file_path = '/Users/a./github/kpssApi/genel_trivia.json'

def count_difficulties():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "categories" in data and "Genel Kültür" in data["categories"]:
            questions = data["categories"]["Genel Kültür"]
            print(f"Total questions: {len(questions)}")
            
            difficulties = [q.get("difficulty", "Unknown") for q in questions]
            counts = Counter(difficulties)
            
            print("\nDifficulty Distribution:")
            for difficulty in sorted(counts.keys(), key=lambda x: int(x) if isinstance(x, int) else -1, reverse=True):
                 print(f"Difficulty {difficulty}: {counts[difficulty]}")
                 
        else:
            print("Category 'Genel Kültür' not found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    count_difficulties()
