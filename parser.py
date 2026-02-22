# parser.py

import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# --------------------------
# Налаштування через GitHub Secrets
# --------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHANNEL_USERNAME = "power_prystolychka"
KEYWORDS = ["Дударків", "#dudarkiv"]

bot = Bot(token=BOT_TOKEN)

LAST_SCHEDULE_FILE = "last_schedule_date.txt"
LAST_MESSAGE_FILE = "last_message.txt"

# --------------------------
# Графік відключень
# --------------------------
SCHEDULE_URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"

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
        return "Не вдалося знайти графік на сторінці"

def send_schedule_once():
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = None
    if os.path.exists(LAST_SCHEDULE_FILE):
        with open(LAST_SCHEDULE_FILE, "r") as f:
            last_date = f.read().strip()

    if last_date == today_str:
        print("Графік вже надіслано сьогодні")
        return

    schedule_text = get_shutdown_schedule()
    bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень для Дударків (черга 6.2) на сьогодні:\n\n{schedule_text}"
    )
    print("Графік надіслано")

    with open(LAST_SCHEDULE_FILE, "w") as f:
        f.write(today_str)

# --------------------------
# Telegram канал
# --------------------------
def get_latest_messages():
    url = f"https://t.me/s/{CHANNEL_USERNAME}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Не вдалося отримати дані з каналу")
        return []

    posts = re.findall(r'<div class="tgme_widget_message_text" dir="auto">(.*?)</div>', resp.text, re.DOTALL)
    clean_posts = [re.sub(r'<.*?>', '', p).strip() for p in posts]
    return clean_posts

def send_new_messages():
    last_message_id = None
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, "r") as f:
            last_message_id = f.read().strip()

    messages = get_latest_messages()
    if not messages:
        return

    latest = messages[0]
    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        bot.send_message(chat_id=CHAT_ID, text=latest)
        print("Надіслано повідомлення:", latest[:50], "...")
        with open(LAST_MESSAGE_FILE, "w") as f:
            f.write(latest)
    else:
        print("Нових повідомлень немає або ключові слова не знайдено")

# --------------------------
# Запуск
# --------------------------
if __name__ == "__main__":
    print("START")
    send_schedule_once()
    print("Перевіряємо канал...")
    send_new_messages()
    print("DONE")
