import os, requests, datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")
TD_KEY = os.getenv("TWELVE_DATA_KEY")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)

try:
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=5&apikey={TD_KEY}"
    r = requests.get(url, timeout=20).json()
    if "values" not in r:
        send(f"❌ API Error: {r}"); exit(0)

    candles = r["values"][::-1]
    last_closed = candles[-2]

    o = float(last_closed["open"])
    h = float(last_closed["high"])
    l = float(last_closed["low"])
    c = float(last_closed["close"])
    td_time_str = last_closed["datetime"]

    body = abs(c - o)
    if body < 0.05: body = 0.05
    upper = h - max(o,c)
    lower = min(o,c) - l
    upper_pct = (upper/body)*100
    lower_pct = (lower/body)*100

    # STRICT Exness wickless
    buy_wickless = lower_pct < 10 and c > o
    sell_wickless = upper_pct < 10 and c < o

    utc_dt = datetime.datetime.strptime(td_time_str, "%Y-%m-%d %H:%M:%S")
    exness_time = utc_dt.strftime("%H:%M") # Exness = GMT+0 = UTC
    sa_time = (utc_dt + datetime.timedelta(hours=2)).strftime("%H:%M SAST")

    details = f"Exness {exness_time} | SA {sa_time}\nO:{o:.2f} H:{h:.2f} L:{l:.2f} C:{c:.2f}\nUp:{upper_pct:.1f}% Low:{lower_pct:.1f}%"

    if buy_wickless:
        send(f"🟢 *WICKLESS BUY - EXNESS*\n{details}\nPrice: {c}")
    elif sell_wickless:
        send(f"🔴 *WICKLESS SELL - EXNESS*\n{details}\nPrice: {c}")
    else:
        send(f"⏳ No wickless\n{details}")

except Exception as e:
    send(f"⚠️ {e}")
