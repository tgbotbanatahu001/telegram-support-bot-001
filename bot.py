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
            m1.status in ["member", "administrator", "creator"]
            and
            m2.status in ["member", "administrator", "creator"]
        )
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ADMIN_NAMES[user.id] = user.username or "NoUsername"

    joined = await check_membership(context.application, user.id)

    if joined:
        return await update.message.reply_text("🤖 Bot is alive — drop your queries")

    keyboard = [
        [
            InlineKeyboardButton("➤ Join Channel", url="https://t.me/moviesnseries4k"),
            InlineKeyboardButton("➤ Must Join", url="https://t.me/GxNS_OFFICIAL")
        ],
        [
            InlineKeyboardButton("✅ I Joined", callback_data="verify_join")
        ]
    ]

    await update.message.reply_text(
        "🔔 Please join the channels to connect with admins\n\n"
        "After joining, click *I Joined* 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def verify(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    joined = await check_membership(context.application, user_id)

    if joined:
        await query.edit_message_text(
            "🎉 Successfully verified!\n\n"
            "You are now free to drop your queries here — admins will reply soon 💬"
        )
    else:
        await query.edit_message_text(
            "⚠️ Please join *ALL* channels first",
            parse_mode="Markdown"
        )


async def promote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    uid = int(context.args[0])
    ADMINS.add(uid)

    await update.message.reply_text(f"⭐ Promoted `{uid}`", parse_mode="Markdown")


async def demote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    uid = int(context.args[0])
    ADMINS.discard(uid)

    await update.message.reply_text(f"⬇️ Demoted `{uid}`", parse_mode="Markdown")


async def adminlist(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    text = "👑 *Admin List*\n\n"
    for uid in ADMINS:
        username = ADMIN_NAMES.get(uid, "Unknown")
        text += f"• `{uid}` — @{username}\n"

    text += f"\nTotal admins: *{len(ADMINS)}*"

    await update.message.reply_text(text, parse_mode="Markdown")


async def connect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    user_id = int(context.args[0])
    ACTIVE_CHATS[user_id] = admin

    await update.message.reply_text(f"🔗 Connected `{user_id}`")


async def disconnect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    user_id = int(context.args[0])
    ACTIVE_CHATS.pop(user_id, None)

    await update.message.reply_text(f"❌ Disconnected `{user_id}`")


async def reply(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])

    await context.bot.send_message(user_id, f"💬 Admin Reply:\n\n{message}")


async def forward_user(update, context):
    user = update.effective_user
    ADMIN_NAMES[user.id] = user.username or "NoUsername"

    if not await check_membership(context.application, user.id):
        return

    caption = update.message.caption or ""
    header = (
        "📩 *New Query*\n\n"
        f"👤 `{user.first_name or ''}`\n"
        f"🔗 @{user.username or 'None'}\n"
        f"🆔 `{user.id}`\n\n"
    )

    for admin in ADMINS:
        msg = update.message
        if msg.text:
            await context.bot.send_message(admin, header + msg.text, parse_mode="Markdown")
        else:
            await msg.copy(admin, caption=header + caption, parse_mode="Markdown")


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

    print("BOT FILE STARTED")
    app.run_polling()


if __name__ == "__main__":
    main()
