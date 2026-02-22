import os
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CHANNEL_USERNAME = "power_prystolychka"
KEYWORDS = ["Дударків", "#dudarkiv"]

SCHEDULE_URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"

bot = Bot(token=BOT_TOKEN)

# --------------------------
# Перевіряємо чи це ранковий запуск (7:00 Київ)
# --------------------------
def is_morning_run():
    now_utc = datetime.now(timezone.utc)
    return now_utc.hour == 4  # 7:00 Київ = 4:00 UTC (зараз зимовий час)

# --------------------------
# Отримання графіку
# --------------------------
def get_shutdown_schedule():
    try:
        resp = requests.get(SCHEDULE_URL, timeout=10)
        if resp.status_code != 200:
            return f"Не вдалося отримати графік: {resp.status_code}"
    except Exception as e:
        return f"Помилка запиту: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator="\n").strip()
    return text[:3500]

def send_schedule():
    print("Надсилаємо ранковий графік...")
    schedule_text = get_shutdown_schedule()

    bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень Дударків (черга 6.2):\n\n{schedule_text}"
    )

# --------------------------
# Перевірка каналу
# --------------------------
def get_latest_messages():
    url = f"https://t.me/s/{CHANNEL_USERNAME}"
    resp = requests.get(url)

    if resp.status_code != 200:
        print("Не вдалося отримати канал")
        return []

    posts = re.findall(
        r'<div class="tgme_widget_message_text" dir="auto">(.*?)</div>',
        resp.text,
        re.DOTALL,
    )

    clean_posts = [re.sub(r"<.*?>", "", p).strip() for p in posts]
    return clean_posts

def check_channel():
    print("Перевіряємо Пристоличку...")
    messages = get_latest_messages()

    if not messages:
        return

    latest = messages[0]

    if any(k in latest for k in KEYWORDS):
        bot.send_message(chat_id=CHAT_ID, text=latest)
        print("Знайдено новину про Дударків")

# --------------------------
# MAIN (ОДИН запуск!)
# --------------------------
if __name__ == "__main__":
    print("START")

    if is_morning_run():
        send_schedule()

    check_channel()

    print("DONE")
