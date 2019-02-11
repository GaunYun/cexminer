###############################################################
# import necessary packages
###############################################################
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
import mysql.connector
import datetime
import time
import ccxt
import numpy as np

###############################################################
# Configure necessary info
###############################################################

###############################################################
# Declare global variables
###############################################################

###############################################################
# Declare Classes and Functions
###############################################################
class Boll_Bands:
    # Public Variables
    query = ""

    def __init__(self, store):
        self.store = store

    def run(self, bot_id, ):
        store = self.store
        store.log.info('Running bot id =' + str(bot_id) + ' with Bollinger Bands ...')

        log_str = ""
        ############   Return Bot parameters with Dictionary Type
        ## Field names are as follow:
        # bot_status
        # exchange
        # api_key
        # secret_key
        # stragegy
        # pair : =bot_info['pair']ex:BTC/USDT
        # trading_volume
        # order_type
        # buy_higher
        # sell_cheaper
        # double_fee
        # profitable
        # take_profit
        # stop_loss

        bot_info = self.get_bot_info(self, bot_id)

        ############ Return bollinger band parameter based on Dictionary Type
        ## Fields are as below
        # period
        # upper
        # lower
        strategy_info = self.get_bollinger_info(self, bot_id)

        ############ Return Current Coin Data based on Dictionary Type and Check Order Status
        ## Fields are as below
        # bid_price
        # ask_price
        # timestamp  ex: 1530000000000
        # date_time   ex: '2018-07-05 16:05:45'
        # coin_balance
        # base_balance
        # sell_fee
        # buy_fee
        # order_status

        coin_data = self.get_coin_data(self, bot_id, bot_info['exchange'], bot_info['pair'], bot_info['api_key'], bot_info['secret_key'])
        if coin_data['order_status'] == "open":
            return
        ########## Return History Data from DB    *** Add present price of coin in last position
        ##
        history_data = self.get_hist_data(self, bot_info['exchange_id'], bot_info['pair'], coin_data['bid_price'], coin_data['ask_price'])
        if history_data is None:
            return

        # ********* Logice Start **********
        if bot_info['exchange'] == "binance":
            exchange_obj = ccxt.binance({
                'proxies': {
                    'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                },
                'apiKey': bot_info['api_key'],
                'secret': bot_info['secret_key'],
            })
        buy_t_volume = min(coin_data['base_balance'] / coin_data['ask_price'], bot_info['trading_volume'])
        sell_t_volume = min(coin_data['coin_balance'], bot_info['trading_volume'])
        query = "select count(order_id) from trading_history where bot_id=%d" % (bot_id,)
        store.set_query(query)
        order_count = store.read()
        bid_avg = np.mean(history_data['bid'])
        bid_dev = np.std(history_data['bid'])
        bid_upper_price = round(bid_avg + bid_dev * strategy_info[1], 8)
        bid_lower_price = round(bid_avg + bid_dev * strategy_info[2], 8)
        ask_avg = np.mean(history_data['ask'])
        ask_dev = np.std(history_data['ask'])
        ask_upper_price = round(ask_avg + ask_dev * strategy_info[1], 8)
        ask_lower_price = round(ask_avg + ask_dev * strategy_info[2], 8)
        if divmod(int(order_count), 2)[1] == 0:
            if coin_data['base_balance'] >= 0.95 * bot_info['trading_volume'] * coin_data['ask_price']:
                log_str = str(coin_data['date_time']) + ': ' + 'compare: buy without none ' + bot_info['pair'] + \
                          '(e_price=' + str(coin_data['ask_price']) + ', bb_price=' + str(ask_lower_price) + \
                          ', bb_u_dev=' + str(strategy_info['upper']) + ', bb_l_dev=' + str(ask_lower_price) + ', balance:' + \
                          bot_info['pair'].split("/")[0] + '=' + str(coin_data['coin_balance']) + \
                          ' ' + bot_info['pair'].split("/")[1]+ '=' + str(coin_data['base_balance']) + ')\n'
                store.log.info(log_str)
                if coin_data['ask_price'] <= ask_lower_price:
                    log_str = str(coin_data['date_time']) + ': ' + 'parameter: buy without none ' + bot_info['pair'] + \
                              '(e_price=' + str(coin_data['ask_price']) + ', bb_price=' + str(ask_lower_price) + ', bb_u_dev=' + \
                              str(strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + \
                              bot_info['pair'].split("/")[0] + '=' + str(coin_data['coin_balance']) + ' ' + \
                              bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(coin_data['buy_fee']) + ')\n'
                    store.log.info(log_str)

                    eval_result = self.eval_bb_trading_cond(self, 0, bot_id, "lower", coin_data['ask_price'], coin_data['last_buy_price'],
                                                            coin_data['last_sell_price'], coin_data['buy_higher'], coin_data['sell_cheaper'], buy_t_volume, bot_info['profitable'],
                                                       coin_data['double_fee'], coin_data['buy_fee'], coin_data['date_time'])
                    if eval_result == "open":
                        try:
                            order_id = exchange_obj.create_limit_buy_order(bot_info['pair'], buy_t_volume, coin_data['ask_price'])
                            query = "insert into trading_history (`order_id`, `bot_id`, `time`, `type`, `side`, " \
                                    "`price`, `filled`, `fee`, `profit`, `total`) " \
                                    "values (%d, %d, %s, %s, %s, %s, %s, %s, %s, %s)" % \
                                    (order_id, bot_id, coin_data['date_time'], 'market', 'sell', coin_data['bid_price'],
                                     0, coin_data['sell_fee'], '', '')
                            store.set_query(query)
                            store.write()
                            log_str = str(coin_data['date_time']) + ': ' + 'Buy ' + bot_info['pair'] + '(e_price=' + \
                                      str(coin_data['ask_price']) + ', bb_price=' + str(ask_lower_price) + ', bb_u_dev=' + \
                                      str(strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] +\
                                      '=' + str(coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + \
                                      ', fee=' + str( coin_data['buy_fee']) + ')\n'
                        except:
                            log_str = str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + bot_info['exchange'] + "API Error occurred while creating buy order"
                        store.log.info(log_str)
                    else:
                        store.log.info(str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "parameter compare failed in buy with none\n")
                else:
                    store.log.info(str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "ask price is greater than lower price in buy with none\n")
            else:
                store.log.info(str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "base balance is less than trading volume in sell with none\n")
            if coin_data['coin_balance'] >= 0.95 * bot_info['trading_volume']:
                log_str = str(coin_data['date_time']) + ': ' + 'compare: sell without none ' + bot_info['pair']+ '(e_price=' + str(
                    coin_data['bid_price']) + ', bb_price=' + str(ask_lower_price) + ', bb_u_dev=' + str(
                    strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(
                    coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ')\n'
                store.log.info(log_str)

                if coin_data['bid_price'] >= bid_upper_price:
                    log_str = str(coin_data['date_time']) + ': ' + 'compare: sell without none ' + bot_info['pair']+ '(e_price=' + str(
                        coin_data['bid_price']) + ', bb_price=' + str(ask_lower_price) + ', bb_u_dev=' + str(
                        strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(
                        coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(coin_data['sell_fee']) + ')\n'
                    store.log.info(log_str)

                    eval_result = self.eval_bb_trading_cond(self, bot_id, "upper", coin_data['bid_price'], coin_data['last_buy_price'], coin_data['last_sell_price'],
                                                       bot_info['buy_higher'], bot_info['sell_cheaper'], sell_t_volume,
                                                            bot_info['profitable'],  bot_info['double_fee'], coin_data['sell_fee'], coin_data['date_time'])
                    if eval_result != "":
                        try:
                            order_id = exchange_obj.create_limit_sell_order(bot_info['pair'], sell_t_volume, coin_data['bid_price'])
                            query = "insert into trading_history (`order_id`, `bot_id`, `time`, `type`, `side`, " \
                                    "`price`, `filled`, `fee`, `profit`, `total`) " \
                                    "values (%d, %d, %s, %s, %s, %s, %s, %s, %s, %s)" % \
                                    (order_id, bot_id, coin_data['date_time'], 'market', 'sell', coin_data['bid_price'], 0,coin_data['sell_fee'], '', '')
                            store.set_query(query)
                            store.write()
                            log_str = str(coin_data['date_time']) + ': ' + 'Sell ' + bot_info['pair']+ '(e_price=' + str(
                                coin_data['bid_price']) + ', bb_price=' + str(ask_lower_price) + ', bb_u_dev=' + str(
                                strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(
                                coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(
                                coin_data['base_balance']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(
                                coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                coin_data['sell_fee']) + ')\n'
                        except:
                            log_str = str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + coin_data['exchange'] + "API Error occurred while creating sell order"
                        store.log.info(log_str)
                    else:
                        store.log.info(str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "parameter compare failed in sell with none\n")
                else:
                    store.log.info(
                        str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "bid price is less than upper price in sell with none\n")
            else:
                store.log.info(
                    str(coin_data['date_time']) + ': ' + bot_info['pair']+ ': ' + "coin balance is less than trading volume in sell with none\n")
            if coin_data['bid_price'] >= bid_upper_price:
                if coin_data['order_type'] == "market":
                    trading_volume = self.get_new_volume(bot_info['exchange'], bot_info['pair'], bot_info['api_key'],
                                                         bot_info['secret_key'], coin_data['bid_price'])
                    trading_volume = min(bot_info['trading_volume'], trading_volume)
                    if coin_data['coin_balance'] >= 0.95 * trading_volume:
                        trading_volume = min(coin_data['coin_valance'], trading_volume)
                        result = self.eval_bb_trading_cond(self, 0, bot_info['bot_id'], 'upper', coin_data['bid_price'], coin_data['last_buy_price'], coin_data['last_sell_price'], bot_info['buy_higher'], bot_info['sell_cheaper'],
                                                   trading_volume, bot_info['profitable'], bot_info['double_fee'], coin_data['sell_fee'], coin_data['date_time'])
                        if result == "ok":
                            order_id = exchange_obj.create_market_sell_order(bot_info['pair'], trading_volume)
                            query = "insert into trading_history (`order_id`, `bot_id`, `time`, `type`, `side`, `price`, `filled`, `fee`, `profit`, `total`) values (%d, %d, %s, %s, %s, %s, %s, %s, %s, %s)" % (order_id, bot_id, coin_data['date_time'], 'market', 'sell', coin_data['bid_price'], 0, coin_data['sell_fee'], )
        else:
            query = "select order_id, side from trading_history where bot_id=%d order by time desc" % (bot_id,)
            store.set_query(query)
            temp_data = store.read()
            order_id = temp_data[0][0]
            side = temp_data[0][1]
            if side == "buy":                
                log_str = str(coin_data['date_time']) + ': ' + 'compare: sell with buy ' + bot_info['pair'] + '(e_price=' + str(coin_data['bid_price']) + ', bb_price=' + str(bid_upper_price) + ', bb_u_dev=' + str(strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ')\n'
                store.log.info(log_str)

                if coin_data['bid_price'] >= bid_upper_price:
                    # if coin_balance >= trading_volume * 0.95:
                    if coin_data['coin_balance'] > 0:
                        log_str = str(coin_data['date_time']) + ': ' + 'parameter: sell with buy ' + bot_info['pair'] + '(e_price=' + str(bid_price) + ', bb_price=' + str(bid_upper_price) + ', bb_u_dev=' + str(strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(coin_data['coin_balance']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(coin_data['sell_fee']) + ')\n'
                        store.log.info(log_str)

                        eval_result = self.eval_bb_trading_cond(self, bot_id, "upper", bid_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, sell_t_volume, stay_profitable,
                                                           double_fee, sell_fee, t)
                        if eval_result == "close":  # why is this return value close?
                            try:
                                exchange_obj.create_market_sell_order(bot_info['pair'], sell_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Sell ' + bot_info['pair'] + '(sell_price=' + str(
                                    bid_price) + ', bot_price=' + str(bid_upper_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    sell_fee) + ')\n'
                            except:
                                log_str = str(
                                    t) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                            store.log.info(log_str)
                        else:
                            add_bot_log(str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "parameter compare failed in sell with buy\n")
                    else:
                        add_bot_log(str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "coin balance is less than trading volume in sell with buy\n")
                else:
                    if bid_price >= (buy_price + float(profit) * buy_price / 100):
                        eval_result = eval_bb_trading_cond(bot_id, "upper", bid_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, sell_t_volume, stay_profitable,
                                                           double_fee, sell_fee, t)
                        if eval_result == "close":  # why is this return value close?
                            try:
                                exchange_obj.create_market_sell_order(bot_info['pair'], sell_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Sell ' + bot_info['pair'] + '(sell_price=' + str(
                                    bid_price) + ', bot_price=' + str(bid_upper_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    sell_fee) + ')\n'
                            except:
                                log_str = str(t) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                            store.log.info(log_str)
                        else:
                            add_bot_log(str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "parameter compare failed in sell with buy\n")
                    else:
                        if bid_price <= (buy_price - float(stop_loss) * buy_price / 100):
                            try:
                                exchange_obj.create_market_sell_order(bot_info['pair'], sell_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Sell ' + bot_info['pair'] + ' for stop_loss (sell_price=' + str(
                                    bid_price) + ', bot_price=' + str(bid_upper_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    sell_fee) + ')\n'
                            except:
                                log_str = str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating sell order in sell with buy\n"
                        else:
                            add_bot_log(str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "bid price is less than upper price in sell with buy\n")

            elif side == "sell":
                ### add ask_price to history data for buying with sell order
                # hist_data.append([cur_time, 0, 0, 0, ask_price, 0])
                # for i in range(0, period):
                #    bb_temp.append(hist_data[i][4])
                avg = np.mean(ask_hist_data)  # avg = np.mean(bb_temp)
                stand_dev = np.std(ask_hist_data)  # stand_dev = np.std(bb_temp)
                upper_price = round(avg + stand_dev * upper_dev, 8)
                lower_price = round(avg + stand_dev * lower_dev, 8)

                buy_order_book = exchange_obj.fetch_order_book(coin_pair)['asks']
                for order in buy_order_book:
                    if order[0] <= ask_price:
                        trading_volume += float(order[1])
                    else:
                        break

                buy_t_volume = min(base_balance, trading_volume * coin_data['ask_price'])

                log_str = str(coin_data['date_time']) + ': ' + 'compare: buy with sell ' + bot_info['pair'] + '(e_price=' + str(
                    coin_data['ask_price']) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(
                    strategy_info['upper']) + ', bb_l_dev=' + str(strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                    total_balance[selected_coin]['total']) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(
                    total_balance[base_currency]['total']) + ')\n'
                store.log.info(log_str)

                if ask_price <= lower_price:
                    # if base_balance >= 0.95 * trading_volume * ask_price:
                    if base_balance > 0:
                        log_str = str(coin_data['date_time']) + ': ' + 'parameter: buy with sell ' + bot_info['pair'] + '(e_price=' + str(
                            coin_data['ask_price']) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(
                            strategy_info['upper']) + ', bb_l_dev=' + str(lower_price) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                            coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                            buy_fee) + ')\n'
                        store.log.info(log_str)

                        eval_result = eval_bb_trading_cond(bot_id, 'lower', ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, buy_t_volume, stay_profitable,
                                                           double_fee, buy_fee, t)
                        if eval_result == "close":
                            try:
                                exchange_obj.create_market_buy_order(bot_info['pair'], buy_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Buy ' + bot_info['pair'] + '(e_price=' + str(
                                    coin_data['ask_price']) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    buy_fee) + ')\n'
                            except:
                                log_str = str(
                                    t) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating buy order\n"
                            store.log.info(log_str)
                        else:
                            add_bot_log(
                                str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "parameter compare failed in buy with sell\n")
                    else:
                        add_bot_log(str(
                            t) + ': ' + bot_info['pair'] + ': ' + "base balance is less than trading volume in buy with sell\n")
                else:
                    if ask_price <= (sell_price - float(profit) * sell_price / 100):
                        print("take profit success")
                        eval_result = eval_bb_trading_cond(bot_id, 'lower', ask_price, last_buy_price, last_sell_price,
                                                           buy_higher, sell_cheaper, buy_t_volume, stay_profitable,
                                                           double_fee, buy_fee, t)
                        if eval_result == "close":
                            try:
                                exchange_obj.create_market_buy_order(bot_info['pair'], buy_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Buy ' + bot_info['pair'] + '(e_price=' + str(
                                    coin_data['ask_price']) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    buy_fee) + ')\n'
                            except:
                                log_str = str(  t) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating buy order\n"
                            store.log.info(log_str)
                        else:
                            add_bot_log(str(coin_data['date_time']) + ': ' + bot_info['pair'] + ': ' + "parameter compare failed in buy with sell\n")
                    else:
                        if coin_data['ask_price'] >= (coin_data['sell_price'] + float(bot_info['stop_loss']) * coin_data['sell_price'] / 100):
                            try:
                                exchange_obj.create_market_buy_order(bot_info['pair'], buy_t_volume)
                                log_str = str(coin_data['date_time']) + ': ' + 'Buy ' + bot_info['pair'] + '(e_price=' + str(
                                    coin_data['ask_price']) + ', bb_price=' + str(lower_price) + ', bb_u_dev=' + str(
                                    strategy_info['upper']) + ', bb_l_dev=' + str(
                                    strategy_info['lower']) + ', balance:' + bot_info['pair'].split("/")[0] + '=' + str(
                                    coin_balance) + ' ' + bot_info['pair'].split("/")[1] + '=' + str(coin_data['base_balance']) + ', fee=' + str(
                                    buy_fee) + ')\n'
                            except:
                                log_str = str(
                                    t) + ': ' + bot_info['pair'] + ': ' + exchange + "API Error occurred while creating buy order\n"
                            store.log.info(log_str)
                        else:
                            add_bot_log(str(
                                t) + ': ' + bot_info['pair'] + ': ' + "ask price is greater than lower price in buy with sell\n")



        return
    def get_bot_info(self, bot_id):
        store = self.store
        store.log.info('Run get_bot_info() ...')
        query = "select bot.*, bollinger_bands.period, bollinger_bands.upper, bollinger_bands.lower from bot inner join bollinger_bands on bot.bot_id=bollinger_bands.bot_id where bot.bot_id=%d" % (bot_id,)
        store.set_query(query)
        bot_obj = store.read()
        status = bot_obj[1]
        exchange_id = bot_obj[3]
        stragegy_tb = bot_obj[4]
        pair = bot_obj[5]
        trading_volume = bot_obj[6]
        order_type = bot_obj[7]
        buy_higher = bot_obj[8]
        sell_cheaper = bot_obj[9]
        double_fee = bot_obj[10]
        profitable = bot_obj[11]
        take_profit = bot_obj[12]
        stop_loss = bot_obj[13]

        ####### Get Api Key and Secret Key
        query = "select api_key, secret_key, name from exchange_info where exchange_id=%d" % (exchange_id,)
        store.set_query(query)
        exchange_obj = store.read()
        api_key = exchange_obj[0]
        secret_key = exchange_obj[1]
        exchange = exchange_obj[2]

        ######### Last Buy Price and Last Sell Price
        query = "select price from trading_history where bot_id=%d and side=%s order by time desc" % (bot_id, 'Buy')
        store.set_query(query)
        p = store.read()
        if p is None:
            last_buy_price = 0
        else:
            last_buy_price = store.read()[0][0]
        query = "select price from trading_history where bot_id=%d and side=%s order by time desc" % (bot_id, 'Sell')
        store.set_query(query)
        p = store.read()
        if p is None:
            last_sell_price = 0
        else:
            last_sell_price = store.read()[0][0]
        context = {
            'bot_status': status,
            'exchange': exchange,
            'api_key': api_key,
            'secret_key': secret_key,
            'strategy': stragegy_tb,
            'pair': pair,
            'trading_volume': trading_volume,
            'order_type': order_type,
            'buy_higher': buy_higher,
            'sell_cheaper': sell_cheaper,
            'double_fee': double_fee,
            'profitable': profitable,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'last_buy_price': last_buy_price,
            'last_sell_price': last_sell_price
        }
        return context
    def get_bollinger_info(self, bot_id):
        store = self.store
        store.log.info('Run get_bollinger_info ...')

        query = "select period, upper, lower from bollinger_bands where bot_id=%d" % (bot_id,)
        store.set_query(query)
        bollinger_data = store.read()

        context = {
            'period': bollinger_data[0],
            'upper': bollinger_data[1],
            'lower': bollinger_data[2]
        }
        return context
    def get_coin_data(self, bot_id, exchange, pair, api_key, secret_key):
        store = self.store
        store.log.info('Run get_bollinger_info ...')
        if exchange == "binance":
            exchange_obj = ccxt.binance({
                'proxies': {
                    'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                },
                'apiKey': api_key,
                'secret': secret_key,
            })
            cur_data = exchange_obj.fetch_ticker(pair)
            bid_price = float(cur_data['info']['bidPrice'])
            ask_price = float(cur_data['info']['askPrice'])
            cur_timestamp = cur_data['timestamp']
            cur_standard_time = datetime.datetime.fromtimestamp(cur_timestamp/1000)

            total_balance = exchange_obj.fetch_balance()
            base_balance = float(total_balance[pair.split("/")[1]]['total'])
            coin_balance = float(total_balance[pair.split("/")[0]]['total'])
            
            buy_exchange_fee = exchange_obj.calculate_fee(pair, 'market', 'buy', 1, ask_price, 'maker')
            buy_fee = round(ask_price * float(buy_exchange_fee['rate']), 8)  # is this right, it is necessary to multiply ask_price
            sell_exchange_fee = exchange_obj.calculate_fee(pair, 'market', 'sell', 1, bid_price, 'maker')
            sell_fee = round(bid_price * float(sell_exchange_fee['rate']), 8)

            ###### Check order status
            query = "select order_id from trading_history where bot.bot_id=%d and filled=0" % (bot_id,)
            store.set_query(query)
            order_id = store.read()
            if len(order_id) > 0:
                if exchange == "binance":
                    order_info = exchange_obj.fetch_order(id=order_id[0][0], symbol=pair)
                    order_status = order_info['status']
                    if order_status == "closed":
                        query = "update trading_history set filled=1 where order_id=%d" % (order_id[0][0], )
                        store.set_query(query)
                        store.write()
                    elif order_status == "open":
                        store.log.info("There are open order still ...")

            context = {
                'bid_price': bid_price,
                'ask_price': ask_price,
                'timestamp': cur_timestamp,
                'date_time': cur_standard_time,
                'coin_balance': coin_balance,
                'base_balance': base_balance,
                'sell_fee': sell_fee,
                'buy_fee': buy_fee,                
                'order_status': order_status
            }
            return context
    def get_hist_data(self, exchange_id, pair, period, bid_price, ask_price):
        store = self.store
        store.log.info('Run get_bollinger_info ...')
        bid_hist_data = []
        ask_hist_data = []
        query = "select last_price from price_history where exchange_id=%d and pair=%s order by time" % (exchange_id, pair)
        store.set_query(query)
        temp_data = store.read()

        if len(temp_data) >= (period-1):
            for i in range(len(temp_data) - period + 1, period):
                bid_hist_data.append(temp_data[i][0])
                ask_hist_data.append(temp_data[i][0])
            bid_hist_data.append(bid_price)
            ask_hist_data.append(ask_price)
            context = {
                'bid': bid_hist_data,
                'ask': ask_hist_data
            }
            return context
        else:
            store.log.info('History data is not enough ...')
            return None
    def get_new_volume(self, exchange, pair, api_key, secret_key, side, price):
        store = self.store
        store.log.info('Check open order ...')
        trading_volume = 0.0
        if exchange == "binance":
            exchange_obj = ccxt.binance({
                'proxies': {
                    'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                },
                'apiKey': api_key,
                'secret': secret_key,
            })
        if side == "bids":
            sell_order_book = exchange_obj.fetch_order_book(pair)[side]
            for order in sell_order_book:
                if order[0] >= price:
                    trading_volume += float(order[1])
                else:
                    break
            return trading_volume
        elif side == "asks":
            buy_order_book = exchange_obj.fetch_order_book(pair)[side]
            for order in buy_order_book:
                if order[0] <= price:
                    trading_volume += float(order[1])
                else:
                    break
            return trading_volume
    def check_order(self, bot_id):
        store = self.store
        store.log.info('Check open order ...')

        query = "select order_id from trading_history where bot.bot_id=%d and filled=0" % (bot_id, )
        store.set_query(query)
        order_id = store.read()
        if len(order_id) > 0:
            query = "select exchange_info.name, exchange_info.api_key, exchange_info.secret_key, bot.pair from bot inner join exchange_info on bot.exchange_id=exchange_info.exchange_id where bot.bot_id=%d" % (bot_id, )
            store.set_query(query)
            temp_data = store.read()

            if temp_data[0][0] == "binance":
                exchange_obj = ccxt.binance({
                    'proxies': {
                        'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                    },
                    'apiKey': temp_data[0][1],
                    'secret': temp_data[0][2],
                })
                order_info = exchange_obj.fetch_order(id=order_id[0][0], symbol=temp_data[0][3])
                order_status = order_info['status']

    def eval_bb_trading_cond(self, order_id, bot_id, trend, coin_price, last_buy_price, last_sell_price, buy_higher, sell_cheaper,
                             trading_volume, stay_profitable, double_fee, exchange_fee, time):
        store = self.store
        store.log.info('Evaluate bollinger trading condition ...')
        result_str = ""
        if trend == "lower":
            if order_id == 0:
                if buy_higher == "On" and coin_price > last_sell_price and last_sell_price != 0:
                    return ""
                query = "insert into trading_history (`bot_id`, `order_type`, `order_status`, `buy_time`, `buy_price`, `buy_fee`) values (%d, %s, %s, %s, %s, %s )" % (bot_id, 'buy', 'create', time, coin_price, exchange_fee)
                store.set_query(query)
                store.write()
                result_str = "open"
            else:
                query = "select * from trading_history where order_id=%d" % (order_id,)
                store.set_query(query)
                result = store.read()
                if result[0][5] == "sell":
                    if buy_higher == "On" and coin_price > last_sell_price:
                        return ""
                    if double_fee == "On" and (float(result[0][6]) - float(coin_price)) <= (exchange_fee + float(result[0][8])):
                        return ""
                    if stay_profitable == "On" and coin_price >= result[0][6]:
                        return ""
                    query = "update trading_history set order_status='complete', order_type='buy', buy_price=%s, buy_time=%s, buy_fee=%s where bot_id=%s and order_type='sell' and order_status='create'" % (coin_price, time, exchange_fee, bot_id)
                    store.set_query(query)
                    store.write()
                    result_str = "close"
            return result_str
        elif trend == "upper":
            query = """select * from trading_history where bot_id=%d and order_status='create'""" % (bot_id,)
            store.set_query(query)
            result1 = store.read()
            if len(result1) <= 0:
                if sell_cheaper == "On" and coin_price < last_buy_price and last_buy_price != 0:
                    return ""
                query_conn.execute(
                    """insert into `trading_history` (`bot_id`, `order_type`, `order_status`, `sell_time`, `sell_price`, `sell_fee`) values (%s, %s, %s, %s, %s, %s )""",
                    (bot_id, 'sell', 'create', time, coin_price, exchange_fee))
                db_conn.commit()
                result_str = "open"
            else:
                if result1[0][2] == "buy":
                    buy_price = float(result1[0][6])
                    if sell_cheaper == "On" and coin_price < last_buy_price:
                        return ""
                    if double_fee == "On" and (trading_volume * coin_price - buy_price) < (
                            exchange_fee + result1[0][9]):
                        return ""
                    if stay_profitable == "On" and coin_price < buy_price:
                        return ""
                    query = "update trading_history set order_status='complete', order_type='sell', sell_price=%s, sell_time=%s, sell_fee=%s where bot_id=%s and order_type='buy' and order_status='create'" % (coin_price, time, exchange_fee, bot_id)
                    store.set_query(query)
                    store.write()
                    result_str = "close"
            return result_str


