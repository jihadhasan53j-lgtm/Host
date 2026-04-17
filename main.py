import os
import requests
from dotenv import load_dotenv

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

CHANNEL = "@devxjihad"

users = set()
bots_created = 0

# ---------------- MENU ---------------- #
menu = ReplyKeyboardMarkup(
    [
        ["📂 Upload", "🤖 My Bots"],
        ["📊 Live Stats"]
    ],
    resize_keyboard=True
)

# ---------------- START ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    users.add(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/devxjihad")],
        [InlineKeyboardButton("✅ I Joined", callback_data="check")]
    ]

    await update.message.reply_text(
        f"👋 Welcome {user}\n\nJoin channel first to use bot:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- CHECK JOIN ---------------- #
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        member = await context.bot.get_chat_member(CHANNEL, query.from_user.id)

        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text("🎉 Join Successful ✅")
            await query.message.reply_text("👇 Main Menu", reply_markup=menu)
        else:
            await query.edit_message_text("❌ Join First")

    except:
        await query.edit_message_text("⚠️ Make bot admin in channel")

# ---------------- GITHUB CREATE REPO ---------------- #
def create_repo(repo_name):
    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "name": repo_name,
        "private": False
    }

    r = requests.post(url, json=data, headers=headers)

    if r.status_code in [200, 201]:
        return r.json()["html_url"]
    return None

# ---------------- HANDLE TEXT ---------------- #
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bots_created

    text = update.message.text
    user_id = update.effective_user.id
    users.add(user_id)

    # 📂 Upload
    if text == "📂 Upload":
        bots_created += 1
        repo = create_repo(f"bot-{user_id}-{bots_created}")

        if repo:
            await update.message.reply_text(
                f"📂 Upload received\n🚀 GitHub Repo Created:\n{repo}"
            )
        else:
            await update.message.reply_text("❌ GitHub error")

    # 🤖 My Bots
    elif text == "🤖 My Bots":
        await update.message.reply_text(
            "🤖 Your Bots:\n\n1️⃣ DemoBot\n2️⃣ HostingBot\n\n(Upgrade needed for DB)"
        )

    # 📊 Live Stats
    elif text == "📊 Live Stats":
        await update.message.reply_text(
            f"📊 LIVE DASHBOARD\n\n"
            f"👥 Users: {len(users)}\n"
            f"🤖 Bots Created: {bots_created}"
        )

    else:
        await update.message.reply_text("Use menu buttons")

# ---------------- MAIN ---------------- #
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
