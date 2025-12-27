
import json

def list_keys():
    file_path = '/Users/a./github/kpssApi/genel_trivia.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Keys found:", list(data.keys()))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_keys()
