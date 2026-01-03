# لازم يعمل
import os
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# 🌐 واجهة ويب بسيطة لتتبع الحالة
from flask import Flask, jsonify, render_template_string

# ---------------------- سجل الأحداث ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()

# ---------------------- إعدادات البيئة ----------------------
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
YOUR_USER_ID = int(os.getenv("YOUR_USER_ID", "0"))

try:
    MONITORED_CHATS = eval(os.getenv("MONITORED_CHATS", "[]"))
except:
    MONITORED_CHATS = []

TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

SIGNATURE = "\nالاخبار العاجلة"

# ---------------------- متغيرات الحالة ----------------------
BOT_STATUS = "⚠️ غير متصل"
POSTS_FORWARDED = 0
LAST_MESSAGE = "لا يوجد"
LAST_ACTIVITY = "-"

# ---------------------- العميل ----------------------
from telethon.sessions import StringSession

SESSION_STRING = os.getenv("SESSION_STRING", "")
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    # للتطوير المحلي فقط
    client = TelegramClient("session", API_ID, API_HASH)
# ---------------------- واجهة الويب ----------------------
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<title>حالة البوت</title>
<style>
body { font-family: Tahoma, sans-serif; background: #f4f4f4; color: #333; padding: 20px; }
h1 { color: #0066cc; }
.card { background: #fff; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<h1>حالة البوت</h1>
<div class="card"><strong>الوضع:</strong> {{status}}</div>
<div class="card"><strong>آخر منشور:</strong> {{last_msg}}</div>
<div class="card"><strong>عدد المنشورات المنسوخة:</strong> {{count}}</div>
<div class="card"><strong>آخر نشاط:</strong> {{last_act}}</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        status=BOT_STATUS,
        last_msg=LAST_MESSAGE,
        count=POSTS_FORWARDED,
        last_act=LAST_ACTIVITY
    )

def start_web_ui():
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = ["0.0.0.0:" + os.getenv("PORT", "5000")]
    
    async def serve_flask():
        await serve(app, config)

    asyncio.create_task(serve_flask())
# ---------------------- مراقبة الرسائل ----------------------
@client.on(events.NewMessage(chats=MONITORED_CHATS))
async def copy_all(event):
    global POSTS_FORWARDED, LAST_MESSAGE, LAST_ACTIVITY
    msg = event.message
    text = msg.message or ""
    media = msg.media if isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)) else None

    if not text.strip() and not media:
        return

    try:
        final_text = (text + SIGNATURE).strip()
        chat = await event.get_chat()
        source = getattr(chat, "title", getattr(chat, "username", "Unknown"))

        if not text.strip() and media:
            await client.send_file(
                entity=TARGET_CHANNEL,
                file=media,
                caption=SIGNATURE.strip(),
                parse_mode=None
            )
        else:
            await client.send_message(
                entity=TARGET_CHANNEL,
                message=final_text,
                file=media,
                parse_mode=None,
                link_preview=False
            )

        POSTS_FORWARDED += 1
        LAST_MESSAGE = text[:60] + "…" if len(text) > 60 else text
        LAST_ACTIVITY = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"✅ نُسخ من '{source}'")

    except Exception as e:
        logger.error(f"❌ فشل النسخ: {e}")
        if YOUR_USER_ID:
            try:
                await client.send_message(YOUR_USER_ID, f"⚠️ خطأ: {e}")
            except:
                pass

# ---------------------- التشغيل ----------------------
async def main():
    global BOT_STATUS
    # start_web_ui()  # ← عطّله مؤقتًا
    logger.info("🌐 واجهة الويب معطلة مؤقتًا")

    while True:
        try:
            await client.start(PHONE_NUMBER)
            BOT_STATUS = "✅ متصل ويعمل"
            logger.info(f"🤖 يراقب: {MONITORED_CHATS}")
            await client.run_until_disconnected()
        except Exception as e:
            BOT_STATUS = f"❌ خطأ: {type(e).__name__}"
            logger.error(f"⚠️ انقطاع: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())




