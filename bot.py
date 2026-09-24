import os
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("BOT_TOKEN", "").strip()
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0").strip() or "0")
except ValueError:
    ADMIN_ID = 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
DB_FILE = os.path.join(BASE_DIR, "database.db")

os.makedirs(FILES_DIR, exist_ok=True)

# =========================
# DATABASE
# =========================
db = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    name TEXT,
    joined TEXT,
    files INTEGER DEFAULT 0
)
""")
db.commit()


def save_user(user):
    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username, name, joined, files)
        VALUES (?, ?, ?, ?, 0)
        """,
        (
            user.id,
            user.username or "",
            user.first_name or "",
            datetime.now().strftime("%Y-%m-%d"),
        ),
    )

    cursor.execute(
        """
        UPDATE users SET username = ?, name = ?
        WHERE user_id = ?
        """,
        (user.username or "", user.first_name or "", user.id),
    )
    db.commit()


def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤  Upload File", callback_data="upload"),
            InlineKeyboardButton("📁  My Files", callback_data="files"),
        ],
        [
            InlineKeyboardButton("🤖  My Bot", callback_data="mybot"),
            InlineKeyboardButton("📊  Statistics", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("🧬  Host Userbot", callback_data="userbot"),
        ],
        [
            InlineKeyboardButton("⚙️  Settings", callback_data="settings"),
        ],
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️  Back", callback_data="home")]
    ])


def mybot_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("▶️  Start", callback_data="bot_start"),
            InlineKeyboardButton("⏹️  Stop", callback_data="bot_stop"),
        ],
        [
            InlineKeyboardButton("🔄  Restart", callback_data="bot_restart"),
            InlineKeyboardButton("📜  Logs", callback_data="bot_logs"),
        ],
        [
            InlineKeyboardButton("🗑️  Delete", callback_data="bot_delete"),
        ],
        [
            InlineKeyboardButton("◀️  Back", callback_data="home"),
        ],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    await update.message.reply_text(
        "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
        "      𓆩 𝐆𝐎𝐃 𝐈𝐓𝐀𝐂𝐇𝐈 𓆪\n"
        "       𝐅𝐈𝐋𝐄 𝐇𝐎𝐒𝐓𝐈𝐍𝐆\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "✦ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐅𝐈𝐋𝐄 𝐒𝐓𝐎𝐑𝐄\n\n"
        "👤 𝐍𝐀𝐌𝐄      : " + (user.first_name or "Unknown") + "\n"
        "🆔 𝐔𝐒𝐄𝐑 𝐈𝐃   : " + str(user.id) + "\n"
        "🎖 𝐑𝐎𝐋𝐄      : " + ("ADMIN" if user.id == ADMIN_ID and ADMIN_ID != 0 else "USER") + "\n\n"
        "Select an option below:",
        reply_markup=main_menu(),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    save_user(user)

    if query.data == "home":
        await query.edit_message_text(
            "╭━━━━━━━━━━━━━━━━━━━━━━╮\n"
            "      𓆩 𝐆𝐎𝐃 𝐈𝐓𝐀𝐂𝐇𝐈 𓆪\n"
            "       𝐅𝐈𝐋𝐄 𝐇𝐎𝐒𝐓𝐈𝐍𝐆\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "✦ 𝐒𝐄𝐋𝐄𝐂𝐓 𝐀 𝐏𝐀𝐍𝐄𝐋",
            reply_markup=main_menu(),
        )

    elif query.data == "upload":
        await query.edit_message_text(
            "📤 𝐔𝐏𝐋𝐎𝐀𝐃 𝐅𝐈𝐋𝐄\n\n"
            "Send a .py or .zip file here.\n\n"
            "✅ Allowed: .py, .zip",
            reply_markup=back_button(),
        )

    elif query.data == "files":
        user_dir = os.path.join(FILES_DIR, str(user.id))
        files = os.listdir(user_dir) if os.path.exists(user_dir) else []

        if not files:
            text = "📁 𝐌𝐘 𝐅𝐈𝐋𝐄𝐒\n\nNo files uploaded yet."
        else:
            text = "📁 𝐌𝐘 𝐅𝐈𝐋𝐄𝐒\n\n"
            for n, name in enumerate(files, 1):
                text += f"▫️ {n}. `{name}`\n"

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_button(),
        )

    elif query.data == "stats":
        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(files), 0) FROM users")
        files = cursor.fetchone()[0]

        await query.edit_message_text(
            "📊 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒\n\n"
            f"👥 Users       : {users}\n"
            f"📁 Total Files : {files}\n"
            "🟢 Status      : Online",
            reply_markup=back_button(),
        )

    elif query.data == "mybot":
        await query.edit_message_text(
            "🤖 𝐌𝐘 𝐁𝐎𝐓\n\n"
            "Manage your hosted bot from here.",
            reply_markup=mybot_menu(),
        )

    elif query.data == "userbot":
        await query.edit_message_text(
            "🧬 𝐇𝐎𝐒𝐓 𝐔𝐒𝐄𝐑𝐁𝐎𝐓\n\n"
            "Send your supported project file to upload it.\n\n"
            "⚠️ Uploaded code is stored only; this starter version does not "
            "automatically execute arbitrary user code.",
            reply_markup=back_button(),
        )

    elif query.data == "settings":
        await query.edit_message_text(
            "⚙️ 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒\n\n"
            "• File types: .py / .zip\n"
            "• Storage: Local\n"
            "• Execution: Disabled",
            reply_markup=back_button(),
        )

    elif query.data in ("bot_start", "bot_stop", "bot_restart", "bot_logs", "bot_delete"):
        messages = {
            "bot_start": "▶️ Start selected.\n\nNo project is configured yet.",
            "bot_stop": "⏹️ Stop selected.\n\nNo project is currently running.",
            "bot_restart": "🔄 Restart selected.\n\nNo project is configured yet.",
            "bot_logs": "📜 Logs\n\nNo logs available.",
            "bot_delete": "🗑️ Delete selected.\n\nNo hosted project is configured.",
        }

        await query.edit_message_text(
            messages[query.data],
            reply_markup=back_button(),
        )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    document = update.message.document
    filename = document.file_name or "unknown"

    if not filename.lower().endswith((".py", ".zip")):
        await update.message.reply_text(
            "❌ Only .py and .zip files are allowed."
        )
        return

    user_dir = os.path.join(FILES_DIR, str(user.id))
    os.makedirs(user_dir, exist_ok=True)

    safe_name = os.path.basename(filename)
    path = os.path.join(user_dir, safe_name)

    try:
        await update.message.reply_text("⏳ Uploading...")

        tg_file = await document.get_file()
        await tg_file.download_to_drive(path)

        cursor.execute(
            "UPDATE users SET files = files + 1 WHERE user_id = ?",
            (user.id,),
        )
        db.commit()

        await update.message.reply_text(
            f"╭━━━━━━━━━━━━━━━━━━╮\n"
            f"       ✅ 𝐔𝐏𝐋𝐎𝐀𝐃𝐄𝐃\n"
            f"╰━━━━━━━━━━━━━━━━━━╯\n\n"
            f"📄 File : `{safe_name}`\n"
            f"🆔 ID   : `{user.id}`",
            parse_mode="Markdown",
            reply_markup=main_menu(),
        )

    except Exception as error:
        await update.message.reply_text(f"❌ Upload failed:\n{error}")


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID == 0 or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(files), 0) FROM users")
    files = cursor.fetchone()[0]

    await update.message.reply_text(
        "👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋\n\n"
        f"👥 Users : {users}\n"
        f"📁 Files : {files}\n"
        "🟢 Status : ONLINE"
    )


async def error_handler(update, context):
    print("ERROR:", context.error)


def main():
    if not TOKEN:
        print("ERROR: Set BOT_TOKEN in your hosting environment.")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(filters.Document.ALL, receive_file)
    )
    app.add_error_handler(error_handler)

    print("================================")
    print("     GOD ITACHI FILE HOSTING")
    print("     BOT IS RUNNING...")
    print("================================")

    app.run_polling()


if __name__ == "__main__":
    main()
