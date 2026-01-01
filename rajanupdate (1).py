
# Multi-bot GC / Slide / Swipe tool (updated TOKENS & OWNER)
# - Spawns one Application per token and registers command handlers on each.
# - Commands available: /gcnc, /ncemo, /stopgcnc, /stopall, /delay, /status,
#   /targetslide, /stopslide, /slidespam, /stopslidespam, /swipe, /stopswipe,
#   /spamloop, /stopspam, /emospam, /stopemospam, /replytext, /stopreplytext,
#   /voice, /stopvoice, /addsudo, /delsudo, /listsudo, /myid, /ping, /help
#
# NOTE: These tokens are sensitive. If they are real, revoke/rotate them after testing.

import asyncio
import json
import os
import random
import time
import logging
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import error as telegram_error
from gtts import gTTS
import io

# ---------------------------
# CONFIG (UPDATED)
# ---------------------------
TOKENS = [
   "8573637179:AAGCSunvJ2ImXo91uiZMsL8qYosalHbxG8g",
"8568640757:AAGnx23gXlyYtyANpfFR6QUTe1XBh7aGo0k",
"8132064693:AAFbzGudnXFAhVAYBu4Nr3AL6IyGPVRSCCw",
"8573986079:AAEIihNgDJOPBHUv6aYrIWR3xzrGVUt6tQ0",
"8233444972:AAFIHE5gM5QM6hB9TlSqVhnczdADd1G6jPE",
"8218342121:AAFIxqyLP9CrWsVnTwlOo9yEwhsRraqqh5E",
"8495037330:AAGoJZlDq02bDxa5Vw3g9mr5O2-Sp-gI7vE",
]

# Owner / initial sudo (you provided "Chat id 6416341860")
OWNER_ID = 7261954726
SUDO_FILE = "sudo.json"

# ---------------------------
# RAID TEXTS & EMOJIS
# ---------------------------
RAID_TEXTS = [
    "×~🌷1🌷×~",
    "~×🌼2🌼×~",
    "××🌻3🌻××",
    "~~🌺4🌺~~",
    "~×🌹5🌹×~",
    "×~🏵️6🏵️×~",
    "~×🪷7🪷×~",
    "××💮8💮××",
    "~~🌸9🌸~~",
    "~×🌷10🌷×~",
    "×~🌼11🌼×~",
    "~×🌻12🌻×~",
    "××🌺13🌺××",
    "~~🌹14🌹~~",
    "~×🏵️15🏵️×~",
    "×~🪷16🪷×~",
    "~×💮17💮×~",
    "××🌸18🌸××",
    "~~🌷19🌷~~",
    "~×🌼20🌼×~",
    "×~🌻21🌻×~",
    "~×🌺22🌺×~",
    "××🌹23🌹××",
    "~~🏵️24🏵️~~",
    "~×🪷25🪷×~",
    "×~💮26💮×~",
    "~×🌸27🌸×~",
    "××🌷28🌷××",
    "~~🌼29🌼~~",
    "~×🌻30🌻×~",
    "×~🌺31🌺×~",
    "~×🌹32🌹×~",
    "××🏵️33🏵️××",
    "~~🪷34🪷~~",
    "~×💮35💮×~",
    "×~🌸36🌸×~",
    "~×🌷37🌷×~",
    "××🌼38🌼××",
    "~~🌻39🌻~~",
    "~×🌺40🌺×~",
    "×~🌹41🌹×~",
    "~×🏵️42🏵️×~",
    "××🪷43🪷××",
    "~~💮44💮~~",
    "~×🌸45🌸×~",
    "×~🌷46🌷×~",
    "~×🌼47🌼×~",
    "××🌻48🌻××",
    "~~🌺49🌺~~",
    "~×🌹50🌹×~",
    "×~🏵️51🏵️×~",
    "~×🪷52🪷×~",
    "××💮53💮××",
    "~~🌸54🌸~~",
    "~×🌷55🌷×~",
    "×~🌼56🌼×~",
    "~×🌻57🌻×~",
    "××🌺58🌺××",
    "~~🌹59🌹~~",
    "~×🏵️60🏵️×~"
]

NCEMO_EMOJIS = [
    "🌷1🌷",
    "🌼2🌼",
    "🌻3🌻",
    "🌺4🌺",
    "🌹5🌹",
    "🏵️6🏵️",
    "🪷7🪷",
    "💮8💮",
    "🌸9🌸",
    "🌷10🌷",
    "🌼11🌼",
    "🌻12🌻",
    "🌺13🌺",
    "🌹14🌹",
    "🏵️15🏵️",
    "🪷16🪷",
    "💮17💮",
    "🌸18🌸",
    "🌷19🌷",
    "🌼20🌼",
    "🌻21🌻",
    "🌺22🌺",
    "🌹23🌹",
    "🏵️24🏵️",
    "🪷25🪷",
    "💮26💮",
    "🌸27🌸",
    "🌷28🌷",
    "🌼29🌼",
    "🌻30🌻",
    "🌺31🌺",
    "🌹32🌹",
    "🏵️33🏵️",
    "🪷34🪷",
    "💮35💮",
    "🌸36🌸",
    "🌷37🌷",
    "🌼38🌼",
    "🌻39🌻",
    "🌺40🌺",
    "🌹41🌹"
]

EMOSPAM_PATTERNS = [
    "[ any text ] 1-//--🩷" * 40,
    "[ any text ] l --🦋" * 40,
    "[ any text ]k-//--💗" * 40,
    "[ any text ] l - 🤍" * 40
]

SPAM_PATTERNS = EMOSPAM_PATTERNS  # For spamloop

VOICE_BYTES = []

emospam_tasks: Dict[int, asyncio.Task] = {}
voice_tasks: Dict[int, asyncio.Task] = {}


# ---------------------------
# GLOBAL STATE
# ---------------------------
# load or initialize SUDO users
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r", encoding="utf-8") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}
with open(SUDO_FILE, "w", encoding="utf-8") as f:
    json.dump(list(SUDO_USERS), f)

def save_sudo():
    with open(SUDO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(SUDO_USERS), f)

# Per-chat group tasks: chat_id -> dict[token_key -> task]
group_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
spam_tasks: Dict[int, asyncio.Task] = {}
slide_targets = set()
slidespam_targets = set()
swipe_mode = {}
replytext_mode = {}
replytext_counter = {}
apps, bots = [], []
delay = 0.5

logging.basicConfig(level=logging.INFO)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            return await update.message.reply_text("❌𝐒ᴏʀʀʏ 🇧 🇧 🇾  𝐀ᴘ 𝐆ᴀʀʀᴇʙ 𝐇ᴏ.")
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID:
            return await update.message.reply_text("❌ LOFI KO ABBU BOL.")
        return await func(update, context)
    return wrapper

# ---------------------------
# BOT LOOP used by gcnc/ncemo
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    # Find bot index to use different RAID text patterns
    bot_index = None
    for idx, token in enumerate(TOKENS):
        if bot.token == token:
            bot_index = idx
            break
    if bot_index is None:
        bot_index = 0  # fallback

    i = 0
    while True:
        try:
            if mode == "raid":
                # Each bot uses RAID texts with different wrapper patterns
                if bot_index % 5 == 0:
                    # Bot 0,5,10,... uses ×~ pattern
                    bot_raid_texts = [t for t in RAID_TEXTS if t.startswith("×~")]
                elif bot_index % 5 == 1:
                    # Bot 1,6,11,... uses ~× pattern
                    bot_raid_texts = [t for t in RAID_TEXTS if t.startswith("~×")]
                elif bot_index % 5 == 2:
                    # Bot 2,7,12,... uses ×× pattern
                    bot_raid_texts = [t for t in RAID_TEXTS if t.startswith("××")]
                elif bot_index % 5 == 3:
                    # Bot 3,8,13,... uses ~~ pattern
                    bot_raid_texts = [t for t in RAID_TEXTS if t.startswith("~~")]
                else:
                    # Bot 4,9,14,... uses remaining patterns
                    bot_raid_texts = [t for t in RAID_TEXTS if not (t.startswith("×~") or t.startswith("~×") or t.startswith("××") or t.startswith("~~"))]

                if bot_raid_texts:
                    text = f"{base} {bot_raid_texts[i % len(bot_raid_texts)]}"
                else:
                    text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"  # fallback
            else:
                text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(delay)
        except telegram_error.RetryAfter as e:
            # No sleep - continue immediately
            pass
        except Exception as e:
            # No sleep - continue instantly even on errors
            pass

async def spam_loop(update, text):
    chat_id = update.message.chat_id
    i = 0
    while True:
        try:
            spam_pattern = SPAM_PATTERNS[i % len(SPAM_PATTERNS)]
            spam_text = spam_pattern.replace("[ text ]", text).replace("[ Text ]", text).replace("[ any text ]", text)
            await update.message.reply_text(spam_text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            await asyncio.sleep(0.001)

async def voice_loop(update, text):
    chat_id = update.message.chat_id
    while True:
        try:
            tts = gTTS(text=text, lang='en')
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            await update.message.reply_voice(voice=audio_bytes)
            await asyncio.sleep(delay)
        except telegram_error.RetryAfter as e:
            # No sleep - continue immediately
            pass
        except Exception as e:
            # No sleep - continue instantly even on errors
            pass

# ---------------------------
# COMMANDS
# ---------------------------
@only_owner
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💗 Welcome to lofi Bot!\nUse /help to see all commands.")

@only_owner
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ lofi BOT MENU ✨\n\n"
        "🎪 Group Decorations:\n"
        "/ncloop <text> - Continuous group name cycling\n"
        "/ncemo <text> - Emoji group name cycling\n"
        "/stopgcnc - Stop name decoration\n"
        "/stopall - Stop all decorations\n"
        "/delay <sec> - Set loop speed (0 for ultra-fast)\n"
        "/status - Check active loops\n\n"
        "🎤 Voice Attacks:\n"
        "/targetslide (reply) - Voice flood target user\n"
        "/stopslide (reply) - Stop voice flood\n"
        "/slidespam (reply) - Continuous voice spam\n"
        "/stopslidespam (reply) - Stop voice spam\n"
        "/swipe <name> - Voice flood entire chat\n"
        "/stopswipe - Stop chat voice flood\n\n"
        "💬 Text Attacks:\n"
        "/spamloop <text> - Continuous text pattern spam\n"
        "/stopspam - Stop text spam\n"
        "/emospam <text> - Emoji pattern spam\n"
        "/stopemospam - Stop emoji spam\n"
        "/replytext <text> - Reply to every message with text + RAID texts\n"
        "/stopreplytext - Stop reply text mode\n\n"
        "🎵 Custom Voice:\n"
        "/voice <text> - Continuous voice message loop\n"
        "/stopvoice - Stop voice loop\n\n"
        "👑 Admin:\n"
        "/addsudo (reply) - Add sudo user\n"
        "/delsudo (reply) - Remove sudo user\n"
        "/listsudo - List sudo users\n\n"
        "🛠 Info:\n"
        "/myid - Your Telegram ID\n"
        "/ping - Test bot speed\n"
        "/help - Show this menu"
    )

@only_owner
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    latency = int((end_time - start_time) * 1000)
    await msg.edit_text(f"🏓 Pong! ✅ {latency} ms")

@only_owner
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

@only_owner
async def voice_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /voice <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in voice_tasks:
        voice_tasks[chat_id].cancel()
    task = asyncio.create_task(voice_loop(update, text))
    voice_tasks[chat_id] = task
    await update.message.reply_text(f"🎤 Voice loop started with text: {text}")

@only_owner
async def stopvoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in voice_tasks:
        voice_tasks[chat_id].cancel()
        del voice_tasks[chat_id]
        await update.message.reply_text("🛑 Voice loop stopped.")
    else:
        await update.message.reply_text("❌ No voice loop running.")

# --- GC Loops ---
@only_owner
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gcnc <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raid"))
            group_tasks[chat_id][key] = task
    await update.message.reply_text("🔄चुदाई suru hua.")

@only_owner
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "emoji"))
            group_tasks[chat_id][key] = task
    await update.message.reply_text("🔄 Emoji loop started with all bots.")

@only_owner
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
        await update.message.reply_text("⏹ Loop stopped in this GC.")

@only_owner
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(group_tasks.keys()):
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
    await update.message.reply_text("⏹ All loops stopped.")

@only_owner
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args: return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = float(context.args[0])
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except: await update.message.reply_text("⚠️ Invalid number.")

@only_owner
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Active Loops:\n"
    for chat_id, tasks in group_tasks.items():
        msg += f"Chat {chat_id}: {len(tasks)} bots running\n"
    await update.message.reply_text(msg)

# --- SUDO ---
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid); save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid); save_sudo()
            await update.message.reply_text(f"🗑 {uid} removed from sudo.")

@only_owner
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 SUDO USERS:\n" + "\n".join(map(str, SUDO_USERS)))

# --- Slide / Spam / Swipe ---
@only_owner
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slide_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🎯 Target slide added.")

@only_owner
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slide_targets.discard(uid)
        await update.message.reply_text("🛑 Target slide stopped.")

@only_owner
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("💥 Slide spam started.")

@only_owner
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.discard(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🛑 Slide spam stopped.")

@only_owner
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /swipe <name>")
    swipe_mode[update.message.chat_id] = " ".join(context.args)
    await update.message.reply_text(f"⚡ Swipe mode ON with name: {swipe_mode[update.message.chat_id]}")

@only_owner
async def stopswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    swipe_mode.pop(update.message.chat_id, None)
    await update.message.reply_text("🛑 Swipe mode stopped.")

# --- Nonstop Spam ---
@only_owner
async def spamloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /spamloop <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
    task = asyncio.create_task(spam_loop(update, text))
    spam_tasks[chat_id] = task
    await update.message.reply_text("🔄 चुदाई suru hua spam loop.")

@only_owner
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
        spam_tasks.pop(chat_id)
        await update.message.reply_text("🛑 Spam stopped.")
    else:
        await update.message.reply_text("❌ No spam running.")

async def emospam_loop(update, text):
    chat_id = update.message.chat_id
    i = 0
    while True:
        try:
            pattern = EMOSPAM_PATTERNS[i % len(EMOSPAM_PATTERNS)]
            emo_text = pattern.replace("[ any text ]", text).replace("[ text ]", text).replace("[ Text ]", text)
            await update.message.reply_text(emo_text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            await asyncio.sleep(0.001)

@only_owner
async def emospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /emospam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
    task = asyncio.create_task(emospam_loop(update, text))
    emospam_tasks[chat_id] = task
    await update.message.reply_text("🎯 Emoji spam started!")

@only_owner
async def stopemospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
        emospam_tasks.pop(chat_id)
        await update.message.reply_text("🛑 Emoji spam stopped.")
    else:
        await update.message.reply_text("❌ No emoji spam running.")

@only_owner
async def replytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /replytext <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    replytext_mode[chat_id] = base
    replytext_counter[chat_id] = 0
    await update.message.reply_text(f"🔄 Reply text mode enabled with base: '{base}'. Will reply to every message with '{base} + RAID texts'.")

@only_owner
async def stopreplytext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in replytext_mode:
        replytext_mode.pop(chat_id)
        replytext_counter.pop(chat_id, None)
        await update.message.reply_text("🛑 Reply text mode stopped.")
    else:
        await update.message.reply_text("❌ Reply text mode not active.")

# --- Auto Replies ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid, chat_id = update.message.from_user.id, update.message.chat_id
    if uid in slide_targets:
        tasks = [update.message.reply_voice(voice=VOICE_BYTES[i]) for i in range(len(RAID_TEXTS))]
        await asyncio.gather(*tasks)
    if uid in slidespam_targets:
        tasks = [update.message.reply_voice(voice=VOICE_BYTES[i]) for i in range(len(RAID_TEXTS))]
        await asyncio.gather(*tasks)
    if chat_id in swipe_mode:
        tasks = []
        for text in RAID_TEXTS:
            full_text = f"{swipe_mode[chat_id]} {text}"
            tts = gTTS(text=full_text, lang='en')
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            tasks.append(update.message.reply_voice(voice=audio_bytes))
        await asyncio.gather(*tasks)
    if chat_id in replytext_mode:
        base = replytext_mode[chat_id]
        counter = replytext_counter.get(chat_id, 0)
        text = f"{base} {RAID_TEXTS[counter % len(RAID_TEXTS)]}"
        await update.message.reply_text(text)
        replytext_counter[chat_id] = counter + 1

# ---------------------------
# BUILD APP & RUN
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("voice", voice_cmd))
    app.add_handler(CommandHandler("stopvoice", stopvoice))
    app.add_handler(CommandHandler("ncloop", gcnc))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))
    app.add_handler(CommandHandler("targetslide", targetslide))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("slidespam", slidespam))
    app.add_handler(CommandHandler("stopslidespam", stopslidespam))
    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("stopswipe", stopswipe))
    app.add_handler(CommandHandler("spamloop", spamloop))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("emospam", emospam))
    app.add_handler(CommandHandler("stopemospam", stopemospam))
    app.add_handler(CommandHandler("replytext", replytext))
    app.add_handler(CommandHandler("stopreplytext", stopreplytext))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    return app

async def generate_voices():
    global VOICE_BYTES
    for i, text in enumerate(RAID_TEXTS):
        tts = gTTS(text=text, lang='en')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        VOICE_BYTES.append(audio_bytes.getvalue())

async def run_all_bots():
    global apps, bots
    await generate_voices()
    # deduplicate tokens while preserving order
    seen = set(); unique_tokens = []
    for t in TOKENS:
        if t and t not in seen:
            seen.add(t); unique_tokens.append(t)

    for token in unique_tokens:
        try:
            app = build_app(token)
            apps.append(app)
            # app.bot may not be fully initialized until app.start(); keep reference from app after start
            bots.append(app.bot)
        except Exception as e:
            print("Failed building app:", e)

    # initialize & start apps
    for app in apps:
        try:
            await app.initialize(); await app.start(); await app.updater.start_polling()
            await asyncio.sleep(1)  # Delay to avoid conflicts between bots
        except Exception as e:
            print("Failed starting app:", e)

    print("🚀 lofi Bot is running (all bots started).")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user (Ctrl+C)")
    finally:
        loop.close()