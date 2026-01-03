# web_ui.py
from flask import Flask
import threading
import os

# 📊 مؤشرات الأداء (مشتركة مع bot.py)
BOT_STATUS = "Starting..."
POSTS_FORWARDED = 0
LAST_MESSAGE = "—"
LAST_ACTIVITY = "—"

app = Flask(__name__)

@app.route('/')
def status():
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📡 حالة البوت</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ font-family: sans-serif; margin: 40px; background: #f5f5f5; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px #ccc; }}
            .status {{ font-size: 1.2em; }}
            .green {{ color: #2e7d32; }}
            .red {{ color: #c62828; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🤖 حالة إعادة النشر</h2>
            <p><strong>الحالة:</strong> <span class="status {'green' if 'متصل' in BOT_STATUS else 'red'}">{BOT_STATUS}</span></p>
            <p><strong>عدد المنشورات المنسوخة:</strong> {POSTS_FORWARDED}</p>
            <p><strong>آخر نشاط:</strong> {LAST_ACTIVITY}</p>
            <p><strong>آخر رسالة:</strong> {LAST_MESSAGE[:100]}...</p>
        </div>
    </body>
    </html>
    '''
    return html

def start_web_ui():
    port = int(os.getenv("PORT", 8000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False)).start()