from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os

# ====== SOZLAMALAR ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8516074866  # <-- SENING ID (O‘ZGARTIRILMAYDI)

CHANNELS = []  # majburiy obuna kanallari

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await check_subscriptions(user_id, context):
        text = "❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n\n"
        text += "\n".join(CHANNELS)
        await update.message.reply_text(text)
        return

    await update.message.reply_text("✅ Xush kelibsiz! Bot ishlayapti.")

# ====== OBUNA TEKSHIRISH ======
async def check_subscriptions(user_id, context):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ====== ADMIN PANEL ======
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        ["➕ Kanal qo‘shish"],
        ["➖ Kanal o‘chirish"],
        ["📋 Kanallar ro‘yxati"]
    ]

    await update.message.reply_text(
        "🔐 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ====== KANAL QO‘SHISH ======
async def add_channel(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    context.user_data["state"] = "add"
    await update.message.reply_text("➕ Kanal username yuboring (@ bilan)")

# ====== KANAL O‘CHIRISH ======
async def remove_channel(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    context.user_data["state"] = "remove"
    await update.message.reply_text("➖ Qaysi kanalni o‘chiramiz? (@ bilan)")

# ====== RO‘YXAT ======
async def list_channels(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    if not CHANNELS:
        await update.message.reply_text("📭 Kanal yo‘q")
    else:
        await update.message.reply_text(
            "📋 Kanallar:\n" + "\n".join(CHANNELS)
        )

# ====== ADMIN ACTIONS ======
async def admin_actions(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text
    state = context.user_data.get("state")

    if text.startswith("@") and state == "add":
        if text not in CHANNELS:
            CHANNELS.append(text)
            await update.message.reply_text(f"✅ Qo‘shildi: {text}")
        context.user_data.clear()

    elif text.startswith("@") and state == "remove":
        if text in CHANNELS:
            CHANNELS.remove(text)
            await update.message.reply_text(f"❌ O‘chirildi: {text}")
        else:
            await update.message.reply_text("⚠️ Bunday kanal yo‘q")
        context.user_data.clear()

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(MessageHandler(filters.Regex("➕ Kanal qo‘shish"), add_channel))
    app.add_handler(MessageHandler(filters.Regex("➖ Kanal o‘chirish"), remove_channel))
    app.add_handler(MessageHandler(filters.Regex("📋 Kanallar ro‘yxati"), list_channels))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_actions))

    app.run_polling()

if __name__ == "__main__":
    main()
