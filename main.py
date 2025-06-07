import logging
import openai
from aiogram import Bot, Dispatcher, types, executor
import random
import time
import asyncio

# --- Настройки ---

TELEGRAM_TOKEN = ''
OPENROUTER_API_KEY = ''

# --- Конфигурация OpenAI / OpenRouter ---
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = OPENROUTER_API_KEY

# --- Логирование ---
logging.basicConfig(level=logging.INFO)

# --- Инициализация бота ---
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# --- Промпт для стиля Kaoru ---
base_prompt = """
You are Kaoru, a 20 y.o. girl from Ho Chi Minh, Vietnam.
You are friendly, flirty, playful and use lots of emojis and casual chat.
You chat on Telegram with your fans.
You often use words like: baby, bae, hun, sexy, daddy, my love, hehe, lol, miss u, I’m online now, kiss u, wanna play, wanna see me, hehe naughty 🤭
But you also chat casually: asking about their day, movies, food, fun, and other normal topics.

You do not answer questions about politics, religion, real name, address, phone number or finances. Politely avoid if asked.

Your style is short sentences, casual, lots of emotion and emoji.
"""

# --- Чтение auto_messages.txt ---
with open('auto_messages.txt', 'r', encoding='utf-8') as f:
    auto_messages = [line.strip() for line in f if line.strip()]

# --- Таймеры для авто-сообщений ---
last_message_time = {}

# --- Хэндлер сообщений ---
@dp.message_handler()
async def chat_with_kaoru(message: types.Message):
    global last_message_time

    user_id = message.from_user.id
    last_message_time[user_id] = time.time()

    user_message = message.text

    # Запрос к OpenAI через OpenRouter
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.8,
        max_tokens=200
    )

    reply_text = response['choices'][0]['message']['content']
    await message.reply(reply_text)

# --- Фоновая задача для авто-сообщений ---
async def auto_message_sender():
    global last_message_time
    while True:
        now = time.time()
        for user_id, last_time in list(last_message_time.items()):
            if now - last_time > 1800:  # 30 минут
                msg = random.choice(auto_messages)
                try:
                    await bot.send_message(chat_id=user_id, text=msg)
                except Exception as e:
                    logging.error(f"Failed to send auto message to {user_id}: {e}")
                last_message_time[user_id] = now
        await asyncio.sleep(60)  # проверяем каждую минуту

# --- Запуск бота ---
if name == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(auto_message_sender())
    executor.start_polling(dp, skip_updates=True)
