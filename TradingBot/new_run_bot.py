# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
import mysql.connector
import datetime
import time
import ccxt
import numpy as np

db_conn = mysql.connector.Connect(host='localhost', user='cso', password='Royal616@', database='trading_bot')
query_conn = db_conn.cursor(buffered=True)

def run_bot_thread(mutex_object=None, period_in_seconds=60, bot_level="enthusiast"):
    t_list = []
    while True:
        v = str(datetime.datetime.now())
        h1 = v[11:13]
        n1 = v[14:16]
        s1 = v[17:19]
        current_time = 3600 * int(h1) + 60 * int(n1) + int(s1)
        num1 = divmod(current_time, period_in_seconds)
        num2 = divmod(num1[1], 5)
        if num2[1] == 0:
            t_list.append(num1[1])
            if not mutex_object.locked():
                t = str(t_list[0])
                t_list.pop(0)
                run_bot(bot_level, t, mutex_object)

def add_price_table(exchange="binance"):
    ## API Key and Secret Key
    api = ""
    secret = ""
    exchange_obj = None
    if exchange == "binance":
        exchange_obj = ccxt.binance({
            'proxies': {
                'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
            },
            'apiKey': api,
            'secret': secret,
        })
        cur_data = exchange_obj.fetch_ticker(coin_pair)
        bid_price = float(cur_data['info']['bidPrice'])
        ask_price = float(cur_data['info']['askPrice'])
        cur_time = cur_data['timestamp']
    elif exchange == "cryptopia":
        exchange_obj = ccxt.cryptopia({
            'proxies': {
                'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
            },
            'apiKey': api,
            'secret': secret,
        })
        cur_data = exchange_obj.fetch_ticker(coin_pair)
        bid_price = float(cur_data['info']['BidPrice'])
        ask_price = float(cur_data['info']['AskPrice'])
        cur_time = cur_data['timestamp']
    elif exchange == "bittrex":
        exchange_obj = ccxt.bittrex({
            'proxies': {
                'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
            },
            'apiKey': api,
            'secret': secret,
        })
        cur_data = exchange_obj.fetch_ticker(coin_pair)
        bid_price = float(cur_data['info']['Bid'])
        ask_price = float(cur_data['info']['Ask'])
        cur_time = cur_data['timestamp']
    elif exchange == "hitbtc":
        exchange_obj = ccxt.hitbtc2({
            'proxies': {
                'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
            },
            'apiKey': api,
            'secret': secret,
        })
        cur_data = exchange_obj.fetch_ticker(coin_pair)
        bid_price = float(cur_data['info']['bid'])
        ask_price = float(cur_data['info']['ask'])
        cur_time = cur_data['timestamp']
    else:
        print ("Unsupported Exchange platform")
        return


def run_bot(bot_level, run_time, mutex_object):
    mutex_object.acquire()

    run_table = 'run_' + bot_level + '_bot'
    sql_query = "select bot_id from %s where run_time=%s" % (run_table, run_time)
    query_conn.execute(sql_query)
    records = query_conn.fetchall()
    temp = str(records[0][0])

    bot_id_list = temp.split(",")
    db_conn.commit()

    for bot_iterator in bot_id_list:
        if bot_iterator != "":
            query_conn.execute("select * from bot where absID=%s", (bot_iterator,))
            bot = query_conn.fetchone()
            db_conn.commit()

            bot_kind = bot[3]
            exchange = str(bot[6])
            if bot_kind == "Indicator BB Bot":
                run_Indicator_BB_bot(bot, exchange)
            elif bot_kind == "Indicator MACD Bot":
                run_Indicator_MACD_bot(bot, exchange)
            elif bot_kind == "Indicator RSI Bot":
                run_Indicator_RSI_bot(bot, exchange)
    mutex_object.release()
    return True

def run_Indicator_BB_bot(bot, exchange="binance"):
    # Bot parmeters
    user_id = bot[5]
    interval = bot[35]
    can_interval = get_candle_interval(interval)
    bot_id = str(bot[0])
    bot_name = str(bot[1])
    bot_type = str(bot[2])
    base_currency = str(bot[8])
    selected_coin = str(bot[9])
    coin_pair = selected_coin + "/" + base_currency
    buy_higher = str(bot[11])
    sell_cheaper = str(bot[12])
    profit = float(bot[15])
    stop_loss = float(bot[16])
    stay_profitable = str(bot[14])
    double_fee = str(bot[13])
    trading_volume = float(bot[10])
    period = int(bot[29])
    upper_dev = float(bot[30])
    lower_dev = float(bot[31])

    # Declare local variables
    indicator_profit = 0.0
    sum_plus = 0.0
    sum_minus = 0.0

    coin_balance = 0.0
    base_balance = 0.0

    last_buy_price = 0.0
    last_sell_price = 0.0
    bid_price = 0.0
    ask_price = 0.0

    temp_data = []
    value_dif = []
    hist_data = []
    cur_data = []
    total_balance = []

    middle_price = 0.0  # average value corresponding the p
    upper_price = 0.0
    lower_price = 0.0
    bb_temp = []
    avg = 0
    stand_dev = 0.0
    bb_index = 0 # not used?
    cur_time = ""

    order_type = ""
    order_status = ""
    buy_time = ""
    sell_time = ""
    buy_price = 0.0
    sell_price = 0.0
    buy_fee = 0.0
    sell_fee = 0.0

    log_str = ""

    # Get API key and secret key
    query_conn.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s", (user_id, exchange))
    key_data = query_conn.fetchone()
    api = key_data[0]
    secret = key_data[1]
    db_conn.commit()

def run_Indicator_RSI_bot(bot, exchange="binance"):
    return
def run_Indicator_MACD_bot(bot, exchange="binance"):
    return

def get_candle_interval(interval):
    can_interval = ""  # interval for candle
    if interval == "1s":
        can_interval = 1000
    elif interval == "1m":
        can_interval = 60000
    elif interval == "5m":
        can_interval = 300000
    elif interval == "15m":
        can_interval = 900000
    elif interval == "30m":
        can_interval = 1800000
    elif interval == "1h":
        can_interval = 3600000
    elif interval == "2h":
        can_interval = 7200000
    elif interval == "4h":
        can_interval = 14400000
    elif interval == "1d":
        can_interval == 86400000
    return can_interval

run_bot_thread(threading.Lock(), 60)

add_price_table()