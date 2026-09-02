import os, requests, datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT = os.getenv("CHAT_ID")
TD_KEY = os.getenv("TWELVE_DATA_KEY")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)

try:
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=20&apikey={TD_KEY}"
    r = requests.get(url, timeout=20).json()
    if "values" not in r:
        send(f"❌ TwelveData Error: {r}")
        exit(0)

    candles = r["values"][::-1]
    last = candles[-2]
    
    open_p = float(last["open"])
    high = float(last["high"])
    low = float(last["low"])
    close = float(last["close"])
    
    body = abs(close - open_p)
    upper_wick = high - max(open_p, close)
    lower_wick = min(open_p, close) - low
    
    wickless_buy = lower_wick < (body * 0.3) and close > open_p
    wickless_sell = upper_wick < (body * 0.3) and close < open_p
    
    time_now = datetime.datetime.utcnow().strftime("%H:%M UTC")
    
    if wickless_buy:
        send(f"🟢 *WICKLESS BUY* XAU/USD\nTime: {time_now}\nPrice: {close}\nStrong bullish wickless candle!")
    elif wickless_sell:
        send(f"🔴 *WICKLESS SELL* XAU/USD\nTime: {time_now}\nPrice: {close}\nStrong bearish wickless candle!")
    else:
        send(f"⏳ XAU Check {time_now}\nPrice: {close}\nNo wickless signal yet - bot monitoring every 5min.")
        
except Exception as e:
    send(f"⚠️ Error: {str(e)}")
