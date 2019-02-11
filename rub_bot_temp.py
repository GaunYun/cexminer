# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
import mysql.connector
import datetime
import time
import ccxt
import numpy as np

db_conn = mysql.connector.Connect(host='localhost', user='root', password='', database='trading_bot')
query_conn = db_conn.cursor(buffered=True)

#######################
## bot_level: {newbie, adpoter, enthusiast}, string value
## period_in_seconds: interval value calculated in seconds, integer value
## mutex_object: Thread Mutex for 3 kind of bots, here is 3 mutex defined for now, mutex1, mutex2, mutex3, should be able to create without limitation
#######################
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

#######################
## bot_level: {newbie, adpoter, enthusiast}, string value
## run time: time point to run the bot
## mutex_object: Thread Mutex for 3 kind of bots, here is 3 mutex defined for now, mutex1, mutex2, mutex3, should be able to create without limitation
#######################
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

#######################
##
def add_price_thread(mutex_object=None):
    t_list = []
    while True:
        v = str(datetime.datetime.now())
        h1 = v[11:13]
        n1 = v[14:16]
        s1 = v[17:19]
        current_time = 3600 * int(h1) + 60 * int(n1) + int(s1)
        num1 = divmod(current_time, 5)
        #num2 = divmod(num1[1], 5)
        if num1[1] == 0:
            t_list.append(num1[1])
            if not mutex_object.locked():
                t = str(t_list[0])
                t_list.pop(0)
                add_price(mutex_object)

########################
##
def add_price(mutex_object):
    mutex_object.acquire()

    query_conn.execute(
        "select exchange1, selected_coin, base_currency, user_id from bot where bot_type='Live' and bot_status='On'")
    records = query_conn.fetchall()
    db_conn.commit()

    for r in records:
        exchange = r[0]
        selected_coin = r[1]
        base_currency = r[2]
        coin_pair = selected_coin + "/" + base_currency
        user_id = r[3]
        if exchange == "binance":
            query_conn.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                               (user_id, exchange))
            key_data = query_conn.fetchone()
            api = key_data[0]
            secret = key_data[1]
            db_conn.commit()
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
            coin_price = float(cur_data['info']['lastPrice'])
            cur_time = cur_data['timestamp']
        t = str(datetime.datetime.fromtimestamp(cur_time / 1000))
        cur_date = t[:10]
        query_conn.execute("select bid_price, ask_price, coin_price from coin_price where exchange=%s and coin_pair=%s and date=%s", (exchange, coin_pair, cur_date,))
        r = query_conn.fetchall()
        db_conn.commit()
        if len(r) > 0:
            bid_price_text = str(r[0][0])
            ask_price_text = str(r[0][1])
            coin_price_text = str(r[0][2])
            bid_price_list = bid_price_text.split(",")
            ask_price_list = ask_price_text.split(",")
            coin_price_list = coin_price_text.split(",")
            last_bid_price_data = bid_price_list[len(bid_price_list)-1].split("-")
            last_ask_price_data = ask_price_list[len(ask_price_list)-1].split("-")
            last_coin_price_data = coin_price_list[len(coin_price_list)-1].split("-")
            last_bid_price_time = last_bid_price_data[0]
            last_ask_price_time = last_ask_price_data[0]
            last_coin_price_time = last_coin_price_data[0]
            print(cur_time)
            #print(last_bid_price_time)
            #print(last_ask_price_time)
            if int(cur_time) > int(last_bid_price_time):
                #bid_price_text = str(cur_time) + "-" + str(bid_price) + "," + bid_price_text
                bid_price_text += "," + str(cur_time) + "-" + str(bid_price)
                query_conn.execute("update coin_price set bid_price=%s where exchange=%s and coin_pair=%s and date=%s", (bid_price_text, exchange, coin_pair, cur_date))
                db_conn.commit()
            if int(cur_time) > int(last_ask_price_time):
                #ask_price_text = str(cur_time) + "-" + str(ask_price) + "," + ask_price_text
                ask_price_text += "," + str(cur_time) + "-" + str(ask_price)
                query_conn.execute("update coin_price set ask_price=%s where exchange=%s and coin_pair=%s and date=%s", (ask_price_text, exchange, coin_pair, cur_date))
                db_conn.commit()
            if int(cur_time) > int(last_coin_price_time):
                #coin_price_text = str(cur_time) + "-" + str(coin_price) + "," + coin_price_text
                coin_price_text += "," + str(cur_time) + "-" + str(coin_price)
                query_conn.execute("update coin_price set coin_price=%s where exchange=%s and coin_pair=%s and date=%s", (coin_price_text, exchange, coin_pair, cur_date))
                db_conn.commit()
        else:
            query_conn.execute("insert into `coin_price` (`exchange`, `coin_pair`, `date`, `bid_price`, `ask_price`, `coin_price`) VALUES (%s, %s, %s, %s, %s, %s )", (exchange, coin_pair, cur_date, str(cur_time) + "-" + str(bid_price), str(cur_time) + "-" + str(ask_price), str(cur_time) + "-" + str(coin_price)))
            db_conn.commit()
    mutex_object.release()
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
    #trading_volume = float(bot[10])
    period = int(bot[29])
    upper_dev = float(bot[30])
    lower_dev = float(bot[31])

    # Declare local variables
    indicator_profit = 0.0
    sum_plus = 0.0
    sum_minus = 0.0

    trading_volume = 0.0

    coin_balance = 0.0
    base_balance = 0.0

    last_buy_price = 0.0
    last_sell_price = 0.0
    bid_price = 0.0
    ask_price = 0.0

    temp_data = []
    value_dif = []
    hist_data = []
    bid_hist_data = []
    ask_hist_data = []
    sell_order_book = []
    buy_order_book = []
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

######### Get historical data from exchnage
    exchange_obj.has['fetchOHLCV'] = 'emulated'
    hist_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period - 1)


    total_balance = exchange_obj.fetch_balance()
    base_balance = float(total_balance[base_currency]['total'])
    coin_balance = float(total_balance[selected_coin]['total'])
    #buy_t_volume = min(base_balance/ask_price, trading_volume)
    #sell_t_volume = min(coin_balance, trading_volume)
    buy_exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', 1, ask_price, 'maker')
    buy_fee = round(ask_price * float(buy_exchange_fee['rate']), 8) # is this right, it is necessary to multiply ask_price
    sell_exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', 1, bid_price, 'maker')
    sell_fee = round(bid_price * float(sell_exchange_fee['rate']), 8)

    #hist_data.append([cur_time, 0, 0, 0, bid_price, 0])
    #for i in range(0, period):
    #    bb_temp.append(hist_data[i][4])
    #avg = np.mean(bb_temp)
    #stand_dev = np.std(bb_temp)
    #upper_price = round(avg + stand_dev * upper_dev, 8)
    #lower_price = round(avg + stand_dev * lower_dev, 8)

    query_conn.execute("select buy_price from trading_history where bot_id=%s and buy_price<>'0' order by absID desc", (bot_id,))
    temp = query_conn.fetchone()
    if query_conn.rowcount:
        last_buy_price = temp[0]
    else:
        last_buy_price = 0
    db_conn.commit()
    query_conn.execute("select sell_price from trading_history where bot_id=%s and sell_price<>'0' order by absID desc", (bot_id,))
    temp = query_conn.fetchone()
    if query_conn.rowcount:
        last_sell_price = temp[0]
    else:
        last_sell_price = 0
    db_conn.commit()

    query_conn.execute("select order_type, buy_price, sell_price from trading_history where bot_id=%s and order_status=%s", (bot_id, 'create'))
    trans_data = query_conn.fetchall()
    db_conn.commit()

    t = datetime.datetime.fromtimestamp(cur_time / 1000)

    ######### Get historical data from database
    query_conn.execute("select bid_price, ask_price from coin_price where exchange=%s and coin_pair=%s and date=%s", (exchange, coin_pair, t[:10]))
    temp_data = query_conn.fetchall()
    db_conn.commit()
    temp_bid_data = str(temp_data[0][0]).split(",")
    temp_ask_data = str(temp_data[0][1])
    if len(temp_bid_data) < (period-1):
        return
    else:
        for i in range(len(temp_bid_data)-period+1, period):
            bid_hist_data.append(temp_bid_data[i].split("-")[1])
            ask_hist_data.append(temp_ask_data[i].split("-")[1])
        bid_hist_data.append(bid_price)
        ask_hist_data.append(ask_price)

    if len(trans_data) > 0: # if there is an order with the create status
        order_type = trans_data[0][0]
        buy_price = float(trans_data[0][1])
        sell_price = float(trans_data[0][2])

        if order_type == "buy":
            #### add bid_price for selling with buy order
            #hist_data.append([cur_time, 0, 0, 0, bid_price, 0])
            #for i in range(0, period):
            #    bb_temp.append(hist_data[i][4])
            avg = np.mean(bid_hist_data)    #avg = np.mean(bb_temp)
            stand_dev = np.std(bid_hist_data) #stand_dev = np.std(bb_temp)
            upper_price = round(avg + stand_dev * upper_dev, 8)
            lower_price = round(avg + stand_dev * lower_dev, 8)

            sell_order_book = exchange_obj.fetch_order_book(coin_pair)['bids']
            for order in sell_order_book:
                if order[0] >= bid_price:
                    trading_volume += float(order[1])
                else:
                    break

            sell_t_volume = min(coin_balance, trading_volume)

            log_str = str(t) + ': ' + 'compare: sell with buy ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+')\n';
            add_bot_log(log_str)

            if bid_price >= upper_price:
                #if coin_balance >= trading_volume * 0.95:
                if coin_balance > 0:
                    log_str = str(t) + ': ' + 'parameter: sell with buy ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(sell_fee) + ')\n'
                    add_bot_log(log_str)

                    eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, sell_t_volume, stay_profitable, double_fee, sell_fee, t)
                    if eval_result == "close": # why is this return value close?
                        try:
                            exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                            log_str = str(t) + ': ' + 'Sell ' + coin_pair + '(sell_price=' + str(bid_price) + ', bot_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                        add_bot_log(log_str)
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in sell with buy\n")
                else:
                    add_bot_log(str(t) + ': ' + coin_pair + ': ' + "coin balance is less than trading volume in sell with buy\n")
            else:
                if bid_price >= (buy_price + float(profit) * buy_price / 100):
                    eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price,
                                                       buy_higher, sell_cheaper, sell_t_volume, stay_profitable,
                                                       double_fee, sell_fee, t)
                    if eval_result == "close":  # why is this return value close?
                        try:
                            exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                            log_str = str(t) + ': ' + 'Sell ' + coin_pair + '(sell_price=' + str(bid_price) + ', bot_price=' + str(upper_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(sell_fee) + ')\n'
                        except:
                            log_str = str(
                                t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                        add_bot_log(log_str)
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in sell with buy\n")
                else:
                    if bid_price <= (buy_price - float(stop_loss) * buy_price / 100):
                        try:
                            exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                            log_str = str(t) + ': ' + 'Sell ' + coin_pair + ' for stop_loss (sell_price=' + str(bid_price) + ', bot_price=' + str(upper_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(sell_fee) + ')\n'
                        except:
                            log_str = str(
                                t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "bid price is less than upper price in sell with buy\n")

        elif order_type == "sell":
            ### add ask_price to history data for buying with sell order
            #hist_data.append([cur_time, 0, 0, 0, ask_price, 0])
            #for i in range(0, period):
            #    bb_temp.append(hist_data[i][4])
            avg = np.mean(ask_hist_data) #avg = np.mean(bb_temp)
            stand_dev = np.std(ask_hist_data) #stand_dev = np.std(bb_temp)
            upper_price = round(avg + stand_dev * upper_dev, 8)
            lower_price = round(avg + stand_dev * lower_dev, 8)

            buy_order_book = exchange_obj.fetch_order_book(coin_pair)['asks']
            for order in buy_order_book:
                if order[0] <= ask_price:
                    trading_volume += float(order[1])
                else:
                    break

            buy_t_volume = min(base_balance, trading_volume * ask_price)

            log_str = str(t) + ': ' + 'compare: buy with sell ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n'
            add_bot_log(log_str)

            if ask_price <= lower_price:
                #if base_balance >= 0.95 * trading_volume * ask_price:
                if base_balance > 0:
                    log_str = str(t) + ': ' + 'parameter: buy with sell ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_price)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(buy_fee) +')\n'
                    add_bot_log(log_str)

                    eval_result = eval_bb_trading_cond(bot_id, 'lower', ask_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, buy_t_volume, stay_profitable, double_fee, buy_fee, t)
                    if eval_result == "close":
                        try:
                            exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                            log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order\n"
                        add_bot_log(log_str)
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in buy with sell\n")
                else:
                    add_bot_log(str(t) + ': ' + coin_pair + ': ' + "base balance is less than trading volume in buy with sell\n")
            else:
                if ask_price <= (sell_price - float(profit) * sell_price / 100):
                    print("take profit success")
                    eval_result = eval_bb_trading_cond(bot_id, 'lower', ask_price, last_buy_price, last_sell_price,
                                                       buy_higher, sell_cheaper, buy_t_volume, stay_profitable,
                                                       double_fee, buy_fee, t)
                    if eval_result == "close":
                        try:
                            exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                            log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order\n"
                        add_bot_log(log_str)
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in buy with sell\n")
                else:
                    if ask_price >= (sell_price + float(stop_loss) * sell_price / 100):
                        try:
                            exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                            log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order\n"
                        add_bot_log(log_str)
                    else:
                        add_bot_log(str(t) + ': ' + coin_pair + ': ' + "ask price is greater than lower price in buy with sell\n")
    else: # if there is no order with the create status
        if base_balance >= 0.95 * trading_volume * ask_price:
            ### add ask_price to history data for buying without any created order
            # hist_data.append([cur_time, 0, 0, 0, ask_price, 0])
            # for i in range(0, period):
            #    bb_temp.append(hist_data[i][4])
            avg = np.mean(ask_hist_data)  # avg = np.mean(bb_temp)
            stand_dev = np.std(ask_hist_data)  # stand_dev = np.std(bb_temp)
            upper_price = round(avg + stand_dev * upper_dev, 8)
            lower_price = round(avg + stand_dev * lower_dev, 8)

            log_str = str(t) + ': ' + 'compare: buy without none ' + coin_pair + '(e_price=' +str(ask_price)+', bb_price='+str(lower_price)+', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n'
            add_bot_log(log_str)

            if ask_price <= lower_price:
                log_str = str(t) + ': ' + 'parameter: buy without none ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                add_bot_log(log_str)

                eval_result = eval_bb_trading_cond(bot_id, "lower", ask_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, buy_t_volume, stay_profitable, double_fee, buy_fee, t)
                if eval_result == "open":
                    try:
                        exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                        log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(buy_fee) +')\n'
                    except:
                        log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order"
                    add_bot_log(log_str)
                else:
                    add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in buy with none\n")
            else:
                add_bot_log(str(t) + ': ' + coin_pair + ': ' + "ask price is greater than lower price in buy with none\n")
        else:
            add_bot_log(str(t) + ': ' + coin_pair + ': ' + "base balance is less than trading volume in sell with none\n")
        if coin_balance >= 0.95 * trading_volume:
            ### add bid price to history data for selling without any created order
            # hist_data.append([cur_time, 0, 0, 0, bid_price, 0])
            # for i in range(0, period):
            #    bb_temp.append(hist_data[i][4])
            avg = np.mean(bid_hist_data)  # avg = np.mean(bb_temp)
            stand_dev = np.std(bid_hist_data)  # stand_dev = np.std(bb_temp)
            upper_price = round(avg + stand_dev * upper_dev, 8)
            lower_price = round(avg + stand_dev * lower_dev, 8)

            log_str = str(t) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+')\n'
            add_bot_log(log_str)

            if bid_price >= upper_price:
                log_str = str(t) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                add_bot_log(log_str)

                eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, sell_t_volume, stay_profitable, double_fee, sell_fee, t)
                if eval_result == "open":
                    try:
                        exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                        log_str = str(t) + ': ' + 'Sell ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                    except:
                        log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order"
                    add_bot_log(log_str)
                else:
                    add_bot_log(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in sell with none\n")
            else:
                add_bot_log(str(t) + ': ' + coin_pair + ': ' + "bid price is less than upper price in sell with none\n")
        else:
            add_bot_log(str(t) + ': ' + coin_pair + ': ' + "coin balance is less than trading volume in sell with none\n")

def run_Indicator_MACD_bot(bot, exchange):
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
    slow_period = int(bot[26])
    fast_period = float(bot[27])
    signal_period = float(bot[28])

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
    bb_index = 0  # not used?
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
    query_conn.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s",
                       (user_id, exchange))
    key_data = query_conn.fetchone()
    api = key_data[0]
    secret = key_data[1]
    db_conn.commit()

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
def run_Indicator_RSI_bot(bot, exchange):
    return

#######################################################

def eval_bb_trading_cond(bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, time):
    result_str = ""
    if trend == "lower":
        query_conn.execute("""select * from trading_history where bot_id=%s and order_status='create'""",(bot_id,))
        result = query_conn.fetchall()
        db_conn.commit()
        if len(result) <= 0:
            if buy_higher == "On" and coin_price > last_sell_price and last_sell_price != 0:
                return ""
            query_conn.execute("""insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%s, %s, %s, %s, %s, %s )""", (bot_id, 'buy', 'create', time, coin_price, exchange_fee))
            db_conn.commit()
            result_str = "open"
        else:
            if result[0][2] == "sell":
                if buy_higher == "On" and coin_price > last_sell_price:
                    return ""
                if double_fee == "On" and (float(result[0][7]) - float(coin_price)) <= (exchange_fee + float(result[0][10])):
                    return ""
                if stay_profitable == "On" and coin_price >= result[0][7]:
                    return ""
                query_conn.execute(
                    "update trading_history set order_status='complete', order_type='buy', buy_price=%s, buy_time=%s, buy_fee=%s where bot_id=%s and order_type='sell' and order_status='create'",
                    (coin_price, time, exchange_fee, bot_id))
                db_conn.commit()
                result_str = "close"
        return result_str
    elif trend == "upper":
        query_conn.execute(
            """select * from trading_history where bot_id=%s and order_status='create'""", (bot_id,))
        result1 = query_conn.fetchall()
        # print(result1)
        db_conn.commit()
        if len(result1) <= 0:
            if sell_cheaper == "On" and coin_price < last_buy_price and last_buy_price != 0:
                return ""
            query_conn.execute("""insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `sell_time`, `sell_price`, `sell_fee`) values (%s, %s, %s, %s, %s, %s )""",(bot_id, 'sell', 'create', time, coin_price, exchange_fee))
            db_conn.commit()
            result_str = "open"
        else:
            if result1[0][2] == "buy":
                buy_price = float(result1[0][6])
                if sell_cheaper == "On" and coin_price < last_buy_price:
                    return ""
                if double_fee == "On" and (trading_volume * coin_price - buy_price) < (exchange_fee + result1[0][9]):
                    return ""
                if stay_profitable == "On" and coin_price < buy_price:
                    return ""
                query_conn.execute(
                    "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'",(coin_price, time, exchange_fee, bot_id))
                db_conn.commit()
                result_str = "close"
        return result_str

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

def add_bot_log(log_str):
    print (log_str)
    with open("bot_log.txt", "a") as log_file:
        log_file.write(log_str + '\n')

#run_bot_thread(threading.Lock(), 60)

add_price_thread(threading.Lock())
