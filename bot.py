import hashlib
import hmac
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def compute_hash(user_data: dict, token: str) -> str:
    secret = hashlib.sha256(token.encode()).digest()
    check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(user_data.items())
    )
    return hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = {
        "id": str(user.id),
        "first_name": user.first_name,
        "auth_date": str(int(time.time())),
    }
    if user.last_name:
        data["last_name"] = user.last_name
    if user.username:
        data["username"] = user.username

    auth_hash = compute_hash(data, BOT_TOKEN)
    params = "&".join(f"{k}={v}" for k, v in data.items())
    deep_link = f"eidos://auth?{params}&hash={auth_hash}"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Open Eidos App", url=deep_link)
    ]])

    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\nPress the button to sign in to Eidos:",
        reply_markup=keyboard
    )

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
