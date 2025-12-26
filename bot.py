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
from telegram.request import HTTPXRequest


# ================= CONFIG =================
BOT_TOKEN = "7948885160:AAGbjiBKnFKY0mIjsZ3tkBmDzOk9ONe-BSw"

CHANNEL_1 = "@moviesnseries4k"
CHANNEL_2 = "@GxNS_OFFICIAL"

OWNER_ID = 8512543648      # ONLY ONE OWNER
ADMINS = {OWNER_ID}       # owner is always admin

ACTIVE_CHATS = {}         # user_id -> admin_id
ADMIN_NAMES = {}          # store usernames for /adminlist
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


# =============== /start ==================

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


# ======== VERIFY JOIN BUTTON =========

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


# ========== PROMOTE / DEMOTE / ADMINLIST ==========

async def promote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /promote USER_ID")

    uid = int(context.args[0])
    ADMINS.add(uid)

    await update.message.reply_text(f"⭐ Promoted to admin: `{uid}`", parse_mode="Markdown")


async def demote(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /demote USER_ID")

    uid = int(context.args[0])
    ADMINS.discard(uid)

    await update.message.reply_text(f"⬇️ Demoted: `{uid}`", parse_mode="Markdown")


async def adminlist(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    text = "👑 *Admin List*\n\n"

    for uid in ADMINS:
        username = ADMIN_NAMES.get(uid, "Unknown")
        text += f"• `{uid}` — @{username}\n"

    text += f"\nTotal admins: *{len(ADMINS)}*"

    await update.message.reply_text(text, parse_mode="Markdown")


# ========== CONNECT / DISCONNECT ==========

async def connect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /connect USER_ID")

    user_id = int(context.args[0])
    ACTIVE_CHATS[user_id] = admin

    await update.message.reply_text(f"🔗 Connected to `{user_id}`", parse_mode="Markdown")


async def disconnect(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /disconnect USER_ID")

    user_id = int(context.args[0])

    if user_id in ACTIVE_CHATS:
        del ACTIVE_CHATS[user_id]

    await update.message.reply_text(f"❌ Disconnected from `{user_id}`", parse_mode="Markdown")


# ========== REPLY COMMAND ==========

async def reply(update, context):
    admin = update.effective_user.id
    if admin not in ADMINS:
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /reply USER_ID message")

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])

    await context.bot.send_message(
        chat_id=user_id,
        text=f"💬 *Admin Reply:*\n\n{message}",
        parse_mode="Markdown"
    )


# ========== COMMAND LIST ==========

async def commandlist(update, context):
    await update.message.reply_text(
        "✨ Public Commands (Everyone)\n"
        "/start — Check if the bot is online and running 🚀\n\n"
        "👑 Owner-Only Commands\n"
        "/promote USER_ID — Promote a user to admin ⭐\n"
        "/demote USER_ID — Remove admin rights and set back to user 🔽\n"
        "/adminlist — View the list of all admins 📜\n\n"
        "🛡️ Admin Commands\n"
        "/connect USER_ID — Connect with a user for support 🤝\n"
        "/disconnect USER_ID — End the connection with a user ❌\n"
        "/reply USER_ID message text — Reply to users (alternative reply method 💬)"
    )


# ======= USER → ADMIN FORWARD =======

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
        try:
            msg = update.message
            if msg.text:
                await context.bot.send_message(admin, header + msg.text, parse_mode="Markdown")
            else:
                await msg.copy(admin, caption=header + caption, parse_mode="Markdown")
        except:
            pass


# =============== MAIN ==================

def main():
    request = HTTPXRequest()

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify_join"))

    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("adminlist", adminlist))

    app.add_handler(CommandHandler("connect", connect))
    app.add_handler(CommandHandler("disconnect", disconnect))

    app.add_handler(CommandHandler("reply", reply))

    app.add_handler(CommandHandler("commandlist", commandlist))

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_user))

    print("BOT FILE STARTED")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
