import os, requests, datetime
TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT=os.getenv("CHAT_ID")
def send(m):
 url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
 requests.post(url,data={"chat_id":CHAT,"text":m},timeout=20)
try:
 d=requests.get("https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=5m&limit=1",timeout=10).json()[0]
 o=float(d[1]);h=float(d[2]);l=float(d[3]);c=float(d[4])
 now=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=2)
 rng=h-l
 if rng<0.01:
  rng=0.01
 body=abs(c-o)
 if body<0.01:
  body=0.01
 up=h-max(o,c);low=min(o,c)-l
 up_p=up/rng*100;low_p=low/rng*100;body_p=body/rng*100
 t=now.strftime("%H:%M:%S")
 info=f"TIME:{t} SAST LIVE\nO:{o} H:{h} L:{l} C:{c}\nUp:{up_p:.0f}% Low:{low_p:.0f}%"
 if low_p<15 and body_p>40 and c>o:
  send("BUY LIVE\n"+info)
 elif up_p<15 and body_p>40 and c<o:
  send("SELL LIVE\n"+info)
 else:
  send("No signal\n"+info)
except Exception as e:
 send(f"Error {e}")
