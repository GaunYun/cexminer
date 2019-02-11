# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from threading import Thread
import logging

import mysql.connector
import datetime
import time
import ccxt
import numpy as np

logging.basicConfig(format='%(message)s', filename='debug.log', level=logging.WARNING)

db_conn = mysql.connector.Connect(host='localhost', user='root', password='', database='trading_bot')
query_conn = db_conn.cursor(buffered=True)

threads = []
#######################
## bot_level: {newbie, adpoter, enthusiast}, string value
## period_in_seconds: interval value calculated in seconds, integer value
## mutex_object: Thread Mutex for 3 kind of bots, here is 3 mutex defined for now, mutex1, mutex2, mutex3, should be able to create without limitation
#######################
def run_bot_thread(bot_id=0):
    while True:
        query_conn.execute("select * from bot where absID=%s", (bot_id,))
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

    exchange_obj.has['fetchOHLCV'] = 'emulated'
    hist_data = exchange_obj.fetch_ohlcv(coin_pair, interval, limit=period - 1)
    total_balance = exchange_obj.fetch_balance()
    base_balance = float(total_balance[base_currency]['total'])
    coin_balance = float(total_balance[selected_coin]['total'])
    buy_t_volume = min(base_balance/ask_price, trading_volume)
    sell_t_volume = min(coin_balance, trading_volume)
    buy_exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'buy', buy_t_volume, ask_price, 'maker')
    buy_fee = round(ask_price * float(buy_exchange_fee['rate']), 8) # is this right, it is necessary to multiply ask_price
    sell_exchange_fee = exchange_obj.calculate_fee(coin_pair, 'market', 'sell', sell_t_volume, bid_price, 'maker')
    sell_fee = round(bid_price * float(sell_exchange_fee['rate']), 8)

    hist_data.append([cur_time, 0, 0, 0, bid_price, 0])
    for i in range(0, period):
        bb_temp.append(hist_data[i][4])
    avg = np.mean(bb_temp)
    stand_dev = np.std(bb_temp)
    upper_price = round(avg + stand_dev * upper_dev, 8)
    lower_price = round(avg + stand_dev * lower_dev, 8)

    query_conn.execute("select buy_price from trading_history where bot_id=%s and buy_price<>'' order by absID desc", (bot_id,))
    temp = query_conn.fetchone()
    if query_conn.rowcount:
        last_buy_price = temp[0]
    else:
        last_buy_price = 0
    db_conn.commit()
    query_conn.execute("select sell_price from trading_history where bot_id=%s and buy_price<>'' order by absID desc", (bot_id,))
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

    if len(trans_data) > 0: # if there is an order with the create status
        order_type = trans_data[0][0]

        if order_type == "buy":
            log_str = str(t) + ': ' + 'compare: sell with buy ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+')\n';
            print (log_str)
            logging.warning(log_str)

            if bid_price >= upper_price:
                if coin_balance >= trading_volume * 0.95:
                    log_str = str(t) + ': ' + 'parameter: sell with buy ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(sell_fee) + ')\n'
                    print (log_str)
                    logging.warning(log_str)

                    eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, sell_t_volume, stay_profitable, double_fee, sell_fee, t)
                    if eval_result == "close": # why is this return value close?
                        try:
                            exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                            log_str = str(t) + ': ' + 'Sell ' + coin_pair + '(sell_price=' + str(bid_price) + ', bot_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                            print (log_str)
                            logging.warning(log_str)
                    else:
                        print (log_str)
                        logging.warning(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in sell with buy\n")
                else:
                    print (log_str)
                    logging.warning(str(t) + ': ' + coin_pair + ': ' + "coin balance is less than trading volume in sell with buy\n")
            else:
                print (log_str)
                logging.warning(str(t) + ': ' + coin_pair + ': ' + "bid price is less than upper price in sell with buy\n")
        elif order_type == "sell":
            log_str = str(t) + ': ' + 'compare: buy with sell ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n'
            print (log_str)
            logging.warning(log_str)

            if ask_price <= lower_price:
                if base_balance >= 0.95 * trading_volume * ask_price:
                    log_str = str(t) + ': ' + 'parameter: buy with sell ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_price)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(buy_fee) +')\n'
                    print (log_str)
                    logging.warning(log_str)

                    eval_result = eval_bb_trading_cond(bot_id, 'lower', ask_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, buy_t_volume, stay_profitable, double_fee, buy_fee, t)
                    if eval_result == "close":
                        try:
                            exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                            log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                        except:
                            log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order\n"
                        print (log_str)
                        logging.warning(log_str)
                    else:
                        print (log_str)
                        logging.warning(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in buy with sell\n")
                else:
                    print (log_str)
                    logging.warning(str(t) + ': ' + coin_pair + ': ' + "base balance is less than trading volume in buy with sell\n")
            else:
                print (log_str)
                logging.warning(str(t) + ': ' + coin_pair + ': ' + "ask price is greater than lower price in buy with sell\n")
    else: # if there is no order with the create status
        if base_balance >= 0.95 * trading_volume * ask_price:
            log_str = str(t) + ': ' + 'compare: buy without none ' + coin_pair + '(e_price=' +str(ask_price)+', bb_price='+str(lower_price)+', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+')\n'
            print (log_str)
            logging.warning(log_str)

            if ask_price <= lower_price:
                log_str = str(t) + ': ' + 'parameter: buy without none ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(upper_dev) + ', bb_l_dev=' + str(lower_dev) + ', balance:' + selected_coin + '=' + str(coin_balance) + ' ' + base_currency + '=' + str(base_balance) + ', fee=' + str(buy_fee) + ')\n'
                print (log_str)
                logging.warning(log_str)

                eval_result = eval_bb_trading_cond(bot_id, "lower", ask_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, buy_t_volume, stay_profitable, double_fee, buy_fee, t)
                if eval_result == "open":
                    try:
                        exchange_obj.create_market_buy_order(coin_pair, buy_t_volume)
                        log_str = str(t) + ': ' + 'Buy ' + coin_pair + '(e_price=' + str(ask_price) + ', bb_price=' + str(lower_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(buy_fee) +')\n'
                    except:
                        log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating buy order"
                    logging.warning(log_str)
                    print (log_str)
                else:
                    logging.warning(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in buy with none\n")
                    print (log_str)
            else:
                logging.warning(str(t) + ': ' + coin_pair + ': ' + "ask price is greater than lower price in buy with none\n")
                print (log_str)
        else:
            logging.warning(str(t) + ': ' + coin_pair + ': ' + "base balance is less than trading volume in sell with none\n")
            print (log_str)
        if coin_balance >= 0.95 * trading_volume:
            log_str = str(t) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+')\n'
            logging.warning(log_str)
            print (log_str)

            if bid_price >= upper_price:
                log_str = str(t) + ': ' + 'compare: sell without none ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                logging.warning(log_str)
                print (log_str)

                eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, sell_t_volume, stay_profitable, double_fee, sell_fee, t )
                if eval_result == "open":
                    try:
                        exchange_obj.create_market_sell_order(coin_pair, sell_t_volume)
                        log_str = str(t) + ': ' + 'Sell ' + coin_pair + '(e_price=' + str(bid_price) + ', bb_price=' + str(upper_price) + ', bb_u_dev='+str(upper_dev)+', bb_l_dev='+str(lower_dev)+', balance:'+selected_coin+'='+str(total_balance[selected_coin]['total'])+' '+base_currency+'='+str(total_balance[base_currency]['total'])+', balance:'+selected_coin+'='+str(coin_balance)+' '+base_currency+'='+str(base_balance)+', fee='+ str(sell_fee) +')\n'
                    except:
                        log_str = str(t) + ': ' + coin_pair + ': ' + exchange + "API Error occurred while creating sell order"
                    logging.warning(log_str)
                    print (log_str)
                else:
                    logging.warning(str(t) + ': ' + coin_pair + ': ' + "parameter compare failed in sell with none\n")
                    print (log_str)
            else:
                logging.warning(str(t) + ': ' + coin_pair + ': ' + "bid price is less than upper price in sell with none\n")
                print (log_str)
        else:
            logging.warning(str(t) + ': ' + coin_pair + ': ' + "coin balance is less than trading volume in sell with none\n")
            print (log_str)


def run_Indicator_MACD_bot(bot, exchange):
    return
def run_Indicator_RSI_bot(bot, exchange):
    return

#######################################################

def eval_bb_trading_cond(bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper, trading_volume, stay_profitable, double_fee, exchange_fee, time):
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
    if interval == "1m":
        can_interval = 60000
    if interval == "5m":
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

if __name__ == "__main__":
    query_conn.execute("select absID from bot where bot_status='On' and bot_type='Live'")
    records = query_conn.fetchall()
    db_conn.commit()
    if query_conn.rowcount > 0:
        for bot_iterator in records:
            t = Thread(target=run_bot_thread, args=(bot_iterator[0],))
            threads.append(t)
            t.setDaemon(True)
            t.start()
    while True:
        pass