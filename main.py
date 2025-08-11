import os
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# токены берём из переменных окружения (Railway Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_KEY

# история сообщений {user_id: [ {"role": ..., "content": ...}, ... ]}
user_history = {}

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # создаём историю, если её нет
    if user_id not in user_history:
        user_history[user_id] = [{"role": "system", "content": "Ты дружелюбный помощник"}]

    # добавляем сообщение пользователя
    user_history[user_id].append({"role": "user", "content": message.text})

    # запрос к OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # можно поменять на gpt-5
            messages=user_history[user_id],
            max_tokens=500
        )

        reply = response.choices[0].message["content"]

        # добавляем ответ бота в историю
        user_history[user_id].append({"role": "assistant", "content": reply})

        # отправляем ответ
        await message.answer(reply)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

if __name__ == "__main__":
    executor.start_polling(dp)
