import os
import time
import requests
from datetime import datetime, timezone

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TWELVE_DATA_KEY = os.environ["TWELVE_DATA_KEY"]

SYMBOL = "XAU/USD"
INTERVAL = "1min"

last_alert = {
    "M1": None,
    "M5": None
}


def get_candles():
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "outputsize": 10,
        "apikey": TWELVE_DATA_KEY
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    if "values" not in data:
        raise Exception(str(data))

    return data["values"]


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=20
    )


def is_wickless_up(candle):
    o = float(candle["open"])
    l = float(candle["low"])
    c = float(candle["close"])

    # Bullish candle opening at its low
    return c > o and abs(o - l) <= 0.01


def is_wickless_down(candle):
    o = float(candle["open"])
    h = float(candle["high"])
    c = float(candle["close"])

    # Bearish candle opening at its high
    return c < o and abs(o - h) <= 0.01


def check_m1(candle):
    candle_time = candle["datetime"]

    if last_alert["M1"] == candle_time:
        return

    if is_wickless_up(candle):
        message = (
            "🟢 XAUUSD M1 — UP WICKLESS\n\n"
            f"Time: {candle_time}\n"
            f"Open: {candle['open']}\n"
            f"Low: {candle['low']}\n"
            f"Close: {candle['close']}"
        )

        send_telegram(message)
        last_alert["M1"] = candle_time

    elif is_wickless_down(candle):
        message = (
            "🔴 XAUUSD M1 — DOWN WICKLESS\n\n"
            f"Time: {candle_time}\n"
            f"Open: {candle['open']}\n"
            f"High: {candle['high']}\n"
            f"Close: {candle['close']}"
        )

        send_telegram(message)
        last_alert["M1"] = candle_time


def build_m5(candles):
    groups = {}

    for candle in candles:
        dt = datetime.fromisoformat(
            candle["datetime"].replace("Z", "+00:00")
        )

        minute = (dt.minute // 5) * 5

        bucket = dt.replace(
            minute=minute,
            second=0,
            microsecond=0
        )

        groups.setdefault(bucket, []).append(candle)

    completed = []

    for bucket, group in groups.items():
        if len(group) < 5:
            continue

        group = sorted(
            group,
            key=lambda x: x["datetime"]
        )

        completed.append({
            "datetime": bucket.isoformat(),
            "open": group[0]["open"],
            "high": max(float(x["high"]) for x in group),
            "low": min(float(x["low"]) for x in group),
            "close": group[-1]["close"]
        })

    return completed


def check_m5(candle):
    candle_time = candle["datetime"]

    if last_alert["M5"] == candle_time:
        return

    if is_wickless_up(candle):
        message = (
            "🟢 XAUUSD M5 — UP WICKLESS\n\n"
            f"Time: {candle_time}\n"
            f"Open: {candle['open']}\n"
            f"Low: {candle['low']}\n"
            f"Close: {candle['close']}"
        )

        send_telegram(message)
        last_alert["M5"] = candle_time

    elif is_wickless_down(candle):
        message = (
            "🔴 XAUUSD M5 — DOWN WICKLESS\n\n"
            f"Time: {candle_time}\n"
            f"Open: {candle['open']}\n"
            f"High: {candle['high']}\n"
            f"Close: {candle['close']}"
        )

        send_telegram(message)
        last_alert["M5"] = candle_time


def main():
    send_telegram(
        "🤖 XAU WICKLESS BOT STARTED\n\n"
        "🟢 UP alerts: ON\n"
        "🔴 DOWN alerts: ON\n"
        "⏱ M1 + M5: ON"
    )

    while True:
        try:
            candles = get_candles()

            # API normally returns newest first
            candles = sorted(
                candles,
                key=lambda x: x["datetime"]
            )

            # Use the most recently completed 1-minute candle.
            # The newest candle may still be forming.
            if len(candles) >= 2:
                m1 = candles[-2]
                check_m1(m1)

            m5 = build_m5(candles)

            if len(m5) >= 2:
                # Last M5 group can still be forming.
                completed_m5 = m5[-2]
                check_m5(completed_m5)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(60)


if __name__ == "__main__":
    main()
