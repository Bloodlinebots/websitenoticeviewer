import os
import requests

def download_pdf(url):
    filename = url.split("/")[-1]
    filepath = f"./downloads/{filename}"
    os.makedirs("downloads", exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(requests.get(url).content)
    return filepath

def format_notice_message(notice):
    if notice["type"] == "pdf":
        return {"caption": f"📄 *{notice['title']}*", "parse_mode": "Markdown", "document": open(notice['file'], 'rb')}
    elif notice["type"] == "link":
        return {"text": f"🔗 *{notice['title']}*\n[Open Notice]({notice['url']})", "parse_mode": "Markdown"}
    else:
        return {"text": f"📢 *{notice['title']}*\n{notice['url']}", "parse_mode": "Markdown"}
