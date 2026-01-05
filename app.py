from flask import Flask, request, abort
from datetime import datetime, date
import os
import re

import sqlite3

def init_db():
    conn = sqlite3.connect("baby.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            record_type TEXT,
            value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from db import init_db, get_all_users

app = Flask(__name__)
init_db()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def home():
    return "LINE Baby Bot is running"


@app.route("/daily_push")
def daily_push():
    users = get_all_users()
    today = date.today()

    for user_id, stage, due_date, birth_date in users:
        if stage == "born" and birth_date:
            d = date.fromisoformat(birth_date)
            days = (today - d).days
            msg = f"👶 寶寶今天出生滿 {days} 天囉～"

        elif stage == "pregnant" and due_date:
            d = date.fromisoformat(due_date)
            days = (d - today).days
            msg = f"🤰 距離預產期還有 {days} 天～"

        else:
            continue

        line_bot_api.push_message(user_id, TextSendMessage(text=msg))

    return "ok"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    # ===== 喝奶紀錄 =====
    if text.startswith("喝奶"):
        value = text.replace("喝奶", "").strip()

        conn = sqlite3.connect("baby.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO records (user_id, record_type, value) VALUES (?, ?, ?)",
            (user_id, "feeding", value)
        )
        conn.commit()
        conn.close()

        reply = f"🍼 已紀錄喝奶：{value}"

    # ===== 生日計算（你原本的功能）=====
    else:
        try:
            d = datetime.strptime(text, "%Y-%m-%d").date()
            days = (date.today() - d).days
            reply = f"👶 寶寶今天出生滿 {days} 天了"
        except:
            reply = "請輸入 YYYY-MM-DD，或例如：喝奶 120ml"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )