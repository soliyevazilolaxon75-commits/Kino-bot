import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = # 8516074866 <-- O'Z TELEGRAM ID INGNI YOZ

# Majburiy obuna kanallari
channels = ["@kanal_username"]

movies = {}   # kino_kod : kino_link
users = set()

# ================== MAJBURIY OBUNA TEKSHIRISH ==================
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    for ch in channels:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        buttons = [
            [InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")]
            for ch in channels
        ]
        await update.message.reply_text(
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    users.add(update.effective_user.id)
    await update.message.reply_text("🎬 Kino botga xush kelibsiz!\nKino kodini yuboring")

# ================== ADMIN PANEL ==================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Siz admin emassiz")
        return

    keyboard = [
        ["➕ Kino qo‘shish"],
        ["➕ Kanal qo‘shish", "➖ Kanal o‘chirish"],
        ["📋 Kanallar ro‘yxati"],
        ["📊 Statistika", "📢 Reklama"]
    ]
    await update.message.reply_text(
        "👑 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ================== XABARLAR ==================
async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id

    # ======= ODDIY USER =======
    if uid != ADMIN_ID:
        if text in movies:
            await update.message.reply_text(movies[text])
        else:
            await update.message.reply_text("❌ Bunday kino yo‘q")
        return

    # ======= ADMIN =======
    if text == "➕ Kino qo‘shish":
        context.user_data["add_movie"] = "code"
        await update.message.reply_text("🎬 Kino kodini yuboring")

    elif context.user_data.get("add_movie") == "code":
        context.user_data["movie_code"] = text
        context.user_data["add_movie"] = "link"
        await update.message.reply_text("🔗 Kino linkini yuboring")

    elif context.user_data.get("add_movie") == "link":
        movies[context.user_data["movie_code"]] = text
        context.user_data.clear()
        await update.message.reply_text("✅ Kino qo‘shildi")

    elif text == "➕ Kanal qo‘shish":
        context.user_data["add_channel"] = True
        await update.message.reply_text("➕ Kanal username yuboring (@kanal)")

    elif context.user_data.get("add_channel"):
        if text.startswith("@"):
            channels.append(text)
            context.user_data.clear()
            await update.message.reply_text("✅ Kanal qo‘shildi")
        else:
            await update.message.reply_text("❌ @ bilan boshlanishi kerak")

    elif text == "➖ Kanal o‘chirish":
        context.user_data["remove_channel"] = True
        await update.message.reply_text("➖ O‘chiriladigan kanalni yuboring")

    elif context.user_data.get("remove_channel"):
        if text in channels:
            channels.remove(text)
            await update.message.reply_text("✅ Kanal o‘chirildi")
        else:
            await update.message.reply_text("❌ Kanal topilmadi")
        context.user_data.clear()

    elif text == "📋 Kanallar ro‘yxati":
        await update.message.reply_text("📋 Kanallar:\n" + "\n".join(channels))

    elif text == "📊 Statistika":
        await update.message.reply_text(
            f"👥 Users: {len(users)}\n🎬 Kinolar: {len(movies)}\n📢 Kanallar: {len(channels)}"
        )

    elif text == "📢 Reklama":
        context.user_data["ads"] = True
        await update.message.reply_text("📢 Reklama matnini yuboring")

    elif context.user_data.get("ads"):
        for u in users:
            try:
                await context.bot.send_message(u, text)
            except:
                pass
        context.user_data.clear()
        await update.message.reply_text("✅ Reklama yuborildi")

# ================== MAIN ==================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN topilmadi")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
