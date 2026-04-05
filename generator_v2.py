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
        "style": "dark cinematic sky with iconic red Aviator biplane soaring upward through dramatic storm clouds, glowing orange-red multiplier graph curve climbing steeply, motion blur speed lines, atmospheric depth",
        "key_elements": "Aviator red biplane with engine glow, multiplier graph peaking at 100x+, coin burst particle effects",
        "colors": "deep crimson red, burnt orange, jet black, metallic gold accents",
        "logo": "AVIATOR",
    },
    "jetx": {
        "style": "cinematic deep-space background with JetX rocket blasting upward in a pillar of blue plasma fire, neon multiplier numbers floating in zero gravity, holographic UI panels, futuristic HUD overlay",
        "key_elements": "JetX rocket with afterburner exhaust, star-field depth, glowing neon blue fire trail, coin explosions",
        "colors": "deep space navy, electric blue, violet purple, metallic gold, bright white",
        "logo": "JetX",
    },
    "chicken_road": {
        "style": "vibrant cartoon African savanna sunset, brave cartoon chicken in sunglasses leaping over blazing fire ovens, oversized gold coins arcing through the air, cel-shaded 3D art style",
        "key_elements": "cartoon white chicken hero mid-jump, rows of fire ovens, large spinning gold coins, African acacia trees, cartoon zebras",
        "colors": "warm sunset orange, vivid yellow, rich brown, deep gold, lush green",
        "logo": "CHICKEN ROAD",
    },
    "lucky_jet": {
        "style": "high-energy action scene: Lucky Joe cartoon character in red jetpack rocketing diagonally upward against dark gradient sky, speed lines, currency bill explosion",
        "key_elements": "Lucky Joe character with jetpack flames, flying banknotes and currency symbols, dynamic motion blur, spark trail",
        "colors": "deep navy blue, fiery orange, bright gold, clean white",
        "logo": "Lucky Jet",
    },
    "spaceman": {
        "style": "vibrant outer-space panorama, cute cartoon astronaut floating freely among giant colorful planets, galaxy nebula backdrop in deep purples and blues",
        "key_elements": "cartoon spaceman astronaut in white suit, ringed planets, twinkling star-field, scattered gold coins in zero-g",
        "colors": "deep cosmic blue, rich purple nebula, bright gold, white starlight, cyan glow",
        "logo": "SPACEMAN",
    },
    "ice_fishing": {
        "style": "dramatic arctic panorama under vivid aurora borealis (purple-green-teal sky), massive luminous golden fish suspended on a helicopter hook and chain above a cracking ice surface, explosive gold coin shower at base",
        "key_elements": "enormous glowing golden fish dangling from hook, helicopter silhouette at top, dramatic ice chunks splitting, cascading pile of gold coins, aurora reflections on ice",
        "colors": "aurora purple-teal gradient sky, radiant gold fish, crisp white ice, deep midnight blue water",
        "logo": "ICE FISHING LIVE",
    },
    "sweet_bonanza": {
        "style": "explosive candy-land wonderland, oversized photorealistic 3D candy symbols tumbling through a pastel dreamscape, rainbow lollipops framing the scene, multiplier bomb detonations mid-air",
        "key_elements": "giant 3D candy symbols (watermelon, plum, grape, lollipop), multiplier bombs with glowing fuses, confetti burst, candy-stripe background",
        "colors": "hot pink, vivid purple, sunshine yellow, lime green, sky blue",
        "logo": "SWEET BONANZA",
    },
    "big_bass": {
        "style": "golden-hour fishing lake scene, enormous photorealistic largemouth bass leaping from shimmering water, droplets catching sunset light, proud fisherman silhouette on dock",
        "key_elements": "large realistic bass fish airborne with water spray, fishing line taut, coins and banknotes erupting from water, trophy cup",
        "colors": "amber sunset gold, deep lake blue-green, lush forest green, rich brown, gleaming orange",
        "logo": "BIG BASS BONANZA",
    },
    "fruit_party": {
        "style": "festive fruit fiesta explosion, giant hyper-realistic 3D fruit symbols raining down in a party atmosphere, streamers and confetti swirling, bright disco lighting",
        "key_elements": "oversized 3D fruits (watermelon, grapes, strawberry, lemon), bursting confetti cannons, party streamers, bright spotlights",
        "colors": "vivid red, tropical green, rich purple, bright yellow, party-light magenta",
        "logo": "FRUIT PARTY",
    },
    "gates_olympus": {
        "style": "epic Greek mythology panorama, mighty Zeus standing on Mount Olympus above swirling storm clouds, divine golden light radiating from above, ancient white marble temple columns, crackling purple lightning bolts",
        "key_elements": "Zeus god figure with raised lightning bolt, crumbling Parthenon columns, cascading gold coins, dramatic storm clouds, purple electrical arcs",
        "colors": "divine gold, celestial blue sky, pure white marble, electric purple lightning, radiant godly light",
        "logo": "GATES OF OLYMPUS",
    },
    "naija_wheel": {
        "style": "vibrant West African celebration scene, giant glittering prize wheel spinning with Ankara-pattern prize sectors, confetti and naira notes filling the air, festive crowd energy",
        "key_elements": "large spinning prize wheel with colored sectors, money bags bursting open, African Ankara fabric patterns, celebratory crowd silhouettes",
        "colors": "emerald green, bright gold, deep red, royal blue, vibrant Ankara pattern colors",
        "logo": "NAIJA WHEEL",
    },
    "betsafe_virtual": {
        "style": "cinematic football stadium at peak match moment, floodlights blazing over a perfectly manicured pitch, dramatic action mid-kick, stadium crowd energy",
        "key_elements": "packed stadium with roaring crowd, ball mid-trajectory, player silhouette, broadcast camera angle",
        "colors": "vivid pitch green, stadium floodlight white, brand blue, crisp white",
        "logo": "BETSAFE VIRTUAL",
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
# FONT LOADING (Pillow)
# ============================================================
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_FONT_CACHE: dict = {}

_FONT_URLS = {
    "bold":    "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf",
    "black":   "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-ExtraBold.ttf",
    "regular": "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-SemiBold.ttf",
}


def _ensure_fonts():
    os.makedirs(_FONT_DIR, exist_ok=True)
    for name, url in _FONT_URLS.items():
        path = os.path.join(_FONT_DIR, f"Montserrat-{name}.ttf")
        if not os.path.exists(path):
            logger.info(f"Downloading font: {name}")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)


def _font(weight: str, size: int):
    key = (weight, size)
    if key not in _FONT_CACHE:
        from PIL import ImageFont
        _ensure_fonts()
        path = os.path.join(_FONT_DIR, f"Montserrat-{weight}.ttf")
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


# ============================================================
# TEXT OVERLAY (Pillow)
# ============================================================
def add_text_overlay(
    image_bytes: bytes,
    offer: str,
    headline: str,
    sub: str,
    cta: str,
    payments_short: str,
    download: str,
    game_logo: str,
) -> bytes:
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    W, H = img.size  # square_hd = 1024x1024

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    pad = int(W * 0.04)

    # Font sizes relative to image height
    f_hero = _font("black", int(H * 0.088))    # headline
    f_sub  = _font("bold",  int(H * 0.046))    # subtitle
    f_cta  = _font("black", int(H * 0.042))    # CTA button
    f_logo = _font("bold",  int(H * 0.038))    # game logo
    f_sm   = _font("regular", int(H * 0.028))  # payments / badge
    f_bdg  = _font("bold",  int(H * 0.034))    # offer badge

    def text_w(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]

    def text_h(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]

    def draw_shadow(pos, text, font, fill, shadow=(0, 0, 0, 210), offset=3):
        x, y = pos
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow)
        draw.text(pos, text, font=font, fill=fill)

    def rounded_rect(xy, r, fill):
        x1, y1, x2, y2 = xy
        draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
        draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
        draw.ellipse([x1, y1, x1 + 2 * r, y1 + 2 * r], fill=fill)
        draw.ellipse([x2 - 2 * r, y1, x2, y1 + 2 * r], fill=fill)
        draw.ellipse([x1, y2 - 2 * r, x1 + 2 * r, y2], fill=fill)
        draw.ellipse([x2 - 2 * r, y2 - 2 * r, x2, y2], fill=fill)

    # ---- Dark gradient strip at bottom (readability) ----
    strip_h = int(H * 0.50)
    strip_y = H - strip_h
    for i in range(strip_h):
        alpha = int(200 * (i / strip_h) ** 0.7)
        draw.line([(0, strip_y + i), (W, strip_y + i)], fill=(0, 0, 0, alpha))

    # ---- Semi-dark strip at top for badge/logo ----
    top_h = int(H * 0.12)
    for i in range(top_h):
        alpha = int(140 * (1 - i / top_h))
        draw.line([(0, i), (W, i)], fill=(0, 0, 0, alpha))

    # ---- OFFER BADGE (top-left) ----
    btext = offer.upper()
    bw = text_w(btext, f_bdg) + pad * 2
    bh = text_h(btext, f_bdg) + int(pad * 0.8)
    bx, by = pad, pad
    rounded_rect((bx, by, bx + bw, by + bh), r=10, fill=(210, 20, 20, 235))
    bb = draw.textbbox((0, 0), btext, font=f_bdg)
    draw.text((bx + pad, by + (bh - (bb[3] - bb[1])) // 2), btext, font=f_bdg, fill=(255, 255, 255, 255))

    # ---- GAME LOGO (top-right or top-center) ----
    logo_text = game_logo
    lw = text_w(logo_text, f_logo)
    lx = W - lw - pad
    ly = pad + 4
    draw_shadow((lx, ly), logo_text, f_logo, fill=(255, 215, 0, 240), offset=2)

    # ---- HEADLINE ----
    hl_y = int(H * 0.54)
    hw = text_w(headline, f_hero)
    # wrap if too wide
    if hw > W - pad * 2:
        words = headline.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        lh = text_h(line1, f_hero)
        hx1 = max(pad, (W - text_w(line1, f_hero)) // 2)
        hx2 = max(pad, (W - text_w(line2, f_hero)) // 2)
        draw_shadow((hx1, hl_y), line1, f_hero, fill=(255, 215, 0, 255), offset=4)
        draw_shadow((hx2, hl_y + lh + 4), line2, f_hero, fill=(255, 215, 0, 255), offset=4)
        next_y = hl_y + lh * 2 + 12
    else:
        hx = max(pad, (W - hw) // 2)
        draw_shadow((hx, hl_y), headline, f_hero, fill=(255, 215, 0, 255), offset=4)
        next_y = hl_y + text_h(headline, f_hero) + 10

    # ---- SUBTITLE ----
    sub_y = next_y + int(H * 0.012)
    sw = text_w(sub, f_sub)
    sx = max(pad, (W - sw) // 2)
    draw_shadow((sx, sub_y), sub, f_sub, fill=(255, 255, 255, 240), offset=2)

    # ---- CTA BUTTON ----
    cta_y = sub_y + text_h(sub, f_sub) + int(H * 0.035)
    cw = text_w(cta, f_cta)
    ch = text_h(cta, f_cta)
    btn_w = cw + int(W * 0.16)
    btn_h = ch + int(H * 0.038)
    btn_x = (W - btn_w) // 2
    # glow ring
    rounded_rect((btn_x - 4, cta_y - 4, btn_x + btn_w + 4, cta_y + btn_h + 4), r=btn_h // 2 + 4, fill=(255, 180, 0, 70))
    # button body
    rounded_rect((btn_x, cta_y, btn_x + btn_w, cta_y + btn_h), r=btn_h // 2, fill=(255, 130, 0, 245))
    draw.text(
        (btn_x + (btn_w - cw) // 2, cta_y + (btn_h - ch) // 2),
        cta, font=f_cta, fill=(255, 255, 255, 255)
    )

    # ---- PAYMENT ICONS ROW ----
    pay_y = cta_y + btn_h + int(H * 0.022)
    pw = text_w(payments_short, f_sm)
    px = max(pad, (W - pw) // 2)
    draw_shadow((px, pay_y), payments_short, f_sm, fill=(210, 210, 210, 230), offset=1)

    # ---- APP BADGE ----
    dl_y = pay_y + text_h(payments_short, f_sm) + int(H * 0.015)
    dw = text_w(download, f_sm)
    dx = max(pad, (W - dw) // 2)
    draw_shadow((dx, dl_y), download, f_sm, fill=(190, 190, 190, 210), offset=1)

    # Composite and return
    out_img = Image.alpha_composite(img, layer).convert("RGB")
    buf = io.BytesIO()
    out_img.save(buf, format="JPEG", quality=93)
    return buf.getvalue()


# ============================================================
# PROMPT BUILDER  (visual scene only — NO text instructions)
# ============================================================
def build_prompt(game_id: str, geo: str, variant: dict) -> str:
    g = GEO[geo]
    gv = GAME_VISUALS.get(game_id, GAME_VISUALS["ice_fishing"])
    angle = variant["angle"]

    person_desc = ""
    if variant["person"]:
        if variant["phone"] and angle in ["SOCIAL PROOF", "NIGHT WIN", "LOCAL PAYMENT"]:
            if angle == "NIGHT WIN":
                person_desc = (
                    f"{g['person']} sitting in car at night, face lit by phone screen, "
                    f"wide excited expression, city bokeh lights in background"
                )
            else:
                person_desc = (
                    f"{g['person']} holding smartphone with big beaming smile, natural light"
                )
        else:
            person_desc = (
                f"{g['person']} holding fan of crisp {g['currency']} banknotes spread wide, "
                f"ecstatic joyful expression, celebratory pose"
            )

    bg_modifier = "night-time scene, dark moody cinematic lighting with neon accents, " if angle == "NIGHT WIN" else ""

    prompt = (
        f"Professional iGaming advertisement background visual, square 1:1 format, "
        f"ultra-high-definition render, commercial quality. No text, no words, no letters, no UI overlays.\n\n"
        f"GAME VISUAL SCENE: {bg_modifier}{gv['style']}.\n"
        f"KEY ELEMENTS: {gv['key_elements']}.\n"
        f"COLOR PALETTE: {gv['colors']}.\n\n"
        f"{f'PERSON IN FOREGROUND: {person_desc}.' if person_desc else ''}\n\n"
        f"COMPOSITION: hero game visual dominates center and upper half. "
        f"Lower 45% of image fades naturally to dark (vignette) to allow text overlay. "
        f"Top area slightly darker for badge placement.\n\n"
        f"Style: Spribe/Pragmatic Play official game marketing art. "
        f"Photorealistic render, vibrant colors, high production value, zero artifacts, no watermarks, no text."
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
        "guidance_scale": 4.5,
        "num_images": 1,
        "output_format": "png",
        "safety_tolerance": "6",
    }

    if input_image_bytes:
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
    g = GEO[geo]
    gv = GAME_VISUALS.get(game, GAME_VISUALS["ice_fishing"])
    variants_to_use = VARIANTS[:count]

    for i, variant in enumerate(variants_to_use):
        try:
            await context.bot.send_message(chat_id, f"🖼 {i+1}/{count} — {variant['angle']}...")

            # 1. Build visual-only prompt
            prompt = build_prompt(game, geo, variant)

            # 2. Generate background with FAL
            image_bytes = await loop.run_in_executor(None, generate_image_fal, prompt, input_photo)

            # 3. Overlay text programmatically with Pillow
            headline = variant["headline"](g)
            sub = variant["sub"](g)
            image_bytes = await loop.run_in_executor(
                None,
                add_text_overlay,
                image_bytes,
                offer,
                headline,
                sub,
                g["cta"],
                g["payments_short"],
                g["download"],
                gv["logo"],
            )

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
