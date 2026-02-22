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

SCHEDULE_URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"

bot = Bot(token=BOT_TOKEN)


# --------------------------
# допоміжні файли стану
# --------------------------
LAST_POST_FILE = "last_post.txt"
LAST_SCHEDULE_FILE = "last_schedule.txt"


def read_file(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return None


def write_file(path, value):
    with open(path, "w") as f:
        f.write(value)


# --------------------------
# 1. Надсилання графіку (1 раз на день)
# --------------------------
def send_schedule_once():
    today = datetime.now().strftime("%Y-%m-%d")
    last_sent = read_file(LAST_SCHEDULE_FILE)

    if last_sent == today:
        print("Графік вже був сьогодні")
        return

    print("Надсилаємо графік...")

    resp = requests.get(SCHEDULE_URL, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    text = soup.get_text("\n")
    text = text[:3500]

    bot.send_message(
        chat_id=CHAT_ID,
        text=f"🌅 Графік відключень Дударків (черга 6.2):\n\n{text}"
    )

    write_file(LAST_SCHEDULE_FILE, today)


# --------------------------
# 2. Перевірка Пристолички
# --------------------------
def check_channel():
    print("Перевіряємо Пристоличку...")

    url = f"https://t.me/s/{CHANNEL_USERNAME}"
    resp = requests.get(url)

    posts = re.findall(
        r'<div class="tgme_widget_message_text" dir="auto">(.*?)</div>',
        resp.text,
        re.DOTALL
    )

    clean_posts = [re.sub(r'<.*?>', '', p).strip() for p in posts]

    if not clean_posts:
        return

    latest = clean_posts[0]
    last_saved = read_file(LAST_POST_FILE)

    if latest == last_saved:
        print("Нових повідомлень нема")
        return

    if any(k in latest for k in KEYWORDS):
        print("Є нове повідомлення → надсилаємо")
        bot.send_message(chat_id=CHAT_ID, text=latest)
        write_file(LAST_POST_FILE, latest)
    else:
        print("Повідомлення не про Дударків")


# --------------------------
# запуск (ОДИН раз!)
# --------------------------
print("START")
send_schedule_once()
check_channel()
print("DONE")
