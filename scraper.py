import requests
from bs4 import BeautifulSoup
from db import get_last_notice, save_last_notice
from utils import download_pdf

def fetch_latest_notice(user_id, site_name, url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']
            title = link.get_text(strip=True)
            if not href or not title:
                continue

            full_url = href if href.startswith("http") else url.rstrip('/') + '/' + href
            last = get_last_notice(user_id, site_name)
            if full_url != last:
                save_last_notice(user_id, site_name, full_url)
                if full_url.endswith(".pdf"):
                    filepath = download_pdf(full_url)
                    return {"type": "pdf", "title": title, "file": filepath}
                else:
                    if ".pdf" in requests.get(full_url).text:
                        return {"type": "link", "title": title, "url": full_url}
                    else:
                        return {"type": "text", "title": title, "url": full_url}
        return None
    except Exception as e:
        print(f"[SCRAPER ERROR] {e}")
        return None
