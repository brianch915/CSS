import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_biden_archives(pages=1):
    output_dir = os.path.expanduser("~/Documents/CSS")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    csv_path = os.path.join(output_dir, "biden_statements.csv")
    
    base_url = "https://bidenwhitehouse.archives.gov/briefing-room/speeches-remarks/page/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    all_data = []

    for page_num in range(1, pages + 1):
        print(f"📡 Accessing Page {page_num}...")
        try:
            response = requests.get(f"{base_url}{page_num}/", headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the links based on the HTML you provided
            links = soup.find_all('a', class_='news-item__title')

            for link_tag in links:
                title = link_tag.get_text(" ", strip=True)
                link = link_tag['href']

                # Case-insensitive filter for President Biden
                if "PRESIDENT BIDEN" not in title.upper():
                    continue

                print(f"   ✅ Scraping: {title[:50]}...")
                
                # Visit individual article
                article_resp = requests.get(link, headers=headers, timeout=10)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')

                # DATE: Usually in a <time> tag
                date_tag = article_soup.find('time')
                date = date_tag.get_text(strip=True) if date_tag else "N/A"
                
                all_data.append({
                    'Date': date,
                    'Title': title,
                    'URL': link
                })
                
                time.sleep(1) # Be gentle with the National Archives

        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")

    # Final Save
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(csv_path, index=False)
        print(f"\n🎉 Done! Saved {len(all_data)} statements to {csv_path}")
    else:
        print("\n❌ No data was collected. Ensure the filter matches the titles.")

if __name__ == "__main__":
    # Test with 2 pages first to verify content is being pulled
    scrape_biden_archives(pages=275)