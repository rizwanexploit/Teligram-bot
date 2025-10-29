#!/usr/bin/env python3
# WhatsAppBot_v6_2.py — Dark Gold Auto Welcome Edition (Public Stats + Personalized Greet)

import re
import json
import asyncio
from pathlib import Path
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ========== CONFIG ==========
TOKEN = "8333618450:AAEt8M-M8TbfgBltndjXYdSCIiienpjBeGM"   # <-- paste your token locally
OWNER_CHAT_ID = 1520382196        # owner id (for /broadcast etc.)
STORE_PATH = Path.home() / "whatsapp_v6_store.json"
RATE_LIMIT_SECONDS = 2.5
DEFAULT_PREFILL_TEMPLATE = "*https://www.instagram.com/rizwan_exploit?igsh=dDE5aGhuejF6YWQ=* 😊 {name}"

# ========== Persistence ==========
def load_store():
    if not STORE_PATH.exists():
        return {"users": {}, "stats": {"requests": 0}}
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"users": {}, "stats": {"requests": 0}}

def save_store(store):
    try:
        STORE_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

store = load_store()

# ========== Helpers ==========
def extract_number(text: str):
    m = re.search(r"(\d{10})$", text.strip())
    return m.group(1) if m else None

def register_user(user):
    uid = str(user.id)
    users = store.setdefault("users", {})
    if uid not in users:
        users[uid] = {"first_name": user.first_name or "", "username": user.username or ""}
        save_store(store)

def increment_requests():
    stats = store.setdefault("stats", {"requests": 0})
    stats["requests"] = stats.get("requests", 0) + 1
    save_store(store)

def is_owner(user_id):
    try:
        return int(user_id) == int(OWNER_CHAT_ID)
    except Exception:
        return False

# runtime rate-limit map
_last_ts = {}

# ========== Handlers ==========

# === START HANDLER (Auto Welcome + Owner Notify) ===
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)

    name = (user.first_name or "User").strip()
    username = f"@{user.username}" if user.username else ""

    welcome_text = (
        f"🌟 *स्वागत है, {name}!* 🌟\n"
        f"{'(' + username + ')' if username else ''}\n\n"
        "🤖 मैं *@rizwan_exploit WhatsApp Bot* हूँ — आपका स्मार्ट लिंक जनरेटर!\n"
        "बस 10-अंकों का मोबाइल नंबर भेजिए और मैं आपका *WhatsApp लिंक* बना दूँगा 🔗\n\n"
        "✨ *क्या कर सकते हैं आप?*\n"
        "• बस कोई नंबर भेजिए 🔢\n"
        "• /stats से users की जानकारी 📊\n"
        "• /help से commands देखिए 🧠\n\n"
        "👇 नीचे से शुरू करें 👇"
    )

    kb = [
        [InlineKeyboardButton("📞 WhatsApp लिंक बनाओ", callback_data="gen")],
        [InlineKeyboardButton("ℹ️ Bot Info", callback_data="about"),
         InlineKeyboardButton("👑 Owner", url="https://t.me/rizwan_exploit")],
        [InlineKeyboardButton("➕ Add To Group", url=f"https://t.me/{context.bot.username}?startgroup=true"),
         InlineKeyboardButton("📊 Stats", callback_data="stats")]
    ]

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

    # Notify owner
    try:
        if user.id != OWNER_CHAT_ID:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=f"🆕 नया यूज़र जुड़ा: *{name}* {username}\n🆔 `{user.id}`",
                parse_mode="Markdown"
            )
    except Exception:
        pass

# === OTHER HANDLERS ===
async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 लिंक बनाओ", callback_data="gen"),
             InlineKeyboardButton("🧠 Help", callback_data="help")],
            [InlineKeyboardButton("👑 Owner", url="https://t.me/rizwan_exploit"),
             InlineKeyboardButton("💬 Support", url="https://www.instagram.com/rizwan_exploit?igsh=dDE5aGhuejF6YWQ=")]
        ])
        text = (
            "🤖 *@rizwan_exploit WhatsApp Link Generator Bot (v6.2)*\n"
            "• Personalized Welcome\n"
            "• Public /stats & /users\n"
            "• Owner Broadcast\n\n"
            "Use /help for commands."
        )
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=buttons)
    else:
        await update.message.reply_text("Use /help or press Bot Info button.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 *Commands:*\n"
        "/start - बॉट शुरू करें\n"
        "/help - यह संदेश\n"
        "/about - बॉट की जानकारी\n"
        "/stats - कुल users (public)\n"
        "/users - registered users (public)\n\n"
        "Owner-only:\n"
        "/broadcast <message> - सभी users को भेजें\n\n"
        "बस 10-अंकों का नंबर भेजें और लिंक मिल जाएगा ✅",
        parse_mode="Markdown"
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data == "gen":
        await q.edit_message_text("📲 कृपया 10-अंकों वाला मोबाइल नंबर भेजिए (उदा: 9876543210).")
    elif data == "about":
        await about_handler(update, context)
    elif data == "help":
        await q.edit_message_text("🧠 Help: बस 10-अंकों का नंबर भेजो (उदा: 993****615).=).", parse_mode="Markdown")
    elif data == "stats":
        total_users = len(store.get("users", {}))
        total_requests = store.get("stats", {}).get("requests", 0)
        await q.edit_message_text(f"📊 *Stats*\n• Users: {total_users}\n• Requests: {total_requests}", parse_mode="Markdown")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    uid = user.id
    register_user(user)

    text = update.message.text.strip()

    # Owner-only broadcast
    if text.startswith("/broadcast"):
        if not is_owner(uid):
            return await update.message.reply_text("❌ सिर्फ owner चला सकता है।")
        parts = text.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            return await update.message.reply_text("उपयोग: /broadcast <message>")
        msg = parts[1].strip()
        await update.message.reply_text("🔔 Broadcast शुरू कर रहा हूँ...")
        await broadcast(msg, context)
        return

    # Public /stats
    if text.strip() == "/stats":
        total_users = len(store.get("users", {}))
        total_requests = store.get("stats", {}).get("requests", 0)
        return await update.message.reply_text(f"📊 *Public Stats*\n• Users: {total_users}\n• Requests: {total_requests}", parse_mode="Markdown")

    # Public /users
    if text.strip() == "/users":
        users = store.get("users", {})
        if not users:
            return await update.message.reply_text("ℹ️ अभी कोई registered user नहीं है।")
        lines = []
        for i, (k, v) in enumerate(list(users.items())[:50], start=1):
            fn = v.get("first_name") or "—"
            lines.append(f"{i}. {fn} (id: {k})")
        return await update.message.reply_text("👥 Registered users:\n" + "\n".join(lines))

    # Rate limit
    import time
    now = time.time()
    last = _last_ts.get(uid, 0)
    if now - last < RATE_LIMIT_SECONDS and not is_owner(uid):
        return await update.message.reply_text(f"⏳ कृपया {RATE_LIMIT_SECONDS} सेकंड बाद कोशिश करें।")
    _last_ts[uid] = now

    # Normal number handling
    number = extract_number(text)
    if number:
        increment_requests()
        full = "91" + number
        name = (user.first_name or "User").strip()
        prefill = DEFAULT_PREFILL_TEMPLATE.format(name=name)
        wa_url = f"https://wa.me/{full}?text=" + quote(prefill)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📞 WhatsApp Chat खोलें", url=wa_url)]])
        await update.message.reply_text(f"✅ WhatsApp लिंक तैयार है: +{full}", reply_markup=kb)
    else:
        await update.message.reply_text("❌ वैध 10-अंकों वाला नंबर भेजें (उदा: 993***1615)।")

# ========== Broadcast Helper ==========
async def broadcast(message: str, context: ContextTypes.DEFAULT_TYPE):
    users = list(store.get("users", {}).keys())
    total = len(users)
    sent = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=message, parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.25)
        except Exception:
            await asyncio.sleep(0.1)
            continue
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"📣 Broadcast Finished.\nTargets: {total}\nSent: {sent}")
    except Exception:
        pass

# ========== Error Handler ==========
async def err_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"⚠️ Error: {context.error}")
    except Exception:
        pass

# ========== Main ==========
def main():
    if not TOKEN or "PASTE_YOUR_TOKEN_HERE" in TOKEN:
        print("⚠️ TOKEN missing — set TOKEN in file before running.")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("about", about_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(err_handler)
    print("✅ WhatsAppBot v6.2 running (Auto Welcome Edition, Public Stats Mode).")
    app.run_polling()

if __name__ == "__main__":
    main()