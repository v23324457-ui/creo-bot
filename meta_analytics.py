import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import json
import time
import os

# ============================================================
# КОНФІГ
# ============================================================
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_APP_ID = "2446713972432354"
META_APP_SECRET = os.getenv("META_APP_SECRET")
SHEET_ID = "1fwaZv8YcNxfJwuPa6MAznxEZlWnQRsPAzEU1AgwHsAM"
GOOGLE_CREDS_FILE = "creo-bot-c37399d77d36.json"
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # твій Telegram ID

AD_ACCOUNTS = [
    "act_776144891628629",
    "act_938062731989633",
    "act_1953299878582351",
    "act_2351351755339244",
    "act_267705732692​11581",
]

METRICS = "impressions,clicks,spend,ctr,cpc,cpm,leads"
DATE_PRESET = "last_30d"  # або last_7d, last_14d

# ============================================================
# GOOGLE SHEETS
# ============================================================
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

def setup_sheets(spreadsheet):
    """Створює потрібні вкладки якщо їх нема"""
    existing = [ws.title for ws in spreadsheet.worksheets()]
    
    tabs = {
        "Креативи": ["Дата", "Акаунт", "Кампанія", "Адсет", "Крео ID", "Назва", 
                     "Impressions", "Clicks", "Spend", "CTR", "CPC", "CPM", "Leads", "URL зображення"],
        "Топ крео": ["Крео ID", "Назва", "CTR", "CPC", "Leads", "Spend", "Акаунт"],
        "Аналіз AI": ["Дата", "Аналіз", "Рекомендації"],
        "Зведення": ["Дата", "Акаунт", "Spend", "Clicks", "Impressions", "CTR", "CPM", "Leads"],
    }
    
    for tab_name, headers in tabs.items():
        if tab_name not in existing:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(headers))
            ws.append_row(headers)
            print(f"✅ Створено вкладку: {tab_name}")
        else:
            print(f"ℹ️ Вкладка вже є: {tab_name}")

# ============================================================
# META ADS API
# ============================================================
def get_ads_insights(account_id):
    """Збирає інсайти по всіх оголошеннях акаунту"""
    url = f"https://graph.facebook.com/v25.0/{account_id}/ads"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "fields": f"id,name,creative{{id,name,image_url,thumbnail_url}},insights.date_preset({DATE_PRESET}){{{METRICS}}}",
        "limit": 100,
    }
    
    all_ads = []
    while url:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if "error" in data:
            print(f"❌ Помилка {account_id}: {data['error']['message']}")
            return []
        
        all_ads.extend(data.get("data", []))
        
        # Пагінація
        paging = data.get("paging", {})
        url = paging.get("next")
        params = {}  # next вже містить всі параметри
        
        time.sleep(0.5)  # щоб не перевищити rate limit
    
    return all_ads

def parse_ad(ad, account_id):
    """Парсить дані оголошення"""
    insights = ad.get("insights", {}).get("data", [{}])[0]
    creative = ad.get("creative", {})
    
    return {
        "account_id": account_id,
        "ad_id": ad.get("id"),
        "ad_name": ad.get("name"),
        "creative_id": creative.get("id"),
        "creative_name": creative.get("name"),
        "image_url": creative.get("image_url") or creative.get("thumbnail_url", ""),
        "impressions": int(insights.get("impressions", 0)),
        "clicks": int(insights.get("clicks", 0)),
        "spend": float(insights.get("spend", 0)),
        "ctr": float(insights.get("ctr", 0)),
        "cpc": float(insights.get("cpc", 0)),
        "cpm": float(insights.get("cpm", 0)),
        "leads": int(insights.get("leads", 0)),
    }

# ============================================================
# ЗБІР ДАНИХ
# ============================================================
def collect_all_data():
    """Збирає дані з усіх акаунтів"""
    all_ads = []
    
    for account_id in AD_ACCOUNTS:
        print(f"📊 Збираю дані з {account_id}...")
        ads = get_ads_insights(account_id)
        
        for ad in ads:
            if ad.get("insights"):  # тільки ті що мають статистику
                parsed = parse_ad(ad, account_id)
                all_ads.append(parsed)
        
        print(f"✅ {account_id}: {len(ads)} оголошень")
        time.sleep(1)
    
    return all_ads

# ============================================================
# ЗАПИС В SHEETS
# ============================================================
def write_to_sheets(spreadsheet, ads_data):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Вкладка "Креативи"
    ws_creo = spreadsheet.worksheet("Креативи")
    rows = []
    for ad in ads_data:
        rows.append([
            today,
            ad["account_id"],
            "",  # кампанія (можна додати пізніше)
            "",  # адсет
            ad["ad_id"],
            ad["ad_name"],
            ad["impressions"],
            ad["clicks"],
            round(ad["spend"], 2),
            round(ad["ctr"], 3),
            round(ad["cpc"], 3),
            round(ad["cpm"], 3),
            ad["leads"],
            ad["image_url"],
        ])
    
    if rows:
        ws_creo.append_rows(rows)
        print(f"✅ Записано {len(rows)} рядків у 'Креативи'")
    
    # Вкладка "Топ крео" — топ 20 по CTR з мін. 1000 показів
    top_ads = sorted(
        [a for a in ads_data if a["impressions"] >= 1000],
        key=lambda x: x["ctr"],
        reverse=True
    )[:20]
    
    ws_top = spreadsheet.worksheet("Топ крео")
    ws_top.clear()
    ws_top.append_row(["Крео ID", "Назва", "CTR", "CPC", "Leads", "Spend", "Акаунт"])
    top_rows = [[
        a["ad_id"], a["ad_name"], round(a["ctr"], 3),
        round(a["cpc"], 3), a["leads"], round(a["spend"], 2), a["account_id"]
    ] for a in top_ads]
    if top_rows:
        ws_top.append_rows(top_rows)
    
    # Вкладка "Зведення"
    ws_sum = spreadsheet.worksheet("Зведення")
    total_spend = sum(a["spend"] for a in ads_data)
    total_clicks = sum(a["clicks"] for a in ads_data)
    total_impressions = sum(a["impressions"] for a in ads_data)
    total_leads = sum(a["leads"] for a in ads_data)
    avg_ctr = total_clicks / total_impressions * 100 if total_impressions else 0
    avg_cpm = total_spend / total_impressions * 1000 if total_impressions else 0
    
    ws_sum.append_row([
        today, "ALL", round(total_spend, 2), total_clicks,
        total_impressions, round(avg_ctr, 3), round(avg_cpm, 3), total_leads
    ])
    
    return top_ads

# ============================================================
# AI АНАЛІЗ
# ============================================================
def analyze_with_claude(top_ads, all_ads):
    """Аналізує паттерни через Claude API"""
    if not ANTHROPIC_KEY:
        return "ANTHROPIC_KEY не налаштований"
    
    summary = f"""
Проаналізуй ці рекламні креативи з Meta Ads і знайди паттерни конверсії.

ЗАГАЛЬНА СТАТИСТИКА:
- Всього крео: {len(all_ads)}
- Загальний spend: ${sum(a['spend'] for a in all_ads):.2f}
- Загальний leads: {sum(a['leads'] for a in all_ads)}

ТОП-10 КРЕО ПО CTR:
"""
    for i, ad in enumerate(top_ads[:10], 1):
        summary += f"{i}. {ad['ad_name']} | CTR: {ad['ctr']:.3f}% | CPC: ${ad['cpc']:.2f} | Leads: {ad['leads']} | Spend: ${ad['spend']:.2f}\n"
    
    summary += "\nДай конкретні рекомендації: які назви/патерни крео дають кращий CTR, що спільне у топ крео, що варто тестувати далі. Відповідай українською."
    
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": summary}]
        }
    )
    
    data = resp.json()
    return data["content"][0]["text"] if "content" in data else "Помилка аналізу"

def save_analysis(spreadsheet, analysis):
    ws = spreadsheet.worksheet("Аналіз AI")
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.append_row([today, analysis, ""])
    print("✅ Аналіз збережено")

# ============================================================
# TELEGRAM ЗВІТ
# ============================================================
def send_telegram_report(top_ads, all_ads, analysis):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram не налаштований")
        return
    
    total_spend = sum(a["spend"] for a in all_ads)
    total_leads = sum(a["leads"] for a in all_ads)
    
    msg = f"""📊 *Creo Analytics Report*
🗓 {datetime.now().strftime('%Y-%m-%d %H:%M')}

💰 Загальний spend: ${total_spend:.2f}
👥 Leads: {total_leads}
🎨 Крео проаналізовано: {len(all_ads)}

🏆 *Топ-5 крео по CTR:*
"""
    for i, ad in enumerate(top_ads[:5], 1):
        msg += f"{i}. `{ad['ad_name'][:30]}` | CTR: {ad['ctr']:.2f}% | Leads: {ad['leads']}\n"
    
    msg += f"\n🤖 *AI Аналіз:*\n{analysis[:500]}..."
    
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }
    )
    print("✅ Telegram звіт відправлено")

# ============================================================
# MAIN
# ============================================================
def main():
    print("🚀 Запуск Creo Analytics...")
    
    # Підключення до Sheets
    spreadsheet = get_sheet()
    setup_sheets(spreadsheet)
    
    # Збір даних
    print("\n📥 Збираю дані з Meta Ads...")
    ads_data = collect_all_data()
    print(f"\n✅ Всього зібрано: {len(ads_data)} крео")
    
    if not ads_data:
        print("❌ Немає даних для аналізу")
        return
    
    # Запис в Sheets
    print("\n📝 Записую в Google Sheets...")
    top_ads = write_to_sheets(spreadsheet, ads_data)
    
    # AI аналіз
    print("\n🤖 Аналізую паттерни через Claude...")
    analysis = analyze_with_claude(top_ads, ads_data)
    save_analysis(spreadsheet, analysis)
    print(f"\n📊 Аналіз:\n{analysis[:300]}...")
    
    # Telegram звіт
    print("\n📨 Відправляю звіт в Telegram...")
    send_telegram_report(top_ads, ads_data, analysis)
    
    print("\n✅ Готово! Дані в Google Sheets.")

if __name__ == "__main__":
    main()
