import os
import requests
import yfinance as yf
from datetime import timedelta, timezone

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)

try:
    data = yf.download("GC=F", period="2d", interval="5m", auto_adjust=True, progress=False)
    if data.empty or len(data) < 3:
        send("❌ Yahoo empty")
        exit(0)

    last = data.iloc[-2]
    prev_time = data.index[-2]

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

    buy = low_pct < 10 and c > o
    sell = up_pct < 10 and c < o

    utc_dt = prev_time.to_pydatetime().replace(tzinfo=timezone.utc)
    exness = utc_dt.strftime("%Y-%m-%d %H:%M Exness")
    sa = (utc_dt + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M SAST")

    det = f"{exness}\n{sa}\nO:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}\nUp:{up_pct:.1f}% Low:{low_pct:.1f}%"

    if buy:
        send(f"🟢 *WICKLESS BUY LIVE*\n{det}")
    elif sell:
        send(f"🔴 *WICKLESS SELL LIVE*\n{det}")
    else:
        send(f"⏳ No wickless\n{det}")

except Exception as e:
    send(f"⚠️ {e}")
