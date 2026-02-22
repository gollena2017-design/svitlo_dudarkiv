from telegram import Bot
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = Bot(token=BOT_TOKEN)

bot.send_message(chat_id=CHAT_ID, text="✅ Тест Telegram працює!")
print("Повідомлення надіслано")
