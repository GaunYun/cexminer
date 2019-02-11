# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
import mysql.connector
import datetime
#import time
import ccxt
import numpy as np

mutex1 = threading.Lock()   # for newbie bot
mutex2 = threading.Lock()   # for adopter bot
mutex3 = threading.Lock()   # for enthusiast bot

#######################
## bot_kind: {newbie, adpoter, enthusiast}, string value
## period_in_seconds: interval value calculated in seconds, integer value
## mutex_object: Thread Mutex for 3 kind of bots, here is 3 mutex defined for now, mutex1, mutex2, mutex3, should be able to create without limitation
#######################
def run_bot_thread(period_in_seconds=60, bot_kind="newbie", mutex_object=None):
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
                if bot_kind == "newbie":
                    run_newbie_bot(t)
                elif bot_kind == "adpoter":
                    run_adopter_bot(t)
                elif bot_kind == "enthusiast":
                    run_enthusiast_bot(t)
                else:
                    print("### Invalid bot kind in running bot threads ####")

def run_enthusiast_bot(run_time):
    mutex1.acquire()
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    c.execute("select bot_id from run_enthusiast_bot where run_time=%s", (run_time,))
    l1 = c.fetchall()
    l2 = str(l1[0][0])
    bot_id_list = l2.split(",")
    conn.commit()
    #print(run_time)
    for b1 in bot_id_list:
        if b1 != "":
            c.execute("select * from bot where absID=%s", (b1,))
            bot = c.fetchone()
            conn.commit()
            bot_kind = bot[3]
            user_id = bot[5]
            interval = bot[35]
            interval1 = ""
            if interval == "1m":
                interval1 = 60000
            if interval == "5m":
                interval1 = 300000
            elif interval == "15m":
                interval1 = 900000
            elif interval == "30m":
                interval1 = 1800000
            elif interval == "1h":
                interval1 = 3600000
            elif interval == "2h":
                interval1 = 7200000
            elif interval == "4h":
                interval1 = 14400000
            elif interval == "1d":
                interval1 == 86400000
            # date_to = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(n1), int(s1))
            # date_from = datetime.datetime(int(y2), int(m2), int(d2), int(h2), int(n2), int(s2))
            # print(date_from)
            # print(date_to)
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
            indicator_profit = 0
            sum_plus = 0
            sum_minus = 0
            fee = 0.0
            exchange_fee = []
            temp_data = []
            value_dif = []
            last_buy_price = 0
            last_sell_price = 0
            chart_data = []
            now_data = []
            coin_balance = 0
            conn.commit()
            if bot_kind == "Indicator RSI Bot":
                exchange = str(bot[6])
                rsi_top = float(bot[24])
                rsi_bottom = float(bot[25])
                rsi_length = int(bot[23])
                rsi_value = 0
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,

                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("rsi data")
                        print(chart_data)
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        print("rsi value")
                        print(rsi_value)
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data) - rsi_length - 1, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > (len(chart_data) - rsi_length - 1):
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == (len(chart_data) - 1):
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(len(chart_data) - rsi_length, len(chart_data) + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append(
                            [str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator MACD Bot":
                exchange = str(bot[6])
                macd_long = int(bot[26])
                macd_short = int(bot[27])
                macd_signal = int(bot[28])
                long_k = 0
                short_k = 0
                macd_long_data = []
                macd_short_data = []
                macd_data = []
                macd_signal_data = []
                temp_data1 = 0
                compare_data = []
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long + macd_signal - 1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - macd_signal + 1, i + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0,len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - len(chart_data) + 2, macd_signal-len(chart_data)+i+1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[macd_signal-len(chart_data)+i+1], float(temp_data1 / macd_signal)])
                        print("macd value")
                        print(compare_data)
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*(macd_long+macd_signal), limit=macd_long + macd_signal - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long+macd_signal-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        print(compare_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator BB Bot":
                middle_data = 0
                upper_data = 0
                lower_data = 0
                bb_temp = []
                ave = 0
                sd = 0
                bb_index = 0
                period = int(bot[29])
                upper = float(bot[30])
                lower = float(bot[31])
                exchange = str(bot[6])
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if bot_type =="Demo":
                        c.execute(
                            "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                            (bot_id, 'buy', 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            print(bot_type)
                            if bid_price >= upper_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                          bid_price, 'maker')
                                fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                                last_buy_price = d1[0][0]
                                last_sell_price = 0
                                bb_trading_condition(bot_id, 'Demo', 'upper', bid_price, last_buy_price,
                                                     last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                     double_fee, fee, t1)
                        else:
                            chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            if ask_price <= lower_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                          ask_price, 'maker')
                                fee = float(ask_price) * float(exchange_fee['rate']) * float(trading_volume)
                                c.execute(
                                    "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc",
                                    (bot_id,))
                                d2 = c.fetchall()
                                last_buy_price = 0
                                if len(d2) > 0:
                                    last_sell_price = d2[0][0]
                                else:
                                    last_sell_price = 0
                                conn.commit()
                                bb_trading_condition(bot_id, bot_type, 'lower', ask_price, last_buy_price, last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                     fee, t1)
                    if bot_type == "Live":
                        c.execute(
                            "select order_type, buy_price, sell_price from trading_history where bot_id=%s and order_status=%s",
                            (bot_id, 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            order_type = d1[0][0]
                            if order_type == "buy":
                                print("sell select coin wiht 1")
                                chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(bid_price)
                                print(upper_data)
                                #log_file = open('bot_log.txt', 'w')
                                total_balance = exchange_obj.fetch_balance()
                                with open("bot_log.txt", "a") as log_file:
                                    log_file.write(
                                        str(t1) + ': ' + 'compare: sell with buy ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n')
                                #log_file.close()
                                if bid_price >= upper_data:
                                    coin_balance = float(total_balance[selected_coin]['total'])
                                    print(str(coin_balance))

                                    if coin_balance >= trading_volume * 0.95:
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  coin_balance,
                                                                                  bid_price, 'maker')
                                        fee = round(float(bid_price) * float(exchange_fee['rate']), 8)
                                        last_buy_price = d1[0][0]
                                        last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price,
                                                                          buy_higher, sell_cheaper, coin_balance,
                                                                          stay_profitable,
                                                                          double_fee, fee, t1)
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'parameter: sell with buy ' + coin_pair + '(e_price=' + str(
                                                    bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')

                                        #print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_sell_order(coin_pair, coin_balance)
                                            print("sell")
                                            print(t1)
                                            print(bid_price)
                                            print(coin_balance)
                                            #log_file = open('bot_log.txt', 'w')
                                            with open("bot_log.txt", "a") as log_file:
                                                log_file.write(
                                                    str(t1) + ': ' + 'Sell ' + coin_pair + '(sell_price=' + str(bid_price) + ', bot_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')
                                            #log_file.close()
                            if order_type == "sell":
                                print("buy seletc coin with 1")
                                chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(ask_price)
                                print(lower_data)
                                #log_file = open('bot_log.txt', 'w')
                                total_balance = exchange_obj.fetch_balance()
                                with open("bot_log.txt", "a") as log_file:
                                    log_file.write(
                                        str(t1) + ': ' + 'compare: buy with sell ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n')
                                #log_file.close()
                                if ask_price <= lower_data:
                                    coin_balance = float(total_balance[base_currency]['total'])
                                    print(str(coin_balance))

                                    if coin_balance >= 0.95 * trading_volume*ask_price:
                                        trading_volume = float(coin_balance/ask_price)
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                                  trading_volume,
                                                                                  ask_price, 'maker')
                                        fee = round(float(ask_price) * float(exchange_fee['rate']), 8)
                                        #c.execute(
                                        #    "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        #    (bot_id,))
                                        #d2 = c.fetchall()
                                        #conn.commit()
                                        last_buy_price = 0
                                        last_sell_price = ask_price
                                        #if len(d2) > 0:
                                        #    last_sell_price = d2[0][0]
                                        #else:
                                        #    last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price, last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper, trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'parameter: buy with sell ' + coin_pair + '(e_price=' +
                                                str(ask_price) + ', bb_price=' + str(lower_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')

                                        #print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                                            print("buy")
                                            print(t1)
                                            print(ask_price)
                                            print(trading_volume)
                                            #log_file = open('bot_log.txt', 'w')
                                            with open("bot_log.txt", "a") as log_file:
                                                log_file.write(
                                                    str(t1) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')
                                            #log_file.close()
                                    else:
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'buy with sell, insufficient balance ' + coin_pair + '\n')

                        else:
                            total_balance = exchange_obj.fetch_balance()
                            coin_balance = float(total_balance[base_currency]['total'])
                            if coin_balance >= trading_volume * ask_price:
                                print("buy select coin with 0")
                                print(str(coin_balance))

                                chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(ask_price)
                                print(lower_data)
                                #log_file = open('bot_log.txt', 'w')
                                with open("bot_log.txt", "a") as log_file:
                                    log_file.write(str(t1) + ': ' + 'compare: buy without none ' + coin_pair + '(e_price=' +str(ask_price)+', bb_price='+str(lower_data)+', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n')
                                #log_file.close()
                                if ask_price <= lower_data:
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume,
                                                                              ask_price, 'maker')
                                    fee = round(float(ask_price) * float(exchange_fee['rate']), 8)
                                    trading_volume = float(coin_balance/ask_price)
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        (bot_id,))
                                    d2 = c.fetchall()
                                    conn.commit()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price,
                                                                      last_buy_price,
                                                                      last_sell_price, buy_higher, sell_cheaper,
                                                                      trading_volume,
                                                                      stay_profitable, double_fee, fee, t1)
                                    with open("bot_log.txt", "a") as log_file:
                                        log_file.write(str(t1) + ': ' + 'parameter :buy without none ' + coin_pair + '(e_price=' + str(
                                            ask_price) + ', bb_price=' + str(lower_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')
                                    #print(result_str)
                                    if result_str == "open":
                                        exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                                        print("buy")
                                        print(t1)
                                        print(ask_price)
                                        print(trading_volume)
                                        #log_file = open('bot_log.txt', 'w')
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')
                                        #log_file.close()
                            else:
                                print("sell select coin with 0")
                                coin_balance = float(total_balance[selected_coin]['total'])
                                print(str(coin_balance))
                                if coin_balance >= trading_volume:
                                    chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                    for i in range(0, period):
                                        bb_temp.append(chart_data[i][4])
                                    ave = np.mean(bb_temp)
                                    sd = np.std(bb_temp)
                                    middle_data = ave
                                    upper_data = round(ave + sd * upper, 8)
                                    lower_data = round(ave + sd * lower, 8)
                                    print(bid_price)
                                    print(upper_data)
                                    #log_file = open('bot_log.txt', 'w')
                                    with open("bot_log.txt", "a") as log_file:
                                        log_file.write(
                                            str(t1) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n')
                                    #log_file.close()
                                    if bid_price >= upper_data:

                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = round(float(bid_price) * float(exchange_fee['rate']), 8)
                                        last_sell_price = 0
                                        last_buy_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper,
                                                                          trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')

                                        #print(result_str)
                                        if result_str == "open":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                                            print("sell")
                                            print(t1)
                                            print(bid_price)
                                            print(trading_volume)
                                            #log_file = open('bot_log.txt', 'w')
                                            with open("bot_log.txt", "a") as log_file:
                                                log_file.write(
                                                    str(t1) + ': ' + 'Sell ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee='+ str(fee) +')\n')
                                            #log_file.close()
                                elif coin_balance >= 0.95*trading_volume:
                                    trading_volume = coin_balance
                                    chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                    for i in range(0, period):
                                        bb_temp.append(chart_data[i][4])
                                    ave = np.mean(bb_temp)
                                    sd = np.std(bb_temp)
                                    middle_data = ave
                                    upper_data = round(ave + sd * upper, 8)
                                    lower_data = round(ave + sd * lower, 8)
                                    print(bid_price)
                                    print(upper_data)
                                    # log_file = open('bot_log.txt', 'w')
                                    with open("bot_log.txt", "a") as log_file:
                                        log_file.write(
                                            str(t1) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' +
                                            str(bid_price) + ', bb_price=' + str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n')
                                    # log_file.close()
                                    if bid_price >= upper_data:
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = round(float(bid_price) * float(exchange_fee['rate']), 8)
                                        last_sell_price = 0
                                        last_buy_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper,
                                                                          trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        with open("bot_log.txt", "a") as log_file:
                                            log_file.write(
                                                str(t1) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' +
                                                str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee=' + str(fee) + ')\n')

                                        # print(result_str)
                                        if result_str == "open":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                                            print("sell")
                                            print(t1)
                                            print(bid_price)
                                            print(trading_volume)
                                            # log_file = open('bot_log.txt', 'w')
                                            with open("bot_log.txt", "a") as log_file:
                                                log_file.write(
                                                    str(t1) + ': ' + 'Sell ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' +
                                                    str(upper_data) + ', bb_u_dev='+str(upper)+', bb_l_dev='+str(lower)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', fee=' + str(fee) + ')\n')
                                                # log_file.close()
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data)-period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(len(chart_data) - period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*period, limit=period - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("bb data")
                        print(chart_data)
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        print("bb value")
                        print(lower_data)
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price, buy_higher,
                                                 sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if bot_type =="Demo":
                        c.execute(
                            "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                            (bot_id, 'buy', 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            print(bot_type)
                            if bid_price >= upper_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                          bid_price, 'maker')
                                fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                                last_buy_price = d1[0][0]
                                last_sell_price = 0
                                bb_trading_condition(bot_id, 'Demo', 'upper', bid_price, last_buy_price,
                                                     last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                     double_fee, fee, t1)
                        else:
                            chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            if ask_price <= lower_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                          ask_price, 'maker')
                                fee = float(ask_price) * float(exchange_fee['rate']) * float(trading_volume)
                                c.execute(
                                    "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc",
                                    (bot_id,))
                                d2 = c.fetchall()
                                last_buy_price = 0
                                if len(d2) > 0:
                                    last_sell_price = d2[0][0]
                                else:
                                    last_sell_price = 0
                                conn.commit()
                                bb_trading_condition(bot_id, bot_type, 'lower', ask_price, last_buy_price, last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                     fee, t1)
                    if bot_type == "Live":
                        c.execute(
                            "select order_type, buy_price, sell_price from trading_history where bot_id=%s and order_status=%s",
                            (bot_id, 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            order_type = d1[0][0]
                            if order_type == "buy":
                                print("sell select coin wiht 1")
                                chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(bid_price)
                                print(upper_data)
                                if bid_price >= upper_data:
                                    total_balance = exchange_obj.fetch_balance()
                                    coin_balance = float(total_balance[selected_coin]['total'])
                                    print(str(coin_balance))

                                    if coin_balance >= trading_volume:
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = round(float(bid_price) * float(exchange_fee['rate']), 8)
                                        last_buy_price = d1[0][0]
                                        last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price,
                                                                          buy_higher, sell_cheaper, trading_volume,
                                                                          stay_profitable,
                                                                          double_fee, fee, t1)
                                        #print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                                            print("sell")
                                            print(t1)
                                            print(bid_price)
                                            print(trading_volume)
                            if order_type == "sell":
                                print("buy seletc coin with 1")
                                chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(ask_price)
                                print(lower_data)
                                if ask_price <= lower_data:
                                    total_balance = exchange_obj.fetch_balance()
                                    coin_balance = float(total_balance[base_currency]['total'])
                                    print(str(coin_balance))

                                    if coin_balance >= trading_volume*ask_price:
                                        trading_volume = float(coin_balance/ask_price)
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                                  trading_volume,
                                                                                  ask_price, 'maker')
                                        fee = round(float(ask_price) * float(exchange_fee['rate']), 8)
                                        #c.execute(
                                        #    "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        #    (bot_id,))
                                        #d2 = c.fetchall()
                                        #conn.commit()
                                        last_buy_price = 0
                                        last_sell_price = ask_price
                                        #if len(d2) > 0:
                                        #    last_sell_price = d2[0][0]
                                        #else:
                                        #    last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price, last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper, trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        #print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                                            print("buy")
                                            print(t1)
                                            print(ask_price)
                                            print(trading_volume)
                        else:
                            total_balance = exchange_obj.fetch_balance()
                            coin_balance = float(total_balance[base_currency]['total'])
                            if coin_balance >= trading_volume * ask_price:
                                print("buy select coin with 0")
                                print(str(coin_balance))

                                chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = round(ave + sd * upper, 8)
                                lower_data = round(ave + sd * lower, 8)
                                print(ask_price)
                                print(lower_data)
                                if ask_price <= lower_data:
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume,
                                                                              ask_price, 'maker')
                                    fee = round(float(ask_price) * float(exchange_fee['rate']), 8)
                                    trading_volume = float(coin_balance/ask_price)
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        (bot_id,))
                                    d2 = c.fetchall()
                                    conn.commit()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price,
                                                                      last_buy_price,
                                                                      last_sell_price, buy_higher, sell_cheaper,
                                                                      trading_volume,
                                                                      stay_profitable, double_fee, fee, t1)
                                    #print(result_str)
                                    if result_str == "open":
                                        exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                                        print("buy")
                                        print(t1)
                                        print(ask_price)
                                        print(trading_volume)
                            else:
                                print("sell select coin with 0")
                                coin_balance = float(total_balance[selected_coin]['total'])
                                print(str(coin_balance))
                                if coin_balance >= trading_volume:
                                    chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                    for i in range(0, period):
                                        bb_temp.append(chart_data[i][4])
                                    ave = np.mean(bb_temp)
                                    sd = np.std(bb_temp)
                                    middle_data = ave
                                    upper_data = round(ave + sd * upper, 8)
                                    lower_data = round(ave + sd * lower, 8)
                                    print(bid_price)
                                    print(upper_data)
                                    if bid_price >= upper_data:

                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = round(float(bid_price) * float(exchange_fee['rate']), 8)
                                        last_sell_price = 0
                                        last_buy_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper,
                                                                          trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        #print(result_str)
                                        if result_str == "open":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                                            print("sell")
                                            print(t1)
                                            print(bid_price)
                                            print(trading_volume)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
    mutex1.release()

def run_adopter_bot(run_time):
    mutex2.acquire()
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    c.execute("select bot_id from run_adopter_bot where run_time=%s", (run_time,))
    l1 = c.fetchall()
    l2 = str(l1[0][0])
    bot_id_list = l2.split(",")
    conn.commit()
    for b1 in bot_id_list:
        if b1 != "":
            c.execute("select * from bot where absID=%s", (b1,))
            bot = c.fetchone()
            conn.commit()
            bot_kind = bot[3]
            user_id = bot[5]
            interval = bot[35]
            interval1 = ""
            if interval == "1m":
                interval1 = 60000
            if interval == "5m":
                interval1 = 300000
            elif interval == "15m":
                interval1 = 900000
            elif interval == "30m":
                interval1 = 1800000
            elif interval == "1h":
                interval1 = 3600000
            elif interval == "2h":
                interval1 = 7200000
            elif interval == "4h":
                interval1 = 14400000
            elif interval == "1d":
                interval1 == 86400000
            # date_to = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(n1), int(s1))
            # date_from = datetime.datetime(int(y2), int(m2), int(d2), int(h2), int(n2), int(s2))
            # print(date_from)
            # print(date_to)
            bot_id = str(bot[0])
            bot_name = str(bot[1])
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
            indicator_profit = 0
            sum_plus = 0
            sum_minus = 0
            fee = 0.0
            exchange_fee = []
            temp_data = []
            value_dif = []
            last_buy_price = 0
            last_sell_price = 0
            chart_data = []
            now_data = []
            conn.commit()
            if bot_kind == "Indicator RSI Bot":
                exchange = str(bot[6])
                rsi_top = float(bot[24])
                rsi_bottom = float(bot[25])
                rsi_length = int(bot[23])
                rsi_value = 0
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("rsi data")
                        print(chart_data)
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        print("rsi value")
                        print(rsi_value)
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data) - rsi_length - 1, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > (len(chart_data) - rsi_length - 1):
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == (len(chart_data) - 1):
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(len(chart_data) - rsi_length, len(chart_data) + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append(
                            [str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator MACD Bot":
                exchange = str(bot[6])
                macd_long = int(bot[26])
                macd_short = int(bot[27])
                macd_signal = int(bot[28])
                long_k = 0
                short_k = 0
                macd_long_data = []
                macd_short_data = []
                macd_data = []
                macd_signal_data = []
                temp_data1 = 0
                compare_data = []
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long + macd_signal - 1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - macd_signal + 1, i + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0,len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - len(chart_data) + 2, macd_signal-len(chart_data)+i+1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[macd_signal-len(chart_data)+i+1], float(temp_data1 / macd_signal)])
                        print("macd value")
                        print(compare_data)
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*(macd_long+macd_signal), limit=macd_long + macd_signal - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long+macd_signal-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator BB Bot":
                middle_data = 0
                upper_data = 0
                lower_data = 0
                bb_temp = []
                ave = 0
                sd = 0
                bb_index = 0
                period = int(bot[29])
                upper = float(bot[30])
                lower = float(bot[31])
                exchange = str(bot[6])
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data)-period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(len(chart_data) - period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*period, limit=period - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("bb data")
                        print(chart_data)
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        print("bb value")
                        print(lower_data)
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price, buy_higher,
                                                 sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
    mutex2.release()

def run_newbie_bot(run_time):
    mutex3.acquire()
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    c.execute("select bot_id from run_newbie_bot where run_time=%s", (run_time,))
    l1 = c.fetchall()
    l2 = str(l1[0][0])
    bot_id_list = l2.split(",")
    conn.commit()
    for b1 in bot_id_list:
        if b1 != "":
            c.execute("select * from bot where absID=%s", (b1,))
            bot = c.fetchone()
            conn.commit()
            bot_kind = bot[3]
            user_id = bot[5]
            interval = bot[35]
            interval1 = ""
            if interval == "1m":
                interval1 = 60000
            if interval == "5m":
                interval1 = 300000
            elif interval == "15m":
                interval1 = 900000
            elif interval == "30m":
                interval1 = 1800000
            elif interval == "1h":
                interval1 = 3600000
            elif interval == "2h":
                interval1 = 7200000
            elif interval == "4h":
                interval1 = 14400000
            elif interval == "1d":
                interval1 == 86400000
            # date_to = datetime.datetime(int(y1), int(m1), int(d1), int(h1), int(n1), int(s1))
            # date_from = datetime.datetime(int(y2), int(m2), int(d2), int(h2), int(n2), int(s2))
            # print(date_from)
            # print(date_to)
            bot_id = str(bot[0])
            bot_type = str(bot[2])
            bot_name = str(bot[1])
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
            indicator_profit = 0
            sum_plus = 0
            sum_minus = 0
            fee = 0.0
            exchange_fee = []
            temp_data = []
            value_dif = []
            last_buy_price = 0
            last_sell_price = 0
            chart_data = []
            now_data = []
            coin_balance = 0
            conn.commit()
            if bot_kind == "Indicator RSI Bot":
                exchange = str(bot[6])
                rsi_top = float(bot[24])
                rsi_bottom = float(bot[25])
                rsi_length = int(bot[23])
                rsi_value = 0
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("rsi data")
                        print(chart_data)
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        print("rsi value")
                        print(rsi_value)
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data) - rsi_length - 1, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > (len(chart_data) - rsi_length - 1):
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == (len(chart_data) - 1):
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(len(chart_data) - rsi_length, len(chart_data) + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append(
                            [str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(loss))))
                        if rsi_value >= rsi_top:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            rsi_trading_condition(bot_id, 'top', bid_price, last_buy_price, last_sell_price,
                                                  buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                  fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])

                        for i in range(0, rsi_length + 1):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i > 0:
                                value_dif.append(float(temp_data[i][3]) - float(temp_data[i - 1][3]))
                            if i == rsi_length:
                                for j in range(0, rsi_length):
                                    if value_dif[j] > 0:
                                        sum_plus += value_dif[j]
                                    else:
                                        sum_minus += value_dif[j]
                                gain = float(sum_plus) / rsi_length
                                loss = float(sum_minus) / rsi_length
                                rsi_value = float(100 - 100 / (1 + float(float(gain) / float(abs(loss)))))
                        if rsi_value <= rsi_bottom:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                      ask_price, 'maker')
                            fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            rsi_trading_condition(bot_id, 'bottom', ask_price, last_buy_price, last_sell_price,
                                                  buy_higher,
                                                  sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator MACD Bot":
                exchange = str(bot[6])
                macd_long = int(bot[26])
                macd_short = int(bot[27])
                macd_signal = int(bot[28])
                long_k = 0
                short_k = 0
                macd_long_data = []
                macd_short_data = []
                macd_data = []
                macd_signal_data = []
                temp_data1 = 0
                compare_data = []
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long + macd_signal - 1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0, len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - macd_signal + 1, i + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        #for i in range(len(chart_data) - macd_long - macd_signal, len(chart_data)):
                        for i in range(0,len(chart_data)):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            #if i == (len(chart_data) - macd_long - macd_signal):
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            #if i > (len(chart_data) - macd_long - macd_signal):
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (len(chart_data) - macd_signal - 1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (len(chart_data) - 2):
                                for k in range(i - len(chart_data) + 2, macd_signal-len(chart_data)+i+1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[macd_signal-len(chart_data)+i+1], float(temp_data1 / macd_signal)])
                        print("macd value")
                        print(compare_data)
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*(macd_long+macd_signal), limit=macd_long + macd_signal - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=macd_long+macd_signal-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        if m1 < m2:
                            if s1 > s2:
                                if ((s2 > m1 and s2 < m2) or (s1 > m1 and s1 < m2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and m1 > s1) or (s2 < m2 and s1 > m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                              trading_volume,
                                                                              bid_price, 'maker')
                                    fee = float(bid_price) * float(exchange_fee['rate']) * trading_volume
                                    last_buy_price = d1[0][0]
                                    last_sell_price = 0
                                    macd_trading_condition(bot_id, "down_trend", bid_price, last_buy_price,
                                                           last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                    else:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                        print("macd data")
                        print(len(chart_data))
                        print(chart_data)
                        long_k = float(2 / float(macd_long + 1))
                        short_k = float(2 / float(macd_short + 1))
                        for i in range(0, macd_long + macd_signal):
                            data = chart_data[i]
                            data.pop(5)
                            temp_data.append([data[1], data[2], data[3], data[4]])
                            if i == 0:
                                macd_long_data.append(data[4])
                                macd_short_data.append(data[4])
                            if i > 0:
                                macd_long_data.append(float(data[4] * float(long_k)) + float(macd_long_data[i - 1])*float(1 - float(long_k)))
                                macd_short_data.append(float(data[4] * float(short_k)) + float(macd_short_data[i - 1])*float(1 - float(short_k)))
                            if i >= (macd_long-1):
                                macd_data.append(float(macd_short_data[i] - macd_long_data[i]))
                            if i >= (macd_long + macd_signal - 2):
                                for k in range(i - macd_long - macd_signal + 1, i - macd_long + 1):
                                    temp_data1 += macd_data[k]
                                compare_data.append(
                                    [macd_data[i - macd_long - macd_signal + 1], float(temp_data1 / macd_signal)])
                        m1 = compare_data[1][0]
                        m2 = compare_data[0][0]
                        s1 = compare_data[1][1]
                        s2 = compare_data[0][1]
                        print(compare_data)
                        if m1 > m2:
                            if s1 > s2:
                                if ((m1 > s1 and s2 > m2) or (s1 > m1 and m2 > s2)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                            if s1 < s2:
                                if ((s2 > m2 and s2 < m1) or (s2 > m1 and s1 < m1)):
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume, ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * trading_volume
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                                    d2 = c.fetchall()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    conn.commit()
                                    macd_trading_condition(bot_id, "up_trend", ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                           double_fee, fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
            if bot_kind == "Indicator BB Bot":
                middle_data = 0
                upper_data = 0
                lower_data = 0
                bb_temp = []
                ave = 0
                sd = 0
                bb_index = 0
                period = int(bot[29])
                upper = float(bot[30])
                lower = float(bot[31])
                exchange = str(bot[6])
                result_str = ""
                if exchange == "binance":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "binance"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    conn.commit()
                    exchange_obj = ccxt.binance({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bidPrice'])
                    ask_price = float(now_data['info']['askPrice'])
                    now_time = now_data['timestamp']
                    if bot_type =="Demo":
                        c.execute(
                            "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                            (bot_id, 'buy', 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            print(bot_type)
                            if bid_price >= upper_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                          bid_price, 'maker')
                                fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                                last_buy_price = d1[0][0]
                                last_sell_price = 0
                                bb_trading_condition(bot_id, 'Demo', 'upper', bid_price, last_buy_price,
                                                     last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable,
                                                     double_fee, fee, t1)
                        else:
                            chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                            for i in range(0, period):
                                bb_temp.append(chart_data[i][4])
                            ave = np.mean(bb_temp)
                            sd = np.std(bb_temp)
                            middle_data = ave
                            upper_data = ave + sd * upper
                            lower_data = ave + sd * lower
                            if ask_price <= lower_data:
                                exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', trading_volume,
                                                                          ask_price, 'maker')
                                fee = float(ask_price) * float(exchange_fee['rate']) * float(trading_volume)
                                c.execute(
                                    "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc",
                                    (bot_id,))
                                d2 = c.fetchall()
                                last_buy_price = 0
                                if len(d2) > 0:
                                    last_sell_price = d2[0][0]
                                else:
                                    last_sell_price = 0
                                conn.commit()
                                bb_trading_condition(bot_id, bot_type, 'lower', ask_price, last_buy_price, last_sell_price,
                                                     buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                     fee, t1)
                    if bot_type == "Live":
                        c.execute(
                            "select order_type, buy_price, sell_price from trading_history where bot_id=%s and order_status=%s",
                            (bot_id, 'create'))
                        t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                        d1 = c.fetchall()
                        conn.commit()
                        if len(d1) > 0:
                            order_type = d1[0][0]
                            if order_type == "buy":
                                chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = ave + sd * upper
                                lower_data = ave + sd * lower
                                if bid_price >= upper_data:
                                    total_balance = exchange_obj.fetch_balance()
                                    coin_balance = total_balance[selected_coin]
                                    if coin_balance >= trading_volume:
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                                        last_buy_price = d1[0][0]
                                        last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price,
                                                                          buy_higher, sell_cheaper, trading_volume,
                                                                          stay_profitable,
                                                                          double_fee, fee, t1)
                                        print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                            if order_type == "sell":
                                chart_data.append([now_data['timestamp'], 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = ave + sd * upper
                                lower_data = ave + sd * lower
                                if ask_price <= lower_data:
                                    total_balance = exchange_obj.fetch_balance()
                                    coin_balance = total_balance[base_currency]
                                    if coin_balance >= trading_volume*ask_price:
                                        trading_volume = float(coin_balance/ask_price)
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                                  trading_volume,
                                                                                  ask_price, 'maker')
                                        fee = float(ask_price) * float(exchange_fee['rate']) * float(trading_volume)
                                        #c.execute(
                                        #    "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        #    (bot_id,))
                                        #d2 = c.fetchall()
                                        #conn.commit()
                                        last_buy_price = 0
                                        last_sell_price = ask_price
                                        #if len(d2) > 0:
                                        #    last_sell_price = d2[0][0]
                                        #else:
                                        #    last_sell_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price, last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper, trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        print(result_str)
                                        if result_str == "close":
                                            exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                        else:
                            total_balance = exchange_obj.fetch_balance()
                            coin_balance = total_balance[base_currency]
                            if coin_balance >= trading_volume * ask_price:
                                chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                                for i in range(0, period):
                                    bb_temp.append(chart_data[i][4])
                                ave = np.mean(bb_temp)
                                sd = np.std(bb_temp)
                                middle_data = ave
                                upper_data = ave + sd * upper
                                lower_data = ave + sd * lower
                                if ask_price <= lower_data:
                                    exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy',
                                                                              trading_volume,
                                                                              ask_price, 'maker')
                                    fee = float(ask_price) * float(exchange_fee['rate']) * float(trading_volume)
                                    c.execute(
                                        "select sell_price from trading_history where bot_id=%s and order_status='complete' order by sell_time desc",
                                        (bot_id,))
                                    d2 = c.fetchall()
                                    conn.commit()
                                    last_buy_price = 0
                                    if len(d2) > 0:
                                        last_sell_price = d2[0][0]
                                    else:
                                        last_sell_price = 0
                                    result_str = bb_trading_condition(bot_id, 'Live', 'lower', ask_price,
                                                                      last_buy_price,
                                                                      last_sell_price, buy_higher, sell_cheaper,
                                                                      trading_volume,
                                                                      stay_profitable, double_fee, fee, t1)
                                    print(result_str)
                                    if result_str == "open":
                                        exchange_obj.create_market_buy_order(coin_pair, trading_volume)
                            else:
                                coin_balance = total_balance[selected_coin]
                                if coin_balance >= trading_volume:
                                    chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                                    for i in range(0, period):
                                        bb_temp.append(chart_data[i][4])
                                    ave = np.mean(bb_temp)
                                    sd = np.std(bb_temp)
                                    middle_data = ave
                                    upper_data = ave + sd * upper
                                    lower_data = ave + sd * lower
                                    if bid_price >= upper_data:
                                        exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell',
                                                                                  trading_volume,
                                                                                  bid_price, 'maker')
                                        fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                                        last_sell_price = 0
                                        last_buy_price = 0
                                        result_str = bb_trading_condition(bot_id, 'Live', 'upper', bid_price,
                                                                          last_buy_price,
                                                                          last_sell_price, buy_higher, sell_cheaper,
                                                                          trading_volume,
                                                                          stay_profitable, double_fee, fee, t1)
                                        print(result_str)
                                        if result_str == "open":
                                            exchange_obj.create_market_sell_order(coin_pair, trading_volume)
                elif exchange == "cryptopia":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cryptopia({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['BidPrice'])
                    ask_price = float(now_data['info']['AskPrice'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(len(chart_data)-period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(len(chart_data) - period, len(chart_data)):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "cexio":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cexio"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.cex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=rsi_length)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']

                elif exchange == "bittrex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "bittrex"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.bittrex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'

                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['Bid'])
                    ask_price = float(now_data['info']['Ask'])
                    now_time = now_data['timestamp']
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, since=now_time-interval1*period, limit=period - 1)
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        print("bb data")
                        print(chart_data)
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        print("bb value")
                        print(lower_data)
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price, buy_higher,
                                                 sell_cheaper, trading_volume, stay_profitable, double_fee, fee, t1)
                elif exchange == "hitbtc":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "hitbtc"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.hitbtc2({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period-1)
                    now_data = exchange_obj.fetch_ticker(coin_pair)
                    bid_price = float(now_data['info']['bid'])
                    ask_price = float(now_data['info']['ask'])
                    now_time = now_data['timestamp']
                    c.execute(
                        "select buy_price from trading_history where bot_id=%s and order_type=%s and order_status=%s",
                        (bot_id, 'buy', 'create'))
                    t1 = datetime.datetime.fromtimestamp(now_time / 1000)
                    d1 = c.fetchall()
                    conn.commit()
                    if len(d1) > 0:
                        chart_data.append([now_data['timestamp'], 0, 0, 0, bid_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price >= upper_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            last_buy_price = d1[0][0]
                            last_sell_price = 0
                            bb_trading_condition(bot_id, 'upper', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                    else:
                        chart_data.append([str(now_data['timestamp']), 0, 0, 0, ask_price, 0])
                        for i in range(0, period):
                            bb_temp.append(chart_data[i][4])
                        ave = np.mean(bb_temp)
                        sd = np.std(bb_temp)
                        middle_data = ave
                        upper_data = ave + sd * upper
                        lower_data = ave + sd * lower
                        if bid_price <= lower_data:
                            exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', trading_volume,
                                                                      bid_price, 'maker')
                            fee = float(bid_price) * float(exchange_fee['rate']) * float(trading_volume)
                            c.execute(
                                "select sell_price from trading_history where bot_id=%s and order_type='sell' and order_status='complete' order by sell_time desc", (bot_id,))
                            d2 = c.fetchall()
                            last_buy_price = 0
                            if len(d2) > 0:
                                last_sell_price = d2[0][0]
                            else:
                                last_sell_price = 0
                            conn.commit()
                            bb_trading_condition(bot_id, 'lower', bid_price, last_buy_price, last_sell_price,
                                                 buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee,
                                                 fee, t1)
                elif exchange == "okex":
                    c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                              (user_id, "cryptopia"))
                    key_data = c.fetchone()
                    api = key_data[0]
                    secret = key_data[1]
                    exchange_obj = ccxt.okex({
                        'proxies': {
                            'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                            'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        },
                        'apiKey': api,
                        'secret': secret,
                    })
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
                    exchange_obj.has['fetchOHLCV'] = 'emulated'
                    chart_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=50)
    mutex3.release()

def rsi_trading_condition(bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    str1 = "rsi"+trend+str(coin_price)+str(time)
    print(str1)
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    # print(user_id)
    result_str = ""
    if trend == "bottom":
        c.execute(
            """select * from trading_history where bot_id=%s and order_type='buy' and order_status='create'""",
            (bot_id,))
        result = c.fetchall()
        conn.commit()
        if len(result) <= 0:
            # print("open long")
            # print(coin_price)
            if buy_higher == "On" and coin_price > last_sell_price:
                return ""
            c.execute(
                """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%s, %s, %s, %s, %s, %s )""",
                (bot_id, 'buy', 'create', time, coin_price, exchange_fee))
            conn.commit()
            result_str = "open long"

        return result_str
    if trend == "top":
        c.execute(
            """select buy_price from trading_history where bot_id=%s and  order_type='buy' and order_status='create'""",
            (bot_id,))
        result1 = c.fetchall()
        # print(result1)
        conn.commit()
        if len(result1) > 0:
            buy_price = float(result1[0][0])
            if sell_cheaper == "On" and coin_price < last_buy_price:
                return ""
            if double_fee == "On" and float(trading_volume) * (float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                return ""
            if stay_profitable == "On" and coin_price < buy_price:
                return ""
            c.execute(
                "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'",
                (coin_price, time, exchange_fee, bot_id))
            conn.commit()
            result_str = "close long"
        # conn.close()
        return result_str

def macd_trading_condition(bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    str1 = "macd" + trend + str(coin_price) + str(time)
    print(str1)
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    # print(user_id)
    result_str = ""
    if trend == "up_trend":
        c.execute(
            """select * from trading_history where bot_id=%s and order_type='buy' and order_status='create'""",
            (bot_id,))
        result = c.fetchall()
        conn.commit()
        if len(result) <= 0:
            # print("open long")
            # print(coin_price)
            if buy_higher == "On" and coin_price > last_sell_price:
                return ""
            c.execute(
                """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%s, %s, %s, %s, %s, %s )""",
                (bot_id, 'buy', 'create', time, coin_price, exchange_fee))
            conn.commit()
            result_str = "open long"

        return result_str
    if trend == "down_trend":
        c.execute(
            """select buy_price from trading_history where bot_id=%s and  order_type='buy' and order_status='create'""",
            (bot_id,))
        result1 = c.fetchall()
        # print(result1)
        conn.commit()
        if len(result1) > 0:
            buy_price = float(result1[0][0])
            if sell_cheaper == "On" and coin_price < last_buy_price:
                return ""
            if double_fee == "On" and float(trading_volume) * (float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                return ""
            if stay_profitable == "On" and coin_price < buy_price:
                return ""
            c.execute(
                "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'",
                (coin_price, time, exchange_fee, bot_id))
            conn.commit()
            result_str = "close long"
        # conn.close()
        return result_str

def bb_trading_condition(bot_id, bot_type, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                  trading_volume, stay_profitable, double_fee, exchange_fee, time):
    #str1 = "bb" + trend + str(coin_price) + str(time)
    #print(str1)
    conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')
    c = conn.cursor(buffered=True)
    # print(user_id)
    result_str = ""
    if bot_type == "Demo":
        if trend == "lower":
            c.execute(
                """select * from trading_history where bot_id=%s and order_type='buy' and order_status='create'""",
                (bot_id,))
            result = c.fetchall()
            conn.commit()
            if len(result) <= 0:
                # print("open long")
                # print(coin_price)
                if buy_higher == "On" and coin_price > last_sell_price:
                    return ""
                c.execute(
                    """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%s, %s, %s, %s, %s, %s )""",
                    (bot_id, 'buy', 'create', time, coin_price, exchange_fee))
                conn.commit()
                result_str = "open long"

            return result_str
        if trend == "upper":
            c.execute(
                """select buy_price from trading_history where bot_id=%s and  order_type='buy' and order_status='create'""",
                (bot_id,))
            result1 = c.fetchall()
            # print(result1)
            conn.commit()
            if len(result1) > 0:
                buy_price = float(result1[0][0])
                if sell_cheaper == "On" and coin_price < last_buy_price:
                    return ""
                if double_fee == "On" and float(trading_volume) * (
                        float(coin_price) - float(buy_price)) < 2 * exchange_fee:
                    return ""
                if stay_profitable == "On" and coin_price < buy_price:
                    return ""
                c.execute(
                    "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'",
                    (coin_price, time, exchange_fee, bot_id))
                conn.commit()
                result_str = "close long"
            # conn.close()
            return result_str
    if bot_type == "Live":
        if trend == "lower":
            c.execute(
                """select * from trading_history where bot_id=%s and order_status='create'""",
                (bot_id,))
            result = c.fetchall()
            conn.commit()
            if len(result) <= 0:
                # print("open long")
                # print(coin_price)
                if buy_higher == "On" and coin_price > last_sell_price:
                    return ""
                c.execute(
                    """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%s, %s, %s, %s, %s, %s )""",
                    (bot_id, 'buy', 'create', time, coin_price, exchange_fee))
                conn.commit()
                conn.close()
                result_str = "open"
            else:
                if result[0][2] == "sell":
                    if buy_higher == "On" and coin_price > last_sell_price:
                        return ""
                    if double_fee == "On" and (float(result[0][7])-float(coin_price)) <= (exchange_fee+float(result[0][10])):
                        return ""
                    if stay_profitable == "On" and coin_price >= result[0][7]:
                        return ""
                    c.execute(
                        "update trading_history set order_status='complete', order_type='buy', buy_price=%s, buy_time=%s, buy_fee=%s where bot_id=%s and order_type='sell' and order_status='create'",
                        (coin_price, time, exchange_fee, bot_id))
                    result_str = "close"
                    conn.close()
            return result_str
        if trend == "upper":
            c.execute(
                """select * from trading_history where bot_id=%s and order_status='create'""",
                (bot_id,))
            result1 = c.fetchall()
            # print(result1)
            conn.commit()
            if len(result1) <= 0:
                if sell_cheaper == "On" and coin_price < last_buy_price:
                    return ""
                print(exchange_fee)
                c.execute(
                    """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `sell_time`, `sell_price`, `sell_fee`) values (%s, %s, %s, %s, %s, %s )""",
                    (bot_id, 'sell', 'create', time, coin_price, exchange_fee))
                conn.commit()
                conn.close()
                result_str = "open"
            else:
                if result1[0][2] == "buy":
                    buy_price = float(result1[0][6])
                    if sell_cheaper == "On" and coin_price < last_buy_price:
                        return ""
                    if double_fee == "On" and float(trading_volume) * (
                            float(coin_price) - float(buy_price)) < (exchange_fee+result1[0][9]):
                        return ""
                    if stay_profitable == "On" and coin_price < buy_price:
                        return ""
                    c.execute(
                        "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'",
                        (coin_price, time, exchange_fee, bot_id))
                    conn.commit()
                    result_str = "close"
            conn.close()
            return result_str

threading.Thread(target=run_bot_thread(30, "enthusiast", mutex1)).start()
#t2 = threading.Thread(target=thread2).start()
#t3 = threading.Thread(target=thread3).start()