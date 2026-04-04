# Creo Generator Bot

Telegram бот для автоматичної генерації рекламних крео для iGaming.

## Як запустити

### 1. Завантаж на GitHub

1. Йди на github.com → New repository → назви `creo-bot`
2. Завантаж всі файли з цієї папки

### 2. Задеплой на Railway

1. Йди на railway.app
2. New Project → Deploy from GitHub repo
3. Вибери `creo-bot`
4. Додай змінні середовища (Variables):

```
BOT_TOKEN=твій_telegram_token
ANTHROPIC_KEY=твій_anthropic_key
FAL_KEY=твій_fal_key
```

5. Deploy → бот живе 24/7

### 3. Використання

Відкрий бота в Telegram і пиши:

```
/creo 5 GH 1xBet
/creo 10 TZ MelBet
/creo 3 GH 1xBet 150 Free Spins
```

## Як працює

1. Ти пишеш `/creo 10 GH 1xBet`
2. Claude генерує 10 промтів з аналізом якості
3. Якщо якість < 7/10 — автоматично перегенеровує
4. fal.ai FLUX генерує зображення
5. Бот надсилає тобі фото з підписом

## Файли

- `bot.py` — основний файл бота
- `generator.py` — логіка генерації (Claude + fal.ai)
- `requirements.txt` — залежності
- `.env` — ключі (НЕ завантажуй на GitHub!)

## Гео

- GH — Гана (GHS, MTN Mobile Money)
- TZ — Танзанія (TZS, M-Pesa)
- IN — Індія (INR, UPI/PhonePe)
