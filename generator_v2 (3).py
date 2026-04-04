import os
import base64
import asyncio
import anthropic
import requests
import io
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
FAL_KEY = os.getenv("FAL_KEY")

# ============================================================
# GEO
# ============================================================
GEO = {
    "GH": {
        "name": "Ghana", "currency": "GHS", "min_deposit": "1 GHS",
        "language": "English", "flag": "Ghana flag red gold green black star",
        "payments": "MTN Mobile Money, Vodafone Cash, AirtelTigo",
        "payments_short": "MTN | Vodafone | AirtelTigo",
        "person": "young Ghanaian Black African man age 25-35 smiling",
        "big_win": "8,500 GHS", "medium_win": "500 GHS",
        "cta": "PLAY NOW", "cta2": "CLAIM BONUS",
        "urgency": "Today Only!", "urgency2": "New Game!",
        "exclusive": "Exclusive for Ghana Players",
        "download": "★ 4.4  |  1M+ Downloads",
    },
    "TZ": {
        "name": "Tanzania", "currency": "TZS", "min_deposit": "2,000 TZS",
        "language": "Swahili", "flag": "Tanzania flag green yellow black diagonal",
        "payments": "M-Pesa, Airtel Money, Tigo Pesa",
        "payments_short": "M-Pesa | Airtel | Tigo",
        "person": "young Tanzanian Black African man age 25-35 smiling",
        "big_win": "500,000 TZS", "medium_win": "50,000 TZS",
        "cta": "ANZA SASA", "cta2": "PATA BONUS",
        "urgency": "Leo Tu!", "urgency2": "Mchezo Mpya!",
        "exclusive": "Kwa Wachezaji wa Tanzania",
        "download": "★ 4.4  |  Upakuaji Milioni 1+",
    },
    "IN": {
        "name": "India", "currency": "INR", "min_deposit": "100 INR",
        "language": "Hindi", "flag": "India flag saffron white green Ashoka chakra",
        "payments": "UPI, PhonePe, Paytm",
        "payments_short": "UPI | PhonePe | Paytm",
        "person": "young Indian man age 25-35 smiling",
        "big_win": "50,000 INR", "medium_win": "5,000 INR",
        "cta": "ABHI KHELO", "cta2": "BONUS LO",
        "urgency": "Sirf Aaj!", "urgency2": "Naya Game!",
        "exclusive": "India Ke Liye Special",
        "download": "★ 4.4  |  1M+ Downloads",
    }
}

# ============================================================
# GAME VISUALS
# ============================================================
GAME_VISUALS = {
    "aviator": {
        "style": "dark dramatic background with red Aviator plane flying upward, orange multiplier graph curve going steeply up, dark atmospheric clouds, red and orange colors, crash game aesthetic",
        "key_elements": "Aviator plane, multiplier graph 100x+, cash out button visible on phone screen",
        "colors": "dark red, orange, black, gold",
        "logo": "AVIATOR game logo in red and white at top",
    },
    "jetx": {
        "style": "space dark background with JetX rocket flying upward trailing fire, multiplier numbers floating, futuristic UI elements",
        "key_elements": "JetX rocket, multiplier display, space atmosphere, blue fire trail",
        "colors": "dark blue, purple, gold, white",
        "logo": "JetX logo in blue and white",
    },
    "chicken_road": {
        "style": "cartoon African savanna with fire pits, funny cartoon chicken character jumping over ovens, gold coins, vibrant warm colors, African trees and animals in background",
        "key_elements": "cartoon white chicken with accessories, fire ovens/pits, coins, African landscape, zebras",
        "colors": "warm orange, yellow, brown, gold, vibrant green",
        "logo": "CHICKEN ROAD game logo in golden letters",
    },
    "lucky_jet": {
        "style": "dark background with Lucky Joe character in jetpack flying up, multiplier display, dynamic action scene",
        "key_elements": "Lucky Joe character with jetpack, multiplier numbers, currency symbols",
        "colors": "dark blue, gold, orange, white",
        "logo": "Lucky Jet logo",
    },
    "spaceman": {
        "style": "outer space background with cartoon astronaut floating, stars and planets, multiplier display, colorful space theme",
        "key_elements": "cartoon spaceman astronaut, space background, multiplier counter, stars",
        "colors": "deep blue, purple, gold, white, cyan",
        "logo": "SPACEMAN game logo",
    },
    "ice_fishing": {
        "style": "icy arctic scene with bright blue sky OR aurora purple-green background, large golden glowing fish hanging from helicopter hook on chain, ice chunks breaking, gold coins exploding",
        "key_elements": "large golden fish on hook, helicopter at top, ice chunks, gold coins pile at bottom",
        "colors": "bright blue, gold, white ice, purple aurora",
        "logo": "ICE FISHING LIVE logo with fish icon at top center",
    },
    "sweet_bonanza": {
        "style": "candy land bright colorful background, giant 3D candy symbols floating, lollipops, multiplier bombs, sugar rush atmosphere, vivid pink and purple",
        "key_elements": "giant candy symbols, lollipops, tumble reels effect, multiplier bombs, scatter symbols",
        "colors": "bright pink, purple, yellow, green, vibrant candy colors",
        "logo": "SWEET BONANZA game logo in candy style letters",
    },
    "big_bass": {
        "style": "fishing lake or ocean scene with large bass fish jumping, fisherman character, gold coins, trophy fish, sunset or bright sky",
        "key_elements": "large realistic bass fish, fishing rod and hook, coins exploding, trophy, lake scenery",
        "colors": "blue water, green nature, gold, brown, sunset orange",
        "logo": "BIG BASS BONANZA game logo",
    },
    "fruit_party": {
        "style": "colorful fruit party background, giant 3D fruit symbols floating, grapes, watermelons, party atmosphere, confetti",
        "key_elements": "giant fruit symbols, confetti, multiplier symbols, party decorations",
        "colors": "bright red, green, purple, yellow, vibrant party colors",
        "logo": "FRUIT PARTY game logo with fruits",
    },
    "gates_olympus": {
        "style": "Greek mythology scene with Zeus god on clouds, lightning bolts, ancient temple ruins, divine golden light, epic mythological atmosphere",
        "key_elements": "Zeus character with lightning, ancient Greek temple, gold coins, lightning bolts, clouds",
        "colors": "gold, blue sky, white clouds, purple lightning, divine light",
        "logo": "GATES OF OLYMPUS game logo in epic golden letters",
    },
    "naija_wheel": {
        "style": "colorful African-themed spinning wheel, Nigerian/Ghanaian patterns, bright colors, festive atmosphere, money symbols",
        "key_elements": "large spinning wheel with prize sectors, African patterns, money bags, celebrations",
        "colors": "green, gold, red, African pattern colors",
        "logo": "NAIJA WHEEL logo",
    },
    "betsafe_virtual": {
        "style": "football/soccer stadium background, virtual sports betting screen, action shot, dramatic stadium lights",
        "key_elements": "football stadium, virtual game screen, betting odds display, sports action",
        "colors": "green pitch, stadium lights, blue, white",
        "logo": "BETSAFE VIRTUAL logo",
    },
}

# ============================================================
# VARIANTS
# ============================================================
VARIANTS = [
    {"id": 1, "angle": "BIG WIN", "person": True, "phone": False, "urgency": False,
     "headline": lambda g: f'WIN {g["big_win"]}', "sub": lambda g: f'Start from {g["min_deposit"]} only'},
    {"id": 2, "angle": "FREE SPINS", "person": False, "phone": False, "urgency": True,
     "headline": lambda g: "150 FREE SPINS", "sub": lambda g: f'For New Players • {g["min_deposit"]} only'},
    {"id": 3, "angle": "SOCIAL PROOF", "person": True, "phone": True, "urgency": False,
     "headline": lambda g: f'I Won {g["medium_win"]}!', "sub": lambda g: f'Real withdrawal via {g["payments"].split(",")[0]}'},
    {"id": 4, "angle": "URGENCY TODAY", "person": True, "phone": False, "urgency": True,
     "headline": lambda g: g["urgency"], "sub": lambda g: f'WIN {g["big_win"]} • {g["min_deposit"]}'},
    {"id": 5, "angle": "LOCAL PAYMENT", "person": True, "phone": True, "urgency": False,
     "headline": lambda g: f'Instant {g["payments"].split(",")[0]} Payout', "sub": lambda g: f'WIN {g["big_win"]} now'},
    {"id": 6, "angle": "LOW BARRIER", "person": False, "phone": False, "urgency": True,
     "headline": lambda g: f'{g["min_deposit"]} → {g["big_win"]}', "sub": lambda g: "Start Small Win Big"},
    {"id": 7, "angle": "MULTIPLIER", "person": False, "phone": False, "urgency": False,
     "headline": lambda g: "5000x MULTIPLIER", "sub": lambda g: f'WIN {g["big_win"]} • {g["min_deposit"]}'},
    {"id": 8, "angle": "NIGHT WIN", "person": True, "phone": True, "urgency": False,
     "headline": lambda g: f'Won {g["big_win"]} in 5 min!', "sub": lambda g: f'Via {g["payments"].split(",")[0]}'},
    {"id": 9, "angle": "200% BONUS", "person": False, "phone": False, "urgency": True,
     "headline": lambda g: "200% BONUS", "sub": lambda g: f'On First Deposit + 150 Free Spins'},
    {"id": 10, "angle": "EXCLUSIVE GEO", "person": True, "phone": False, "urgency": True,
     "headline": lambda g: g["exclusive"], "sub": lambda g: f'150 FREE SPINS + WIN {g["big_win"]}'},
]

# ============================================================
# PROMPT BUILDER
# ============================================================
def build_prompt(game_id: str, geo: str, offer: str, variant: dict) -> str:
    g = GEO[geo]
    gv = GAME_VISUALS.get(game_id, GAME_VISUALS["ice_fishing"])

    headline = variant["headline"](g)
    sub = variant["sub"](g)
    cta = g["cta"]
    angle = variant["angle"]

    person_desc = ""
    if variant["person"]:
        if variant["phone"] and angle in ["SOCIAL PROOF", "NIGHT WIN", "LOCAL PAYMENT"]:
            if angle == "NIGHT WIN":
                person_desc = f"{g['person']} sitting in car at night holding phone showing '{g['medium_win']} to {g['payments'].split(',')[0]}' withdrawal notification, excited expression, city lights background"
            else:
                person_desc = f"{g['person']} holding phone showing successful withdrawal of {g['medium_win']} to {g['payments'].split(',')[0]}, big smile"
        else:
            person_desc = f"{g['person']} celebrating with fan of {g['currency']} banknotes in hands, big joyful smile"

    bg_modifier = "at night, dark dramatic scene, " if angle == "NIGHT WIN" else ""

    prompt = f"""Professional iGaming advertisement banner, square 1:1 format, ultra high quality, photorealistic, vibrant colors, sharp details.

GAME THEME: {gv['style']}. {bg_modifier}
KEY GAME ELEMENTS: {gv['key_elements']}.
COLOR PALETTE: {gv['colors']}.

{f'PERSON: {person_desc}.' if person_desc else ''}

TEXT ON IMAGE (clear, bold, readable):
- Top-left: "{offer}" logo badge in red background
- Game logo: {gv['logo']}
- Large main text in gold/yellow: "{headline}"
- White subtitle text: "{sub}"
- Orange rounded CTA button: "{cta}"
- Bottom payment row: "{g['payments_short']}"
- Bottom badge: "{g['download']}"
{f'- Country flag: {g["flag"]}' if angle == "EXCLUSIVE GEO" else ''}

Style: professional gambling advertisement like {game_id} original game marketing material. High production value, realistic render, commercial quality."""

    return prompt

# ============================================================
# FAL IMAGE GENERATION
# ============================================================
def generate_image_fal(prompt: str, input_image_bytes: bytes = None) -> bytes:
    os.environ["FAL_KEY"] = FAL_KEY

    import fal_client

    if input_image_bytes:
        # Якщо є шаблон — завантажуємо як reference image
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(input_image_bytes)
            tmp_path = f.name

        image_url = fal_client.upload_file(tmp_path)
        os.unlink(tmp_path)

        result = fal_client.run(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "strength": 0.75,
                "image_size": "square_hd",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "output_format": "jpeg",
            }
        )
    else:
        result = fal_client.run(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "image_size": "square_hd",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "output_format": "jpeg",
            }
        )

    image_url = result["images"][0]["url"]
    response = requests.get(image_url, timeout=60)
    return response.content

# ============================================================
# GENERATE BY GAME
# ============================================================
async def generate_by_game(update, context, game: str, geo: str, offer: str, count: int, chat_id: int, input_photo: bytes = None):
    loop = asyncio.get_event_loop()
    variants_to_use = VARIANTS[:count]

    for i, variant in enumerate(variants_to_use):
        try:
            await context.bot.send_message(chat_id, f"🖼 {i+1}/{count} — {variant['angle']}...")
            prompt = build_prompt(game, geo, offer, variant)
            image_bytes = await loop.run_in_executor(None, generate_image_fal, prompt, input_photo)

            caption = f"#{i+1} {variant['angle']} | {game} | {geo} | {offer}"
            await context.bot.send_photo(chat_id=chat_id, photo=io.BytesIO(image_bytes), caption=caption)
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error variant {i+1}: {e}")
            await context.bot.send_message(chat_id, f"⚠️ Варіант {i+1} пропущено: {str(e)[:100]}")
            await asyncio.sleep(2)

# ============================================================
# ANALYZE CREATIVE
# ============================================================
def analyze_creative(photo_bytes: bytes) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    image_data = base64.standard_b64encode(photo_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": """Analyze this iGaming ad. Return ONLY JSON:
{"game_name":"exact name","game_id":"aviator|jetx|chicken_road|lucky_jet|spaceman|ice_fishing|sweet_bonanza|big_bass|fruit_party|gates_olympus|naija_wheel|betsafe_virtual|unknown","style":"describe in 20 words","colors":["c1","c2","c3"],"key_elements":["e1","e2","e3"]}"""}
            ]
        }]
    )
    import json
    text = response.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# ============================================================
# ANALYZE AND GENERATE
# ============================================================
async def analyze_and_generate(update, context, photo_bytes: bytes, geo: str, offer: str, count: int, chat_id: int):
    loop = asyncio.get_event_loop()

    await context.bot.send_message(chat_id, "🔍 Claude аналізує крео...")

    try:
        analysis = await loop.run_in_executor(None, analyze_creative, photo_bytes)
        game_id = analysis.get("game_id", "ice_fishing")
        game_name = analysis.get("game_name", "casino game")
        await context.bot.send_message(chat_id, f"✅ Визначено: {game_name}\nГенерую {count} варіантів...")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        game_id = "ice_fishing"
        await context.bot.send_message(chat_id, "⚡ Генерую варіації...")

    await generate_by_game(update, context, game_id, geo, offer, count, chat_id, photo_bytes)
