# parser.py
import os
import asyncio
import time
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHANNEL_USERNAME = "power_prystolychka"
KEYWORDS = ["Дударків", "#dudarkiv"]
CHECK_INTERVAL = 300  # 5 хв
LAST_SCHEDULE_FILE = "last_schedule_date.txt"

bot = Bot(token=BOT_TOKEN)
last_message_id = None

SCHEDULE_URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"

# --------------------------
# Графік відключень
# --------------------------
def get_shutdown_schedule():
    try:
        resp = requests.get(SCHEDULE_URL, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return f"Не вдалося отримати графік: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="schedule")
    if content_div:
        return content_div.get_text(separator="\n").strip()
    else:
        return soup.get_text(separator="\n").strip()[:2000]

async def send_schedule_once():
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = None
    if os.path.exists(LAST_SCHEDULE_FILE):
        with open(LAST_SCHEDULE_FILE, "r") as f:
            last_date = f.read().strip()

    if last_date == today_str:
        print("Графік вже надсилали сьогодні")
        return

    schedule_text = get_shutdown_schedule()
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень для Дударків (черга 6.2) на сьогодні:\n\n{schedule_text}"
    )
    print("Графік надіслано")
    with open(LAST_SCHEDULE_FILE, "w") as f:
        f.write(today_str)

# --------------------------
# Парсер Telegram-каналу
# --------------------------
def get_latest_messages():
    url = f"https://t.me/s/{CHANNEL_USERNAME}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except:
        print("Не вдалося отримати дані з каналу")
        return []

    posts = re.findall(r'<div class="tgme_widget_message_text" dir="auto">(.*?)</div>', resp.text, re.DOTALL)
    clean_posts = [re.sub(r'<.*?>', '', p).strip() for p in posts]
    return clean_posts

async def send_new_messages():
    global last_message_id
    messages = get_latest_messages()
    if not messages:
        return

    latest = messages[0]
    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        try:
            await bot.send_message(chat_id=CHAT_ID, text=latest)
            print("Надіслано повідомлення:", latest[:50], "...")
            last_message_id = latest
        except Exception as e:
            print("Помилка надсилання:", e)

# --------------------------
# Основний цикл
# --------------------------
async def main():
    await send_schedule_once()
    print("Світлобот Дударків запущено...")

    while True:
        await send_new_messages()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
