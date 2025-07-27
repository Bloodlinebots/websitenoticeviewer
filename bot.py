import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from db import add_user, get_all_users, is_admin, get_sites
from scraper import fetch_latest_notice
from scheduler import start_scheduler
from utils import format_notice_message

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.reply("👋 Welcome! You’ll get notified when new notices are posted.")

@dp.message_handler(commands=['addsite'])
async def add_site(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("⛔ Only admin can add websites.")
        return
    args = message.get_args()
    if not args:
        await message.reply("Usage: `/addsite <website_name> <url>`", parse_mode="Markdown")
        return
    try:
        name, url = args.split(maxsplit=1)
        from db import add_site
        add_site(name, url)
        await message.reply(f"✅ Site *{name}* added for monitoring.", parse_mode="Markdown")
    except Exception:
        await message.reply("❌ Error! Make sure to provide: `<name> <url>`")

@dp.message_handler(commands=['update'])
async def manual_update(message: types.Message):
    sites = get_sites()
    if not sites:
        await message.reply("No websites are being tracked yet.")
        return
    kb = InlineKeyboardMarkup()
    for site in sites:
        kb.add(InlineKeyboardButton(site['name'], callback_data=f"check_{site['name']}"))
    await message.reply("📍 Choose a website to check manually:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def process_site_check(callback_query: types.CallbackQuery):
    site_name = callback_query.data.split("_", 1)[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"🔍 Checking *{site_name}*...", parse_mode="Markdown")
    
    site = next((s for s in get_sites() if s['name'] == site_name), None)
    if site:
        notice = fetch_latest_notice(site['name'], site['url'])
        if notice:
            await bot.send_message(callback_query.from_user.id, **format_notice_message(notice))
        else:
            await bot.send_message(callback_query.from_user.id, "⚠️ No new notice found.")
    else:
        await bot.send_message(callback_query.from_user.id, "❌ Site not found.")

if __name__ == '__main__':
    start_scheduler(bot)
    executor.start_polling(dp, skip_updates=True)
