# parser.py

import requests
import time
from telegram import Bot

# --------------------------
# Налаштування
# --------------------------
BOT_TOKEN = "тут_твій_новий_BOT_TOKEN"
CHAT_ID = "тут_твій_CHAT_ID"  # числовий ID чату або групи
CHANNEL_USERNAME = "power_prystolychka"  # без @
KEYWORDS = ["Дударків", "#dudarkiv"]
CHECK_INTERVAL = 300  # 5 хв у секундах

bot = Bot(token=BOT_TOKEN)

# Змінна для останнього повідомлення (щоб не дублювати)
last_message_id = None

# --------------------------
# Основна функція перевірки
# --------------------------
def get_latest_messages():
    """
    Отримує останні повідомлення з каналу через Telegram API.
    Використовує офіційний Telegram Bot API: getUpdates не підходить для каналів,
    тому тут буде простий HTTP-запит через @t.me/s/ посилання у HTML.
    """
    url = f"https://t.me/s/{CHANNEL_USERNAME}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Не вдалося отримати дані з каналу")
        return []

    # Шукаємо всі повідомлення через регулярку
    import re
    posts = re.findall(r'<div class="tgme_widget_message_text" dir="auto">(.*?)</div>', resp.text, re.DOTALL)
    # чистимо HTML-теги всередині постів
    clean_posts = [re.sub(r'<.*?>', '', p).strip() for p in posts]
    return clean_posts

def send_new_messages():
    global last_message_id
    messages = get_latest_messages()
    if not messages:
        return

    # беремо останнє повідомлення
    latest = messages[0]

    # якщо воно нове і містить ключові слова
    if latest != last_message_id and any(k in latest for k in KEYWORDS):
        try:
            bot.send_message(chat_id=CHAT_ID, text=latest)
            print("Надіслано повідомлення:", latest[:50], "...")
            last_message_id = latest
        except Exception as e:
            print("Помилка надсилання:", e)

# --------------------------
# Запуск циклу
# --------------------------
if __name__ == "__main__":
    print("Світлобот Дударків запущено...")
    while True:
        send_new_messages()
        time.sleep(CHECK_INTERVAL)
