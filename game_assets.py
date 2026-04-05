"""
game_assets.py — повна база даних ігор для creo-bot
Містить: офіційні кольори бренду, логотипи, стилі крео, візуальні елементи.
"""

from __future__ import annotations
import os
import io
import requests
import logging
from pathlib import Path
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# ============================================================
# GAME DATABASE
# ============================================================
# Структура кожної гри:
#   provider       — розробник гри
#   brand_colors   — офіційні кольори бренду (primary, secondary, accent, bg)
#   logo_url       — пряме посилання на PNG-логотип з прозорим фоном
#   logo_file      — локальна назва файлу в assets/
#   logo_text      — текстовий fallback якщо логотип недоступний
#   style          — опис сцени для FAL (тільки візуал, без тексту)
#   key_elements   — ключові елементи сцени
#   person_style   — стиль людини/персонажа (або None)
#   mood           — атмосфера крео
#   cta_color      — колір CTA кнопки (hex)
#   headline_color — колір хедлайну (hex)

GAMES: dict[str, dict] = {

    # ----------------------------------------------------------
    "aviator": {
        "name": "Aviator",
        "provider": "Spribe",
        "brand_colors": {
            "primary":   "#E30613",   # Aviator red
            "secondary": "#FF6B00",   # orange multiplier
            "accent":    "#FFD700",   # gold
            "bg":        "#0A0A0F",   # near-black
        },
        # Official Spribe press kit / CDN
        "logo_url": "https://spribe.co/wp-content/uploads/2021/05/aviator-logo.png",
        "logo_file": "aviator_logo.png",
        "logo_text": "AVIATOR",
        "style": (
            "dark cinematic stormy sky, iconic red biplane soaring steeply upward, "
            "dramatic orange-red multiplier graph line climbing to top-right, "
            "motion blur speed streaks, scattered clouds with back-lighting, "
            "atmospheric depth with particle glow"
        ),
        "key_elements": [
            "red Aviator biplane with engine flame glow",
            "bold multiplier curve graph (100x+)",
            "coin burst particle effects",
            "dark storm-cloud atmosphere",
        ],
        "person_style": None,
        "mood": "high-stakes tension, rush, adrenaline",
        "cta_color":       "#E30613",
        "headline_color":  "#FF6B00",
        "badge_color":     "#E30613",
    },

    # ----------------------------------------------------------
    "jetx": {
        "name": "JetX",
        "provider": "SmartSoft Gaming",
        "brand_colors": {
            "primary":   "#0057FF",   # JetX electric blue
            "secondary": "#7B2FFF",   # purple
            "accent":    "#FFD700",
            "bg":        "#060B1A",
        },
        "logo_url": "https://smartsoft-games.com/wp-content/uploads/2022/01/JetX-logo.png",
        "logo_file": "jetx_logo.png",
        "logo_text": "JetX",
        "style": (
            "deep outer-space background, JetX sleek rocket blasting vertically upward "
            "in a column of electric blue plasma exhaust, neon holographic multiplier "
            "numbers floating in zero-gravity, star-field with nebula glow, "
            "futuristic HUD rings, coin explosion at launch"
        ),
        "key_elements": [
            "JetX rocket with blue-white afterburner",
            "scrolling multiplier counter (x1 → x500+)",
            "star-field depth with purple nebula",
            "gold coin burst at base",
            "holographic HUD overlay rings",
        ],
        "person_style": None,
        "mood": "futuristic, high-tech, zero-gravity thrill",
        "cta_color":      "#0057FF",
        "headline_color": "#FFD700",
        "badge_color":    "#0057FF",
    },

    # ----------------------------------------------------------
    "chicken_road": {
        "name": "Chicken Road",
        "provider": "Spribe",
        "brand_colors": {
            "primary":   "#FF8C00",   # fire orange
            "secondary": "#FFD700",   # gold
            "accent":    "#FF3300",   # flame red
            "bg":        "#1A0A00",
        },
        "logo_url": "https://spribe.co/wp-content/uploads/2023/10/chicken-road-logo.png",
        "logo_file": "chicken_road_logo.png",
        "logo_text": "CHICKEN ROAD",
        "style": (
            "vibrant cartoon African savanna at golden sunset, "
            "brave cartoon chicken character in sunglasses leaping heroically over a "
            "row of blazing fire ovens, large shining gold coins arcing through the air, "
            "African acacia tree silhouettes, cartoon zebras in background, "
            "cel-shaded 3D art with exaggerated cartoon physics"
        ),
        "key_elements": [
            "cartoon white chicken hero with accessories (mid-jump pose)",
            "row of fire ovens with visible bright flames",
            "oversized spinning gold coins in arc trajectory",
            "African savanna background: acacia trees, zebras",
            "warm golden sunset lighting",
        ],
        "person_style": None,
        "mood": "fun, adventurous, cartoonish excitement",
        "cta_color":      "#FF8C00",
        "headline_color": "#FFD700",
        "badge_color":    "#FF3300",
    },

    # ----------------------------------------------------------
    "lucky_jet": {
        "name": "Lucky Jet",
        "provider": "Gaming Corps",
        "brand_colors": {
            "primary":   "#1B3FFF",   # Lucky Jet blue
            "secondary": "#FF7A00",   # orange
            "accent":    "#FFD700",
            "bg":        "#050C1E",
        },
        "logo_url": "https://cdn.gamingcorps.com/lucky-jet-logo.png",
        "logo_file": "lucky_jet_logo.png",
        "logo_text": "Lucky Jet",
        "style": (
            "high-energy night sky background with gradient from deep navy to dark teal, "
            "Lucky Joe cartoon character in red-and-white jetpack rocketing diagonally upward, "
            "dynamic motion speed-lines radiating behind him, "
            "glowing orange multiplier counter orb, "
            "banknote bills and currency symbols exploding outward"
        ),
        "key_elements": [
            "Lucky Joe cartoon character (helmet, red jetpack, wide grin)",
            "speed-line motion blur streaks",
            "glowing multiplier counter (x1.00 → x150+)",
            "banknote and coin explosion",
            "spark trail behind jetpack",
        ],
        "person_style": None,
        "mood": "action, speed, cartoon fun",
        "cta_color":      "#FF7A00",
        "headline_color": "#FFD700",
        "badge_color":    "#1B3FFF",
    },

    # ----------------------------------------------------------
    "spaceman": {
        "name": "Spaceman",
        "provider": "Pragmatic Play",
        "brand_colors": {
            "primary":   "#6A0DAD",   # Pragmatic purple
            "secondary": "#00C8FF",   # cyan
            "accent":    "#FFD700",
            "bg":        "#030818",
        },
        "logo_url": (
            "https://www.pragmaticplay.com/wp-content/uploads/2022/08/spaceman_logo.png"
        ),
        "logo_file": "spaceman_logo.png",
        "logo_text": "SPACEMAN",
        "style": (
            "vibrant deep-space panorama, cute cartoon astronaut in white spacesuit "
            "floating weightlessly at center, giant ringed planet glowing in the background, "
            "colorful nebula clouds of purple and teal, dense sparkling star-field, "
            "oversized multiplier orb glowing gold in the foreground, "
            "scattered gold coins drifting in zero-gravity"
        ),
        "key_elements": [
            "cartoon spaceman astronaut (round helmet, expressive visor, thumbs up)",
            "large ringed Saturn-like planet",
            "purple-teal nebula cloud backdrop",
            "glowing gold multiplier counter",
            "gold coins floating in zero-g",
        ],
        "person_style": None,
        "mood": "wonder, cosmic adventure, colorful",
        "cta_color":      "#6A0DAD",
        "headline_color": "#00C8FF",
        "badge_color":    "#6A0DAD",
    },

    # ----------------------------------------------------------
    "ice_fishing": {
        "name": "Ice Fishing Live",
        "provider": "BGaming",
        "brand_colors": {
            "primary":   "#00BFFF",   # icy blue
            "secondary": "#9B59FF",   # aurora purple
            "accent":    "#FFD700",
            "bg":        "#050D1A",
        },
        "logo_url": "https://bgaming.com/wp-content/uploads/2023/ice-fishing-live-logo.png",
        "logo_file": "ice_fishing_logo.png",
        "logo_text": "ICE FISHING LIVE",
        "style": (
            "dramatic arctic landscape under a vivid aurora borealis sky "
            "(flowing purple, teal, and green northern lights), "
            "enormous luminous golden fish suspended on a helicopter chain-hook "
            "above a dramatically cracking ice surface, "
            "gold coin shower erupting at the base, "
            "reflections of aurora in the dark water below the ice"
        ),
        "key_elements": [
            "massive glowing golden fish (dangling from steel hook and chain)",
            "helicopter silhouette at top with spotlight beam",
            "aurora borealis (purple-green-teal curtains) sky",
            "cracking ice surface with blue glow beneath",
            "cascading gold coin pile at base",
        ],
        "person_style": None,
        "mood": "epic, cold adventure, jackpot anticipation",
        "cta_color":      "#00BFFF",
        "headline_color": "#FFD700",
        "badge_color":    "#00BFFF",
    },

    # ----------------------------------------------------------
    "sweet_bonanza": {
        "name": "Sweet Bonanza",
        "provider": "Pragmatic Play",
        "brand_colors": {
            "primary":   "#FF1493",   # hot pink
            "secondary": "#9400D3",   # deep purple
            "accent":    "#FFD700",
            "bg":        "#1A0030",
        },
        "logo_url": (
            "https://www.pragmaticplay.com/wp-content/uploads/2019/06/Sweet_Bonanza_Logo.png"
        ),
        "logo_file": "sweet_bonanza_logo.png",
        "logo_text": "SWEET BONANZA",
        "style": (
            "explosive candy-land dreamscape bursting with color, "
            "oversized photorealistic 3D candy symbols tumbling through the air "
            "(giant watermelon, plum, grape, strawberry, lollipop), "
            "rainbow lollipops framing both sides, "
            "multiplier bombs with glowing golden fuses detonating mid-air, "
            "confetti and sparkle rain, candy-stripe cloud background"
        ),
        "key_elements": [
            "giant 3D candy symbols: watermelon, plum, grape, lollipop",
            "multiplier bombs with golden fuse (x2–x100)",
            "confetti and sparkle explosion",
            "rainbow lollipop frame elements",
            "candy-stripe background clouds",
        ],
        "person_style": None,
        "mood": "joyful, sweet, explosive wins",
        "cta_color":      "#FF1493",
        "headline_color": "#FFD700",
        "badge_color":    "#9400D3",
    },

    # ----------------------------------------------------------
    "big_bass": {
        "name": "Big Bass Bonanza",
        "provider": "Pragmatic Play",
        "brand_colors": {
            "primary":   "#1B6CA8",   # lake blue
            "secondary": "#228B22",   # forest green
            "accent":    "#FFD700",
            "bg":        "#0A1A0A",
        },
        "logo_url": (
            "https://www.pragmaticplay.com/wp-content/uploads/2020/11/Big_Bass_Bonanza_Logo.png"
        ),
        "logo_file": "big_bass_logo.png",
        "logo_text": "BIG BASS BONANZA",
        "style": (
            "golden-hour fishing lake at sunset, "
            "enormous photorealistic largemouth bass leaping dramatically from shimmering water, "
            "droplets catching warm orange sunlight, "
            "fishing line pulled taut from the water, "
            "proud fisherman silhouette on wooden dock, "
            "gold coins and banknotes erupting from the water like a geyser, "
            "trophy cup visible on the dock"
        ),
        "key_elements": [
            "large realistic largemouth bass (airborne, water-spray halo)",
            "taut fishing line and rod",
            "gold coins + banknotes erupting from water",
            "fisherman silhouette on dock",
            "sunset over calm lake with tree reflections",
        ],
        "person_style": None,
        "mood": "outdoorsy triumph, big catch, rewarding",
        "cta_color":      "#1B6CA8",
        "headline_color": "#FFD700",
        "badge_color":    "#228B22",
    },

    # ----------------------------------------------------------
    "fruit_party": {
        "name": "Fruit Party",
        "provider": "Pragmatic Play",
        "brand_colors": {
            "primary":   "#FF4500",   # vivid red-orange
            "secondary": "#32CD32",   # lime green
            "accent":    "#FFD700",
            "bg":        "#1A0A1A",
        },
        "logo_url": (
            "https://www.pragmaticplay.com/wp-content/uploads/2020/07/Fruit_Party_Logo.png"
        ),
        "logo_file": "fruit_party_logo.png",
        "logo_text": "FRUIT PARTY",
        "style": (
            "festive tropical fruit explosion, "
            "giant hyper-realistic 3D fruit symbols raining down from above "
            "(watermelon halves, grape clusters, strawberries, lemons, cherries), "
            "confetti cannon burst in every direction, "
            "disco spotlights sweeping across a dark party background, "
            "streamers and balloons, multiplier badge stars floating"
        ),
        "key_elements": [
            "oversized 3D fruits: watermelon, grapes, strawberry, lemon, cherry",
            "confetti cannon burst (multi-color)",
            "disco ball spotlight beams",
            "multiplier star badges",
            "party streamer ribbons",
        ],
        "person_style": None,
        "mood": "celebration, tropical party, colorful wins",
        "cta_color":      "#FF4500",
        "headline_color": "#FFD700",
        "badge_color":    "#32CD32",
    },

    # ----------------------------------------------------------
    "gates_olympus": {
        "name": "Gates of Olympus",
        "provider": "Pragmatic Play",
        "brand_colors": {
            "primary":   "#8B00FF",   # divine purple
            "secondary": "#FFD700",   # gold
            "accent":    "#FFFFFF",
            "bg":        "#0A0518",
        },
        "logo_url": (
            "https://www.pragmaticplay.com/wp-content/uploads/2021/04/Gates_of_Olympus_Logo.png"
        ),
        "logo_file": "gates_olympus_logo.png",
        "logo_text": "GATES OF OLYMPUS",
        "style": (
            "epic Greek mythology panorama, "
            "mighty Zeus god standing upon clouds of Mount Olympus, "
            "divine golden light radiating downward from parted storm clouds, "
            "ancient white marble Parthenon columns in the background, "
            "crackling purple and white lightning bolts arcing across the sky, "
            "cascading gold coins raining down, "
            "atmospheric god-rays cutting through dramatic purple clouds"
        ),
        "key_elements": [
            "Zeus figure (raised lightning bolt, flowing white robe, divine glow)",
            "ancient Parthenon columns (weathered marble)",
            "purple-white lightning bolts",
            "divine god-ray beam of golden light",
            "gold coin cascade",
            "dramatic storm-cloud backdrop",
        ],
        "person_style": None,
        "mood": "epic, mythological, divine power",
        "cta_color":      "#8B00FF",
        "headline_color": "#FFD700",
        "badge_color":    "#8B00FF",
    },

    # ----------------------------------------------------------
    "naija_wheel": {
        "name": "Naija Wheel",
        "provider": "Internal / African Studio",
        "brand_colors": {
            "primary":   "#008000",   # Nigeria green
            "secondary": "#FFD700",   # gold
            "accent":    "#FF0000",   # red
            "bg":        "#0A1A00",
        },
        "logo_url": "",  # no official CDN — use logo_text fallback
        "logo_file": "naija_wheel_logo.png",
        "logo_text": "NAIJA WHEEL",
        "style": (
            "vibrant West African celebration scene, "
            "giant glittering prize wheel at center spinning with momentum, "
            "prize sectors decorated with Ankara fabric patterns in green, gold, red, "
            "bursting money bags and naira notes flying through the air, "
            "festive confetti and drumbeat energy, "
            "silhouettes of celebrating crowd in background, "
            "market lights and lanterns ambiance"
        ),
        "key_elements": [
            "large prize wheel with Ankara-pattern sectors and prize labels",
            "naira and USD banknotes bursting out",
            "money bags splitting open",
            "celebrating crowd silhouettes",
            "African pattern confetti and lantern lights",
        ],
        "person_style": None,
        "mood": "festive, African celebration, community win",
        "cta_color":      "#008000",
        "headline_color": "#FFD700",
        "badge_color":    "#FF0000",
    },

    # ----------------------------------------------------------
    "betsafe_virtual": {
        "name": "Betsafe Virtual",
        "provider": "Betsafe",
        "brand_colors": {
            "primary":   "#005C99",   # Betsafe blue
            "secondary": "#228B22",   # pitch green
            "accent":    "#FFFFFF",
            "bg":        "#030D1A",
        },
        "logo_url": "https://www.betsafe.com/assets/images/betsafe-logo.png",
        "logo_file": "betsafe_virtual_logo.png",
        "logo_text": "BETSAFE VIRTUAL",
        "style": (
            "cinematic top-down broadcast camera angle of a professional football stadium "
            "at the peak moment of a match, "
            "stadium floodlights blazing over a perfectly manicured green pitch, "
            "player mid-kick with ball arcing toward goal, "
            "roaring crowd blur in the stands, "
            "virtual sports betting HUD overlay with live odds panel, "
            "broadcast lower-third graphic bar"
        ),
        "key_elements": [
            "football player silhouette mid-kick",
            "perfectly lit stadium pitch (aerial angle)",
            "roaring crowd in stands",
            "live odds panel / HUD overlay",
            "broadcast camera graphic bars",
        ],
        "person_style": None,
        "mood": "sports excitement, live action, competitive energy",
        "cta_color":      "#005C99",
        "headline_color": "#FFFFFF",
        "badge_color":    "#005C99",
    },
}


# ============================================================
# LOGO LOADER
# ============================================================
def get_logo(game_id: str, size: tuple[int, int] = (200, 80)) -> Optional[Image.Image]:
    """
    Повертає логотип гри як PIL Image (RGBA) або None якщо недоступний.
    Зберігає в assets/ для кешування.
    """
    game = GAMES.get(game_id)
    if not game:
        return None

    logo_path = ASSETS_DIR / game["logo_file"]

    # Використовуємо кеш
    if logo_path.exists():
        try:
            return Image.open(logo_path).convert("RGBA").resize(size, Image.LANCZOS)
        except Exception:
            logo_path.unlink(missing_ok=True)

    # Завантажуємо якщо є URL
    if game.get("logo_url"):
        try:
            r = requests.get(game["logo_url"], timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            img.save(logo_path)
            logger.info(f"Logo cached: {game_id}")
            return img.resize(size, Image.LANCZOS)
        except Exception as e:
            logger.warning(f"Logo download failed for {game_id}: {e}")

    return None  # caller uses logo_text fallback


def get_brand_color(game_id: str, key: str = "primary") -> tuple[int, int, int]:
    """Повертає RGB tuple кольору бренду гри."""
    game = GAMES.get(game_id, {})
    colors = game.get("brand_colors", {})
    hex_color = colors.get(key, "#FF6600")
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_cta_color(game_id: str) -> tuple[int, int, int]:
    game = GAMES.get(game_id, {})
    return _hex_to_rgb(game.get("cta_color", "#FF6600"))


def get_headline_color(game_id: str) -> tuple[int, int, int]:
    game = GAMES.get(game_id, {})
    return _hex_to_rgb(game.get("headline_color", "#FFD700"))


def get_badge_color(game_id: str) -> tuple[int, int, int]:
    game = GAMES.get(game_id, {})
    return _hex_to_rgb(game.get("badge_color", "#CC0000"))


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ============================================================
# PROMPT HELPERS
# ============================================================
def get_fal_prompt(game_id: str, geo_person_desc: str = "", angle: str = "") -> str:
    """
    Повертає готовий FAL-промпт для фонової сцени гри (без тексту).
    """
    game = GAMES.get(game_id, GAMES["ice_fishing"])
    bg_mod = "night-time cinematic lighting, dark moody atmosphere, " if angle == "NIGHT WIN" else ""

    person_block = f"\nPERSON IN SCENE: {geo_person_desc}." if geo_person_desc else ""
    elements_str = "\n".join(f"  - {el}" for el in game["key_elements"])

    return (
        f"Professional iGaming advertisement background visual. "
        f"Square 1:1 format. Ultra-HD. Commercial quality. "
        f"Photorealistic render. No text. No words. No letters. No UI overlays. No watermarks.\n\n"
        f"GAME THEME ({game['name']} by {game['provider']}): {bg_mod}{game['style']}.\n\n"
        f"KEY VISUAL ELEMENTS:\n{elements_str}\n\n"
        f"COLOR PALETTE: "
        f"primary {game['brand_colors']['primary']}, "
        f"secondary {game['brand_colors']['secondary']}, "
        f"accent {game['brand_colors']['accent']}, "
        f"bg {game['brand_colors']['bg']}.\n"
        f"{person_block}\n\n"
        f"COMPOSITION: hero game visual fills center and upper 55%. "
        f"Lower 45% fades to dark via natural vignette (space for text overlay). "
        f"Top 10% slightly dark (space for branding badge). "
        f"Cinematic lighting, high production value, "
        f"style of {game['provider']} official marketing art."
    )


# ============================================================
# QUICK LOOKUP
# ============================================================
def game_ids() -> list[str]:
    return list(GAMES.keys())


def game_name(game_id: str) -> str:
    return GAMES.get(game_id, {}).get("name", game_id)


def game_provider(game_id: str) -> str:
    return GAMES.get(game_id, {}).get("provider", "Unknown")


if __name__ == "__main__":
    # Тест: виводимо всі ігри
    for gid, g in GAMES.items():
        print(f"{gid:20s} | {g['provider']:25s} | {g['brand_colors']['primary']}")
