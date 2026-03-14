import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random

output_dir = os.path.expanduser("~/Documents/CSS")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
csv_path = os.path.join(output_dir, "putin_links.csv")

def scrape_putin(limit=None):
    base_url = "http://en.kremlin.ru/events/president/transcripts/page/"
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    all_links = []
    
    # 1. Collect links from the listing pages
    for i in range(24, limit):
        url = f"{base_url}{i+1}"
        print(f"📡 Accessing list page: {url}")
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Referer': 'http://en.kremlin.ru/',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 403:
                print(f"⛔ 403 Forbidden on page {i+1}. Stopping to avoid IP ban.")
                print("💡 Recommendation: Wait 30 mins, use a VPN, or increase sleep time.")
                break
            
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Based on your HTML: find the div
            news_list = soup.find('div', class_='entry-content lister-page')
            
            if not news_list:
                print("❌ Could not find the listing container.")
                continue

            # Find all divs that contain a link and a date
            items = news_list.find_all('div', recursive=False)
            
            for item in items:
                h3 = item.find('h3', class_='hentry__title_special')
                link_tag = h3.find('a') if h3 else None
                
                title_tag = item.find('span', class_='p-name')
                date_tag = item.find('time', class_='dt-published')

                if link_tag and title_tag:
                    title = title_tag.get_text(strip=True)
                    relative_url = link_tag['href']
                    full_url = 'http://en.kremlin.ru' + relative_url if relative_url.startswith('/') else relative_url
                    date = date_tag.get_text(strip=True) if date_tag else "N/A"
                    
                    all_links.append({
                        'Date': date,
                        'Title': title,
                        'URL': full_url
                    })
            time.sleep(random.uniform(2.0, 5.0))
        
        except Exception as e:
            print(f"❌ Error on list page {i}: {e}")
            break
    
    if all_links:
        df = pd.DataFrame(all_links)
        df.to_csv(csv_path, index=False)
        print(f"\n🎉 Done! Saved {len(all_links)} statements to {csv_path}")

if __name__ == "__main__":
    scrape_putin(limit=209)