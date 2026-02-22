# parser.py

import os
import time
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
CHECK_INTERVAL = 300  # 5 хв у секундах

bot = Bot(token=BOT_TOKEN)

last_message_id = None

# --------------------------
# Графік відключень з bezsvitla.com.ua
# --------------------------
SCHEDULE_URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"

def get_shutdown_schedule():
    try:
        resp = requests.get(SCHEDULE_URL, timeout=10)
        if resp.status_code != 200:
            return f"Не вдалося отримати графік: статус {resp.status_code}"
    except Exception as e:
        return f"Помилка при запиті: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    content_div = soup.find("div", class_="schedule")  # клас може змінюватися
    if content_div:
        return content_div.get_text(separator="\n").strip()
    else:
        # Альтернатива: взяти весь текст сторінки (обмеження Telegram 2000 символів)
        text = soup.get_text(separator="\n").strip()
        return text[:2000]

def send_schedule():
    schedule_text = get_shutdown_schedule()
    bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень для Дударків (черга 6.2) на сьогодні:\n\n{schedule_text}"
    )
    print("Графік надіслано")

# --------------------------
# Парсер Telegram-каналу
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
    global last_message_id
    messages = get_latest_messages()
    if not messages:
        return

    latest = messages[0]
    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        try:
            bot.send_message(chat_id=CHAT_ID, text=latest)
            print("Надіслано повідомлення:", latest[:50], "...")
            last_message_id = latest
        except Exception as e:
            print("Помилка надсилання:", e)

# --------------------------
# Запуск
# --------------------------
if __name__ == "__main__":
    now = datetime.now()
    # Надсилаємо графік, якщо запуск після 7:00 або при першому старті
    if now.hour >= 7:
        send_schedule()
    else:
        print("Ще рано надсилати графік, почекаємо до 7:00")

    print("Світлобот Дударків запущено...")

    while True:
        send_new_messages()
        time.sleep(CHECK_INTERVAL)
