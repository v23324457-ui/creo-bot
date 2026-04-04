import os
import logging
import requests
import io
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

WAITING_PHOTO = 1
WAITING_GEO = 2
WAITING_OFFER = 3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎨 *Creo Generator Pro*\n\n"
        "Скинь крео як шаблон — адаптую під будь-яке гео та оффер.\n"
        "Генерую 10 варіантів з різними фішками.\n\n"
        "👇 Скинь фото крео зараз",
        parse_mode="Markdown"
    )
    return WAITING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    response = requests.get(file.file_path)
    context.user_data['photo_bytes'] = response.content
    
    keyboard = [["🇬🇭 GH — Ghana", "🇹🇿 TZ — Tanzania"], ["🇮🇳 IN — India"]]
    await update.message.reply_text(
        "✅ Фото отримано!\n\nВибери гео для адаптації:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return WAITING_GEO

async def handle_geo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "GH" in text:
        context.user_data['geo'] = "GH"
    elif "TZ" in text:
        context.user_data['geo'] = "TZ"
    elif "IN" in text:
        context.user_data['geo'] = "IN"
    else:
        await update.message.reply_text("Вибери гео з кнопок вище")
        return WAITING_GEO

    keyboard = [["1xBet", "MelBet"]]
    await update.message.reply_text(
        "Вибери оффер:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return WAITING_OFFER

async def handle_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offer = update.message.text
    geo = context.user_data['geo']
    photo_bytes = context.user_data['photo_bytes']

    await update.message.reply_text(
        f"🔄 Аналізую крео і генерую 10 варіантів...\n"
        f"Гео: {geo} | Оффер: {offer}\n"
        f"⏳ ~5-7 хвилин",
        reply_markup=ReplyKeyboardRemove()
    )

    from generator_v2 import analyze_and_generate
    await analyze_and_generate(update, context, photo_bytes, geo, offer)

    await update.message.reply_text(
        "✅ Готово! Скинь наступне фото для нового батчу.",
    )
    context.user_data.clear()
    return WAITING_PHOTO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Скасовано.", reply_markup=ReplyKeyboardRemove())
    return WAITING_PHOTO

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.PHOTO, handle_photo)
        ],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            WAITING_GEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_geo)],
            WAITING_OFFER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_offer)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )
    app.add_handler(conv)
    logger.info("Creo Bot v2 started")
    app.run_polling()

if __name__ == "__main__":
    main()
