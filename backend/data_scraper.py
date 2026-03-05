import requests
import json
import time
import os

def extract_deep_scheme_details():
    # 1. Open the summary dataset you scraped earlier
    input_file = "myscheme_rag_dataset.json"
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find '{input_file}'. Make sure it is in the same folder as this script.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        basic_schemes = json.load(f)

    detailed_dataset = []
    
    # 2. Your exact headers and the newly discovered endpoint
    url = 'https://api.myscheme.gov.in/schemes'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'x-api-key': 'tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc', # Make sure this hasn't expired!
        'Origin': 'https://www.myscheme.gov.in',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    print(f"Loaded {len(basic_schemes)} schemes from {input_file}.")
    print("Starting deep extraction. Grab a coffee, this will take some time to do safely...")

    # 3. Loop through every scheme and fetch its deep details
    # 1. The Corrected URL
    url = 'https://api.myscheme.gov.in/schemes'
    
    # ... (keep your headers exactly as they are) ...

    for index, scheme in enumerate(basic_schemes):
        fields = scheme.get("fields", {})
        scheme_slug = fields.get("slug") 
        
        if not scheme_slug:
            continue
            
        params = {
            'slug': scheme_slug,
            'lang': 'en',
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                json_response = response.json()
                
                # Dive straight into the data, ignore their weird "error" fields
                payload = json_response.get("data", {})
                
                # In your screenshot, the real info is nested inside an "en" (English) dictionary
                if "en" in payload:
                    scheme_details = payload["en"]
                    scheme_details["slug"] = scheme_slug # Keep the slug so we can identify it later
                else:
                    scheme_details = payload
                
                detailed_dataset.append(scheme_details)
                print(f"[{index + 1}/{len(basic_schemes)}] Success: Downloaded full data for '{scheme_slug}'")
                
                time.sleep(1.2) # Keep the sleep to avoid bans!
                
            else:
                print(f"[{index + 1}/{len(basic_schemes)}] Failed on {scheme_slug}. Status: {response.status_code}")
                if response.status_code in [401, 403]:
                    print("API Key expired! Update the headers.")
                    break
                
        except Exception as e:
            print(f"Error fetching {scheme_slug}: {e}")

    # 4. Save your master RAG database
    output_file = "myscheme_deep_rag_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(detailed_dataset, f, indent=4, ensure_ascii=False)
        
    print(f"\n✅ Deep scraping complete! Saved {len(detailed_dataset)} massive scheme files to {output_file}.")

if __name__ == "__main__":
    extract_deep_scheme_details()