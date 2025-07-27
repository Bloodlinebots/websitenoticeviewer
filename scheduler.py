from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import fetch_latest_notice
from db import get_sites, get_all_users
from utils import format_notice_message

def start_scheduler(bot):
    scheduler = AsyncIOScheduler()

    async def check_sites():
        for site in get_sites():
            notice = fetch_latest_notice(site['name'], site['url'])
            if notice:
                for uid in get_all_users():
                    try:
                        await bot.send_message(uid, **format_notice_message(notice))
                    except Exception as e:
                        print(f"[SEND ERROR] {e}")

    scheduler.add_job(check_sites, 'interval', hours=1)
    scheduler.start()
