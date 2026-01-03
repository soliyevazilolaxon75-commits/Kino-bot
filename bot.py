from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8516074866  # 👈 admin id

# Majburiy obuna kanallari (boshlanishida 1 ta)
channels = ["@kanalingiz"]

users = set()
movies = {}

# 🔐 Kanal tekshirish
async def check_sub(update):
    for ch in channels:
        try:
            member = await update.bot.get_chat_member(ch, update.effective_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update):
        buttons = [
            [InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch[1:]}")]
            for ch in channels
        ]
        await update.message.reply_text(
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    users.add(update.effective_user.id)
    await update.message.reply_text("🎬 Kino botga xush kelibsiz!\nKino kodini yuboring")

# 👑 Admin panel
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Siz admin emassiz")
        return

    keyboard = [
        ["➕ Kanal qo‘shish", "➖ Kanal o‘chirish"],
        ["📋 Kanallar ro‘yxati"],
        ["➕ Kino qo‘shish", "📊 Statistika"],
        ["📢 Reklama yuborish"]
    ]
    await update.message.reply_text(
        "👑 Admin panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Admin amallar
async def admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # 👤 Oddiy user
    if uid != ADMIN_ID:
        if text in movies:
            await update.message.reply_text(movies[text])
        else:
            await update.message.reply_text("❌ Bunday kino yo‘q")
        return

    # 👑 Admin
    if text == "➕ Kanal qo‘shish":
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
        await update.message.reply_text(
            "📋 Majburiy kanallar:\n" + "\n".join(channels)
        )

    elif text == "➕ Kino qo‘shish":
        context.user_data["add_movie"] = True
        await update.message.reply_text("🎬 Kino kodini yuboring")

    elif context.user_data.get("add_movie"):
        context.user_data["movie_code"] = text
        context.user_data["add_movie"] = "link"
        await update.message.reply_text("🔗 Kino linkini yuboring")

    elif context.user_data.get("add_movie") == "link":
        movies[context.user_data["movie_code"]] = text
        context.user_data.clear()
        await update.message.reply_text("✅ Kino saqlandi")

    elif text == "📊 Statistika":
        await update.message.reply_text(
            f"👥 Users: {len(users)}\n🎞 Kinolar: {len(movies)}\n📢 Kanallar: {len(channels)}"
        )

    elif text == "📢 Reklama yuborish":
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

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_actions))

    app.run_polling()

if __name__ == "__main__":
    main()
