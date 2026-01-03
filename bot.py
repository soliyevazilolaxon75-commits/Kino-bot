import telebot
import os

# Bu yerga TOKEN yozilmaydi, Railway orqali environment variable qo'shamiz
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎬 Kino botga xush kelibsiz!\nKino kodini yuboring."
    )

# Barcha xabarlar uchun (hozircha test)
@bot.message_handler(func=lambda message: True)
def kino(message):
    bot.send_message(
        message.chat.id,
        f"✅ {message.text} kodi bo‘yicha kino topildi (test)"
    )

# Botni ishga tushirish
bot.infinity_polling()
