from flask import Flask
import logging
import sys
import os
from datetime import datetime
from datetime import timedelta
import pytz
import pandas as pd
import numpy as np
import requests
from tvDatafeed import TvDatafeed, Interval

app = Flask(__name__)
ist = pytz.timezone('Asia/Kolkata')
tv = TvDatafeed("mekalaganeshreddy796", "Ganesh?!1")

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger(__name__)

logger.info("Application starting at %s", datetime.now(ist))
print("Application starting at", datetime.now(ist))

def is_trading_time():
    now = datetime.now(ist)
    logger.info(f"Checking time: {now}, Weekday: {now.weekday()}, Hour: {now.hour}")
    print(f"Checking time: {now}, Weekday: {now.weekday()}, Hour: {now.hour}")
    if now.weekday() >= 5:
        logger.info("Outside trading: Weekend")
        print("Outside trading: Weekend")
        return False
    is_trading = 9 <= now.hour < 16
    logger.info(f"Is trading time: {is_trading}")
    print(f"Is trading time: {is_trading}")
    return is_trading

def fetch_data_with_retry(symbol, exchange, interval, n_bars, retries=3):
    for attempt in range(retries):
        try:
            data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            if data is not None and not data.empty:
                logger.info(f"Successfully fetched data for {symbol}")
                print(f"Successfully fetched data for {symbol}")
                return data
            logger.warning(f"Attempt {attempt+1}: No data for {symbol}, retrying...")
            print(f"Attempt {attempt+1}: No data for {symbol}, retrying...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Attempt {attempt+1}: Error fetching {symbol}: {e}")
            print(f"Attempt {attempt+1}: Error fetching {symbol}: {e}")
            time.sleep(5)
    logger.error(f"Failed to fetch data for {symbol} after {retries} attempts")
    print(f"Failed to fetch data for {symbol} after {retries} attempts")
    return None

def my_function():
    logger.info("Starting my_function")
    print("Starting my_function")
    try:
        # Fetch data
        length = 100  # Reduced to minimize memory usage
        hdfc = fetch_data_with_retry('HDFCBANK', 'NSE', Interval.in_15_minute, length)
        if hdfc is None:
            logger.error("Aborting my_function: No HDFC data")
            print("Aborting my_function: No HDFC data")
            return
        banknifty = fetch_data_with_retry('NIFTY', 'NSE', Interval.in_15_minute, length)
        if banknifty is None:
            logger.error("Aborting my_function: No BankNIFTY data")
            print("Aborting my_function: No BankNIFTY data")
            return

        # Localize and convert time zones
        banknifty = banknifty.tz_localize('UTC').tz_convert('Asia/Kolkata')
        # logger.info(f"HDFC Data: {hdfc.head()}")
        # print(f"HDFC Data: {hdfc.head()}")
        # logger.info(f"BankNIFTY Data: {banknifty.head()}")
        # print(f"BankNIFTY Data: {banknifty.head()}")

        # Trading logic
        countlimit = length
        taken = 0
        triggered = 0
        total_profit = 0
        total_loss = 0
        net_profit = 0
        current_profit = 0
        countCandles = 0
        flag = True
        eachamount = 7000
        sumofselltobuy = []
        l = []
        g = 0
        d = -1
        reversefalse = False
        #hdfc_close_list = hdfc['close'][g:d].tolist()
        hdfc_open_list = hdfc['open'][g:d].tolist()
        #hdfc_volume_list = hdfc['volume'][g:d].tolist()
        #hdfc_high_list = hdfc['high'][g:d].tolist()
        #hdfc_low_list = hdfc['low'][g:d].tolist()

        hdfc_high_list = hdfc['high'][g:d].tolist()
        hdfc_low_list = hdfc['low'][g:d].tolist()
        hdfc_close_list = banknifty['close'][g:d].tolist()
        
        hhdfc_close_list = hdfc['close'][g:d].tolist()
        hhdfc_open_list = hdfc['open'][g:d].tolist()
        hhdfc_volume_list = hdfc['volume'][g:d].tolist()


        
        banknifty_close_list = banknifty['close'][g:d].tolist()
        banknifty_open_list = banknifty['open'][g:d].tolist()
        banknifty_high_list = banknifty['high'][g:d].tolist()
        banknifty_low_list = banknifty['low'][g:d].tolist()
        banknifty_volume_list = banknifty['volume'][g:d].tolist()
        banknifty_datetime = banknifty.index[g:d].tolist()
        entry_price = None
        position_type = None
        loss_threshold = 20
        reversal_count = 0
        max_reversals = 2
        max_profit_points = 500
        max_loss_points = 150
        k = None
        store = None
        take_profit_pct = 0.01
        entrydate = None
        entrytime = None
        trade_data = []
        demo_trade = []
        j = 0

        for i in range(2, len(hdfc_close_list)):
            current_time = banknifty_datetime[i]
            current_date_str = current_time.strftime("%Y-%m-%d")
            current_time_str = current_time.strftime("%H:%M")
            # logger.info(f"Processing candle {i}: {current_date_str} {current_time_str}")
            # print(f"Processing candle {i}: {current_date_str} {current_time_str}")

            day_of_week = datetime.strptime(current_date_str, "%Y-%m-%d").strftime("%A")
            hour = current_time_str.split(":")[0]

            if current_time_str == "09:15":
                flag = False
            if current_time_str == "15:00":
                if position_type:
                    exit_price = hdfc_close_list[i]
                    if position_type == 'buy':
                        trade_profit = exit_price - entry_price
                    else:
                        trade_profit = entry_price - exit_price
                    if trade_profit >= 0:
                        total_profit += trade_profit
                    else:
                        total_loss += abs(trade_profit)
                    net_profit = total_profit - total_loss
                    s = ((trade_profit) * 100 * 5 / hdfc_close_list[i])
                    l.append(s)
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Exit_Price': exit_price
                    })
                    logger.info(f"Exit trade: {demo_trade[-1]}")
                    print(f"Exit trade: {demo_trade[-1]}")
                    triggered += 1
                    flag = False
                    position_type = None
                    entry_price = None
                    reversal_count = 0
                    current_profit = 0
                continue

            # all_buy = hdfc_close_list[i] > hdfc_open_list[i]
            # all_sell = hdfc_close_list[i] < hdfc_open_list[i]
            # if 1400000 < hdfc_volume_list[i] < 1800000:
            #     flag = True

            all_buy = (
                
                 hhdfc_close_list[i] > hhdfc_open_list[i]
            )
            all_sell = (
               hhdfc_close_list[i] < hhdfc_open_list[i]
            )


            if (hhdfc_volume_list[i])>1400000 and hhdfc_volume_list[i]<3400000:
              flag=True

            if all_buy and flag and position_type != 'buy':
                if position_type == 'sell':
                    exit_price = hdfc_close_list[i]
                    trade_profit = entry_price - exit_price
                    if trade_profit >= 0:
                        total_profit += trade_profit
                    else:
                        total_loss += abs(trade_profit)
                    net_profit = total_profit - total_loss
                    s = ((trade_profit) * 100 / hdfc_close_list[i])
                    l.append(s)
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Exit_Price': exit_price
                    })
                    logger.info(f"Exit trade: {demo_trade[-1]}")
                    print(f"Exit trade: {demo_trade[-1]}")
                    triggered += 1
                    position_type = None
                    entry_price = None
                if current_time_str != "15:00" and current_time_str != "15:15":
                    countlimit = 14
                    countCandles = 0
                    taken += 1
                    entrydate = current_date_str
                    entrytime = current_time_str
                    flag = False
                    position_type = 'buy'
                    reversefalse = False
                    entry_price = hdfc_close_list[i]
                    reversal_count = 0
                    current_profit = 0
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Entry_Price': entry_price
                    })
                    logger.info(f"Entry trade: {demo_trade[-1]}")
                    print(f"Entry trade: {demo_trade[-1]}")

            if all_sell and flag and position_type != 'sell':
                if position_type == 'buy':
                    exit_price = hdfc_close_list[i]
                    trade_profit = exit_price - entry_price
                    if trade_profit >= 0:
                        total_profit += trade_profit
                    else:
                        total_loss += abs(trade_profit)
                    net_profit = total_profit - total_loss
                    s = (trade_profit * 5 * 100 / 1800)
                    l.append(s)
                    eachamount += eachamount * (s / 100)
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Exit_Price': exit_price
                    })
                    logger.info(f"Exit trade: {demo_trade[-1]}")
                    print(f"Exit trade: {demo_trade[-1]}")
                    position_type = None
                    entry_price = None
                    triggered += 1
                if current_time_str != "15:00" and current_time_str != "15:15":
                    countlimit = 13
                    countCandles = 0
                    taken += 1
                    k = banknifty_open_list[i]
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Entry_Price': entry_price
                    })
                    entrydate = current_date_str
                    entrytime = current_time_str
                    reversefalse = False
                    flag = False
                    entry = banknifty_close_list[0]
                    position_type = 'sell'
                    entry_price = hdfc_close_list[i]
                    reversal_count = 0
                    current_profit = 0
                    demo_trade.append({
                        'symbol': 'HDFC',
                        'Date': entrydate,
                        'Position_Type': position_type,
                        'Time': current_time_str,
                        'Entry_Price': entry_price
                    })
                    logger.info(f"Entry trade: {demo_trade[-1]}")
                    print(f"Entry trade: {demo_trade[-1]}")

        if demo_trade:
            last_trade = demo_trade[-1]
            logger.info(f"Last trade: {last_trade}")
            print(f"Last trade: {last_trade}")
            last_trade_time_str = last_trade.get('Time')
            last_trade_date_str = last_trade.get('Date')
            last_trade_datetime = datetime.strptime(f"{last_trade_date_str} {last_trade_time_str}", "%Y-%m-%d %H:%M")
            last_trade_datetime = ist.localize(last_trade_datetime)
            now = datetime.now(ist)
            diff_seconds = (now - last_trade_datetime).total_seconds()
            logger.info(f"Difference in seconds: {diff_seconds}")
            print(f"Difference in seconds: {diff_seconds}")

            if diff_seconds < 1500:  # 2 minutes
            # if 1:
                # 2 minutes
                lasttrade_list = last_trade.keys()
                last_trade['symbol']='NIFTY'
                if 'Entry_Price' in lasttrade_list:
                    bot_token = '7747497929:AAHPFWQ3G-59BtozjVPN4Qqpu4qux4TP-WE'
                    chat_id = '1608202016'
                    message = f"New Entry: {last_trade['symbol']} {last_trade['Position_Type']} at {last_trade['Entry_Price']} on {last_trade['Date']} {last_trade['Time']}"
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
                    params = {'chat_id': chat_id, 'text': message}
                    try:
                        response = requests.get(url, params=params)
                        logger.info(f"Telegram response: {response.json()}")
                        print(f"Telegram response: {response.json()}")
                    except Exception as e:
                        logger.error(f"Failed to send Telegram message: {e}")
                        print(f"Failed to send Telegram message: {e}")
                if 'Exit_Price' in lasttrade_list:
                    bot_token = '7747497929:AAHPFWQ3G-59BtozjVPN4Qqpu4qux4TP-WE'
                    chat_id = '1608202016'
                    message = f"New Exit: {last_trade['symbol']} {last_trade['Position_Type']} at {last_trade['Exit_Price']} on {last_trade['Date']} {last_trade['Time']}"
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
                    params = {'chat_id': chat_id, 'text': message}
                    try:
                        response = requests.get(url, params=params)
                        logger.info(f"Telegram response: {response.json()}")
                        print(f"Telegram response: {response.json()}")
                    except Exception as e:
                        logger.error(f"Failed to send Telegram message: {e}")
                        print(f"Failed to send Telegram message: {e}")
        else:
            logger.info("No trades executed")
            print("No trades executed")

        logger.info("Trading logic completed")
        print("Trading logic completed")

    except Exception as e:
        logger.error(f"Error in my_function: {e}", exc_info=True)
        print(f"Error in my_function: {e}")

@app.route("/")
def home():
    logger.info("Home endpoint accessed")
    print("Home endpoint accessed")
    return "✅ Render alive. Trading runs Mon–Fri, 9AM–4PM via /run-trading."

@app.route("/health")
def health():
    logger.info("Health check accessed")
    print("Health check accessed")
    return "App is running"

@app.route("/test-trading")
def test_trading():
    logger.info("Manual trigger for my_function")
    print("Manual trigger for my_function")
    my_function()
    return "Trading logic triggered"

@app.route("/run-trading")
def run_trading():
    now = datetime.now()
    # Quarter-hour marks
    quarter_hours = [0, 15, 30, 45]

    # Check if current minute is within 0–3 minutes after any quarter hour
    if any(0 <= (now.minute - q) <= 3 for q in quarter_hours):
        logger.info(f"Manual trigger for my_function at {now}")
        print(f"Manual trigger for my_function at {now}")
        my_function()
        return "triggered"
    else:
        print(f"Skipped at {now.minute} minute")
        return "not triggered"


@app.route("/debug-thread")
def debug_thread():
    # No thread exists, but keep for compatibility
    status = {"thread_running": False, "thread_alive": False, "message": "Using scheduled /run-trading endpoint"}
    logger.info(f"Debug status: {status}")
    print(f"Debug status: {status}")
    return status

if __name__ == "__main__":
    logger.info("Starting Flask app")
    print("Starting Flask app")
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
