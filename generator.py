import os
import asyncio
import anthropic
import fal_client
import logging

logger = logging.getLogger(__name__)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
FAL_KEY = os.getenv("FAL_KEY")

GEO_CONFIG = {
    "GH": {
        "name": "Ghana", "currency": "GHS", "min_deposit": "1 GHS",
        "big_win": "8,500 GHS", "payment": "MTN Mobile Money",
        "bonus": "150 Free Spins + 200% first deposit",
        "cta_text": "PLAY NOW - FREE SPINS",
    },
    "TZ": {
        "name": "Tanzania", "currency": "TZS", "min_deposit": "2,000 TZS",
        "big_win": "500,000 TZS", "payment": "M-Pesa, Airtel, Tigo Pesa",
        "bonus": "Mizunguko 250 Bure",
        "cta_text": "ANZA SASA",
    },
    "IN": {
        "name": "India", "currency": "INR", "min_deposit": "100 INR",
        "big_win": "50,000 INR", "payment": "UPI, PhonePe, Paytm",
        "bonus": "150 Free Spins + 200% first deposit",
        "cta_text": "ABHI KHELO",
    }
}

# Pre-written Ice Fishing style image prompts - NO text in image
GH_IMAGE_PROMPTS = [
    "Digital art, 3D cartoon game illustration style, vibrant saturated colors, glossy render. Center: one large glowing golden fish hanging from metal fishing hook on chain. Top center: red helicopter with fishing line attached to fish hook. Right side: young smiling Black African man chest portrait, casual shirt, holding spread fan of banknotes in both hands raised up, big happy smile, looking forward. Background: bright blue sky gradient with white clouds, golden light rays bursting from center. Bottom third: massive pile of shiny golden coins and green emerald gems overflowing. No text, no letters, no numbers, no words anywhere.",
    "Digital art 3D cartoon illustration. Top: two blue-yellow helicopters at top left and top right corners, each holding fishing hooks on chains hanging down. Center: three large shiny golden fish hanging from the hooks, glowing with golden light. Background: bright tropical sky blue with golden glow radiating outward, white clouds. Bottom: explosion of gold coins, green gems, red rubies scattered in big pile. Ghana red gold green colors as decorative light streaks on sides. No text, no letters, no numbers.",
    "Digital 3D game art illustration. Center-left: smiling young Black Ghanaian man in colorful kente pattern shirt, holding large golden fish trophy raised up in right hand, left hand holding spread of banknotes, big grin looking at viewer. Right side: large glowing golden fish hanging from helicopter hook. Background: Ghana tropical scenery, palm trees blurred, golden sunset sky, ocean glimmers. Foreground bottom: gold coins pile, sparkling light effects, green gem stones. Top: helicopter visible at top. No text, no letters, no numbers.",
    "3D cartoon game banner illustration, vibrant colors. Center: giant golden fish jumping from sparkling glowing water, coins exploding outward from the impact. Top: red helicopter with branded hook catching the fish. Left side: excited Black man with huge grin, arms raised, holding cash money. Background: deep blue aurora sky with purple and green light streaks. Bottom: hundreds of gold coins and gems pile. No text, no letters, no numbers in image.",
    "3D cartoon game art illustration, glossy professional. Center: confident smiling young Black man in modern casual clothes, one hand holding phone up, other hand thumbs up toward viewer. Left side: large golden fish on hook. Right side: large golden fish on hook. Top: two small helicopters. Background: bright sky blue, rays of golden light from behind character. Bottom: overflowing pile of gold coins, diamonds, emeralds. No text, no letters, no words anywhere in image.",
]

TZ_IMAGE_PROMPTS = [
    "Digital art 3D cartoon illustration. Center: smiling Tanzanian man holding banknote fan, large golden fish on hook beside him, helicopter top. Sky blue background. Gold coins bottom. No text.",
    "3D game art. Three golden fish hanging from helicopter hooks. Blue sky golden glow. Massive gold coins gems bottom. No text.",
]

IN_IMAGE_PROMPTS = [
    "Digital art 3D cartoon. Smiling Indian man holding rupee notes, golden fish hooks helicopters. Bright background gold coins bottom. No text.",
]

PROMPTS_MAP = {"GH": GH_IMAGE_PROMPTS, "TZ": TZ_IMAGE_PROMPTS, "IN": IN_IMAGE_PROMPTS}

HEADLINES = {
    "GH": ["WIN 8,500 GHS TODAY!", "FREE SPINS — START NOW!", "1 GHS → 8,500 GHS WIN!", "GET 150 FREE SPINS!", "WIN BIG TODAY ONLY!"],
    "TZ": ["SHINDA 500,000 TZS!", "SPINSI 250 BURE!", "ANZA NA 2,000 TZS!", "PATA BONUS LEO!", "WIN KUBWA LEO!"],
    "IN": ["WIN 50,000 INR TODAY!", "150 FREE SPINS NOW!", "START WITH ₹100!", "GET BONUS TODAY!", "WIN BIG NOW!"],
}

async def generate_creos(update, context, count: int, geo: str, offer: str, status_msg):
    from overlay import add_overlay
    import io

    cfg = GEO_CONFIG[geo]
    os.environ["FAL_KEY"] = FAL_KEY
    sent = 0
    attempts = 0

    await status_msg.edit_text(f"🎨 Генерую {count} крео Ice Fishing стиль...\nГео: {geo} | {offer}")

    while sent < count and attempts < count + 5:
        attempts += 1
        try:
            img_prompts = PROMPTS_MAP.get(geo, GH_IMAGE_PROMPTS)
            img_prompt = img_prompts[sent % len(img_prompts)]
            headlines = HEADLINES.get(geo, HEADLINES["GH"])
            headline = headlines[sent % len(headlines)]

            await status_msg.edit_text(f"🖼 FLUX генерує зображення {sent+1}/{count}...")

            # Generate base image
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    "fal-ai/flux/dev",
                    arguments={
                        "prompt": img_prompt,
                        "image_size": "square_hd",
                        "num_inference_steps": 35,
                        "guidance_scale": 4.5,
                        "num_images": 1,
                        "enable_safety_checker": False
                    }
                )
            )
            image_url = result["images"][0]["url"]

            await status_msg.edit_text(f"✏️ Накладаю текст і логотипи {sent+1}/{count}...")

            # Add overlay with text, logos, CTA button
            final_image_bytes = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: add_overlay(
                    image_url=image_url,
                    geo=geo,
                    offer=offer,
                    headline=headline,
                    win_amount=cfg["big_win"],
                    cta=cfg["cta_text"],
                    index=sent
                )
            )

            caption = (
                f"✅ Крео #{sent+1} | {geo} | {offer}\n"
                f"💰 {cfg['big_win']} | 🎯 {cfg['cta_text']}"
            )

            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=io.BytesIO(final_image_bytes),
                caption=caption
            )

            sent += 1
            if sent < count:
                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error attempt {attempts}: {e}")
            await status_msg.edit_text(f"⚠️ Помилка {sent+1}/{count}, повтор...\n{str(e)[:120]}")
            await asyncio.sleep(3)

    await status_msg.edit_text(f"✅ Готово! {sent}/{count} крео готові\nГео: {geo} | {offer}")
