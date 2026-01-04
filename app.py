from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime
from db import init_db, save_user, get_user
import os
import re

from datetime import date
from db import DB_PATH
import sqlite3

@app.route("/daily_push")
def daily_push():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT line_user_id, stage, due_date, birth_date
        FROM users
    """)
    users = cur.fetchall()
    conn.close()

    today = date.today()

    for user_id, stage, due_date, birth_date in users:
        try:
            if stage == "born" and birth_date:
                d = date.fromisoformat(birth_date)
                days = (today - d).days
                msg = f"👶 寶寶今天出生滿 {days} 天囉～記得多抱抱寶貝唷! 💛"

            elif stage == "pregnant" and due_date:
                d = date.fromisoformat(due_date)
                days = (d - today).days
                msg = f"🤰 距離預產期還有 {days} 天，爸比媽咪加加油～寶貝正在努力長大唷!🌱"

            else:
                continue

            line_bot_api.push_message(
                user_id,
                TextSendMessage(text=msg)
            )

        except Exception as e:
            print("push error:", e)

    return "ok"

app = Flask(__name__)

# ====== LINE 金鑰（用你原本的）======
LINE_CHANNEL_ACCESS_TOKEN = "DPZQZHEyYtLj8CJL0gMDJmvW3fhJg1qPTgBZCkHkcSlPuMaD1Wlcc6kNNlSop6sCXdTZvwEarSAS427KL4yCPGhQSfZ0HJdXpavOjY3ASsYaifjWqYMYapb7Q73CLrylu133S4FXYosVaPNTDWMkyAdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "90c3e574c08026f9a54e3cae10cd9f66"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ====== Webhook ======
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ====== 唯一的訊息處理器（只有一個）======

def daily_push():
    users = get_all_users()
    today = datetime.today().date()

    for user_id, stage, due_date, birth_date in users:
        if stage == "born" and birth_date:
            bd = datetime.strptime(birth_date, "%Y-%m-%d").date()
            days = (today - bd).days
            text = f"👶 寶寶今天出生滿 {days} 天囉～記得多抱抱寶貝唷! ❤️"

        elif stage == "pregnant" and due_date:
            dd = datetime.strptime(due_date, "%Y-%m-%d").date()
            left = (dd - today).days
            text = f"🤰 距離預產期還有 {left} 天，爸比媽咪加加油～寶貝正在努力長大唷!"

        else:
            continue

        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=text)
        )
@handler.add(MessageEvent, message=TextMessage)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    try:
        # 情況 1：設定生日 2025-01-02
        if user_text.startswith("設定生日"):
            birthday_str = user_text.replace("設定生日", "").strip()

        # 情況 2：只輸入 2025-01-02
        elif re.match(date_pattern, user_text):
            birthday_str = user_text

        else:
            raise ValueError("格式不正確")

        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        days = (today - birthday).days

        reply_text = f"👶 寶寶今天出生滿 {days} 天了"

    except:
        reply_text = "請輸入：設定生日 YYYY-MM-DD\n或直接輸入：YYYY-MM-DD"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# ====== 啟動 ======
if __name__ == "__main__":
    app.run(port=5000)

    daily_push()