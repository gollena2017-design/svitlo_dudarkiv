# parser.py

import os
import requests
import re
from telegram import Bot

# --------------------------
# Налаштування через GitHub Secrets
# --------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CHANNEL_USERNAME = "power_prystolychka"  # без @
KEYWORDS = ["Дударків", "#dudarkiv"]

bot = Bot(token=BOT_TOKEN)

# Змінна для останнього повідомлення (щоб не дублювати)
# Зберігатиметься у файлі last_message.txt, щоб після перезапуску бот не дублював
LAST_MESSAGE_FILE = "last_message.txt"

def load_last_message():
    try:
        with open(LAST_MESSAGE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_message(message):
    with open(LAST_MESSAGE_FILE, "w", encoding="utf-8") as f:
        f.write(message)

# --------------------------
# Функція отримання останніх повідомлень з каналу
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

# --------------------------
# Відправка нових повідомлень
# --------------------------
def send_new_messages():
    last_message_id = load_last_message()
    messages = get_latest_messages()
    if not messages:
        return

    latest = messages[0]

    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        try:
            bot.send_message(chat_id=CHAT_ID, text=latest)
            print("Надіслано повідомлення:", latest[:50], "...")
            save_last_message(latest)
        except Exception as e:
            print("Помилка надсилання:", e)

# --------------------------
# Запуск
# --------------------------
if __name__ == "__main__":
    send_new_messages()
