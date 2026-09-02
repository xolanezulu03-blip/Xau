import os, requests, yfinance as yf
from datetime import timedelta, timezone

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT, "text": m, "parse_mode": "Markdown"}, timeout=20)

try:
    df = yf.download("GC=F", period="2d", interval="5m", auto_adjust=True, progress=False)
    last = df.iloc[-2]
    t = df.index[-2]
    
    o, h, l, c = float(last["Open"]), float(last["High"]), float(last["Low"]), float(last["Close"])
    body = max(abs(c-o), 0.05)
    up = h - max(o,c)
    low = min(o,c) - l
    up_pct = up/body*100
    low_pct = low/body*100

    utc = t.to_pydatetime().replace(tzinfo=timezone.utc)
    ex = utc.strftime("%H:%M Exness")
    sa = (utc + timedelta(hours=2)).strftime("%H:%M SAST (%Y-%m-%d)")
    
    info = f"{sa} | {ex}\nO:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}\nUp:{up_pct:.1f}% Low:{low_pct:.1f}%"

    if low_pct < 10 and c > o:
        send(f"🟢 *BUY WICKLESS LIVE*\n{info}")
    elif up_pct < 10 and c < o:
        send(f"🔴 *SELL WICKLESS LIVE*\n{info}")
    else:
        send(f"⏳ No signal\n{info}")
except Exception as e:
    send(f"⚠️ {e}")
