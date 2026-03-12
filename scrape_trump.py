import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_trump_archives(pages=1):
    # Mac path: saving to your Documents/CSS folder as requested
    output_dir = os.path.expanduser("~/Documents/CSS")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    desktop_path = os.path.join(output_dir, "trump_statements.csv")
    
    # Base URL for the archived briefing room
    base_url = "https://trumpwhitehouse.archives.gov/remarks/page/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_data = []

    for page_num in range(1, pages + 1):
        # The archive uses a query parameter for filtering issues
        params = {'issue_filter': 'foreign-policy'}
        print(f"📡 Accessing Page {page_num}...")
        
        try:
            response = requests.get(f"{base_url}{page_num}/", params=params, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. FIX: The archive uses h2 tags for titles
            articles = soup.find_all('h2', class_='briefing-statement__title')

            if not articles:
                print("⚠️ No articles found. The class name might have changed.")
                continue

            for article in articles:
                link_tag = article.find('a')
                if not link_tag: continue
                
                title = link_tag.get_text(strip=True)
                link = link_tag['href']

                print(f"   Reading: {title[:50]}...")
                
                # Visit individual article
                article_resp = requests.get(link, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')

                # 2. FIX: Extract metadata and body for the Archive structure
                date = article_soup.find('time').get_text(strip=True) if article_soup.find('time') else "N/A"
                
                # The archive content is usually in a div with class 'page-content__content'
                body_div = article_soup.find('div', class_='page-content__content') or article_soup.find('div', class_='editor')
                body_text = body_div.get_text(separator=' ', strip=True) if body_div else "Content not found"

                all_data.append({
                    'Date': date,
                    'Title': title,
                    'URL': link,
                    'Content': body_text
                })
                
                time.sleep(1) # Archives can be slower; be gentle

        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")

    # Save to CSV
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(desktop_path, index=False)
        print(f"\n✅ Done! {len(all_data)} statements saved to: {desktop_path}")
    else:
        print("\n❌ No data collected. Check the URL or selectors.")

if __name__ == "__main__":
    scrape_trump_archives(pages=49)