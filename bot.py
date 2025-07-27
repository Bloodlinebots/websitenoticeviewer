import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from db import add_user, add_site_for_user, get_sites_for_user
from scraper import fetch_latest_notice
from scheduler import start_scheduler
from utils import format_notice_message

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.reply("👋 Welcome! Use /addsite to track your university notice site.")

@dp.message_handler(commands=["addsite"])
async def add_site(message: types.Message):
    args = message.get_args()
    if not args:
        await message.reply("Usage:\n`/addsite <name> <url>`", parse_mode="Markdown")
        return
    try:
        name, url = args.split(maxsplit=1)
        add_site_for_user(message.from_user.id, name, url)
        await message.reply(f"✅ Added *{name}* for tracking.", parse_mode="Markdown")
    except:
        await message.reply("❌ Invalid format. Use `/addsite Name URL`")

@dp.message_handler(commands=["update"])
async def update_site(message: types.Message):
    user_id = message.from_user.id
    sites = get_sites_for_user(user_id)
    if not sites:
        await message.reply("❗ You haven’t added any sites yet.")
        return
    kb = InlineKeyboardMarkup()
    for site in sites:
        kb.add(InlineKeyboardButton(site["name"], callback_data=f"check_{site['name']}"))
    await message.reply("📍 Choose a site to check manually:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("check_"))
async def process_check(callback_query: types.CallbackQuery):
    site_name = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id
    sites = get_sites_for_user(user_id)
    site = next((s for s in sites if s["name"] == site_name), None)

    if site:
        await bot.send_message(user_id, f"🔍 Checking *{site_name}*...", parse_mode="Markdown")
        notice = fetch_latest_notice(user_id, site_name, site["url"])
        if notice:
            await bot.send_message(user_id, **format_notice_message(notice))
        else:
            await bot.send_message(user_id, "⚠️ No new notice found.")
    else:
        await bot.send_message(user_id, "❌ Site not found.")

if __name__ == '__main__':
    start_scheduler(bot)
    executor.start_polling(dp)
