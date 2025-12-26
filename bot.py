from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = "7948885160:AAGbjiBKnFKY0mIjsZ3tkBmDzOk9ONe-BSw"

CHANNEL_1 = "@moviesnseries4k"
CHANNEL_2 = "@GxNS_OFFICIAL"

OWNER_ID = 8512543648
ADMINS = {OWNER_ID}

ACTIVE_CHATS = {}
ADMIN_NAMES = {}
# ==========================================


async def check_membership(app, user_id):
    try:
        m1 = await app.bot.get_chat_member(CHANNEL_1, user_id)
        m2 = await app.bot.get_chat_member(CHANNEL_2, user_id)

        return (
            m1.status in ["member", "administrator", "creator"] and
            m2.status in ["member", "administrator", "creator"]
        )
    except:
        return False


# ================= USER START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ADMIN_NAMES[user.id] = user.username or "NoUsername"

    if await check_membership(context.application, user.id):
        return await update.message.reply_text("🤖 Bot is alive — drop your queries")

    keyboard = [
        [
            InlineKeyboardButton("➤ Join Channel", url="https://t.me/moviesnseries4k"),
            InlineKeyboardButton("➤ Must Join", url="https://t.me/GxNS_OFFICIAL")
        ],
        [InlineKeyboardButton("✅ I Joined", callback_data="verify_join")]
    ]

    await update.message.reply_text(
        "🔔 Please join the channels then click *I Joined* 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= VERIFY JOIN =================
async def verify(update, context):
    q = update.callback_query
    await q.answer()

    if await check_membership(context.application, q.from_user.id):
        return await q.edit_message_text("🎉 Verified! You may now chat.")
    else:
        return await q.edit_message_text("⚠️ Please join ALL channels first.")


# ================= OWNER COMMANDS =================
async def promote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /promote USER_ID")

    uid = int(context.args[0])
    ADMINS.add(uid)

    await update.message.reply_text(f"⭐ Promoted `{uid}`", parse_mode="Markdown")


async def demote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /demote USER_ID")

    uid = int(context.args[0])
    ADMINS.discard(uid)

    await update.message.reply_text(f"⬇️ Demoted `{uid}`", parse_mode="Markdown")


async def adminlist(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    text = "👑 *Admin List*\n\n"
    for uid in ADMINS:
        text += f"• `{uid}`\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# ================= ADMIN CONNECTION =================
async def connect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /connect USER_ID")

    user_id = int(context.args[0])
    ACTIVE_CHATS[user_id] = admin

    await update.message.reply_text(f"🔗 Connected to `{user_id}`", parse_mode="Markdown")


async def disconnect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /disconnect USER_ID")

    user_id = int(context.args[0])
    ACTIVE_CHATS.pop(user_id, None)

    await update.message.reply_text(f"❌ Disconnected `{user_id}`", parse_mode="Markdown")


async def reply(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /reply USER_ID message")

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])

    await context.bot.send_message(user_id, f"💬 Admin Reply:\n\n{message}")


# ================= USER → ADMIN FORWARD =================
async def forward_user(update, context):
    user = update.effective_user

    if not await check_membership(context.application, user.id):
        return

    ADMIN_NAMES[user.id] = user.username or "NoUsername"

    text = update.message.text or ""
    caption = update.message.caption or ""

    info = (
        "📩 *New Query*\n\n"
        f"👤 `{user.first_name}`\n"
        f"🔗 @{user.username or 'None'}\n"
        f"🆔 `{user.id}`\n\n"
    )

    for admin in ADMINS:
        try:
            if text:
                await context.bot.send_message(admin, info + text, parse_mode="Markdown")
            else:
                await update.message.copy(admin, caption=info + caption)
        except:
            pass


# ================= RUN BOT =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify_join"))

    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("adminlist", adminlist))

    app.add_handler(CommandHandler("connect", connect))
    app.add_handler(CommandHandler("disconnect", disconnect))
    app.add_handler(CommandHandler("reply", reply))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_user))

    print("BOT ONLINE")
    app.run_polling()


if __name__ == "__main__":
    main()
