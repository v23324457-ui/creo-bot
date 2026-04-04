"""
overlay.py - накладає текст, логотипи, кнопку на згенероване зображення
"""
import os
import requests
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urllib.request

# Download fonts
def get_font(size, bold=False):
    """Get a bold font for overlay text"""
    font_urls = {
        "bold": "https://github.com/google/fonts/raw/main/apache/oswald/Oswald%5Bwght%5D.ttf",
        "regular": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto%5Bwdth%2Cwght%5D.ttf"
    }
    font_path = f"/tmp/font_{'bold' if bold else 'regular'}.ttf"
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve(font_urls["bold" if bold else "regular"], font_path)
        except:
            return ImageFont.load_default()
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def download_logo(url, size=(80, 80)):
    """Download and resize a logo"""
    try:
        r = requests.get(url, timeout=5)
        img = Image.open(io.BytesIO(r.content)).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return img
    except:
        return None

def draw_rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    """Draw rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=outline_width)

def draw_text_with_shadow(draw, pos, text, font, fill, shadow_color=(0,0,0,180), shadow_offset=3):
    """Draw text with shadow for readability"""
    x, y = pos
    # Shadow
    draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill=shadow_color)
    draw.text((x-shadow_offset, y+shadow_offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=fill)

def draw_text_centered(draw, y, text, font, fill, img_width, shadow=True):
    """Draw centered text"""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (img_width - w) // 2
    if shadow:
        draw_text_with_shadow(draw, (x, y), text, font, fill)
    else:
        draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]  # return height

def add_overlay(image_url: str, geo: str, offer: str, headline: str, win_amount: str, cta: str, index: int) -> bytes:
    """
    Download FLUX image and add complete overlay:
    - Win amount (big, center-bottom)
    - Headline
    - Bonus text
    - CTA button
    - Payment logos
    - Offer brand logo area
    """
    # Download base image
    r = requests.get(image_url, timeout=30)
    img = Image.open(io.BytesIO(r.content)).convert("RGBA")
    W, H = img.size  # typically 1024x1024
    
    # Create overlay layer
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # === GRADIENT BOTTOM BAR ===
    # Semi-transparent dark gradient at bottom for text readability
    bar_h = int(H * 0.38)
    bar_y = H - bar_h
    for i in range(bar_h):
        alpha = int(200 * (i / bar_h))
        draw.rectangle([0, bar_y + i, W, bar_y + i + 1], fill=(0, 0, 0, alpha))
    
    # === WIN AMOUNT (biggest text) ===
    win_font = get_font(int(H * 0.10), bold=True)
    win_y = H - bar_h + int(bar_h * 0.05)
    draw_text_centered(draw, win_y, win_amount, win_font, (255, 215, 0), W)
    
    # === HEADLINE ===
    headline_font = get_font(int(H * 0.055), bold=True)
    headline_y = win_y + int(H * 0.12)
    draw_text_centered(draw, headline_y, headline, headline_font, (255, 255, 255), W)
    
    # === BONUS LINE ===
    bonus_configs = {
        "GH": "150 Free Spins • Start from 1 GHS",
        "TZ": "Mizunguko 250 Bure • Anza na 2,000 TZS",
        "IN": "150 Free Spins • Start from ₹100",
    }
    bonus_text = bonus_configs.get(geo, "150 Free Spins • Low Entry")
    bonus_font = get_font(int(H * 0.035))
    bonus_y = headline_y + int(H * 0.07)
    draw_text_centered(draw, bonus_y, bonus_text, bonus_font, (200, 255, 200), W)
    
    # === CTA BUTTON ===
    btn_w = int(W * 0.55)
    btn_h = int(H * 0.072)
    btn_x = (W - btn_w) // 2
    btn_y = bonus_y + int(H * 0.055)
    # Orange/green button
    draw_rounded_rect(draw, [btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], 
                      radius=btn_h//2, fill=(255, 140, 0, 240), 
                      outline=(255, 200, 0), outline_width=3)
    cta_font = get_font(int(H * 0.042), bold=True)
    cta_bbox = draw.textbbox((0,0), cta, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_x = btn_x + (btn_w - cta_w) // 2
    cta_y = btn_y + (btn_h - (cta_bbox[3]-cta_bbox[1])) // 2
    draw.text((cta_x, cta_y), cta, font=cta_font, fill=(255, 255, 255))
    
    # === PAYMENT LOGOS ROW ===
    payment_logos = {
        "GH": [
            ("MTN", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/New-mtn-logo.jpg/240px-New-mtn-logo.jpg"),
            ("Vodafone", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Vodafone_icon.svg/240px-Vodafone_icon.svg.png"),
        ],
        "TZ": [
            ("M-Pesa", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/M-PESA_LOGO-01.svg/240px-M-PESA_LOGO-01.svg.png"),
            ("Airtel", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Airtel_Africa_Logo.png/240px-Airtel_Africa_Logo.png"),
        ],
        "IN": [
            ("UPI", "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/UPI-Logo-vector.svg/240px-UPI-Logo-vector.svg.png"),
            ("PhonePe", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/PhonePe_Logo.png/240px-PhonePe_Logo.png"),
        ],
    }
    
    logos = payment_logos.get(geo, payment_logos["GH"])
    logo_size = int(H * 0.055)
    logo_y = btn_y + btn_h + int(H * 0.02)
    logo_spacing = int(W * 0.15)
    logo_start_x = (W - logo_spacing * len(logos)) // 2
    
    for i, (name, url) in enumerate(logos):
        logo = download_logo(url, (logo_size, logo_size))
        if logo:
            lx = logo_start_x + i * logo_spacing
            overlay.paste(logo, (lx, logo_y), logo)
        else:
            # Fallback: text logo
            lf = get_font(int(H * 0.025), bold=True)
            draw.text((logo_start_x + i * logo_spacing, logo_y), name, font=lf, fill=(255,255,255))
    
    # === TOP LEFT: OFFER BADGE ===
    badge_configs = {
        "GH": ("1xBet", (230, 30, 30)),
        "TZ": ("MelBet", (230, 30, 30)),
        "IN": ("1xBet", (230, 30, 30)),
    }
    badge_text, badge_color = badge_configs.get(geo, ("1xBet", (230, 30, 30)))
    if offer.lower().startswith("mel"):
        badge_text, badge_color = "MelBet", (230, 30, 30)
    
    badge_font = get_font(int(H * 0.045), bold=True)
    badge_bbox = draw.textbbox((0,0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0] + 30
    badge_h = badge_bbox[3] - badge_bbox[1] + 16
    draw_rounded_rect(draw, [20, 20, 20+badge_w, 20+badge_h], 
                      radius=8, fill=(*badge_color, 230), outline=(255,200,0), outline_width=2)
    draw.text((35, 28), badge_text, font=badge_font, fill=(255, 255, 255))
    
    # === TOP RIGHT: MULTIPLIER BADGE ===
    mult_texts = ["5000x", "200%", "150 FREE", "x5 WIN"]
    mult_text = mult_texts[index % len(mult_texts)]
    mult_font = get_font(int(H * 0.04), bold=True)
    mult_bbox = draw.textbbox((0,0), mult_text, font=mult_font)
    mult_w = mult_bbox[2] - mult_bbox[0] + 24
    mult_h = mult_bbox[3] - mult_bbox[1] + 16
    mx = W - mult_w - 20
    draw_rounded_rect(draw, [mx, 20, mx+mult_w, 20+mult_h],
                      radius=mult_h//2, fill=(255, 165, 0, 230), outline=(255,220,0), outline_width=2)
    draw.text((mx+12, 28), mult_text, font=mult_font, fill=(255, 255, 255))
    
    # Merge overlay with base image
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    
    # Save to bytes
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=92)
    output.seek(0)
    return output.getvalue()
