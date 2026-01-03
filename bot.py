import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== SOZLAMALAR ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8516074866  # <-- SENING TELEGRAM ID

# Majburiy obuna kanali (o'zingnikiga almashtir)
CHANNELS = ["@kanal_username"]

users = set()

# ================== MAJBURIY OBUNA ==================

async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ================== /start ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        await update.message.reply_text(
            "❌ Botdan foydalanish uchun kanalga obuna bo‘ling:\n"
            + "\n".join(CHANNELS)
        )
        return

    users.add(update.effective_user.id)
    await update.message.reply_text("🤖 Kino bot ishga tushdi!")

# ================== ADMIN PANEL ==================

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

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "📊 Statistika":
        await update.message.reply_text(f"👥 Foydalanuvchilar soni: {len(users)}")

    elif text == "📢 Reklama yuborish":
        await update.message.reply_text("📝 Reklama matnini yuboring")
        context.user_data["reklama"] = True

    elif context.user_data.get("reklama"):
        for user_id in users:
            try:
                await context.bot.send_message(user_id, text)
            except:
                pass

        await update.message.reply_text("✅ Reklama yuborildi")
        context.user_data["reklama"] = False

# ================== MAIN ==================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
