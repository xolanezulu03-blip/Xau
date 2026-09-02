name: XAU Bot Runner
on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - name: Run XAU Wickless Bot
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
          TWELVE_DATA_KEY: ${{ secrets.TWELVE_DATA_KEY }}
        run: |
          pip install requests > /dev/null
          python3 << 'PY'
          import os, requests, datetime
          
          TOKEN = os.getenv("TELEGRAM_TOKEN")
          CHAT = os.getenv("CHAT_ID")
          TD_KEY = os.getenv("TWELVE_DATA_KEY")
          
          def send(msg):
              url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
              requests.post(url, data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=20)
          
          # Get XAU 5min candles
          try:
              url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=20&apikey={TD_KEY}"
              r = requests.get(url, timeout=20).json()
              if "values" not in r:
                  send(f"❌ TwelveData Error: {r}\n\nKey might be wrong. Check key: {TD_KEY[:6]}...")
                  exit(0)
              
              candles = r["values"][::-1]  # oldest to newest
              last = candles[-2]  # last closed
              prev = candles[-3]
              
              open_p = float(last["open"])
              high = float(last["high"])
              low = float(last["low"])
              close = float(last["close"])
              
              body = abs(close - open_p)
              upper_wick = high - max(open_p, close)
              lower_wick = min(open_p, close) - low
              total_range = high - low
              if total_range == 0: total_range = 0.0001
              
              # Wickless strategy logic
              wickless_buy = lower_wick < (body * 0.3) and close > open_p and upper_wick < body
              wickless_sell = upper_wick < (body * 0.3) and close < open_p and lower_wick < body
              
              time_now = datetime.datetime.utcnow().strftime("%H:%M UTC")
              
              if wickless_buy:
                  send(f"🟢 *WICKLESS BUY SIGNAL* 🟢\n\nPair: XAU/USD (Gold)\nTime: {time_now}\nPrice: {close}\nOpen: {open_p}\nStrategy: Wickless Bullish - Small lower wick, strong body\n\n✅ Enter BUY")
              elif wickless_sell:
                  send(f"🔴 *WICKLESS SELL SIGNAL* 🔴\n\nPair: XAU/USD (Gold)\nTime: {time_now}\nPrice: {close}\nOpen: {open_p}\nStrategy: Wickless Bearish - Small upper wick, strong body\n\n✅ Enter SELL")
              else:
                  send(f"⏳ No signal - XAU/USD\nTime: {time_now}\nPrice: {close}\nUpper wick: {upper_wick:.2f}, Lower wick: {lower_wick:.2f}, Body: {body:.2f}\nBot is working and checking every 5min.")
                  
          except Exception as e:
              send(f"⚠️ Bot Error: {str(e)}")
          PY
