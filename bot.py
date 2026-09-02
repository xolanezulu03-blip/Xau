import os
import requests
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TWELVE_KEY = os.getenv("TWELVE_DATA_KEY")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def get_gold():
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVE_KEY}"
        r = requests.get(url, timeout=10).json()
        price = float(r["price"])
        return price
    except:
        return None

price = get_gold()
if price:
    send_telegram(f"✅ BOT TEST WORKING!\n\nXAUUSD Price: ${price}\n\nIf you see this, bot is LIVE and will send signals every 5 minutes.")
    print(f"Sent price {price}")
else:
    send_telegram("⚠️ Bot running but TwelveData failed - check API key")
    print("Price failed")
