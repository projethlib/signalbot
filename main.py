

import BinanceClient
import datetime
import time
import numpy as np
import logging
import requests

def logg(msg):
    # basic logging 
    logging.basicConfig(level=logging.INFO, filename="output.log", format='%(asctime)s %(message)s') # include timestamp
    logging.info(msg)


DATASIZE = 10
TIMEFRAME = 5 #3min

CH3_2_200 = -1001871978999
CH3_2_100 = -1001663202161
CH3_2_50 = -1001778894869
CH3_5_50 = -1001826966465
CH3_5_100 = -1001884354061
CH3_5_200 = -1001608393477
CH3_10_50 = -1001868265527
CH3_10_100 = -1001897906322
CH3_10_200 = -1001625854593
CH15_2_50 = -1001810084713
CH15_2_100 = -1001850449145
CH15_2_200 = -1001848064130
CH15_5_50 = -1001588512131
CH15_5_100 = -1001557080577
CH15_5_200 = -1001820263196
CH15_10_50 = -1001589191495
CH15_10_100 = -1001877398816
CH15_10_200 = -1001809890013
CH60_2_50 = -1001438184580
CH60_2_100 = -1001722467003
CH60_2_200 = -1001664761082
CH60_5_50 = -1001502951580
CH60_5_100 = -1001883990428
CH60_5_200 = -1001718297642
CH60_10_50 = -1001794592023
CH60_10_100 = -1001877974586
CH60_10_200 = -1001620928540

URL = 'https://api.telegram.org/bot5417356609:AAGfuePUntAH1_Zwdf0h3V7OHrbTOAdSkEc/sendMessage?chat_id={}&text={}&parse_mode=markdown'


trading = True
trades = []

successful_trades = 0
failed_trades = 0


coins_list = []
API_KEY = "Vp06GLHJRNpEx0GgNn87JBgHTU7OOzWKF661QDIUKahfftsnY3yiLoZjWAgJtu7x"
API_SECRET = "sYYr2sMsncJVfNzMbnNZwxlP7j7pm920AULilGX3PgZmeWLiN7LC2o6fTaSb2KPm"


current_time = datetime.datetime.now()
day = current_time.day
print("today is {}".format(current_time))
bc = BinanceClient.BinanceClient(API_KEY, API_SECRET)
client = bc.get_client()
intervals = [client.KLINE_INTERVAL_1MINUTE, client.KLINE_INTERVAL_3MINUTE, client.KLINE_INTERVAL_5MINUTE, client.KLINE_INTERVAL_15MINUTE, client.KLINE_INTERVAL_30MINUTE, client.KLINE_INTERVAL_1HOUR, client.KLINE_INTERVAL_2HOUR, client.KLINE_INTERVAL_4HOUR, client.KLINE_INTERVAL_6HOUR, client.KLINE_INTERVAL_8HOUR, client.KLINE_INTERVAL_12HOUR, client.KLINE_INTERVAL_1DAY, client.KLINE_INTERVAL_3DAY, client.KLINE_INTERVAL_1WEEK, client.KLINE_INTERVAL_1MONTH]
intervals_min = [1, 3, 5, 15, 30, 60, 120, 240, 360, 480, 720, 1440, 4320, 10080, 43200]

top_score = 0

LAST_OPEN = 0

pairs = bc.getPairs(ASSET_BASE=True)
client = bc.get_client()


msg_ctr = 0

max_ = len(pairs)
i = 0
DATA = []
sorted_coins = []


MIN_MC = 75000000 #75M
MAX_MC = 3000000000 #3B

#coin = 'ETH'
#coin = input("Enter coin:")
#coins = ['BTC', 'ETH', 'BNB', 'NEO', 'LTC', 'QTUM', 'ADA', 'XRP', 'EOS', 'IOTA', 'XLM', 'ONT', 'TRX', 'ETC', 'ICX', 'NULS', 'VET', 'LINK', 'WAVES', 'ONG', 'HOT', 'ZIL', 'ZRX', 'FET', 'BAT', 'XMR', 'ZEC', 'IOST', 'CELR', 'DASH', 'OMG', 'THETA', 'ENJ', 'MITH', 'MATIC', 'ATOM', 'TFUEL', 'ONE', 'FTM', 'ALGO', 'GTO', 'DOGE', 'DUSK', 'ANKR', 'WIN', 'COS', 'MTL', 'TOMO']
#coins = [coin]
#coins = coins[5:15]
'''
f = open('coins.txt', 'r')
data = f.read()
coins = data.split(',')
coins = coins[:-20]
'''
#no.send_message("Bot started (v1.2)")
            
def test_trade():
    global trading
    blc = bc.getAssetBalance('USDT')
    print("You currently have {} USDT in your account".format(blc))
    total = 0
    for info in coins_list:
        amount = float(info[1])
        total += amount
    print("Total investment: {} USDT".format(total))
    if total > blc:
        print("You currently don't have enough USDT to start your bot, add more USDT or reduce your investment size to get started")
        trading = False

coins = pairs

in_trade = False
while trading:
    status, error = bc.get_connection_status()
    if status == False:
        while status == False:
            print("Connection failed to establish...reseting the connection")
            print(error)
            print("current time: {}".format(datetime.datetime.now()))
            time.sleep(20)
            status, error = bc.get_connection_status()
        bc.deleteClient()
        del bc
        bc = BinanceClient.BinanceClient(API_KEY, API_SECRET)

    msg_ctr += 1
    string_array = []
    cc_copy = []
    print(datetime.datetime.now())
    t1 = time.time()
    for coin in coins:
        t2 = time.time()
        try:
            df = bc.getHistoricalData(coin, intervals[TIMEFRAME], intervals_min[TIMEFRAME], datapoints=DATASIZE)

            High = np.array(df.High)
            Low = np.array(df.Low)
            Close = np.array(df.Close)
            Open = np.array(df.Open)
            Volume = np.array(df.Volume)
            mean_vol = Volume.mean()

            high = High[-1]
            close_ = Close[-1]
            open_ = Open[-1]

            diff_ =  close_ / open_
            if mean_vol == 0:
                vdiff_ = 0
            else:
                vdiff_ = Volume[-1]/mean_vol
            '''
            if diff_ > 1.02 and vdiff_ > 1.5 :
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH3_2_50, message))
            if diff_ > 1.02 and vdiff_ > 2:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH3_2_100, message))
            if diff_ > 1.02 and vdiff_ > 3:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH3_2_200, message))
            '''
            if diff_ > 1.05 and vdiff_ > 1.5:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_5_50, message))
            if diff_ > 1.05 and vdiff_ > 2:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_5_100, message))
            if diff_ > 1.05 and vdiff_ > 3:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_5_200, message))
            if diff_ > 1.1 and vdiff_ > 1.5:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_10_50, message))
            if diff_ > 1.1 and vdiff_ > 2:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_10_100, message))
            if diff_ > 1.1 and vdiff_ > 3:
                message = "Signal for {}. Current price is {}$. Price increase of {}% and volume increase of {}% so far.".format(coin, close_, 100*(diff_-1), 100*(vdiff_-1))
                print(message)
                requests.get(URL.format(CH60_10_200, message))

        except Exception as e:
            print("error")
            print(e)
        print("time taken: {}s".format(time.time() - t2))
    print("finished looping in {}s".format(time.time() - t1))
    

