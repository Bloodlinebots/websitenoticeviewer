from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client['notice_bot']

def add_user(user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def get_all_users():
    return [u["_id"] for u in db.users.find()]

def add_site_for_user(user_id, name, url):
    db.sites.update_one(
        {"user_id": user_id, "name": name},
        {"$set": {"url": url}},
        upsert=True
    )

def get_sites_for_user(user_id):
    return list(db.sites.find({"user_id": user_id}))

def get_all_sites_with_users():
    return list(db.sites.find())

def save_last_notice(user_id, site_name, notice_url):
    db.notices.update_one(
        {"user_id": user_id, "site": site_name},
        {"$set": {"url": notice_url}},
        upsert=True
    )

def get_last_notice(user_id, site_name):
    doc = db.notices.find_one({"user_id": user_id, "site": site_name})
    return doc['url'] if doc else None
