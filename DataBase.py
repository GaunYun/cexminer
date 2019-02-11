###############################################################
# import necessary packages
###############################################################
import mysql.connector
from mysql.connector import errorcode
import logging
import os

###############################################################
# Declare global variables
###############################################################

class DataBase():
    ###############################################################
    # Configure necessary info
    ###############################################################
    def __init__(self):
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_password = ''
        self.db_name = 'coin_trading_bot'
        self.sql = ''

        self.dirname, self.filename = os.path.split(os.path.abspath(__file__))
        logfile = self.dirname + '../../../debug.log'
        logging.basicConfig(format='%(asctime)s -> %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p', filename=logfile, level=logging.DEBUG)
        self.log = logging.getLogger(__name__)

        # DB connection
        try:
            self.cnx = mysql.connector.Connect(host=self.db_host, database=self.db_name, user=self.db_user, password=self.db_password)
            self.cnx.autocommit = True
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as error:
            if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print 'Something is wrong with your DB user name or password.'
                self.log.error('Something is wrong with your DB user name or password.')
            elif error.errno == errorcode.ER_BAD_DB_ERROR:
                print 'DB does not exist'
                self.log.error('DB does not exist')
            else:
                print error
                self.log.error(error)
        else:
            print 'DB connected!'
            self.log.info('DB connected!')
            try:
                exchange_sql = "CREATE TABLE IF NOT EXISTS `exchange_info` (" \
                               "`exchange_id` int(4) NOT NULL AUTO_INCREMENT, " \
                               "`name` varchar(20) NOT NULL, " \
                               "`api_key` varchar(150) NOT NULL, " \
                               "`secret_key` varchar(150) NOT NULL," \
                               "PRIMARY  KEY (`exchange_id`)" \
                               ") DEFAULT CHARSET=utf8"
                self.cursor.execute(exchange_sql)

                bot_sql = "CREATE TABLE IF NOT EXISTS `bot` (" \
                          "`bot_id` bigint NOT NULL AUTO_INCREMENT, " \
                          "`status` int(1) NOT NULL DEFAULT 0, " \
                          "`name` varchar(20) NOT NULL, " \
                          "`exchange_id` int(4) NOT NULL, " \
                          "`strategy_tb` varchar(20) NOT NULL," \
                          "`pair` varchar(15) NOT NULL, " \
                          "`trading_volume` float NOT NULL, " \
                          "`order_type` varchar(12) NOT NULL DEFAULT 'limit', " \
                          "`disallow_buy_higher` int(1) DEFAULT 1," \
                          "`disallow_sell_cheaper` int(1) DEFAULT 1," \
                          "`check_double_fee` int(1) DEFAULT 1," \
                          "`stay_profitable` int(1) DEFAULT 1," \
                          "`take_profit` float NOT NULL," \
                          "`stop_loss` float NOT NULL, " \
                          "PRIMARY  KEY (`bot_id`)" \
                          ") DEFAULT CHARSET=utf8"
                self.cursor.execute(bot_sql)

                bollinger_sql = "CREATE TABLE IF NOT EXISTS `bollinger_bands` (" \
                                "`ID` bigint NOT NULL AUTO_INCREMENT," \
                                "`bot_id` bigint NOT NULL, " \
                                "`period` float DEFAULT 20," \
                                "`upper` float DEFAULT 2, " \
                                "`lower` float DEFAULT 2, " \
                                "PRIMARY KEY (`ID`)" \
                                ") DEFAULT CHARSET=utf8"
                self.cursor.execute(bollinger_sql)

                trading_history_sql = "CREATE TABLE IF NOT EXISTS `trading_history` (" \
                              "`ID` bigint NOT NULL AUTO_INCREMENT, " \
                              "`order_id` bigint NOT NULL, " \
                              "`bot_id` bigint NOT NULL, " \
                              "`time` datetime NOT NULL, " \
                              "`type` varchar(10) NOT NULL, " \
                              "`side` varchar(4) NOT NULL, " \
                              "`price` float NOT NULL, " \
                              "`filled` float NOT NULL," \
                              "`fee` float NOT NULL, " \
                              "`profit` float NOT NULL, " \
                              "`total` float NOT NULL, " \
                              "PRIMARY KEY (`ID`)" \
                              ") DEFAULT CHARSET=utf8"
                self.cursor.execute(trading_history_sql)

                historical_sql = "CREATE TABLE IF NOT EXISTS `historical_data` (" \
                            "`ID` bigint NOT NULL AUTO_INCREMENT, " \
                            "`time` datetime NOT NULL, " \
                            "`exchange_id` int(4) NOT NULL, " \
                            "`interval` varchar(4) NOT NULL, " \
                            "`pair` varchar(15) NOT NULL, " \
                            "`volume` float NOT NULL, " \
                            "`open` float NOT NULL," \
                            "`close` float NOT NULL," \
                            "`high`  float NOT NULL," \
                            "`low`  float NOT NULL, " \
                            "PRIMARY KEY (`ID`)" \
                            ") DEFAULT CHARSET=utf8"
                self.cursor.execute(historical_sql)

                price_sql = "CREATE TABLE IF NOT EXISTS `price_history` (" \
                            "`ID` bigint NOT NULL AUTO_INCREMENT, " \
                            "`time` bigint NOT NULL, " \
                            "`exchange_id` int(4) NOT NULL," \
                            "`pair` varchar(15) NOT NULL, " \
                            "`bid_price` float NOT NULL," \
                            "`ask_price` float NOT NULL," \
                            "PRIMARY KEY (`ID`)" \
                            ") DEFAULT CHARSET=utf8"
                self.cursor.execute(price_sql)
            except mysql.connector.Error as error:
                self.log.error(error)
            else:
                self.log.info('Tables initialized!')

    ###############################################################
    # Define DB functions
    ###############################################################
    def set_query(self, sql):
        self.sql = sql

    def get_query(self):
        return self.sql

    # Just execute sql queries, like insert & update
    def write(self):
        if self.sql == '':
            return False
        sql = self.sql
        self.sql = ''
        try:
            self.cursor.execute(sql)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.log.error('Invalid field error occurred while running SQL query')
            elif err.errno == errorcode.ER_BAD_TABLE_ERROR:
                self.log.error('Invalid table error occurred while running SQL query')
            else:
                self.log.error(err)
                self.log.debug('Here is the query "' + sql + '"')
            return False
        else:
            self.log.info('SQL query executed successfully!' + ' "' + sql + '"')
            return True

    # Execute sql queries with fetch, like select
    def read(self, fetch='all'):
        if self.sql == '':
            return None
        sql = self.sql
        self.sql = ''
        try:
            self.cursor.execute(sql)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_FIELD_ERROR:
                self.log.error('Invalid field error occurred while running SQL query')
            elif err.errno == errorcode.ER_BAD_TABLE_ERROR:
                self.log.error('Invalid table error occurred while running SQL query')
            else:
                self.log.error(err)
                self.log.debug('Here is the query "' + sql + '"')
            return None
        else:
            self.log.info('SQL query executed successfully!' + ' "' + sql + '"')
            if fetch == 'all':
                return self.cursor.fetchall()
            elif fetch == 'one':
                return self.cursor.fetchone()

    # Add exchange platform info, like name, api key and secret key
    def add_exchange_platform(self, name, api_key, secret_key):
        sql = "INSERT INTO `exchange_info` (`name`, `api_key`, `secret_key`) VALUE ('{0}', '{1}', '{2}')".format(
            name, api_key, secret_key)
        self.sql = sql
        self.write()

    # Add a bot with detail BOT parameters
    def add_bot(self, name, status, exchange_id, strategy_tb, pair, trading_volume, order_type, disallow_buy_higher,
                disallow_sell_cheaper, check_double_fee, stay_profitable, take_profit, stop_loss):
        sql = "INSERT INTO `bot` " \
              "(`name`, `status`, `exchange_id`, `strategy_tb`, `pair`, `trading_volume`, `order_type`, `disallow_buy_higher`, `disallow_sell_cheaper`, `check_double_fee`, `stay_profitable`, `take_profit`, `stop_loss`) " \
              "VALUE ('{0}', {1}, '{2}', '{3}', {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}})".format(name, status, exchange_id,
                                                                                            strategy_tb, pair,
                                                                                            trading_volume,
                                                                                            order_type,
                                                                                            disallow_buy_higher,
                                                                                            disallow_sell_cheaper,
                                                                                            check_double_fee,
                                                                                            stay_profitable,
                                                                                            take_profit, stop_loss)
        self.sql = sql
        self.write()

    # Assign a model to the bot, actually, add the bot to the corresponding trading model table with detail MODEL parameters
    def add_bot_to_model(self, bot_id=0, tb_name='bollinger_bands', params=[]):
        sql = "INSERT INTO `{0}`".format(tb_name)
        if tb_name == 'bollinger_bands':
            sql += " (`bot_id`, `length`, `upper`, `lower`)"
            sql += " VALUE ({0}, {1}, {2}, {3})".format(bot_id, params["length"], params["upper"], params["lower"])
            self.sql = sql
            self.write()

    # Assign a model to the bot, actually, add the bot to the corresponding trading model table with detail MODEL parameters
    def add_price_to_history(self, time, exchange_id, pair, bid_price, ask_price):
        sql = "INSERT INTO `{0}`".format("price_history")
        sql += " (`time`, `exchange_id`, `pair`, `bid_price`, `ask_price`)"
        sql += " VALUE ({0}, {1}, '{2}', {3}, {4})".format(time, exchange_id, pair, bid_price, ask_price)
        self.sql = sql
        self.write()

    def init_sql(self):
        return

#DataBase()
#add_exchange_platform('binance', 'PMAA6594W2Gx2PK1wMhpWhfgxMxnLV56BPvD005EIw6awc3OBFsAncVsEFsQrJYt', 'ZXU6Eg6AQHYPyAx4zL22EjjyZatmcvvuZnx8YqmxFQa4lgDdwqy8CscnL8ktPZmh')
#add_bot('Bin_ADA_USDT', 1, 'bollinger_bands', 'ADA/USDT', 300, 1, 1, 1, 1, 2, 10)
params = {"length": 20, "upper": 2, "lower": 2}
#add_bot_to_model(bot_id=1, params=params)