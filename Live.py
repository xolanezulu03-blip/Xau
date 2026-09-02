import os, requests
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")

def send(m):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": m}, timeout=20)

try:
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=2"
    r = requests.get(url, timeout=10).json()
    last = r[-1]
    o = float(last[1])
    h = float(last[2])
    l = float(last[3])
    c = float(last[4])
    ms = last[0]
    utc = datetime.fromtimestamp(ms/1000, tz=timezone.utc)
    now = datetime.now(timezone.utc) + timedelta(hours=2)
    candle = utc + timedelta(hours=2)
    rng = h - l
    if rng < 0.01:
        rng = 0.01
    body = abs(c - o)
    if body < 0.01:
        body = 0.01
    up = h - max(o,c)
    low = min(o,c) - l
    up_pct = up/rng*100
    low_pct = low/rng*100
    body_pct = body/rng*100
    now_str = now.strftime("%H:%M:%S")
    candle_str = candle.strftime("%H:%M")
    msg1 = f"NOW:{now_str} SAST"
    msg2 = f"Candle:{candle_str} LIVE"
    msg3 = f"O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}"
    msg4 = f"Up:{up_pct:.1f}% Low:{low_pct:.1f}% Body:{body_pct:.1f}%"
    info = msg1 + "\n" + msg2 + "\n" + msg3 + "\n" + msg4
    if low_pct < 15 and body_pct > 40 and c > o:
        send("BUY LIVE\n" + info)
    elif up_pct < 15 and body_pct > 40 and c < o:
        send("SELL LIVE\n" + info)
    else:
        send("No signal\n" + info)
except Exception as e:
    send(f"Error:{e}")
