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
        "payments_text": "MTN  |  Vodafone Cash  |  AirtelTigo",
    },
    "TZ": {
        "name": "Tanzania", "currency": "TZS", "min_deposit": "2,000 TZS",
        "big_win": "500,000 TZS", "payment": "M-Pesa",
        "bonus": "Mizunguko 250 Bure",
        "cta_text": "ANZA SASA",
        "payments_text": "M-Pesa  |  Airtel  |  Tigo Pesa",
    },
    "IN": {
        "name": "India", "currency": "INR", "min_deposit": "100 INR",
        "big_win": "50,000 INR", "payment": "UPI",
        "bonus": "150 Free Spins + 200% first deposit",
        "cta_text": "ABHI KHELO",
        "payments_text": "UPI  |  PhonePe  |  Paytm",
    }
}

PROMPTS = {
    "GH": [
        'Gambling ad banner 1:1. Bright blue sky background, golden light rays. CENTER: large glowing golden fish on hook from red helicopter at top. RIGHT: smiling young Black Ghanaian adult man age 25-35, casual shirt, holding fan of banknotes. BOTTOM: pile of gold coins and green gems. TEXT on image: top-left red badge "1xBET", top-right gold badge "5000x", large gold text "WIN 8,500 GHS", white text "150 Free Spins - Start 1 GHS", orange button "PLAY NOW", bottom bar "MTN | Vodafone | AirtelTigo". Professional iGaming ad style.',
        'Gambling ad banner 1:1. Icy blue background with gold glow. CENTER: three large golden fish hanging from hooks, two helicopters at top corners. BOTTOM: explosion of gold coins and gems. TEXT on image: "1xBET CASINO", large gold "150 FREE SPINS", white "For New Players - 1 GHS only", orange button "PLAY NOW", bottom "MTN Vodafone AirtelTigo". Ice Fishing game style, vibrant 3D cartoon.',
        'Gambling ad banner 1:1. Dark dramatic background with Aviator plane flying up with multiplier graph. LEFT: excited Black Ghanaian man holding phone showing 10x win. TEXT on image: "1xBET" logo, large "I WON 8,500 GHS!", "Cash out at 10x - Start 1 GHS", orange button "PLAY AVIATOR", bottom "MTN | Vodafone | AirtelTigo | Ghana flag". Professional crash game ad.',
        'Social proof gambling ad 1:1. Bright green background with Ghana flag colors. CENTER: happy Black Ghanaian man in yellow shirt holding phone showing withdrawal confirmation "+500 GHS to MTN". TEXT on image: Ghana flag + "1xBET", large "I started with 10 GHS", gold text "withdrew 500 GHS!", "Real withdrawal proof", "Try with 1 GHS - 150 Free Spins", orange button "START NOW", bottom "MTN | Vodafone Cash | AirtelTigo". Authentic testimonial ad style.',
        'Casino slots ad banner 1:1. Dark purple casino atmosphere with gold sparkles. CENTER: slot machine showing three matching gold coins with WIN flash. RIGHT: excited Black Ghanaian man arms up celebrating. TEXT on image: "1xBET CASINO", large gold "150 FREE SPINS", white "200% Bonus First Deposit - from 1 GHS", green button "CLAIM FREE SPINS", bottom "MTN Mobile Money | Vodafone Cash | AirtelTigo", "4.4 stars 1M+ Downloads". Vibrant casino ad.',
    ],
    "TZ": [
        'Gambling ad banner 1:1. Icy blue scene. Large red fish hanging from helicopter hook center. Happy Tanzanian man left holding TZS cash. TEXT: "1xBET", large blue "MIZUNGUKO 250 BURE", white "Kwa Wachezaji Wapya", sub "Anza TZS 2000", red button "ANZA SASA", bottom "M-Pesa Airtel Tigo". Ice Fishing style.',
    ],
    "IN": [
        'Gambling ad banner 1:1. Colorful background. Happy Indian man celebrating. TEXT: "1xBET", large "150 FREE SPINS", "200% Bonus from 100 INR", button "ABHI KHELO", bottom "UPI PhonePe Paytm". Professional iGaming ad.',
    ],
}

def generate_dalle_image(prompt):
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
    img_response = requests.get(image_url, timeout=30)
    return img_response.content

async def generate_creos(update, context, count, geo, offer, status_msg):
    cfg = GEO_CONFIG[geo]
    sent = 0
    attempts = 0

    await status_msg.edit_text(f"🎨 Генерую {count} крео DALL-E 3...\nГео: {geo} | {offer}")

    while sent < count and attempts < count + 3:
        attempts += 1
        try:
            prompts = PROMPTS.get(geo, PROMPTS["GH"])
            prompt = prompts[sent % len(prompts)]
            if "mel" in offer.lower():
                prompt = prompt.replace("1xBET", "MelBet")

            await status_msg.edit_text(f"🖼 DALL-E малює {sent+1}/{count}...")

            loop = asyncio.get_event_loop()
            image_bytes = await loop.run_in_executor(None, generate_dalle_image, prompt)

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
            logger.error(f"Error: {e}")
            await status_msg.edit_text(f"⚠️ Помилка: {str(e)[:150]}")
            await asyncio.sleep(5)

    await status_msg.edit_text(f"✅ Готово! {sent}/{count} крео\nГео: {geo} | {offer}")
