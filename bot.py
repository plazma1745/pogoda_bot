import os, requests, datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
BOT_TOKEN   = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_TOKEN")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши название города и я покажу прогноз на ближайший день.")

# любой текст → погода
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    url  = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": WEATHER_KEY,
        "units": "metric",
        "cnt": 8        # 3-часовые интервалы на ближайшие ≈24 ч
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        await update.message.reply_text("Город не найден 😞")
        return

    data = r.json()
    today = datetime.date.today().strftime("%d.%m.%Y")
    lines = [f"Прогноз на {data['city']['name']} на {today}:\n"]

    for item in data["list"]:
        t = datetime.datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
        lines.append(f"{t}  {item['main']['temp']:.0f}°C, {item['weather'][0]['description']}")
    await update.message.reply_text("\n".join(lines))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, weather))
    app.run_polling()      # для локального теста
