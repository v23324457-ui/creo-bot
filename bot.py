import os
import logging
import requests as req
import base64
import json
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "1032127876"))

GITHUB_REPO = "v23324457-ui/creo-bot"

SELECT_MODE, SELECT_CATEGORY, SELECT_GAME, SELECT_GEO, SELECT_OFFER, SELECT_COUNT, WAITING_PHOTO, AGENT_CHAT = range(8)

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

# ============================================================
# GITHUB TOOLS
# ============================================================

def github_get_file(path: str) -> str:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = req.get(url, headers=headers)
    data = resp.json()
    if "content" in data:
        return base64.b64decode(data["content"]).decode("utf-8")
    return f"Помилка: {data.get('message', 'файл не знайдено')}"

def github_update_file(path: str, content: str, message: str) -> str:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    current = req.get(url, headers=headers).json()
    sha = current.get("sha", "")
    encoded = base64.b64encode(content.encode()).decode()
    data = {"message": message, "content": encoded, "sha": sha}
    resp = req.put(url, headers=headers, json=data)
    if resp.status_code in [200, 201]:
        return f"✅ {path} оновлено! Railway деплоїть автоматично ~2 хв..."
    return f"❌ Помилка: {resp.json().get('message', 'невідома помилка')}"

def github_list_files() -> str:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    resp = req.get(url, headers=headers)
    files = resp.json()
    if isinstance(files, list):
        return "\n".join(f["name"] for f in files)
    return "Помилка отримання файлів"

def railway_get_status() -> str:
    if not RAILWAY_TOKEN:
        return "RAILWAY_TOKEN не налаштований"
    url = "https://backboard.railway.app/graphql/v2"
    headers = {"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"}
    query = """query { me { projects { edges { node { name services { edges { node { name deployments(last: 1) { edges { node { status createdAt } } } } } } } } } } }"""
    try:
        resp = req.post(url, headers=headers, json={"query": query}, timeout=10)
        data = resp.json()
        projects = data.get("data", {}).get("me", {}).get("projects", {}).get("edges", [])
        result = []
        for p in projects:
            project = p["node"]
            for s in project["services"]["edges"]:
                service = s["node"]
                deps = service["deployments"]["edges"]
                if deps:
                    dep = deps[-1]["node"]
                    result.append(f"Проект: {project['name']}\nСервіс: {service['name']}\nСтатус: {dep['status']}\nЧас: {dep['createdAt']}")
        return "\n\n".join(result) if result else "Проекти не знайдено"
    except Exception as e:
        return f"Помилка: {e}"

# ============================================================
# AGENT
# ============================================================

AGENT_SYSTEM = f"""Ти AI агент-девопс для Telegram бота creo-bot який генерує рекламні iGaming креативи для Африки та Індії.

Репо: {GITHUB_REPO}
Основні файли: bot.py, generator_v2.py, requirements.txt, railway.toml, meta_analytics.py

Ігри: Aviator, JetX, Chicken Road, Lucky Jet, Spaceman, Ice Fishing Live, Sweet Bonanza, Big Bass Bonanza, Fruit Party, Gates of Olympus, Naija Wheel, Betsafe Virtual
Гео: GH (Ghana), TZ (Tanzania), IN (India)
Офери: 1xBet, MelBet
Генерація: FAL Flux Pro (fal-ai/flux-pro/v1.1)

Ти маєш доступ до інструментів які пишеш у відповіді:
[GET_FILE: назва_файлу] — читає файл з GitHub
[UPDATE_FILE: назва_файлу | повний_новий_вміст_файлу | коментар до коміту] — оновлює файл на GitHub і тригерить деплой на Railway
[LIST_FILES] — список файлів в репо
[RAILWAY_STATUS] — статус деплою на Railway

Правила роботи:
1. Перед зміною коду — завжди читай файл через GET_FILE
2. При UPDATE_FILE — передавай ПОВНИЙ вміст файлу, не частину
3. Пояснюй що саме змінив і чому
4. Якщо задача складна — роби крок за кроком
5. Відповідай українською мовою
6. Будь конкретним і лаконічним"""

def parse_and_execute_tools(response: str) -> str:
    import re

    result = response

    # GET_FILE
    for match in re.finditer(r'\[GET_FILE: ([^\]]+)\]', response):
        filename = match.group(1).strip()
        content = github_get_file(filename)
        result = result.replace(match.group(0), f"\n📄 `{filename}`:\n```python\n{content[:3000]}\n```")

    # LIST_FILES
    if '[LIST_FILES]' in result:
        files = github_list_files()
        result = result.replace('[LIST_FILES]', f"\n📁 Файли в репо:\n{files}")

    # RAILWAY_STATUS
    if '[RAILWAY_STATUS]' in result:
        status = railway_get_status()
        result = result.replace('[RAILWAY_STATUS]', f"\n🚀 Статус Railway:\n{status}")

    # UPDATE_FILE — шукаємо між тегами
    update_pattern = re.compile(r'\[UPDATE_FILE: ([^|]+)\|(.+?)\|([^\]]+)\]', re.DOTALL)
    for match in update_pattern.finditer(response):
        filename = match.group(1).strip()
        content = match.group(2).strip()
        message = match.group(3).strip()
        update_result = github_update_file(filename, content, message)
        result = result.replace(match.group(0), f"\n{update_result}")

    return result

def call_agent(user_message: str, history: list) -> tuple:
    messages = history + [{"role": "user", "content": user_message}]

    resp = req.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "system": AGENT_SYSTEM,
            "messages": messages,
        }
    )

    data = resp.json()
    response_text = data["content"][0]["text"] if "content" in data else "Помилка агента"
    final_response = parse_and_execute_tools(response_text)
    new_history = messages + [{"role": "assistant", "content": response_text}]

    return final_response, new_history[-30:]

# ============================================================
# KEYBOARDS
# ============================================================

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Вибрати гру", callback_data="mode_game")],
        [InlineKeyboardButton("📸 Завантажити шаблон", callback_data="mode_photo")],
        [InlineKeyboardButton("🤖 Агент", callback_data="mode_agent")],
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
        [InlineKeyboardButton("1xBet", callback_data="offer_1xBet"),
         InlineKeyboardButton("MelBet", callback_data="offer_MelBet")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_geo")],
    ])

def count_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("5", callback_data="count_5"),
         InlineKeyboardButton("10", callback_data="count_10"),
         InlineKeyboardButton("20", callback_data="count_20")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_offer")],
    ])

# ============================================================
# HANDLERS
# ============================================================

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

    if data == "mode_agent":
        if query.message.chat_id != ADMIN_CHAT_ID:
            await query.answer("⛔ Тільки для адміна", show_alert=True)
            return SELECT_MODE
        context.user_data["agent_history"] = []
        await query.edit_message_text(
            "🤖 *Агент активний*\n\n"
            "Пиши мені як людині — я все зроблю сам.\n\n"
            "Приклади:\n"
            "• _покажи generator\\_v2.py_\n"
            "• _додай нову гру Plinko в категорію краш_\n"
            "• _перевір статус деплою_\n"
            "• _змін кількість кроків генерації на 35_\n"
            "• _додай оффер BetWinner_\n\n"
            "/start — повернутись в меню",
            parse_mode="Markdown"
        )
        return AGENT_CHAT

    if data == "back_start":
        context.user_data.clear()
        await query.edit_message_text(
            "🎨 *Creo Generator Pro*\n\nОбери режим:",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return SELECT_MODE

    if data == "mode_photo":
        await query.edit_message_text("📸 Скинь фото крео як шаблон:")
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
            f"🚀 Генерую {count} крео...\n🎮 {game} | 🌍 {geo} | 🎯 {offer}\n⏳ ~{count * 20} сек"
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
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Новий батч", callback_data="back_start")
            ]])
        )
        return SELECT_MODE

async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_CHAT_ID:
        return AGENT_CHAT

    user_msg = update.message.text
    history = context.user_data.get("agent_history", [])

    thinking = await update.message.reply_text("⏳ Думаю...")

    try:
        response, new_history = call_agent(user_msg, history)
        context.user_data["agent_history"] = new_history
        await thinking.delete()

        # Розбиваємо на частини якщо довге
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for chunk in chunks:
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)

    except Exception as e:
        await thinking.delete()
        await update.message.reply_text(f"❌ Помилка: {e}")

    return AGENT_CHAT

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    response = req.get(file.file_path)
    context.user_data['photo_bytes'] = response.content
    context.user_data['mode'] = 'photo'
    await update.message.reply_text("✅ Фото отримано! Вибери гео:", reply_markup=geo_keyboard("back_start"))
    return SELECT_GEO

# ============================================================
# MAIN
# ============================================================

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
            AGENT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_agent_message),
                CallbackQueryHandler(handle_callback),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )
    app.add_handler(conv)
    logger.info("Creo Bot v4 + Agent started")
    app.run_polling()

if __name__ == "__main__":
    main()
