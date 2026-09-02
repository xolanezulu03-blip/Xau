import os
import requests
import yfinance as yf
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)

try:
    data = yf.download("GC=F", period="2d", interval="5m", auto_adjust=True)
    if data.empty:
        send("❌ Yahoo empty")
        exit(0)

    data = data.tail(10)
    last = data.iloc[-2]
    prev_close_time = data.index[-2]

    o = float(last["Open"])
    h = float(last["High"])
    l = float(last["Low"])
    c = float(last["Close"])

    body = abs(c - o)
    if body < 0.05:
        body = 0.05
    upper = h - max(o, c)
    lower = min(o, c) - l
    up_pct = (upper / body) * 100
    low_pct = (lower / body) * 100

    buy_wickless = low_pct < 10 and c > o
    sell_wickless = up_pct < 10 and c < o

    utc_dt = prev_close_time.to_pydatetime().replace(tzinfo=timezone.utc)
    exness_str = utc_dt.strftime("%Y-%m-%d %H:%M Exness")
    sa_dt = utc_dt + timedelta(hours=2)
    sa_str = sa_dt.strftime("%Y-%m-%d %H:%M SAST")

    details = f"{exness_str}\n{sa_str}\nO:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}\nUp:{up_pct:.1f}% Low:{low_pct:.1f}%"

    if buy_wickless:
        send(f"🟢 *WICKLESS BUY LIVE*\n{details}")
    elif sell_wickless:
        send(f"🔴 *WICKLESS SELL LIVE*\n{details}")
    else:
        send(f"⏳ No wickless\n{details}")

except Exception as e:
    send(f"⚠️ {e}")
