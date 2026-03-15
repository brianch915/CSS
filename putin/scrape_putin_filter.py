import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import random

def putin_classify(limit=None):
    file_path = 'putin_links.csv'
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return
    
    df = pd.read_csv(file_path)
    
    if limit:
        print(f"🧪 Testing mode: Classifying only the first {limit} links.")
        df = df.head(limit).copy()
    else:
        print(f"🚀 Full mode: Classifying all {len(df)} links.")
        
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
    
    def classify(url):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            topics_header = soup.find('h3', string=lambda t: t and 'Topics' in t)
        
            if topics_header:
                # Look at the parent or next sibling list to find the specific link
                # This searches for the <a> tag with that exact href anywhere inside the same section
                fp_link = topics_header.find_parent().find('a', href="/catalog/keywords/82/events")
                if fp_link:
                    return True

            selector_match = soup.select_one('li.p-category a[href="/catalog/keywords/82/events"]')
            
            return True if selector_match else False
        except Exception as e:
            print(f"Scraping Error: {e}")
            return f"Scraping Error: {e}"

    FP = []
    
    for index, row in df.iterrows():
        print(f"📑 Processing {index+1}/{len(df)}: {row['Title'][:50]}...")
        fp = classify(row["URL"])
        FP.append(fp)
        time.sleep(random.uniform(2, 5))

    df['Foreign Policy'] = FP
    output_name = 'putin_statements_classified.csv'
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Finished! Data saved to: {output_name}")

if __name__ == "__main__":
    putin_classify(limit=None)