from flask import Flask, request, abort
from datetime import datetime, date
import os
import re

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

    try:
        d = datetime.strptime(text, "%Y-%m-%d").date()
        days = (date.today() - d).days
        reply = f"👶 寶寶今天出生滿 {days} 天了"
    except:
        reply = "請輸入 YYYY-MM-DD"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )