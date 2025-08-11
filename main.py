import telebot
import openai
import os

# токены — лучше через переменные окружения для безопасности
TELEGRAM_TOKEN = os.getenv("TG_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_KEY") 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        user_text = message.text

        # запрос к openai chat completions (gpt-4)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — дружелюбный ассистент, говоришь просто и понятно."},
                {"role": "user", "content": user_text},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()

        bot.send_message(message.chat.id, answer)
    except Exception as e:
        bot.send_message(message.chat.id, "ошибка, попробуй позже")
        print("Ошибка:", e)

if __name__ == "__main__":
    print("бот запущен")
    bot.infinity_polling()
