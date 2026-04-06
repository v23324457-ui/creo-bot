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

# jsDelivr CDN — надійне дзеркало google/fonts, завжди TTF
_FONT_URLS = {
    "bold":    "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-Bold.ttf",
    "black":   "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-ExtraBold.ttf",
    "regular": "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/static/Montserrat-SemiBold.ttf",
}

# Системні шрифти як fallback (Ubuntu / Debian / Railway)
_SYSTEM_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "C:/Windows/Fonts/arialbd.ttf",   # Windows fallback
    "C:/Windows/Fonts/impact.ttf",
]


def _ensure_font(name: str) -> str:
    """Повертає шлях до TTF файлу. Завантажує якщо відсутній, або повертає системний fallback."""
    os.makedirs(_FONT_DIR, exist_ok=True)
    path = os.path.join(_FONT_DIR, f"Montserrat-{name}.ttf")

    if os.path.exists(path):
        return path

    # Спроба завантажити з jsDelivr CDN
    url = _FONT_URLS.get(name)
    if url:
        try:
            logger.info(f"Downloading font '{name}' from jsDelivr...")
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            # Перевіряємо що отримали TTF (перші 4 байти: \x00\x01\x00\x00 або 'OTTO' або 'true')
            if len(r.content) > 4 and r.content[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"\x74\x72\x75\x65"):
                with open(path, "wb") as f:
                    f.write(r.content)
                logger.info(f"Font '{name}' saved to {path}")
                return path
            else:
                logger.warning(f"Font '{name}': received non-TTF response from CDN")
        except Exception as e:
            logger.warning(f"Font CDN download failed for '{name}': {e}")

    # Системний fallback
    for sys_path in _SYSTEM_FONT_CANDIDATES:
        if os.path.exists(sys_path):
            logger.info(f"Using system font fallback: {sys_path}")
            return sys_path

    # Останній fallback — PIL default (некрасиво, але не падає)
    logger.warning(f"No font found for '{name}', using PIL default")
    return ""


def _font(weight: str, size: int):
    key = (weight, size)
    if key not in _FONT_CACHE:
        from PIL import ImageFont
        path = _ensure_font(weight)
        if path:
            try:
                _FONT_CACHE[key] = ImageFont.truetype(path, size)
            except Exception as e:
                logger.warning(f"truetype load failed ({path}): {e}")
                _FONT_CACHE[key] = ImageFont.load_default()
        else:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


# ============================================================
# LOGO LOADING
# ============================================================
_LOGO_CACHE: dict = {}

# Offer logos — кілька URL на кожен бренд, пробуємо по черзі
_OFFER_LOGO_URLS: dict[str, list[str]] = {
    "1xbet": [
        "https://1xbet.com/img/logo/logo-white-new.svg",          # SVG — пропускаємо
        "https://partners.1xbet.com/images/logo/logo-light.png",
        "https://static.1xbet.com/img/logo.png",
        "https://1x-bet.mobi/img/top/logo.png",
    ],
    "melbet": [
        "https://melbet.com/documents/logotypes/MelBet_white_on_dark.png",
        "https://partners.melbet.com/images/logo-white.png",
        "https://cdn.melbet.com/img/logo-white.png",
    ],
    "mostbet": [
        "https://mostbet.com/images/logo-white.png",
        "https://partners.mostbet.com/images/logo.png",
    ],
    "betwinner": [
        "https://betwinner.com/img/logo-white.png",
        "https://partners.betwinner.com/img/logo.png",
    ],
    "1xbit": [
        "https://1xbit.com/img/logo.png",
    ],
}

# Game logos — офіційні CDN провайдерів
_GAME_LOGO_URLS: dict[str, list[str]] = {
    "aviator": [
        "https://spribe.co/wp-content/uploads/2021/05/aviator-logo.png",
        "https://cdn.spribe.co/assets/aviator/logo.png",
    ],
    "jetx": [
        "https://smartsoft-games.com/wp-content/uploads/JetX-logo.png",
        "https://cdn.smartsoft-games.com/jetx/logo.png",
    ],
    "chicken_road": [
        "https://spribe.co/wp-content/uploads/2023/10/chicken-road-logo.png",
        "https://cdn.spribe.co/assets/chicken-road/logo.png",
    ],
    "lucky_jet": [
        "https://cdn.gamingcorps.com/assets/lucky-jet/logo.png",
        "https://gamingcorps.com/wp-content/uploads/lucky-jet-logo.png",
    ],
    "spaceman": [
        "https://www.pragmaticplay.com/wp-content/uploads/2022/08/spaceman_logo.png",
        "https://cdn.pragmaticplay.com/game-assets/spaceman/logo.png",
    ],
    "ice_fishing": [
        "https://bgaming.com/wp-content/uploads/2023/ice-fishing-live-logo.png",
        "https://cdn.bgaming.com/games/ice-fishing-live/logo.png",
        "https://bgaming-network.com/games/IceFishingLive/logo.png",
    ],
    "sweet_bonanza": [
        "https://www.pragmaticplay.com/wp-content/uploads/2019/06/Sweet_Bonanza_Logo.png",
        "https://cdn.pragmaticplay.com/game-assets/vs20fruitsw/logo.png",
    ],
    "big_bass": [
        "https://www.pragmaticplay.com/wp-content/uploads/2020/11/Big_Bass_Bonanza_Logo.png",
        "https://cdn.pragmaticplay.com/game-assets/vs10bbbonanza/logo.png",
    ],
    "fruit_party": [
        "https://www.pragmaticplay.com/wp-content/uploads/2020/07/Fruit_Party_Logo.png",
        "https://cdn.pragmaticplay.com/game-assets/vs20fruitparty/logo.png",
    ],
    "gates_olympus": [
        "https://www.pragmaticplay.com/wp-content/uploads/2021/04/Gates_of_Olympus_Logo.png",
        "https://cdn.pragmaticplay.com/game-assets/vs20olympgate/logo.png",
    ],
    "naija_wheel": [],
    "betsafe_virtual": [
        "https://www.betsafe.com/assets/images/betsafe-logo.png",
    ],
}


def _is_valid_image_bytes(data: bytes) -> bool:
    """Перевіряє magic bytes щоб відрізнити PNG/JPEG від HTML помилок."""
    if len(data) < 8:
        return False
    png_sig = b"\x89PNG\r\n\x1a\n"
    jpeg_sig = b"\xff\xd8\xff"
    webp_sig = b"RIFF"
    return data[:8] == png_sig or data[:3] == jpeg_sig or data[:4] == webp_sig


def _try_download_logo(urls: list[str], cache_path: str, max_h: int = 100) -> "Image.Image | None":
    """
    Пробує завантажити логотип з кількох URL, кешує в cache_path.
    Повертає PIL Image (RGBA, масштабована) або None.
    """
    from PIL import Image as PILImage

    # Перевіряємо кеш
    if os.path.exists(cache_path):
        try:
            img = PILImage.open(cache_path).convert("RGBA")
            # Масштабуємо до max_h
            w, h = img.size
            if h > max_h:
                img = img.resize((int(w * max_h / h), max_h), PILImage.LANCZOS)
            return img
        except Exception:
            os.remove(cache_path)

    for url in urls:
        if not url or url.endswith(".svg"):
            continue
        try:
            r = requests.get(
                url, timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; CreoBot/1.0)"},
            )
            if r.status_code == 200 and _is_valid_image_bytes(r.content):
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "wb") as f:
                    f.write(r.content)
                img = PILImage.open(io.BytesIO(r.content)).convert("RGBA")
                w, h = img.size
                if h > max_h:
                    img = img.resize((int(w * max_h / h), max_h), PILImage.LANCZOS)
                logger.info(f"Logo downloaded: {url}")
                return img
        except Exception as e:
            logger.debug(f"Logo URL failed ({url}): {e}")

    logger.warning(f"All logo URLs failed for {cache_path}")
    return None


_LOGO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logos")


def get_offer_logo(offer: str, max_h: int = 80) -> "Image.Image | None":
    key = offer.lower().replace(" ", "").replace("-", "")
    # Перевіряємо кеш у пам'яті
    cache_key = f"offer_{key}_{max_h}"
    if cache_key in _LOGO_CACHE:
        return _LOGO_CACHE[cache_key]
    urls = _OFFER_LOGO_URLS.get(key, [])
    cache_path = os.path.join(_LOGO_DIR, f"offer_{key}.png")
    img = _try_download_logo(urls, cache_path, max_h)
    _LOGO_CACHE[cache_key] = img
    return img


def get_game_logo(game_id: str, max_h: int = 90) -> "Image.Image | None":
    cache_key = f"game_{game_id}_{max_h}"
    if cache_key in _LOGO_CACHE:
        return _LOGO_CACHE[cache_key]
    urls = _GAME_LOGO_URLS.get(game_id, [])
    cache_path = os.path.join(_LOGO_DIR, f"game_{game_id}.png")
    img = _try_download_logo(urls, cache_path, max_h)
    _LOGO_CACHE[cache_key] = img
    return img


# ============================================================
# TEXT + LOGO OVERLAY (Pillow)
# ============================================================
def add_text_overlay(
    image_bytes: bytes,
    offer: str,
    headline: str,
    sub: str,
    cta: str,
    payments_short: str,
    download: str,
    game_logo_text: str,
    offer_logo_img=None,   # PIL Image | None
    game_logo_img=None,    # PIL Image | None
) -> bytes:
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    W, H = img.size  # square_hd = 1024x1024

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    pad = int(W * 0.04)

    # Font sizes — headline guaranteed min 80px
    hero_size = max(80, int(H * 0.088))
    f_hero = _font("black",   hero_size)
    f_sub  = _font("bold",    max(44, int(H * 0.046)))
    f_cta  = _font("black",   max(40, int(H * 0.042)))
    f_logo = _font("bold",    max(36, int(H * 0.040)))
    f_sm   = _font("regular", max(26, int(H * 0.028)))
    f_bdg  = _font("bold",    max(34, int(H * 0.038)))   # offer text badge

    def text_w(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]

    def text_h(text, font):
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[3] - bb[1]

    def draw_shadow(pos, text, font, fill, shadow=(0, 0, 0, 220), offset=3):
        x, y = pos
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=shadow)
        draw.text(pos, text, font=font, fill=fill)

    def rounded_rect(xy, r, fill):
        x1, y1, x2, y2 = xy
        r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
        draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
        draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
        draw.ellipse([x1, y1, x1 + 2 * r, y1 + 2 * r], fill=fill)
        draw.ellipse([x2 - 2 * r, y1, x2, y1 + 2 * r], fill=fill)
        draw.ellipse([x1, y2 - 2 * r, x1 + 2 * r, y2], fill=fill)
        draw.ellipse([x2 - 2 * r, y2 - 2 * r, x2, y2], fill=fill)

    def paste_logo(logo_img, cx, cy, align="center"):
        """Вставляє RGBA логотип в layer по центру (cx, cy) або по лівому краю."""
        lw, lh = logo_img.size
        if align == "center":
            x = cx - lw // 2
        else:
            x = cx
        y = cy - lh // 2
        layer.paste(logo_img, (max(0, x), max(0, y)), logo_img)
        return lw, lh

    # ---- Dark gradient strip at bottom (readability) ----
    strip_h = int(H * 0.52)
    strip_y = H - strip_h
    for i in range(strip_h):
        alpha = int(210 * (i / strip_h) ** 0.65)
        draw.line([(0, strip_y + i), (W, strip_y + i)], fill=(0, 0, 0, alpha))

    # ---- Semi-dark strip at top ----
    top_h = int(H * 0.145)
    for i in range(top_h):
        alpha = int(165 * (1 - i / top_h) ** 0.8)
        draw.line([(0, i), (W, i)], fill=(0, 0, 0, alpha))

    top_center_y = int(H * 0.072)   # vertical center of top bar

    # ============================================================
    # TOP-LEFT: OFFER LOGO / BADGE
    # ============================================================
    offer_logo_h = int(H * 0.078)  # target height ~80px for 1024
    badge_right_edge = 0

    if offer_logo_img is not None:
        # Scale logo to target height, maintain aspect
        ow, oh = offer_logo_img.size
        scaled_w = int(ow * offer_logo_h / oh)
        scaled = offer_logo_img.resize((scaled_w, offer_logo_h), Image.LANCZOS)
        bx = pad
        by = top_center_y - offer_logo_h // 2
        layer.paste(scaled, (bx, by), scaled)
        badge_right_edge = bx + scaled_w + pad
    else:
        # Text badge fallback — великий та чіткий
        btext = offer.upper()
        bw = text_w(btext, f_bdg) + pad * 2
        bh = text_h(btext, f_bdg) + int(pad * 0.9)
        bx, by = pad, top_center_y - bh // 2
        rounded_rect((bx, by, bx + bw, by + bh), r=12, fill=(210, 20, 20, 240))
        bb = draw.textbbox((0, 0), btext, font=f_bdg)
        draw.text(
            (bx + pad, by + (bh - (bb[3] - bb[1])) // 2),
            btext, font=f_bdg, fill=(255, 255, 255, 255)
        )
        badge_right_edge = bx + bw + pad

    # ============================================================
    # TOP-CENTER: GAME LOGO
    # ============================================================
    game_logo_h = int(H * 0.085)   # ~87px
    avail_left = badge_right_edge
    avail_right = W - pad
    center_x = (avail_left + avail_right) // 2

    if game_logo_img is not None:
        gw, gh = game_logo_img.size
        scaled_w = int(gw * game_logo_h / gh)
        # Cap width so it doesn't crowd offer badge
        max_w = avail_right - avail_left - pad
        if scaled_w > max_w:
            scaled_w = max_w
            game_logo_h = int(gh * scaled_w / gw)
        scaled_g = game_logo_img.resize((scaled_w, game_logo_h), Image.LANCZOS)
        gx = center_x - scaled_w // 2
        gy = top_center_y - game_logo_h // 2
        layer.paste(scaled_g, (max(avail_left, gx), max(0, gy)), scaled_g)
    else:
        # Text fallback — game logo name top-center, gold
        lw = text_w(game_logo_text, f_logo)
        lx = max(avail_left, center_x - lw // 2)
        ly = top_center_y - text_h(game_logo_text, f_logo) // 2
        draw_shadow((lx, ly), game_logo_text, f_logo, fill=(255, 215, 0, 245), offset=2)

    # ============================================================
    # HEADLINE — centered, gold, min 80px ExtraBold
    # ============================================================
    hl_y = int(H * 0.535)

    def draw_headline_line(text, y):
        hw = text_w(text, f_hero)
        hx = max(pad, (W - hw) // 2)
        draw_shadow((hx, y), text, f_hero, fill=(255, 215, 0, 255), offset=4)
        return text_h(text, f_hero)

    hw_total = text_w(headline, f_hero)
    if hw_total > W - pad * 2:
        # Розбиваємо на 2 рядки по словах
        words = headline.split()
        best_split, best_diff = 1, float("inf")
        for s in range(1, len(words)):
            l1 = text_w(" ".join(words[:s]), f_hero)
            l2 = text_w(" ".join(words[s:]), f_hero)
            if abs(l1 - l2) < best_diff:
                best_diff, best_split = abs(l1 - l2), s
        line1 = " ".join(words[:best_split])
        line2 = " ".join(words[best_split:])
        lh1 = draw_headline_line(line1, hl_y)
        lh2 = draw_headline_line(line2, hl_y + lh1 + 6)
        next_y = hl_y + lh1 + lh2 + 10
    else:
        lh = draw_headline_line(headline, hl_y)
        next_y = hl_y + lh + 10

    # ============================================================
    # SUBTITLE
    # ============================================================
    sub_y = next_y + int(H * 0.013)
    sw = text_w(sub, f_sub)
    sx = max(pad, (W - sw) // 2)
    draw_shadow((sx, sub_y), sub, f_sub, fill=(255, 255, 255, 245), offset=2)

    # ============================================================
    # CTA BUTTON
    # ============================================================
    cta_y = sub_y + text_h(sub, f_sub) + int(H * 0.032)
    cw = text_w(cta, f_cta)
    ch = text_h(cta, f_cta)
    btn_w = cw + int(W * 0.18)
    btn_h = ch + int(H * 0.040)
    btn_x = (W - btn_w) // 2

    # Glow ring
    rounded_rect(
        (btn_x - 5, cta_y - 5, btn_x + btn_w + 5, cta_y + btn_h + 5),
        r=btn_h // 2 + 5, fill=(255, 185, 0, 75)
    )
    # Button body
    rounded_rect((btn_x, cta_y, btn_x + btn_w, cta_y + btn_h), r=btn_h // 2, fill=(255, 128, 0, 248))
    # Button text
    draw.text(
        (btn_x + (btn_w - cw) // 2, cta_y + (btn_h - ch) // 2),
        cta, font=f_cta, fill=(255, 255, 255, 255)
    )

    # ============================================================
    # PAYMENT ROW
    # ============================================================
    pay_y = cta_y + btn_h + int(H * 0.022)
    pw = text_w(payments_short, f_sm)
    px = max(pad, (W - pw) // 2)
    draw_shadow((px, pay_y), payments_short, f_sm, fill=(215, 215, 215, 235), offset=1)

    # ============================================================
    # APP BADGE
    # ============================================================
    dl_y = pay_y + text_h(payments_short, f_sm) + int(H * 0.014)
    dw = text_w(download, f_sm)
    dx_pos = max(pad, (W - dw) // 2)
    draw_shadow((dx_pos, dl_y), download, f_sm, fill=(190, 190, 190, 215), offset=1)

    # Composite and return
    out_img = Image.alpha_composite(img, layer).convert("RGB")
    buf = io.BytesIO()
    out_img.save(buf, format="JPEG", quality=94)
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

    # Завантажуємо логотипи один раз перед циклом
    offer_logo_img = await loop.run_in_executor(None, get_offer_logo, offer, 80)
    game_logo_img  = await loop.run_in_executor(None, get_game_logo,  game,  90)

    for i, variant in enumerate(variants_to_use):
        try:
            await context.bot.send_message(chat_id, f"🖼 {i+1}/{count} — {variant['angle']}...")

            # 1. Build visual-only prompt
            prompt = build_prompt(game, geo, variant)

            # 2. Generate background with FAL
            image_bytes = await loop.run_in_executor(None, generate_image_fal, prompt, input_photo)

            # 3. Overlay text + logos programmatically with Pillow
            headline = variant["headline"](g)
            sub      = variant["sub"](g)
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
                offer_logo_img,
                game_logo_img,
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
