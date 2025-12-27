
import json

def inspect_categories():
    file_path = '/Users/a./github/kpssApi/genel_trivia.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('categories')
        if isinstance(categories, list):
            print("Categories is a list. First few items:")
            for item in categories[:3]:
                print(item.get('name', 'No Name') if isinstance(item, dict) else item)
                
            # Search for Kurtlar Vadisi in list
            for item in categories:
                if isinstance(item, dict) and 'Kurtlar Vadisi' in item.values():
                   print("Found Kurtlar Vadisi in list!")
                   return

        elif isinstance(categories, dict):
            print("Categories is a dict. Keys:")
            print(list(categories.keys()))
            
            if "Kurtlar Vadisi" in categories:
                print("Found 'Kurtlar Vadisi' key in categories dict")
                qs = categories["Kurtlar Vadisi"]
                print(f"Count: {len(qs)}")
                # Save to kv_analysis.json
                with open('kv_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(qs, f, indent=2, ensure_ascii=False)
                print("Saved to kv_analysis.json")

        else:
            print(f"Categories is type: {type(categories)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_categories()
