import threading
import time
import random
import yfinance as yf
from backend.strategy import should_buy


WATCHLIST = {
    "7203.T": "Toyota",
    "6758.T": "Sony",
    "9984.T": "SoftBank"
}


bot_state = {
    "enabled": False,
    "today_pnl": 0,
    "logs": [],
    "prices": {},
    "holding": None,
    "candidate": "",

    # リスク設定
    "take_profit": 2,
    "stop_loss": -1,

    # 安全装置
    "consecutive_losses": 0,
    "max_losses": 3,
    "daily_limit": -4000
}


def log(msg):
    t = time.strftime("%H:%M:%S")
    bot_state["logs"].insert(0, f"{t} {msg}")
    bot_state["logs"] = bot_state["logs"][:20]


def safety():
    if bot_state["today_pnl"] <= bot_state["daily_limit"]:
        log("🛑 損失上限停止")
        bot_state["enabled"] = False
        return False

    if bot_state["consecutive_losses"] >= bot_state["max_losses"]:
        log("🛑 連敗停止")
        bot_state["enabled"] = False
        return False

    return True


def run_bot():

    prev = {}

    while True:

        if bot_state["enabled"]:

            if not safety():
                time.sleep(5)
                continue

            for code, name in WATCHLIST.items():

                try:
                    df = yf.Ticker(code).history(
                        period="1d",
                        interval="1m"
                    )

                    if df.empty:
                        continue

                    price = round(df["Close"].iloc[-1], 2)

                    bot_state["prices"][code] = {
                        "name": name,
                        "price": price
                    }

                    p0 = prev.get(code, price)

                    if should_buy(price, p0):

                        bot_state["candidate"] = name

                        if bot_state["holding"] is None:
                            bot_state["holding"] = {
                                "name": name,
                                "buy": price
                            }

                            log(f"📥 仮想買い {name}")

                    prev[code] = price

                except:
                    pass

            h = bot_state["holding"]

            if h:

                pnl = random.randint(-300, 600)
                bot_state["today_pnl"] += pnl

                tp = bot_state["take_profit"]
                sl = bot_state["stop_loss"]

                if pnl >= tp * 200:
                    log(f"💰 利確 {pnl}")
                    bot_state["holding"] = None

                elif pnl <= sl * 200:
                    log(f"📉 損切り {pnl}")
                    bot_state["holding"] = None

                if pnl < 0:
                    bot_state["consecutive_losses"] += 1
                else:
                    bot_state["consecutive_losses"] = 0

        time.sleep(5)


threading.Thread(target=run_bot, daemon=True).start()