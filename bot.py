import os, requests
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
r = requests.post(url, json={"chat_id": CHAT_ID, "text": "✅ TELEGRAM WORKS! Now fix TwelveData key"})
print(r.text)
