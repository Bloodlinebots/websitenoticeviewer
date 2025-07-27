from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client['notice_bot']

def add_user(user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def get_all_users():
    return [u["_id"] for u in db.users.find()]

def add_site(name, url):
    db.sites.update_one({"name": name}, {"$set": {"name": name, "url": url}}, upsert=True)

def get_sites():
    return list(db.sites.find())

def save_last_notice(site_name, notice_url):
    db.notices.update_one({"site": site_name}, {"$set": {"url": notice_url}}, upsert=True)

def get_last_notice(site_name):
    data = db.notices.find_one({"site": site_name})
    return data['url'] if data else None
