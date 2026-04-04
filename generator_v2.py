import os
import base64
import asyncio
import anthropic
import requests
import io
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")

GEO = {
    "GH": {
        "name": "Ghana", "currency": "GHS", "min_deposit": "1 GHS",
        "language": "English", "flag": "Ghana flag red gold green black star",
        "payments": "MTN Mobile Money, Vodafone Cash, AirtelTigo",
        "payments_short": "MTN | Vodafone | AirtelTigo",
        "person": "young Ghanaian Black African man age 25-35",
        "big_win": "8,500 GHS", "medium_win": "500 GHS", "small_win": "50 GHS",
        "cta": "PLAY NOW", "cta2": "CLAIM BONUS", "cta3": "START FREE",
        "urgency": "Today Only!", "urgency2": "Limited Offer!", "urgency3": "New Game!",
        "locale_text": "For Ghana Players Only",
        "download": "★ 4.4  |  1M+ Downloads",
    },
    "TZ": {
        "name": "Tanzania", "currency": "TZS", "min_deposit": "2,000 TZS",
        "language": "Swahili", "flag": "Tanzania flag green yellow black diagonal",
        "payments": "M-Pesa, Airtel Money, Tigo Pesa",
        "payments_short": "M-Pesa | Airtel | Tigo",
        "person": "young Tanzanian Black African man age 25-35",
        "big_win": "500,000 TZS", "medium_win": "50,000 TZS", "small_win": "5,000 TZS",
        "cta": "ANZA SASA", "cta2": "PATA BONUS", "cta3": "CHEZA BURE",
        "urgency": "Leo Tu!", "urgency2": "Muda Mfupi!", "urgency3": "Mchezo Mpya!",
        "locale_text": "Kwa Wachezaji wa Tanzania",
        "download": "★ 4.4  |  Upakuaji Milioni 1+",
    },
    "IN": {
        "name": "India", "currency": "INR", "min_deposit": "100 INR",
        "language": "Hindi", "flag": "India flag saffron white green Ashoka chakra",
        "payments": "UPI, PhonePe, Paytm",
        "payments_short": "UPI | PhonePe | Paytm",
        "person": "young Indian man age 25-35",
        "big_win": "50,000 INR", "medium_win": "5,000 INR", "small_win": "500 INR",
        "cta": "ABHI KHELO", "cta2": "BONUS CLAIM KARO", "cta3": "FREE SHURU KARO",
        "urgency": "Sirf Aaj!", "urgency2": "Limited Offer!", "urgency3": "Naya Game!",
        "locale_text": "India Ke Liye Special Offer",
        "download": "★ 4.4  |  1M+ Downloads",
    }
}

# 10 variant formulas — different angle to push deposit
VARIANT_FORMULAS = [
    {
        "id": 1,
        "angle": "BIG WIN",
        "desc": "Huge win amount front and center, person celebrating",
        "text_focus": "massive win amount in local currency",
        "person": True,
        "urgency": False,
        "social_proof": False,
    },
    {
        "id": 2,
        "angle": "FREE SPINS",
        "desc": "150 free spins offer, low barrier entry",
        "text_focus": "free spins bonus, start from minimum deposit",
        "person": False,
        "urgency": True,
        "social_proof": False,
    },
    {
        "id": 3,
        "angle": "SOCIAL PROOF",
        "desc": "Real person showing phone with withdrawal proof",
        "text_focus": "real withdrawal, trust, local payment success",
        "person": True,
        "urgency": False,
        "social_proof": True,
    },
    {
        "id": 4,
        "angle": "URGENCY",
        "desc": "Today only limited offer, countdown feeling",
        "text_focus": "today only, limited slots, act now",
        "person": True,
        "urgency": True,
        "social_proof": False,
    },
    {
        "id": 5,
        "angle": "LOCAL PAYMENT",
        "desc": "MTN/M-Pesa/UPI prominent, instant withdrawal",
        "text_focus": "instant payout via local payment, fast withdrawal",
        "person": True,
        "urgency": False,
        "social_proof": True,
    },
    {
        "id": 6,
        "angle": "LOW BARRIER",
        "desc": "Start with minimum, win big ratio",
        "text_focus": "start with 1 GHS win thousands, low entry",
        "person": False,
        "urgency": True,
        "social_proof": False,
    },
    {
        "id": 7,
        "angle": "GAME FEATURE",
        "desc": "Show the game's best feature/mechanic",
        "text_focus": "game multiplier, jackpot feature, bonus round",
        "person": False,
        "urgency": False,
        "social_proof": False,
    },
    {
        "id": 8,
        "angle": "NIGHT WIN",
        "desc": "Dark dramatic scene, person in car or night city winning",
        "text_focus": "win anytime anywhere, mobile gaming at night",
        "person": True,
        "urgency": False,
        "social_proof": True,
    },
    {
        "id": 9,
        "angle": "200% BONUS",
        "desc": "Double your money bonus, first deposit",
        "text_focus": "200% bonus on first deposit, double money",
        "person": False,
        "urgency": True,
        "social_proof": False,
    },
    {
        "id": 10,
        "angle": "EXCLUSIVE",
        "desc": "Exclusive offer for this country, flag prominent",
        "text_focus": "exclusive offer for Ghana/Tanzania/India players only",
        "person": True,
        "urgency": True,
        "social_proof": False,
    },
]

def analyze_creative(photo_bytes: bytes) -> dict:
    """Claude Vision analyzes the creative and extracts key info"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    image_data = base64.standard_b64encode(photo_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}
                },
                {
                    "type": "text",
                    "text": """Analyze this iGaming advertisement creative. Return ONLY JSON:
{
  "game_name": "exact game name (Ice Fishing Live, Aviator, Sweet Bonanza, Chicken Road, etc)",
  "game_style": "cartoon|realistic|slot|crash|fishing|arcade",
  "main_colors": ["color1", "color2", "color3"],
  "background": "describe background style in 10 words",
  "has_person": true/false,
  "person_style": "describe person if present",
  "has_helicopter": true/false,
  "has_fish": true/false,
  "has_coins": true/false,
  "original_geo": "TZ/GH/IN/OTHER",
  "original_offer": "1xBet/MelBet/other",
  "composition": "describe layout in 15 words",
  "key_visual_elements": ["element1", "element2", "element3"],
  "creative_type": "ice_fishing|crash|slot|person_win|game_art|free_spins"
}"""
                }
            ]
        }]
    )

    import json
    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def build_dalle_prompt(analysis: dict, geo: str, offer: str, variant: dict) -> str:
    """Build DALL-E prompt for one variant"""
    g = GEO[geo]
    game = analysis.get("game_name", "casino game")
    style = analysis.get("game_style", "cartoon")
    colors = analysis.get("main_colors", ["blue", "gold"])
    bg = analysis.get("background", "bright colorful")
    has_heli = analysis.get("has_helicopter", False)
    has_fish = analysis.get("has_fish", False)
    has_coins = analysis.get("has_coins", True)
    elements = analysis.get("key_visual_elements", [])

    # Build visual description
    visual_parts = []

    # Background
    visual_parts.append(f"Background: {bg}, colors {', '.join(colors)}")

    # Game elements (keep original game style)
    if has_fish:
        visual_parts.append("large golden glowing fish as main visual element")
    if has_heli:
        visual_parts.append(f"helicopter at top with {offer} branding")
    if has_coins:
        visual_parts.append("pile of gold coins and gems at bottom")
    for el in elements[:2]:
        visual_parts.append(el)

    # Person based on variant
    if variant["person"]:
        if variant["angle"] == "SOCIAL PROOF" or variant["angle"] == "NIGHT WIN":
            visual_parts.append(
                f"{g['person']} holding phone showing withdrawal notification "
                f"'{g['medium_win']} to {g['payments'].split(',')[0]}', big smile"
            )
        else:
            visual_parts.append(
                f"{g['person']} celebrating, holding fan of {g['currency']} banknotes, big smile"
            )

    # Text on image
    text_parts = []

    # Offer logo
    text_parts.append(f'top-left corner: "{offer}" logo badge in red/blue')

    # Main text based on angle
    if variant["angle"] == "BIG WIN":
        text_parts.append(f'large gold text: "WIN {g["big_win"]}"')
        text_parts.append(f'white text: "{g["game_name"] if "name" not in g else game} • Start {g["min_deposit"]}"')
    elif variant["angle"] == "FREE SPINS":
        text_parts.append('large gold text: "150 FREE SPINS"')
        text_parts.append(f'white text: "For New Players • Start {g["min_deposit"]}"')
    elif variant["angle"] == "SOCIAL PROOF":
        text_parts.append(f'large text: "I won {g["medium_win"]}!"')
        text_parts.append(f'white text: "Real withdrawal via {g["payments"].split(",")[0]}"')
    elif variant["angle"] == "URGENCY":
        text_parts.append(f'large gold text: "{g["urgency"]}"')
        text_parts.append(f'white text: "WIN {g["big_win"]} • {g["min_deposit"]} only"')
    elif variant["angle"] == "LOCAL PAYMENT":
        text_parts.append(f'large text: "Instant Payout via {g["payments"].split(",")[0]}"')
        text_parts.append(f'gold text: "WIN {g["big_win"]}"')
    elif variant["angle"] == "LOW BARRIER":
        text_parts.append(f'large gold text: "{g["min_deposit"]} → {g["big_win"]}"')
        text_parts.append('white text: "Start Small Win Big Today"')
    elif variant["angle"] == "GAME FEATURE":
        text_parts.append(f'large text: "{game}"')
        text_parts.append(f'gold text: "5000x MULTIPLIER • WIN {g["big_win"]}"')
    elif variant["angle"] == "NIGHT WIN":
        text_parts.append(f'large gold text: "WIN {g["big_win"]}"')
        text_parts.append(f'white text: "In 5 minutes via {g["payments"].split(",")[0]}"')
    elif variant["angle"] == "200% BONUS":
        text_parts.append('large gold text: "200% BONUS"')
        text_parts.append(f'white text: "On First Deposit • + 150 Free Spins"')
    elif variant["angle"] == "EXCLUSIVE":
        text_parts.append(f'large text: "{g["locale_text"]}"')
        text_parts.append(f'gold text: "150 FREE SPINS + WIN {g["big_win"]}"')

    # CTA button
    text_parts.append(f'orange rounded button: "{g["cta"]}"')

    # Payment logos
    text_parts.append(f'bottom bar: "{g["payments_short"]}" payment logos')

    # Download badge
    text_parts.append(f'small badge: "{g["download"]}"')

    # Flag
    if variant["angle"] == "EXCLUSIVE":
        text_parts.append(f'{g["flag"]} flag shown prominently')

    # Combine
    prompt = (
        f"Professional iGaming advertisement banner, square 1:1 format, "
        f"{style} art style, vibrant saturated colors, high quality.\n"
        f"VISUAL: {'. '.join(visual_parts)}.\n"
        f"TEXT ON IMAGE: {'. '.join(text_parts)}.\n"
        f"Style: professional gambling ad like {game} game advertisement."
    )

    return prompt

def generate_image(prompt: str) -> bytes:
    """Generate image via DALL-E 3"""
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "hd",
        "style": "vivid"
    }
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers, json=payload, timeout=90
    )
    data = response.json()
    if "error" in data:
        raise Exception(f"DALL-E: {data['error']['message']}")
    image_url = data["data"][0]["url"]
    return requests.get(image_url, timeout=30).content

async def analyze_and_generate(update, context, photo_bytes: bytes, geo: str, offer: str):
    """Main pipeline: analyze photo → generate 10 variants"""
    chat_id = update.effective_chat.id

    # Step 1: Analyze
    await context.bot.send_message(chat_id, "🔍 Claude аналізує крео...")
    loop = asyncio.get_event_loop()

    try:
        analysis = await loop.run_in_executor(None, analyze_creative, photo_bytes)
        game_name = analysis.get("game_name", "casino game")
        creative_type = analysis.get("creative_type", "unknown")
        await context.bot.send_message(
            chat_id,
            f"✅ Визначено:\n"
            f"🎮 Гра: {game_name}\n"
            f"🎨 Тип: {creative_type}\n\n"
            f"Генерую 10 варіантів під {geo}..."
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        analysis = {"game_name": "casino game", "game_style": "cartoon",
                    "main_colors": ["blue", "gold"], "background": "bright colorful",
                    "has_person": True, "has_helicopter": False, "has_fish": False,
                    "has_coins": True, "key_visual_elements": [], "creative_type": "slot"}
        await context.bot.send_message(chat_id, "⚡ Аналіз завершено. Генерую...")

    # Step 2: Generate 10 variants
    for i, variant in enumerate(VARIANT_FORMULAS):
        try:
            await context.bot.send_message(
                chat_id,
                f"🖼 {i+1}/10 — {variant['angle']}..."
            )

            prompt = build_dalle_prompt(analysis, geo, offer, variant)
            image_bytes = await loop.run_in_executor(None, generate_image, prompt)

            caption = (
                f"#{i+1} | {variant['angle']} | {geo} | {offer}\n"
                f"🎮 {analysis.get('game_name', 'game')}\n"
                f"💡 {variant['desc']}"
            )

            await context.bot.send_photo(
                chat_id=chat_id,
                photo=io.BytesIO(image_bytes),
                caption=caption
            )

            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error variant {i+1}: {e}")
            await context.bot.send_message(chat_id, f"⚠️ Варіант {i+1} пропущено: {str(e)[:100]}")
            await asyncio.sleep(3)
