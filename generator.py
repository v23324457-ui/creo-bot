import os
import asyncio
import anthropic
import logging
import requests
import io

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")

GEO_CONFIG = {
    "GH": {
        "name": "Ghana", "currency": "GHS", "min_deposit": "1 GHS",
        "big_win": "8,500 GHS", "payment": "MTN Mobile Money",
        "bonus": "150 Free Spins + 200% first deposit",
        "cta_text": "PLAY NOW",
        "flag": "Ghana flag (red gold green black star)",
        "payments_text": "MTN  |  Vodafone Cash  |  AirtelTigo",
        "local_lang": "English",
    },
    "TZ": {
        "name": "Tanzania", "currency": "TZS", "min_deposit": "2,000 TZS",
        "big_win": "500,000 TZS", "payment": "M-Pesa",
        "bonus": "Mizunguko 250 Bure",
        "cta_text": "ANZA SASA",
        "flag": "Tanzania flag (green yellow black diagonal)",
        "payments_text": "M-Pesa  |  Airtel  |  Tigo Pesa",
        "local_lang": "Swahili",
    },
    "IN": {
        "name": "India", "currency": "INR", "min_deposit": "100 INR",
        "big_win": "50,000 INR", "payment": "UPI",
        "bonus": "150 Free Spins + 200% first deposit",
        "cta_text": "ABHI KHELO",
        "flag": "India flag (saffron white green Ashoka chakra)",
        "payments_text": "UPI  |  PhonePe  |  Paytm",
        "local_lang": "Hindi",
    }
}

# Creative types for variety
CREATIVE_TYPES = {
    "GH": [
        {
            "type": "winner_man",
            "prompt_template": """Create a gambling advertisement banner image (1:1 square format).

BACKGROUND: Bright blue sky with white clouds and golden light rays from center. Bottom half covered with massive pile of shiny gold coins and green gems.

LEFT SIDE: Real-looking happy smiling young Black African Ghanaian man, age 25-35, casual colorful shirt, holding phone showing money, celebrating with raised fist or open arms. Photorealistic portrait style, chest up.

CENTER/RIGHT: Large glowing golden fish hanging from a metal hook on a chain coming from a red helicopter at top.

TOP LEFT CORNER: Bold text "1xBET" in white on red background badge.
TOP RIGHT CORNER: Bold text "5000x" in gold on dark badge.

BOTTOM SECTION (large bold text, easy to read):
Line 1 (biggest, gold/yellow color, black outline): "WIN 8,500 GHS"
Line 2 (white, black outline): "150 Free Spins + Start from 1 GHS"
Line 3: Orange rounded button with white text "PLAY NOW"
Bottom bar: "MTN  |  Vodafone  |  AirtelTigo" with small payment icons

Ghana flag colors (red gold green) as decorative accents. 
Style: Professional iGaming advertisement, vibrant, high quality."""
        },
        {
            "type": "ice_fishing",
            "prompt_template": """Create a professional gambling advertisement banner (square 1:1).

BACKGROUND: Icy blue scene OR bright tropical blue sky. Light rays from center creating dramatic effect.

CENTER: Three large golden/shiny fish hanging from fishing hooks on chains. Two blue-yellow helicopters at top corners holding the hooks. Fish are glowing with golden light and coins exploding around them.

BOTTOM PILE: Massive overflow of golden coins, green diamond gems, red rubies.

TEXT ON IMAGE (large, bold, readable):
- Top: "1xBET CASINO" logo style text
- Big center text in gold: "150 FREE SPINS"  
- Below in white: "For New Players • Start 1 GHS"
- Bottom orange button: "PLAY NOW"
- Very bottom: "MTN  Vodafone  AirtelTigo" payment row

TOP RIGHT: "★ 4.4  1M+ Downloads" badge

Style: Like Ice Fishing Live game advertisement, 3D cartoon illustration, vibrant saturated colors, professional iGaming ad quality."""
        },
        {
            "type": "crash_aviator",
            "prompt_template": """Create a gambling advertisement banner (square 1:1 format).

SCENE: Dark dramatic background with orange/red Aviator plane flying upward with multiplier graph line going up steeply.

LEFT: Excited happy young Black Ghanaian man holding phone screen showing "10x" multiplier and cash withdrawal notification. Big smile, casual clothes.

GRAPH: Aviator-style crash game curve going up showing "50x", "100x" multipliers in bright green.

TEXT ON IMAGE (bold, large):
Top left: "1xBET" logo
Big text center: "I WON 8,500 GHS"
Below: "Cash Out at 10x • Start with 1 GHS"
Orange button: "PLAY AVIATOR NOW"
Bottom: Ghana flag + "MTN  |  Vodafone Cash  |  AirtelTigo"

Style: Professional sports betting/crash game advertisement, dark dramatic, high energy."""
        },
        {
            "type": "social_proof",
            "prompt_template": """Create a social proof gambling advertisement banner (square 1:1).

BACKGROUND: Bright green or blue gradient with Ghana flag colors accents.

CENTER-LEFT: Happy young Black Ghanaian man in yellow shirt (Ghana colors), holding phone showing withdrawal confirmation screen with "+500 GHS" notification. Big genuine smile.

PHONE SCREEN (visible, readable): Shows "Withdrawal successful: 500 GHS to MTN Mobile Money"

TEXT ON IMAGE:
Top: Ghana flag + "1xBET"  
Large text: "I started with 10 GHS"
Even larger gold text: "and withdrew 500 GHS!"
Below: "Real withdrawal proof"
Sub: "Try with just 1 GHS • 150 Free Spins"
Orange CTA button: "START NOW"
Bottom: "MTN  |  Vodafone Cash  |  AirtelTigo  |  1XBET"

Style: Like real testimonial ad, authentic, trustworthy, professional iGaming advertisement."""
        },
        {
            "type": "slot_bonus",
            "prompt_template": """Create a slots bonus gambling advertisement banner (square 1:1).

BACKGROUND: Dark purple/blue casino atmosphere with golden light effects and sparkles.

CENTER: Slot machine reels showing 3 matching symbols (gold coins or 7s or stars) with "WIN!" flash effect. Coins exploding outward.

RIGHT: Excited young Black Ghanaian man with huge smile, arms up celebrating.

TEXT ON IMAGE (large bold readable):
Top: "1xBET CASINO" 
Center big gold text: "150 FREE SPINS"
Below white: "200% Bonus on First Deposit"
Sub: "Deposit just 1 GHS to start"
Green/Orange button: "CLAIM FREE SPINS"
Bottom: "MTN Mobile Money  |  Vodafone Cash  |  AirtelTigo"
Bottom bar: "★ 4.4  •  1M+ Downloads  •  Fast Payouts"

Style: Casino slot advertisement, vibrant purple/gold, professional quality."""
        },
    ]
}

def get_dalle_prompt(geo: str, offer: str, index: int) -> str:
    cfg = GEO_CONFIG[geo]
    
    if geo == "GH":
        types = CREATIVE_TYPES["GH"]
        creative = types[index % len(types)]
        prompt = creative["prompt_template"]
        # Replace offer name if MelBet
        if "mel" in offer.lower():
            prompt = prompt.replace("1xBET", "MelBet").replace("1xBet", "MelBet")
        return prompt
    elif geo == "TZ":
        return f"""Create a professional gambling advertisement banner (square 1:1).

BACKGROUND: Icy blue arctic scene OR bright blue sky. Large red/golden fish in center hanging from helicopter hook. Gold coins explosion.

LEFT: Happy Tanzanian man holding cash (TZS banknotes), big smile.

TEXT ON IMAGE (large bold):
Top left: "1xBET" or "{offer}" logo
Big text in gold: "MIZUNGUKO 250 BURE"
Below white: "Kwa Wachezaji Wapya"  
Sub: "Anza na TZS 2,000 tu"
Red/Orange button: "ANZA SASA"
Bottom: "M-Pesa  |  Airtel  |  Tigo Pesa"
Bottom: "★ 4.4  •  UPAKUAJI MILIONI 1+"

Style: Professional iGaming advertisement, Ice Fishing style, vibrant."""
    else:
        return f"""Create a professional gambling advertisement banner (square 1:1).

BACKGROUND: Bright colorful Indian-themed or casino background.
CENTER: Happy Indian man celebrating with cricket bat or holding phone showing win.
TEXT: "{offer}" logo, "150 FREE SPINS", "200% Bonus", "Start ₹100", "UPI PhonePe Paytm"
Style: Professional iGaming advertisement."""

async def generate_dalle_image(prompt: str) -> bytes:
    """Generate image using DALL-E 3"""
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
        headers=headers,
        json=payload,
        timeout=60
    )
    
    data = response.json()
    
    if "error" in data:
        raise Exception(f"DALL-E error: {data['error']['message']}")
    
    image_url = data["data"][0]["url"]
    
    # Download the image
    img_response = requests.get(image_url, timeout=30)
    return img_response.content

async def generate_creos(update, context, count: int, geo: str, offer: str, status_msg):
    cfg = GEO_CONFIG[geo]
    sent = 0
    attempts = 0

    await status_msg.edit_text(
        f"🎨 Генерую {count} крео через DALL-E 3...\n"
        f"Гео: {geo} | {offer}\n"
        f"~30 сек на крео"
    )

    while sent < count and attempts < count + 3:
        attempts += 1
        try:
            prompt = get_dalle_prompt(geo, offer, sent)
            
            await status_msg.edit_text(
                f"🖼 DALL-E малює крео {sent+1}/{count}...\n"
                f"Тип: {['winner', 'ice fishing', 'aviator', 'social proof', 'slots'][sent % 5]}"
            )

            image_bytes = generate_dalle_image(prompt)

            caption = (
                f"✅ Крео #{sent+1} | {geo} | {offer}\n"
                f"💰 {cfg['big_win']} | 🎯 {cfg['cta_text']}\n"
                f"💳 {cfg['payments_text']}"
            )

            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=io.BytesIO(image_bytes),
                caption=caption
            )

            sent += 1
            if sent < count:
                await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"Error attempt {attempts}: {e}")
            await status_msg.edit_text(f"⚠️ Помилка {sent+1}/{count}:\n{str(e)[:150]}\nПовтор...")
            await asyncio.sleep(5)

    await status_msg.edit_text(
        f"✅ Готово! {sent}/{count} крео\n"
        f"Гео: {geo} | {offer}"
    )
