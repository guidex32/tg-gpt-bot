import telebot
import openai
import os
import traceback
import sys

# Загружаем токены
TELEGRAM_TOKEN = os.getenv("TG_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_KEY")

if not TELEGRAM_TOKEN:
    print("Ошибка: переменная окружения TG_TOKEN не найдена")
    sys.exit(1)
if not OPENAI_API_KEY:
    print("Ошибка: переменная окружения OPENAI_KEY не найдена")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Память для каждого пользователя
user_histories = {}  # {user_id: [{"role": "...", "content": "..."}]}

def add_to_history(user_id, role, content):
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": role, "content": content})
    # ограничиваем историю до 10 последних сообщений
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]

# Обработка текста
@bot.message_handler(content_types=["text"])
def handle_text(message):
    try:
        user_id = message.from_user.id
        user_text = message.text

        # добавляем сообщение пользователя в память
        add_to_history(user_id, "user", user_text)

        # формируем историю с системным промптом
        messages = [{"role": "system", "content": "Ты — дружелюбный ассистент, говоришь просто и понятно."}]
        messages.extend(user_histories[user_id])

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        answer = response.choices[0].message.content.strip()

        # сохраняем ответ в память
        add_to_history(user_id, "assistant", answer)

        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, "ошибка, попробуй позже")
        print("Ошибка при обработке текста:", e)
        traceback.print_exc()

# Обработка фото
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"

        user_id = message.from_user.id
        add_to_history(user_id, "user", f"[Пользователь отправил фото]({file_url})")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — ассистент, который может описывать и анализировать изображения."},
                {"role": "user", "content": f"Опиши, что на этом фото: {file_url}"}
            ],
            max_tokens=500,
        )

        answer = response.choices[0].message.content.strip()
        add_to_history(user_id, "assistant", answer)

        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, "ошибка при обработке фото")
        print("Ошибка при обработке фото:", e)
        traceback.print_exc()

if __name__ == "__main__":
    print("бот запущен")
    bot.infinity_polling()
