import os
import asyncio
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from generator import generate_creos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Creo Generator Bot\n\n"
        "Формат запиту:\n"
        "/creo [кількість] [гео] [оффер]\n\n"
        "Приклад:\n"
        "/creo 5 GH 1xBet\n"
        "/creo 10 TZ MelBet\n\n"
        "Гео: GH (Гана), TZ (Танзанія), IN (Індія)"
    )

async def creo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    
    if len(args) < 3:
        await update.message.reply_text(
            "❌ Формат: /creo [кількість] [гео] [оффер]\n"
            "Приклад: /creo 5 GH 1xBet"
        )
        return
    
    try:
        count = int(args[0])
        if count > 20:
            count = 20
    except ValueError:
        await update.message.reply_text("❌ Кількість має бути числом. Приклад: /creo 5 GH 1xBet")
        return
    
    geo = args[1].upper()
    offer = " ".join(args[2:])
    
    if geo not in ["GH", "TZ", "IN"]:
        await update.message.reply_text("❌ Гео: GH, TZ або IN")
        return
    
    msg = await update.message.reply_text(
        f"⏳ Генерую {count} крео для {geo} / {offer}...\n"
        f"Це займе ~{count * 15} секунд"
    )
    
    try:
        await generate_creos(update, context, count, geo, offer, msg)
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Помилка: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Команди:\n\n"
        "/creo [к-сть] [гео] [оффер] — генерація крео\n"
        "/start — головне меню\n"
        "/help — допомога\n\n"
        "Макс 20 крео за раз\n"
        "Гео: GH, TZ, IN"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("creo", creo_command))
    app.add_handler(CommandHandler("help", help_command))
    
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
