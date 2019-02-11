# -*- coding: UTF-8 -*-
# @yasinkuyu

import sys
import argparse

sys.path.insert(0, './app')
from Trading import Trading

if __name__ == '__main__':

    # Set parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', required=True)
    parser.add_argument('--amount', type=float, help='Buy/Sell COIN Amount (Ex: 100 ADA)', required=True)
    parser.add_argument('--profit', type=float, help='Target Profit', default=5)
    parser.add_argument('--wait_time', type=float, help='Wait Time (seconds)', default=600)
    parser.add_argument('--debug',
                        help='Debug True/False if set --debug flag, will output all messages every "--wait_time" ',
                        action="store_true", default=False)  # 0=True, 1=False

    option = parser.parse_args()

    t = Trading(option)
    t.run()