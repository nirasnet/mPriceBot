# -*- coding: UTF-8 -*-
# @yasinkuyu

import sys
import argparse

sys.path.insert(0, './app')
sys.path.insert(0, '..')
from CheckPrice import CheckPrice
      
if __name__ == '__main__':
    
    # Set parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVGBTC - XVGETH)', default='ETHBTC')
    parser.add_argument('--wait_time', type=float, help='Wait Time (seconds)', default=20)
    parser.add_argument('--loop', type=int, help='Loop (0 unlimited)', default=0)
    parser.add_argument('--dl', type=float, help='diff Low', default=0.5)
    parser.add_argument('--dh', type=float, help='diff High', default=0.5)

    option = parser.parse_args()
    
    # Get start
    t = CheckPrice(option)
    t.run()
