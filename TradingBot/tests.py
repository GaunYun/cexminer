# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading

import mysql.connector
from django.http import HttpResponse
import datetime
import time
import ccxt
import numpy as np
from operator import itemgetter
#import stripe
import requests
print(datetime.datetime.fromtimestamp(1528869600))
mutex1 = threading.Lock()  # equal to threading.Semaphore(1)
mutex2 = threading.Lock()
t1 = "2018-04-20 06:00:00"
t1 = t1[2:]
t2 = datetime.datetime.strptime(t1, "%y-%m-%d %H:%M:%S")
print(t2)
t3 = t2.strftime("%A, %d. %B %Y at %I:%M%p")
print(t3)
def fun1():
    t_list = []
    t1 = ""
    while True:
        v = str(datetime.datetime.now())
        h1 = v[11:13]
        n1 = v[14:16]
        s1 = v[17:19]
        now_time = 3600 * int(h1) + 60 * int(n1) + int(s1)
        num1 = divmod(now_time, 150)
        num2 = divmod(num1[1], 5)
        #print(num1[1])
        if num2[1] == 0:
            if mutex1.locked():
                t_list.append(num1[1])
            else:
                t_list.append(num1[1])
                t1 = str(t_list[0])
                t_list.pop(0)
                fun3(t1)

def fun2():
    t_list = []
    t1 = ""
    while True:
        v = str(datetime.datetime.now())
        h1 = v[11:13]
        n1 = v[14:16]
        s1 = v[17:19]
        now_time = 3600 * int(h1) + 60 * int(n1) + int(s1)
        num1 = divmod(now_time, 300)
        num2 = divmod(num1[1], 5)
        # print(num1[1])
        if num2[1] == 0:
            if mutex2.locked():
                t_list.append(num1[1])
            else:
                t_list.append(num1[1])
                t1 = t_list[0]
                t_list.pop(0)
                fun4(t1)
def fun3(run_time):
    mutex1.acquire()
    print (str(run_time)+"f1")
    time.sleep(1)
    mutex1.release()
def fun4(run_time):
    mutex2.acquire()
    print (str(run_time)+"f2")
    time.sleep(1)
    mutex2.release()

conn = mysql.connector.Connect(host='localhost', user='cso', password='', database='trading_bot')

c = conn.cursor(buffered=True)
c.execute(" select api_key, secret from exchange_info where user_id=%s and exchange=%s", ('6', "binance"))
key_data = c.fetchone()
api = key_data[0]
secret = key_data[1]
conn.commit()

c.execute("""select * from bot where absID=%s""", (1,))
bot = c.fetchone()
conn.commit()
bot_kind = bot[3]
interval = bot[35]
interval1 = ""


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
exchange_fee = 0.0
indicator_profit = 0
temp_data = []
value_dif = []
sum_plus = 0
sum_minus = 0
gain = 0
loss = 0
rsi_value = 0

exchange_obj = ccxt.binance({
                        #'proxies': {
                        #    'http': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        #    'https': 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280',
                        #},
                        'apiKey': 'PMAA6594W2Gx2PK1wMhpWhfgxMxnLV56BPvD005EIw6awc3OBFsAncVsEFsQrJYt',
                        'secret': 'ZXU6Eg6AQHYPyAx4zL22EjjyZatmcvvuZnx8YqmxFQa4lgDdwqy8CscnL8ktPZmh',
})
                    # exchange_obj.proxy = 'http://andynfx:trieuanh@us-wa.proxymesh.com:31280'
#dd = exchange_obj.fetch_open_orders(symbol='BTC/USDT')
#print(dd)
#data = datetime.datetime.now()
#print(datetime.datetime.fromtimestamp(1529977501))
#m = exchange_obj.fetch_markets()
#for i in m:
#    print(i)

print(exchange_obj.fetch_order(id=33774791, symbol='BCH/USDT'))
print("dsfdsfdsf")
order_book = exchange_obj.fetch_closed_orders('BCH/USDT')
for i in order_book:
    print(i)
print(order_book)
print(order_book['asks'])
info = exchange_obj.fetch_ticker('XLM/USDT')
print(info)
ask_price = info['info']['askPrice']
bid_price = info['info']['bidPrice']
print(info['info']['lastPrice'])
print(ask_price)
print(bid_price)
exchange_fee = exchange_obj.calculate_fee('BCH/USDT', 'market', 'buy', 1, float(ask_price), 'taker')
exchange_fee1 = exchange_obj.calculate_fee('BCH/USDT', 'market', 'sell', 1, float(bid_price), 'maker')

print(exchange_fee)
print(exchange_fee1)
#print(info1)
#print(exchange_obj.fee_to_precision('BTC/USDT', 0.001))
f = open('bot_log.txt', 'w')
for i in range(0,100):
    f.write(str(i)+'\n')

#print(chart_data)
#print(len(chart_data))
#print(info)
#print(info['BTC/USDT']['info']['bidPrice'])
#print(info['BTC/USDT']['info']['askPrice'])


#t1 = threading.Thread(target=fun1).start()
#t2 = threading.Thread(target=fun2).start()
