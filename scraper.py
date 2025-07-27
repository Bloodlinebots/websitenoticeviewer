import requests
from bs4 import BeautifulSoup
from db import get_last_notice, save_last_notice
from utils import download_pdf

def fetch_latest_notice(site_name, url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Adjust these selectors based on website pattern
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            title = link.get_text(strip=True)
            if title and href:
                full_link = href if href.startswith("http") else url.rstrip("/") + "/" + href
                last_notice = get_last_notice(site_name)
                if full_link != last_notice:
                    save_last_notice(site_name, full_link)
                    if full_link.endswith(".pdf"):
                        filepath = download_pdf(full_link)
                        return {"type": "pdf", "title": title, "file": filepath}
                    else:
                        # Try fetching PDF from redirected link
                        sub_response = requests.get(full_link)
                        if ".pdf" in sub_response.text:
                            return {"type": "link", "title": title, "url": full_link}
                        else:
                            return {"type": "text", "title": title, "url": full_link}
        return None
    except Exception as e:
        print(f"[SCRAPER ERROR] {e}")
        return None
