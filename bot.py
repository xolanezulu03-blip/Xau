import os
import requests
import yfinance as yf

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")

def send(m):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": m, "parse_mode": "Markdown"}, timeout=20)

df = yf.download("GC=F", period="1d", interval="1m", auto_adjust=True, progress=False)

if df.empty:
    send("No data")
    exit()

last = df.iloc[-1]
t = df.index[-1]

o = float(last["Open"])
h = float(last["High"])
l = float(last["Low"])
c = float(last["Close"])

body = abs(c-o)
if body < 0.1:
    body = 0.1

up = h - max(o,c)
low = min(o,c) - l

up_pct = up/body*100
low_pct = low/body*100

tm = t.strftime("%H:%M SAST")
info = f"Time:{tm} O:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f} Up:{up_pct:.1f}% Low:{low_pct:.1f}%"

if low_pct < 10 and c > o:
    send(f"BUY {info}")
elif up_pct < 10 and c < o:
    send(f"SELL {info}")
else:
    send(f"No signal {info}")
