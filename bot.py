from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8516074866  # <-- BU YERGA O'Z ID INGIZNI YOZING

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Kino bot ishga tushdi!")

# /admin panel
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Siz admin emassiz")
        return

    keyboard = [
        ["📊 Statistika"],
        ["📢 Reklama yuborish"]
    ]
    await update.message.reply_text(
        "👑 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Admin tugmalar
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "📊 Statistika":
        await update.message.reply_text("📊 Foydalanuvchilar: hozircha yo‘q")

    elif text == "📢 Reklama yuborish":
        await update.message.reply_text("📝 Reklama matnini yuboring")
        context.user_data["reklama"] = True

    elif context.user_data.get("reklama"):
        await update.message.reply_text("✅ Reklama yuborildi")
        context.user_data["reklama"] = False

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
