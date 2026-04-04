import os
import logging
import requests as req
import base64
import json
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
RAILWAY_PROJECT = "optimistic-presence"

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
# AGENT TOOLS
# ============================================================

def github_get_file(path: str) -> dict:
    """Читає файл з GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    resp = req.get(url, headers=headers)
    return resp.json()

def github_update_file(path: str, content: str, message: str) -> bool:
    """Оновлює файл на GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Отримуємо поточний sha
    current = req.get(url, headers=headers).json()
    sha = current.get("sha", "")
    
    encoded = base64.b64encode(content.encode()).decode()
    data = {"message": message, "content": encoded, "sha": sha}
    
    resp = req.put(url, headers=headers, json=data)
    return resp.status_code in [200, 201]

def railway_get_logs() -> str:
    """Отримує логи з Railway через GraphQL"""
    if not RAILWAY_TOKEN:
        return "RAILWAY_TOKEN не налаштований"
    
    url = "https://backboard.railway.app/graphql/v2"
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json"
    }
    query = """
    query {
      me {
        projects {
          edges {
            node {
              name
              services {
                edges {
                  node {
                    name
                    deployments(last: 1) {
                      edges {
                        node {
                          status
                          createdAt
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    try:
        resp = req.post(url, headers=headers, json={"query": query}, timeout=10)
        data = resp.json()
        projects = data.get("data", {}).get("me", {}).get("projects", {}).get("edges", [])
        
        result = ""
        for p in projects:
            project = p["node"]
            if RAILWAY_PROJECT in project["name"].lower():
                for s in project["services"]["edges"]:
                    service = s["node"]
                    deployments = service["deployments"]["edges"]
                    if deployments:
                        dep = deployments[-1]["node"]
                        result += f"Сервіс: {service['name']}\nСтатус: {dep['status']}\nЧас: {dep['createdAt']}\n"
        
        return result or "Проект не знайдено"
    except Exception as e:
        return f"Помилка: {e}"

def call_claude_agent(user_message: str, history: list) -> str:
    """Викликає Claude як агента"""
    system = f"""Ти агент-девопс для Telegram бота creo-bot. 
Репо: {GITHUB_REPO}
Railway проект: {RAILWAY_PROJECT}

Ти вмієш:
1. Читати/редагувати файли в GitHub (github_get_file, github_update_file)
2. Дивитись логи Railway (railway_get_logs)
3. Пояснювати помилки і пропонувати фікси

Коли користувач просить щось зробити — роби конкретні дії.
Якщо треба змінити код — поясни що саме зміниш і запитай підтвердження.
Відповідай коротко і по ділу українською мовою."""

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
            "max_tokens": 1000,
            "system": system,
            "messages": messages,
        }
    )
    
    data = resp.json()
    return data["content"][0]["text"] if "content" in data else "Помилка агента"

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

def agent_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Статус деплою", callback_data="agent_status")],
        [InlineKeyboardButton("📁 Список файлів", callback_data="agent_files")],
        [InlineKeyboardButton("🐛 Перевірити логи", callback_data="agent_logs")],
        [InlineKeyboardButton("💬 Чат з агентом", callback_data="agent_chat")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_start")],
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

    # AGENT
    if data == "mode_agent":
        if query.message.chat_id != ADMIN_CHAT_ID:
            await query.answer("⛔ Тільки для адміна", show_alert=True)
            return SELECT_MODE
        await query.edit_message_text("🤖 *Агент DevOps*\n\nОбери дію або напиши задачу:", reply_markup=agent_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

    if data == "agent_status":
        await query.edit_message_text("⏳ Перевіряю статус деплою...")
        logs = railway_get_logs()
        await query.edit_message_text(f"📊 *Статус Railway:*\n\n```{logs}```", reply_markup=agent_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

    if data == "agent_files":
        await query.edit_message_text("⏳ Отримую список файлів...")
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        resp = req.get(url, headers=headers)
        files = [f["name"] for f in resp.json() if isinstance(resp.json(), list)]
        text = "📁 *Файли в репо:*\n\n" + "\n".join(f"• {f}" for f in files)
        await query.edit_message_text(text, reply_markup=agent_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

    if data == "agent_logs":
        await query.edit_message_text("⏳ Отримую логи...")
        result = call_claude_agent("Перевір логи Railway і скажи чи є помилки", context.user_data.get("agent_history", []))
        await query.edit_message_text(f"🐛 *Аналіз логів:*\n\n{result}", reply_markup=agent_keyboard(), parse_mode="Markdown")
        return SELECT_MODE

    if data == "agent_chat":
        context.user_data["agent_history"] = []
        await query.edit_message_text(
            "💬 *Чат з агентом*\n\nПиши задачу — агент виконає.\n\nПриклади:\n• перевір логи\n• покажи generator_v2.py\n• додай нову гру X\n• виправ помилку Y\n\n/start — вийти",
            parse_mode="Markdown"
        )
        return AGENT_CHAT

    # MAIN FLOW
    if data == "back_start":
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
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Новий батч", callback_data="back_start")]])
        )
        return SELECT_MODE

async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє повідомлення в режимі агента"""
    if update.message.chat_id != ADMIN_CHAT_ID:
        return AGENT_CHAT

    user_msg = update.message.text
    history = context.user_data.get("agent_history", [])

    await update.message.reply_text("⏳ Агент думає...")

    # Перевіряємо чи треба виконати дії
    action_keywords = {
        "покажи": lambda: handle_show_file(user_msg),
        "перевір логи": lambda: railway_get_logs(),
        "статус": lambda: railway_get_logs(),
    }

    extra_context = ""
    for keyword, action in action_keywords.items():
        if keyword in user_msg.lower():
            extra_context = f"\nРезультат інструменту:\n{action()}"
            break

    response = call_claude_agent(user_msg + extra_context, history)

    # Зберігаємо історію
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": response})
    context.user_data["agent_history"] = history[-20:]  # останні 10 обмінів

    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Меню агента", callback_data="mode_agent")]])
    )
    return AGENT_CHAT

def handle_show_file(msg: str) -> str:
    """Показує файл з GitHub"""
    files = ["bot.py", "generator_v2.py", "requirements.txt", "railway.toml", "meta_analytics.py"]
    for f in files:
        if f in msg:
            result = github_get_file(f)
            if "content" in result:
                content = base64.b64decode(result["content"]).decode()
                return content[:2000]  # перші 2000 символів
    return "Файл не знайдено"

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
