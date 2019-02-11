# -*- coding: UTF-8 -*-
# @yasinkuyu

# Define Python imports
import os
import sys
import time
import threading
import math
import logging
import logging.handlers
import ccxt

# Define Custom imports
from Database import Database

formater_str = '%(asctime)s,%(msecs)d %(levelname)s %(name)s: %(message)s'
formatter = logging.Formatter(formater_str)
datefmt="%Y-%b-%d %H:%M:%S"

LOGGER_ENUM = {'debug':'debug.log', 'trading':'trades.log','errors':'general.log'}
#LOGGER_FILE = LOGGER_ENUM['pre']
LOGGER_FILE = "binance-trader.log"
FORMAT = '%(asctime)-15s - %(levelname)s:  %(message)s'

logger = logging.basicConfig(filename=LOGGER_FILE, filemode='a',
                             format=formater_str, datefmt=datefmt,
                             level=logging.INFO)

# Aproximated value to get back the commision for sell and buy
TOKEN_COMMISION = 0.001
BNB_COMMISION   = 0.0005
#((eth*0.05)/100)


class Trading():

    # Define trade vars  

    # percent (When you drop 10%, sell panic.)

    # Buy/Sell qty

    # BTC amount

    # float(step_size * math.floor(float(free)/step_size))

    # Define static vars

    # Type of commision, Default BNB_COMMISION

    def __init__(self, option):
        print("options: {0}".format(option))

        # Get argument parse options
        self.option = option

        # Define parser vars
        self.amount = self.option.amount
        self.pair = self.option.symbol
        self.profit = self.option.profit
        self.wait_time = self.option.wait_time

        self.fee = 0.15
        self.firstcoin, self.secondcoin = self.pair.split("/")

        # setup Logger
        self.logger = self.setup_logger(self.option.symbol, debug=self.option.debug)


    def setup_logger(self, symbol, debug=True):
        """Function setup as many loggers as you want"""
        #handler = logging.FileHandler(log_file)
        #handler.setFormatter(formatter)
        #logger.addHandler(handler)
        logger = logging.getLogger(symbol)

        stout_handler = logging.StreamHandler(sys.stdout)
        if debug:
            logger.setLevel(logging.DEBUG)
            stout_handler.setLevel(logging.DEBUG)

        #handler = logging.handlers.SysLogHandler(address='/dev/log')
        #logger.addHandler(handler)
        stout_handler.setFormatter(formatter)
        logger.addHandler(stout_handler)
        return logger

    def create_bot(self):
        start_time = time.time() * 1000
        Database.write("bot", [self.exchange_id, self.pair, self.amount, start_time, self.profit])
        self.logger.info('bot created exchange_id:%d, pair:%s, volume:%f, start_time:%d, profit:%f' % (
            self.exchange_id, self.pair, self.amount, start_time, self.profit))

    def create_order(self):
        while True:
            try:
                balances = self.exchange_client.fetch_balance()
                first_balance = balances[self.firstcoin]['free']
                if (first_balance > self.amount):
                    self.create_bot()

                sql_query = "SELECT bot.bot_id, bot.exchange_id, bot.pair, bot.volume, bot.start_time, bot.profit_percentage, " \
                            "order_history.order_id, order_history.first_balance, order_history.second_balance, order_history.order_type, " \
                            "order_history.timestamp, order_history.filled FROM bot INNER JOIN order_history ON bot.bot_id=order_history.bot_id " \
                            "WHERE order_history.filled=0"
                open_orders = Database.excute_query(sql_query)

                #binance time entry is miliseconds, so unix time stamp has to be multiplied by 1000.

                sql_query = "SELECT min(timestamp) FROM order_history WHERE filled=0"
                timestamp_data = Database.excute_query(sql_query, "one")
                if timestamp_data[0] == None:
                    since_time = 0
                else:
                    since_time = timestamp_data[0] - 1000

                closed_orders = self.exchange_client.fetch_closed_orders(self.pair, since_time)

                for open_order in open_orders:
                    order_id = open_order[6]
                    bot_id = open_order[0]

                    for order in closed_orders:
                        id = order['info']['orderId']
                        if id == order_id:
                            side = order['side']
                            if side == 'buy':   #if a buy order filled, create a new sell order for the profit
                                amount = order['amount']
                                price = order['price']
                                volume = price * amount

                                sell_volume = volume * (100 + self.profit) / 100
                                sell_amount = self.amount
                                sell_price = sell_volume / sell_amount
                                first_profit = amount - sell_amount
                                new_sell_order = self.exchange_client.create_limit_sell_order(self.pair, sell_amount, sell_price)
                                self.logger.info('new sell order created exchange_id:%d, bot_id: %d, pair:%s, order_id:%d, amount:%f, volume:%f, timestamp:%d, price:%f' % (
                                    self.exchange_id, bot_id, self.pair, new_sell_order['info']['orderId'], sell_amount, sell_volume, new_sell_order['timestamp'], sell_price))

                                #update the database of order_history and profit_history
                                filled = 1
                                Database.update("order_history", [filled, id])
                                Database.write("order_history",
                                               [new_sell_order['info']['orderId'], bot_id, sell_amount, sell_volume, new_sell_order['side'],
                                                new_sell_order['timestamp'], 0])
                                Database.write("profit_history", [order['id'], self.firstcoin, first_profit])

                            if side == 'sell': #if a sell order filled, create a new buy order for the profit, and process the last profit
                                amount = order['amount']
                                price = order['price']
                                volume = amount * price
                                buy_amount = order['amount'] * (100 + self.profit) / 100
                                buy_volume = volume * 100 / (100 + self.profit)
                                buy_price = buy_volume / buy_amount
                                second_profit = volume - buy_volume

                                new_buy_order = self.exchange_client.create_limit_buy_order(self.pair, buy_amount, buy_price)
                                self.logger.info(
                                    'new buy order created exchange_id:%d, bot_id: %d, pair:%s, order_id:%d, volume:%f, amount:%f, timestamp:%d, price:%f' % (
                                        self.exchange_id, bot_id, self.pair, new_buy_order['info']['orderId'], buy_volume, buy_amount,
                                        new_buy_order['timestamp'], buy_price))

                                # update the database of order_history and profit_history
                                filled = 1
                                Database.update("order_history", [filled, id])
                                Database.write("order_history",
                                               [new_buy_order['info']['orderId'], bot_id, buy_amount, buy_volume, new_buy_order['side'],
                                                new_buy_order['timestamp'], 0])
                                Database.write("profit_history", [order['id'], self.secondcoin, second_profit])

                sql_query = "SELECT * from bot"
                bots = Database.excute_query(sql_query)

                for bot in bots:
                    bot_id = bot[0]
                    exist_flag = False
                    for open_order in open_orders:
                        if bot_id == open_order[0]:
                            exist_flag = True
                            break

                    if exist_flag == False:
                        # if no order of the bot, create a new buy order for the profit
                        cur_data = self.exchange_client.fetch_ticker(self.pair)
                        amount = self.amount
                        price = cur_data['last'] * (100 + self.profit) / 100
                        new_sell_order = self.exchange_client.create_limit_sell_order(self.pair, amount, price)
                        self.logger.info(
                            'new sell order created exchange_id:%d, bot_id: %d, pair:%s, order_id:%d, volume:%f, timestamp:%d, price:%f' % (
                                self.exchange_id, bot_id, self.pair, new_sell_order['info']['orderId'], self.amount,
                                new_sell_order['timestamp'], price))

                        Database.write("order_history",
                                       [new_sell_order['info']['orderId'], bot_id, amount, price * amount, new_sell_order['side'],
                                        new_sell_order['timestamp'], 0])
                        break

                time.sleep(self.wait_time)
            except:
                print "one exception rasied!"
                time.sleep(60)

    def run(self):

        symbol = self.option.symbol

        print('Auto Trading for Binance.com. @yasinkuyu Thrashformer')
        print('\n')

        print('Started...')
        print('Trading Symbol: %s' % symbol)
        sql_query = "SELECT * from exchange_site"
        datas = Database.excute_query(sql_query)

        for data in datas:
            self.exchange_id = data[0]
            self.site_name = data[1]
            self.api_key = data[2]
            self.secret_key = data[3]
            if self.site_name == 'binance':
                self.exchange_client = ccxt.binance({
                    'apiKey': self.api_key,
                    'secret': self.secret_key,
                })

            self.create_order()
