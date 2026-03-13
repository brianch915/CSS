import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_xi_speech(limit=None):
    base_url = "https://www.fmprc.gov.cn/eng/xw/zyjh/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_links = []
    
    # 1. Collect links from the listing pages
    for i in range(limit):
        suffix = "index.html" if i == 0 else f"index_{i}.html"
        url = f"{base_url}{suffix}"
        print(f"📡 Accessing list page: {url}")
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Based on your HTML: find the div with class 'news_list'
            news_list = soup.find('div', class_='news_list')
            if not news_list:
                continue

            # Find all divs that contain a link and a date
            items = news_list.find_all('div', recursive=False)
            
            for item in items:
                link_tag = item.find('a')
                date_tag = item.find('div') # The date is in a nested div
                
                if link_tag and date_tag:
                    title = link_tag.get_text(strip=True)
                    # Handle relative path: ./202603/t20260308.html -> 202603/t20260308.html
                    rel_link = link_tag['href'].lstrip('./')
                    full_link = f"{base_url}{rel_link}"
                    date = date_tag.get_text(strip=True)
                    
                    all_links.append({
                        'Date': date,
                        'Title': title,
                        'URL': full_link
                    })
        except Exception as e:
            print(f"❌ Error on list page: {e}")
    
    # 2. Scrape the content from each link
    final_data = []
    for entry in all_links:
        print(f"📑 Scraping: {entry['Title'][:50]}...")
        try:
            res = requests.get(entry['URL'], headers=headers, timeout=15)
            res.encoding = res.apparent_encoding            
            article_soup = BeautifulSoup(res.text, 'html.parser')
            
            content = article_soup.find('div', class_='view_dedault')
            if content:
                entry['Full_Transcript'] = content.get_text(separator='\n', strip=True)
            else:
                content = article_soup.find('div', class_='view_default')
                if content:
                    entry['Full_Transcript'] = content.get_text(separator='\n', strip=True)
                else:
                    content = article_soup.find('div', class_='content_text')
                    entry['Full_Transcript'] = content.get_text(separator='\n', strip=True)
            
            final_data.append(entry)
            time.sleep(1) # Important delay
        except Exception as e:
            print(f"❌ Error scraping {entry['URL']}: {e}")

    # 3. Save to CSV
    df = pd.DataFrame(final_data)
    df.to_csv("xi_jinping_speeches.csv", index=False, encoding='utf-8-sig')
    print(f"\n✅ Done! Saved to xi_jinping_speeches.csv")

if __name__ == "__main__":
    scrape_xi_speech(limit=53)