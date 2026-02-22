import os
import asyncio
from datetime import datetime
from telegram import Bot
from playwright.async_api import async_playwright

# --------------------------
# Telegram налаштування
# --------------------------
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
bot = Bot(token=BOT_TOKEN)

# --------------------------
# URL графіка для Дударкова
# --------------------------
URL = "https://bezsvitla.com.ua/kyiv/cherha-6-2"  # правильна черга Дударків
SCREENSHOT_FILE = "dudarkiv_schedule.png"
LAST_SENT_FILE = "last_schedule_date.txt"

# --------------------------
# Функція захоплення скріншоту потрібного блоку
# --------------------------
async def capture_schedule():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)
        # Чекаємо на блок графіка для черги 6.2
        await page.wait_for_selector(".schedule-block", timeout=10000)
        element = await page.query_selector(".schedule-block")
        if element:
            await element.screenshot(path=SCREENSHOT_FILE)
            print("Скріншот Дударкова збережено:", SCREENSHOT_FILE)
        await browser.close()

# --------------------------
# Відправка фото один раз на день
# --------------------------
async def send_schedule_once():
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = None
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, "r") as f:
            last_date = f.read().strip()

    if last_date == today_str:
        print("Графік Дударкова вже надсилали сьогодні")
        return

    await capture_schedule()

    with open(SCREENSHOT_FILE, "rb") as f:
        bot.send_photo(
            chat_id=CHAT_ID,
            photo=f,
            caption=f"🌅 Графік відключень для Дударків (Київська область, черга 6.2) на сьогодні"
        )

    with open(LAST_SENT_FILE, "w") as f:
        f.write(today_str)

    print("Графік Дударкова надіслано")

# --------------------------
# Запуск
# --------------------------
if __name__ == "__main__":
    print("Світлобот Дударків запущено...")
    asyncio.run(send_schedule_once())
