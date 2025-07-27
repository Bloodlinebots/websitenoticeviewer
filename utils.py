import os
import requests

def download_pdf(url):
    filename = url.split("/")[-1]
    os.makedirs("downloads", exist_ok=True)
    filepath = f"./downloads/{filename}"
    with open(filepath, "wb") as f:
        f.write(requests.get(url).content)
    return filepath

def format_notice_message(notice):
    if notice["type"] == "pdf":
        return {"document": open(notice["file"], "rb"), "caption": f"📄 *{notice['title']}*", "parse_mode": "Markdown"}
    elif notice["type"] == "link":
        return {"text": f"🔗 *{notice['title']}*\n[Open]({notice['url']})", "parse_mode": "Markdown"}
    else:
        return {"text": f"📢 *{notice['title']}*\n{notice['url']}", "parse_mode": "Markdown"}
