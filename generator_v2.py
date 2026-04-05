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
        "style": "dark cinematic background with iconic red Aviator biplane soaring upward through dramatic storm clouds, glowing orange-red multiplier graph curve climbing steeply, motion blur speed lines, atmospheric depth, premium crash-game aesthetic",
        "key_elements": "Aviator red biplane with engine glow, bold multiplier graph peaking at 100x+, cash-out button lit up on phone screen, coin burst particle effects",
        "colors": "deep crimson red, burnt orange, jet black, metallic gold accents",
        "logo": "AVIATOR game logo — bold red italic lettering with white outline at top center",
    },
    "jetx": {
        "style": "cinematic deep-space background with JetX rocket blasting upward in a pillar of blue plasma fire, neon multiplier numbers floating in zero gravity, holographic UI panels, futuristic HUD overlay",
        "key_elements": "JetX rocket with afterburner exhaust, scrolling multiplier counter, star-field depth, glowing neon blue fire trail, coin explosions",
        "colors": "deep space navy, electric blue, violet purple, metallic gold, bright white",
        "logo": "JetX logo — sleek blue and white bold font with rocket icon",
    },
    "chicken_road": {
        "style": "vibrant cartoon African savanna sunset scene, brave cartoon chicken in sunglasses leaping over blazing fire ovens, oversized gold coins arcing through the air, exaggerated cartoon physics, cel-shaded 3D art style",
        "key_elements": "cartoon white chicken hero with accessories mid-jump, rows of fire ovens with visible flames, large spinning gold coins, silhouette African acacia trees, cartoon zebras in background",
        "colors": "warm sunset orange, vivid yellow, rich brown earth, deep gold, lush vibrant green",
        "logo": "CHICKEN ROAD — chunky golden 3D letters with fire glow effect",
    },
    "lucky_jet": {
        "style": "high-energy action scene: Lucky Joe cartoon character in red jetpack rocketing diagonally upward against a dark gradient sky, speed lines, glowing multiplier counter, currency bill explosion",
        "key_elements": "Lucky Joe character with jetpack flames, bold multiplier display, flying banknotes and currency symbols, dynamic motion blur, spark trail",
        "colors": "deep navy blue, fiery orange, bright gold, clean white",
        "logo": "Lucky Jet logo — bold italic font with jet flame accent",
    },
    "spaceman": {
        "style": "vibrant outer-space panorama, cute cartoon astronaut floating freely among giant colorful planets, galaxy nebula backdrop in deep purples and blues, multiplier counter glowing in the foreground",
        "key_elements": "cartoon spaceman astronaut in white suit with expression, ringed planets, twinkling star-field, glowing multiplier orb, scattered gold coins in zero-g",
        "colors": "deep cosmic blue, rich purple nebula, bright gold, white starlight, cyan glow",
        "logo": "SPACEMAN — rounded bold font with star and orbit icon",
    },
    "ice_fishing": {
        "style": "dramatic arctic panorama under vivid aurora borealis (purple-green-teal sky), massive luminous golden fish suspended on a helicopter hook and chain above a cracking ice surface, explosive gold coin shower at base",
        "key_elements": "enormous glowing golden fish dangling from hook, helicopter silhouette at top, dramatic ice chunks splitting, cascading pile of gold coins, aurora reflections on ice",
        "colors": "aurora purple-teal gradient sky, radiant gold fish, crisp white ice, deep midnight blue water",
        "logo": "ICE FISHING LIVE — icy blue bold font with fish icon centered at top",
    },
    "sweet_bonanza": {
        "style": "explosive candy-land wonderland, oversized photorealistic 3D candy symbols tumbling through a pastel dreamscape, rainbow lollipops framing the scene, multiplier bomb detonations mid-air, sugar-rush visual energy",
        "key_elements": "giant 3D candy symbols (watermelon, plum, grape, lollipop), multiplier bombs with glowing fuses, scatter heart symbols, confetti burst, candy-stripe background",
        "colors": "hot pink, vivid purple, sunshine yellow, lime green, sky blue — saturated candy palette",
        "logo": "SWEET BONANZA — candy-style rounded letters with rainbow gradient",
    },
    "big_bass": {
        "style": "golden-hour fishing lake scene, enormous photorealistic largemouth bass leaping from shimmering water, droplets catching sunset light, proud fisherman silhouette on dock, gold coin explosion from water",
        "key_elements": "large realistic bass fish airborne with water spray, fishing line taut, coins and banknotes erupting from water, trophy cup, warm lake and tree reflection",
        "colors": "amber sunset gold, deep lake blue-green, lush forest green, rich brown, gleaming orange",
        "logo": "BIG BASS BONANZA — outdoor adventure bold font with fish icon",
    },
    "fruit_party": {
        "style": "festive fruit fiesta explosion, giant hyper-realistic 3D fruit symbols raining down in a party atmosphere, streamers and confetti swirling, bright disco lighting, celebratory energy",
        "key_elements": "oversized 3D fruits (watermelon, grapes, strawberry, lemon), bursting confetti cannons, multiplier badges, party streamers, bright spotlights",
        "colors": "vivid red, tropical green, rich purple, bright yellow, party-light magenta",
        "logo": "FRUIT PARTY — festive bold font with fruit cluster icon",
    },
    "gates_olympus": {
        "style": "epic Greek mythology panorama, mighty Zeus standing on Mount Olympus above swirling storm clouds, divine golden light radiating from above, ancient white marble temple columns, crackling purple lightning bolts",
        "key_elements": "Zeus god figure with raised lightning bolt, crumbling Parthenon columns, cascading gold coins, dramatic storm clouds, divine beam of light, purple electrical arcs",
        "colors": "divine gold, celestial blue sky, pure white marble, electric purple lightning, radiant godly light",
        "logo": "GATES OF OLYMPUS — epic serif golden letters with laurel wreath and lightning emblem",
    },
    "naija_wheel": {
        "style": "vibrant West African celebration scene, giant glittering prize wheel spinning with Ankara-pattern prize sectors, confetti and naira notes filling the air, festive crowd energy, rich cultural color palette",
        "key_elements": "large spinning prize wheel with colored sectors and prize labels, money bags bursting open, African Ankara fabric patterns as design elements, celebratory crowd silhouettes",
        "colors": "emerald green, bright gold, deep red, royal blue, vibrant Ankara pattern colors",
        "logo": "NAIJA WHEEL — bold Afro-styled lettering with wheel icon",
    },
    "betsafe_virtual": {
        "style": "cinematic football stadium at peak match moment, floodlights blazing over a perfectly manicured pitch, virtual sports betting UI overlaid on broadcast-style camera angle, dramatic action mid-kick",
        "key_elements": "packed stadium with roaring crowd, live betting odds panel overlay, ball mid-trajectory, player silhouette, broadcast lower-third graphics",
        "colors": "vivid pitch green, stadium floodlight white, brand blue, crisp white UI",
        "logo": "BETSAFE VIRTUAL — clean sports-brand bold font with trophy icon",
    },
}

# ============================================================
# VARIANTS
# ============================================================
VARIANTS = [
    {"id": 1, "angle": "BIG WIN", "person": True, "phone": False, "urgency": False,
     "headline": lambda g: f'WIN {g["big_win"]}', "sub": lambda g: f'Start from {g["min_deposit"]} only'},
    {"id": 2, "angle": "FREE SPINS", "person": False, "phone": False, "urgency": True,
     "headline": lambda g: "150 FREE SPINS", "sub": lambda g: f'For New Players - {g["min_deposit"]} only'},
    {"id": 3, "angle": "SOCIAL PROOF", "person": True, "phone": True, "urgency": False,
     "headline": lambda g: f'I Won {g["medium_win"]}!', "sub": lambda g: f'Real withdrawal via {g["payments"].split(",")[0]}'},
    {"id": 4, "angle": "URGENCY TODAY", "person": True, "phone": False, "urgency": True,
     "headline": lambda g: g["urgency"], "sub": lambda g: f'WIN {g["big_win"]} - {g["min_deposit"]}'},
    {"id": 5, "angle": "LOCAL PAYMENT", "person": True, "phone": True, "urgency": False,
     "headline": lambda g: f'Instant {g["payments"].split(",")[0]} Payout', "sub": lambda g: f'WIN {g["big_win"]} now'},
    {"id": 6, "angle": "LOW BARRIER", "person": False, "phone": False, "urgency": True,
     "headline": lambda g: f'{g["min_deposit"]} to {g["big_win"]}', "sub": lambda g: "Start Small Win Big"},
    {"id": 7, "angle": "MULTIPLIER", "person": False, "phone": False, "urgency": False,
     "headline": lambda g: "5000x MULTIPLIER", "sub": lambda g: f'WIN {g["big_win"]} - {g["min_deposit"]}'},
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
                person_desc = (
                    f"{g['person']} sitting in car at night, face lit by phone screen, "
                    f"showing withdrawal notification of {g['medium_win']} to {g['payments'].split(',')[0]}, "
                    f"wide excited expression, city bokeh lights in background"
                )
            else:
                person_desc = (
                    f"{g['person']} holding smartphone displaying successful {g['medium_win']} withdrawal "
                    f"confirmation to {g['payments'].split(',')[0]}, huge beaming smile, natural light"
                )
        else:
            person_desc = (
                f"{g['person']} holding fan of crisp {g['currency']} banknotes spread wide in both hands, "
                f"ecstatic joyful expression, celebratory pose"
            )

    bg_modifier = "night-time scene, dark moody cinematic lighting with neon accents, " if angle == "NIGHT WIN" else ""

    flag_line = f"\n  - COUNTRY FLAG: {g['flag']} — placed in corner, crisp and recognizable" if angle == "EXCLUSIVE GEO" else ""

    text_block = (
        f"TYPOGRAPHY AND TEXT OVERLAY (ultra-sharp, perfectly legible, zero blur, zero distortion):\n"
        f"  - TOP-LEFT BADGE: \"{offer}\" — bold white text on solid red rounded-rectangle badge\n"
        f"  - GAME LOGO: {gv['logo']} — crisp vector-style lettering, centered upper area\n"
        f"  - HEADLINE (largest text, center): \"{headline}\" — extra-bold impact font, gold/yellow color, thick dark drop-shadow and white stroke for maximum contrast\n"
        f"  - SUBTITLE (below headline): \"{sub}\" — clean semi-bold white font, soft dark shadow\n"
        f"  - CTA BUTTON (bottom center): \"{cta}\" — bright orange rounded button, bold white uppercase text inside, subtle glow\n"
        f"  - PAYMENT ICONS ROW (bottom): \"{g['payments_short']}\" — small clean white sans-serif text\n"
        f"  - APP BADGE (bottom): \"{g['download']}\" — small white text, star rating visible"
        f"{flag_line}"
    )

    prompt = (
        f"Professional iGaming advertisement creative, square 1:1 format, ultra-high-definition render, "
        f"commercial print quality, sharp crisp details throughout. "
        f"Style: premium mobile-game marketing banner, Spribe/Pragmatic Play production standard.\n\n"
        f"{text_block}\n\n"
        f"VISUAL BACKGROUND AND GAME THEME: {bg_modifier}{gv['style']}.\n"
        f"KEY GAME ELEMENTS IN SCENE: {gv['key_elements']}.\n"
        f"COLOR PALETTE: {gv['colors']}.\n\n"
        f"{f'FOREGROUND PERSON: {person_desc}.' if person_desc else ''}\n\n"
        f"COMPOSITION LAYOUT: three-zone vertical — (1) branding/logo zone at top, "
        f"(2) hero visual and person in center, (3) CTA and payment bar anchored at bottom. "
        f"Each zone clearly separated with visual contrast.\n\n"
        f"QUALITY REQUIREMENTS: photorealistic render, high production value, "
        f"every text element razor-sharp and fully readable at a glance, "
        f"high contrast between text and background, professional color grading, "
        f"no watermarks, no artifacts, commercial-ready output."
    )

    return prompt


# ============================================================
# FAL IMAGE GENERATION
# ============================================================
def generate_image_fal(prompt: str, input_image_bytes: bytes = None) -> bytes:
    os.environ["FAL_KEY"] = FAL_KEY

    import fal_client

    base_args = {
        "prompt": prompt,
        "image_size": "square_hd",
        "num_inference_steps": 35,
        "guidance_scale": 5.0,
        "num_images": 1,
        "output_format": "jpeg",
        "safety_tolerance": "6",
    }

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
            arguments={**base_args, "image_url": image_url, "strength": 0.80},
        )
    else:
        result = fal_client.run(
            "fal-ai/flux-pro/v1.1",
            arguments=base_args,
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
