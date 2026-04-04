import os 
import asyncio
import aiohttp
import anthropic
import fal_client
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
FAL_KEY = os.getenv("FAL_KEY")

# Geo configs
GEO_CONFIG = {
    "GH": {
        "name": "Ghana",
        "currency": "GHS",
        "min_deposit": "1 GHS",
        "big_win": "8,500 GHS",
        "payment": "MTN Mobile Money",
        "language": "English",
        "bonus": "150 Free Spins + 200% first deposit",
        "urgency": "Today Only",
        "local_color": "vibrant gold and green"
    },
    "TZ": {
        "name": "Tanzania",
        "currency": "TZS",
        "min_deposit": "1 USD",
        "big_win": "500,000 TZS",
        "payment": "M-Pesa",
        "language": "Swahili/English",
        "bonus": "150 Free Spins + 200% first deposit",
        "urgency": "Leo Tu! (Today Only)",
        "local_color": "warm red and yellow"
    },
    "IN": {
        "name": "India",
        "currency": "INR",
        "min_deposit": "100 INR",
        "big_win": "50,000 INR",
        "payment": "UPI / PhonePe",
        "language": "Hindi/English",
        "bonus": "150 Free Spins + 200% first deposit",
        "urgency": "Sirf Aaj! (Today Only)",
        "local_color": "saffron orange and blue"
    }
}

def build_system_prompt():
    return """You are an expert media buyer and creative director for iGaming (betting/casino) ads.
You create highly converting ad creatives for African and Asian markets.

WHAT WORKS:
- Low entry barrier (1 GHS / 1 USD minimum deposit)
- Huge win amounts with local currency
- Local payment methods shown prominently
- Social proof (real names, screenshots)
- Urgency (Today Only, Limited Offer, 24h)
- Local language mix
- Big bold offer taking full banner space

WHAT DOESN'T WORK:
- Small win amounts
- Street slang (Yo bro, OMG)
- No clear offer
- Worldwide targeting
- Aviator as main game (oversaturated)

STYLE REFERENCE: Ice Fishing Live style — bright, gamified
- Big offer on full banner
- Character + prizes + helicopter Evolution style
- Coins and gems at bottom
- CTA button at bottom
- 1xBet logo + payment methods

Always output ONLY valid JSON, no markdown, no explanation."""

def build_user_prompt(geo: str, offer: str, index: int):
    cfg = GEO_CONFIG[geo]
    
    styles = [
        "celebration scene with coins exploding",
        "winner holding phone showing big balance",
        "sports stadium atmosphere with betting odds",
        "casino jackpot moment with flashing lights",
        "mobile phone screen showing huge win notification"
    ]
    style = styles[index % len(styles)]
    
    return f"""Generate a FLUX image prompt for a gambling ad creative.

GEO: {cfg['name']} ({geo})
OFFER: {offer}
BONUS: {cfg['bonus']}
MIN DEPOSIT: {cfg['min_deposit']}
BIG WIN: {cfg['big_win']}
PAYMENT: {cfg['payment']}
URGENCY: {cfg['urgency']}
VISUAL STYLE: {style}
COLOR PALETTE: {cfg['local_color']}
CREATIVE INDEX: {index + 1}

Return JSON with this exact structure:
{{
  "image_prompt": "detailed FLUX prompt for the visual, 100-150 words, photorealistic style, no text in image",
  "headline": "main ad headline in {cfg['language']} (max 6 words)",
  "subtext": "secondary text with offer details",
  "cta": "call to action button text",
  "overlay_text": "big win amount to overlay: {cfg['big_win']}",
  "quality_score": 0-10 score of how converting this creative should be,
  "quality_reason": "one sentence why"
}}"""

async def generate_single_prompt(client: anthropic.Anthropic, geo: str, offer: str, index: int) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": build_user_prompt(geo, offer, index)}]
    )
    
    import json
    text = response.content[0].text.strip()
    # Clean any accidental markdown
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

async def generate_image(prompt_data: dict) -> str:
    """Generate image via fal.ai FLUX"""
    os.environ["FAL_KEY"] = FAL_KEY
    
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: fal_client.run(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt_data["image_prompt"],
                "image_size": "square_hd",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": False
            }
        )
    )
    
    return result["images"][0]["url"]

def is_quality_ok(prompt_data: dict) -> bool:
    """Claude self-check — only send if quality >= 7"""
    score = prompt_data.get("quality_score", 0)
    return score >= 7

async def generate_creos(update, context, count: int, geo: str, offer: str, status_msg):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    cfg = GEO_CONFIG[geo]
    
    sent = 0
    attempts = 0
    max_attempts = count + 5  # allow some retries for low quality
    
    await status_msg.edit_text(
        f"🎨 Генерую промти для {count} крео...\n"
        f"Гео: {geo} | Оффер: {offer}"
    )
    
    while sent < count and attempts < max_attempts:
        attempts += 1
        
        try:
            # Step 1: Claude generates prompt
            logger.info(f"Generating prompt {attempts} for {geo}/{offer}")
            prompt_data = await generate_single_prompt(client, geo, offer, sent)
            
            # Step 2: Quality check
            if not is_quality_ok(prompt_data):
                logger.info(f"Low quality ({prompt_data.get('quality_score')}), regenerating...")
                await status_msg.edit_text(
                    f"🔄 Крео {sent+1}/{count}: низька якість ({prompt_data.get('quality_score')}/10), перегенерую..."
                )
                continue
            
            await status_msg.edit_text(
                f"🖼 Генерую зображення {sent+1}/{count}...\n"
                f"Якість промту: {prompt_data.get('quality_score')}/10"
            )
            
            # Step 3: Generate image
            image_url = await generate_image(prompt_data)
            
            # Step 4: Send to user with caption
            caption = (
                f"✅ Крео #{sent+1} | {geo} | {offer}\n\n"
                f"📝 Заголовок: {prompt_data.get('headline', '')}\n"
                f"💰 Виграш: {prompt_data.get('overlay_text', cfg['big_win'])}\n"
                f"🎯 CTA: {prompt_data.get('cta', '')}\n"
                f"📊 Якість: {prompt_data.get('quality_score')}/10\n"
                f"💡 {prompt_data.get('quality_reason', '')}"
            )
            
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=image_url,
                caption=caption
            )
            
            sent += 1
            
            # Small delay between generations
            if sent < count:
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error on attempt {attempts}: {e}")
            await status_msg.edit_text(
                f"⚠️ Помилка на крео {sent+1}, пробую ще раз...\n{str(e)[:100]}"
            )
            await asyncio.sleep(3)
    
    # Final summary
    await status_msg.edit_text(
        f"✅ Готово! Згенеровано {sent}/{count} крео\n"
        f"Гео: {geo} | Оффер: {offer}\n"
        f"Спроб: {attempts}"
    )
