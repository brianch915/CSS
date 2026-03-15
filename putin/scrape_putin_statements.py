import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import random

def scrape_putin_transcripts(limit=None):
    # 1. Load your new file
    file_path = 'putin_final.csv'
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    df = pd.read_csv(file_path)

    # 2. Apply the limit if specified
    if limit:
        print(f"🧪 Testing mode: Scraping only the first {limit} links.")
        df = df.head(limit).copy()
    else:
        print(f"🚀 Full mode: Scraping all {len(df)} links.")

    # 3. Headers and Scraping Logic
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    headers = {
            'User-Agent': random.choice(user_agents),
            'Referer': 'http://en.kremlin.ru/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_body_text(url):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target the specific section from your HTML snippet
            content_div = soup.find('div', class_='read__content')        
            if content_div:
                return content_div.get_text(separator='\n', strip=True)
            return "Content section not found."
        except Exception as e:
            print(f"Scraping Error: {e}")
            return f"Scraping Error: {e}"

    # 4. Process the links
    transcripts = []
    for index, row in df.iterrows():
        if row["Full_Transcript"][:8] == 'Scraping':
            print(f"📑 Processing {index+1}/{len(df)}: {row['Title'][:50]}...")
        
            text = get_body_text(row['URL'])
            transcripts.append(text)
        
            time.sleep(random.uniform(2.0, 5.0))
        else:
            transcripts.append(row["Full_Transcript"])

    # 5. Save results
    df['Full_Transcript'] = transcripts
    output_name = 'putin_final.csv'
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Finished! Data saved to: {output_name}")

if __name__ == "__main__":
    scrape_putin_transcripts(limit=None)