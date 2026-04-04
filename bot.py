import os
import logging
import requests as req
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

SELECT_MODE, SELECT_CATEGORY, SELECT_GAME, SELECT_GEO, SELECT_OFFER, SELECT_COUNT, WAITING_PHOTO = range(7)

GAMES = {
    "crash": {
        "name": "💥 Краш",
        "games": {
            "aviator": "✈️ Aviator",
            "jetx": "🚀 JetX",
            "chicken_road": "🐔 Chicken Road",
            "lucky_jet": "🎈 Lucky Jet",
            "spaceman": "👨‍🚀 Spaceman",
        }
    },
    "slots": {
        "name": "🎰 Слоти",
        "games": {
            "ice_fishing": "🎣 Ice Fishing Live",
            "sweet_bonanza": "🍬 Sweet Bonanza",
            "big_bass": "🐟 Big Bass Bonanza",
            "fruit_party": "🍓 Fruit Party",
            "gates_olympus": "⚡ Gates of Olympus",
        }
    },
    "local": {
        "name": "🌍 Локальні",
        "games": {
            "naija_wheel": "🎡 Naija Wheel",
            "betsafe_virtual": "⚽ Betsafe Virtual",
        }
    }
}

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Вибрати гру", callback_data="mode_game")],
        [InlineKeyboardButton("📸 Завантажити шаблон", callback_data="mode_photo")],
    ])

def category_keyboard():
    kb = [[InlineKeyboardButton(cat["name"], callback_data=f"cat_{cid}")] for cid, cat in GAMES.items()]
    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_start")])
    return InlineKeyboardMarkup(kb)

def game_keyboard(cat_id):
    cat = GAMES[cat_id]
    kb = [[InlineKeyboardButton(gname, callback_data=f"game_{gid}")] for gid, gname in cat["games"].items()]
    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_category")])
    return InlineKeyboardMarkup(kb)

def geo_keyboard(back="back_game"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇭 Ghana (GH)", callback_data="geo_GH")],
        [InlineKeyboardButton("🇹🇿 Tanzania (TZ)", callback_data="geo_TZ")],
        [InlineKeyboardButton("🇮🇳 India (IN)", callback_data="geo_IN")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=back)],
    ])

def offer_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1xBet", callback_data="offer_1xBet"), InlineKeyboardButton("MelBet", callback_data="offer_MelBet")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_geo")],
    ])

def count_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("5", callback_data="count_5"),
         InlineKeyboardButton("10", callback_data="count_10"),
         InlineKeyboardButton("20", callback_data="count_20")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_offer")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = "🎨 *Creo Generator Pro*\n\nГенерую крео під будь-яку гру та гео.\nОбери режим:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    return SELECT_MODE

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_start" or data == "mode_game" and False:
        context.user_data.clear()
        await query.edit_message_text("🎨 *Creo Generator Pro*\n\nОбери режим:", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

    if data == "mode_photo":
        await query.edit_message_text("📸 Скинь фото крео як шаблон — адаптую під будь-яке гео:")
        return WAITING_PHOTO

    if data == "mode_game":
        await query.edit_message_text("🎮 Вибери категорію гри:", reply_markup=category_keyboard())
        return SELECT_CATEGORY

    if data.startswith("cat_"):
        cat_id = data.replace("cat_", "")
        context.user_data['category'] = cat_id
        await query.edit_message_text(f"{GAMES[cat_id]['name']} — вибери гру:", reply_markup=game_keyboard(cat_id))
        return SELECT_GAME

    if data == "back_category":
        await query.edit_message_text("🎮 Вибери категорію:", reply_markup=category_keyboard())
        return SELECT_CATEGORY

    if data.startswith("game_"):
        game_id = data.replace("game_", "")
        context.user_data['game'] = game_id
        context.user_data['mode'] = 'game'
        await query.edit_message_text("🌍 Вибери гео:", reply_markup=geo_keyboard("back_game"))
        return SELECT_GEO

    if data == "back_game":
        cat_id = context.user_data.get('category', 'crash')
        await query.edit_message_text(f"{GAMES[cat_id]['name']} — вибери гру:", reply_markup=game_keyboard(cat_id))
        return SELECT_GAME

    if data.startswith("geo_"):
        geo = data.replace("geo_", "")
        context.user_data['geo'] = geo
        await query.edit_message_text("🎯 Вибери оффер:", reply_markup=offer_keyboard())
        return SELECT_OFFER

    if data == "back_geo":
        back = "back_game" if context.user_data.get('mode') == 'game' else "back_start"
        await query.edit_message_text("🌍 Вибери гео:", reply_markup=geo_keyboard(back))
        return SELECT_GEO

    if data.startswith("offer_"):
        offer = data.replace("offer_", "")
        context.user_data['offer'] = offer
        game = context.user_data.get('game', '')
        geo = context.user_data.get('geo', '')
        await query.edit_message_text(
            f"✅ Налаштування:\n🎮 {game}\n🌍 {geo}\n🎯 {offer}\n\nСкільки крео?",
            reply_markup=count_keyboard()
        )
        return SELECT_COUNT

    if data == "back_offer":
        await query.edit_message_text("🎯 Вибери оффер:", reply_markup=offer_keyboard())
        return SELECT_OFFER

    if data.startswith("count_"):
        count = int(data.replace("count_", ""))
        game = context.user_data.get('game', '')
        geo = context.user_data.get('geo', '')
        offer = context.user_data.get('offer', '')
        photo_bytes = context.user_data.get('photo_bytes')
        mode = context.user_data.get('mode', 'game')

        await query.edit_message_text(
            f"🚀 Генерую {count} крео...\n🎮 {game} | 🌍 {geo} | 🎯 {offer}\n⏳ ~{count * 35} сек"
        )

        from generator_v2 import generate_by_game, analyze_and_generate
        chat_id = query.message.chat_id

        if mode == 'photo' and photo_bytes:
            await analyze_and_generate(update, context, photo_bytes, geo, offer, count, chat_id)
        else:
            await generate_by_game(update, context, game, geo, offer, count, chat_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Готово!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Новий батч", callback_data="back_start")]])
        )
        return SELECT_MODE

    if data == "back_start":
        context.user_data.clear()
        await query.edit_message_text("🎨 *Creo Generator Pro*\n\nОбери режим:", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    response = req.get(file.file_path)
    context.user_data['photo_bytes'] = response.content
    context.user_data['mode'] = 'photo'

    await update.message.reply_text("✅ Фото отримано! Вибери гео:", reply_markup=geo_keyboard("back_start"))
    return SELECT_GEO

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.PHOTO, handle_photo),
        ],
        states={
            SELECT_MODE: [CallbackQueryHandler(handle_callback)],
            SELECT_CATEGORY: [CallbackQueryHandler(handle_callback)],
            SELECT_GAME: [CallbackQueryHandler(handle_callback)],
            SELECT_GEO: [
                CallbackQueryHandler(handle_callback),
                MessageHandler(filters.PHOTO, handle_photo),
            ],
            SELECT_OFFER: [CallbackQueryHandler(handle_callback)],
            SELECT_COUNT: [CallbackQueryHandler(handle_callback)],
            WAITING_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                CallbackQueryHandler(handle_callback),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )
    app.add_handler(conv)
    logger.info("Creo Bot v3 started")
    app.run_polling()

if __name__ == "__main__":
    main()
