import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHANNEL_USERNAME = "power_prystolychka"
KEYWORDS = ["Дударків", "#dudarkiv"]

bot = Bot(token=BOT_TOKEN)

# --------------------------
# 1️⃣ Графік відключень
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
    return "Графік не знайдено."

def send_schedule():
    today_str = datetime.now().strftime("%Y-%m-%d")
    schedule_text = get_shutdown_schedule()
    bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень для Дударків (черга 6.2) на {today_str}:\n\n{schedule_text}"
    )
    print("Графік надіслано")

# --------------------------
# 2️⃣ Парсер Telegram-каналу
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

def send_new_messages(last_message_id=None):
    messages = get_latest_messages()
    if not messages:
        return None

    latest = messages[0]
    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        try:
            bot.send_message(chat_id=CHAT_ID, text=latest)
            print("Надіслано повідомлення:", latest[:50], "...")
            return latest
        except Exception as e:
            print("Помилка надсилання:", e)
    return last_message_id

# --------------------------
# Запуск
# --------------------------
if __name__ == "__main__":
    mode = os.environ.get("MODE", "channel")  # "schedule" або "channel"

    if mode == "schedule":
        send_schedule()
    else:
        last_message_id = None
        last_message_id = send_new_messages(last_message_id)
