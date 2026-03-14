import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

def scrape_biden_fp_transcripts(limit=None):
    # 1. Load your new file
    file_path = 'biden_statements_FP.csv'
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    df = pd.read_csv(file_path)

    # 2. Apply the limit if specified
    if limit is not None:
        print(f"🧪 Testing mode: Scraping only the first {limit} links.")
        df = df.head(limit).copy()
    else:
        print(f"🚀 Full mode: Scraping all {len(df)} links.")

    # 3. Headers and Scraping Logic
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def get_body_text(url):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target the specific section from your HTML snippet
            content_section = soup.find('section', class_='body-content')
            
            if content_section:
                return content_section.get_text(separator='\n', strip=True)
            return "Content section not found."
        except Exception as e:
            return f"Scraping Error: {e}"

    # 4. Process the links
    transcripts = []
    for index, row in df.iterrows():
        print(f"📑 Processing {index+1}/{len(df)}: {row['Title'][:50]}...")
        
        text = get_body_text(row['URL'])
        transcripts.append(text)
        
        # Polite delay to avoid server blocks
        time.sleep(1)

    # 5. Save results
    df['Full_Transcript'] = transcripts
    output_name = 'biden_fp_transcripts_final.csv'
    df.to_csv(output_name, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Finished! Data saved to: {output_name}")

if __name__ == "__main__":
    # Change 'limit=5' to 'limit=None' when you are ready for the full run
    scrape_biden_fp_transcripts()