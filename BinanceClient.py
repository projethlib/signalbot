from binance.client import Client
import pandas as pd
import time
import math


class BinanceClient:
    def __init__(self, API_KEY, API_SECRET):
        self.KEY = API_KEY
        self.SECRET = API_SECRET
        self.client = Client(self.KEY, self.SECRET, {"timeout": 75})
        self.baseAsset = 'USDT'
        self.current_asset = {"asset": 'USDT', "balance": 0}
    '''
    returns a dataframe with all the coins assets that are none zero
    '''
    def getBalances(self):
        account = self.client.get_account()
        df = pd.DataFrame(account['balances'])
        df.free = pd.to_numeric(df.free, errors='coerce')
        return df.loc[df.free > 0]
    def getAssetBalance(self, Asset):
        info = self.client.get_account()
        balances = info['balances']
        for b in balances:
            if b['asset'] == Asset:
                return float(b['free'])

    '''
    returns the current price of that asset in USDT
    '''
    def getPrice(self, asset):
        symbol = asset + 'USDT'
        return float(self.client.get_symbol_ticker(symbol=symbol)['price'])
    '''
    updates the balance and asset to the one that is currently owened in the highest amount
    '''
    def updateHighestBalanceAsset(self, df):
        df2 = df[['asset', 'free']]
        rows = df2.shape[0]
        asset = ''
        balance = 0
        highest = 0
        for i in range(rows):
            ast = df2.iloc[i, 0]
            amt = df2.iloc[i, 1]
            total = amt
            if 'USDT' not in str(ast):
                total = self.getPrice(ast) * amt
            if total > highest:
                asset = ast
                balance = amt
                highest = total
        self.current_asset['asset'] = asset
        self.current_asset['balance'] = balance
    '''
    returns the balance and asset owned in the highest amount
    '''
    def getBalanceAsset(self):
        return self.current_asset['asset'], self.current_asset['balance']
    '''
    return all the USDT crypto tradable pairs 
    '''
    def getPairs(self, ASSET_BASE=False):
        EI = self.client.get_exchange_info()
        symbols = []
        for ei in EI['symbols']:
            symbol = str(ei['symbol'])
            if symbol.endswith('USDT'):
                if ei['status'] == 'TRADING':
                    if ASSET_BASE:
                        symbols.append(symbol[:-4])
                    else:
                        symbols.append(symbol)
        return symbols

    def getFutures(self, ASSET_BASE=False):
        EI = self.client.futures_exchange_info()
        symbols = []
        for ei in EI['symbols']:
            symbol = str(ei['symbol'])
            if symbol.endswith('USDT'):
                if symbol.startswith('1000'):
                    symbol = symbol[4:]
                if ei['status'] == 'TRADING':
                    if ASSET_BASE:
                        symbols.append(symbol[:-4])
                    else:
                        symbols.append(symbol)
        return symbols

    '''
    return historical data for a coin
    '''

    def getHistoricalData(self, asset, intervalBC, interval1, datapoints=3, mean_vol=10, MA_LENGTH=3000):
        symbol = asset + 'USDT'
        interval = intervalBC
        intervalMS = interval1 * 60 * 1000
        # get the last 400 data points
        lastData = datapoints
        self.client._get_earliest_valid_timestamp(symbol=symbol, interval=interval)
        unix = int(time.time() * 1000)
        bars = self.client.get_historical_klines(symbol=symbol, interval=interval,
                                                 start_str=(unix - (intervalMS * lastData)))
        
        df = pd.DataFrame(bars)
        df["Date"] = pd.to_datetime(df.iloc[:, 0], unit='ms')
        df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume",
                      "Number of Trades",
                      "Taker buy base asset volume", "Taker buy quote asset volume", "ignore", "Date"]
        df = df[["Date", "Open", "High", "Low", "Close", "Volume", "Open Time"]].copy()
        for column in df.columns:
            if column != "Date":
                df[column] = pd.to_numeric(df[column], errors="coerce")
        
        '''
        df['EMA3'] = df['Close'].ewm(span=3).mean()
        df['EMA5'] = df['Close'].ewm(span=5).mean()
        df['EMA8'] = df['Close'].ewm(span=8).mean()
        df['EMA12'] = df['Close'].ewm(span=12).mean()
        df['EMA18'] = df['Close'].ewm(span=18).mean()
        df['EMA26'] = df['Close'].ewm(span=26).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()
     
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA30'] = df['Close'].rolling(30).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['MA100'] = df['Close'].rolling(100).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        '''
        
        #df['TVB'] = 3 * df['Close'] - df['Low'] - df['Open'] - df['High']
        #df['MATVB'] = df['TVB'].rolling(14).mean()

        ''''
        df['stddev'] = df['Close'].rolling(20).std()
        df['Upper'] = df['MA20'] + 4 * df['stddev']
        df['Lower'] = df['MA20'] - 4 * df['stddev']

        df['ATR_DIFFS'] = df['High'] - df['Low']
        df['ATR20'] = df['ATR_DIFFS'].rolling(20).mean()

        df['Mean Volume'] = df['Volume'].rolling(mean_vol).mean()
        
        adx_ind = ta.trend.ADXIndicator(df.High, df.Low, df.Close)
        df['DI+'] = adx_ind.adx_pos()
        df['DI-'] = adx_ind.adx_neg()
        '''
        #df['RSI'] = tal.momentum.rsi(df.Close, 2)

        #print(df.tail(5))
        # df2 = df.copy()
        ''''
        print(df)
        time_interval = 10
        keep = [a + time_interval for a in range(-time_interval, len(df) - time_interval, time_interval)]
        all = [a for a in range(len(df))]
        for element in keep:
            if element in all:
                all.remove(element)
        print(all)
        df2 = df.drop(all)
        print(df2)
        '''
        #df = df.iloc[::5]
        return df
    '''
    returns re;ative coin release time in seconds counting on days
    '''
    def getFirstTimeStamp(self, symbol):
        return self.client._get_earliest_valid_timestamp(symbol=symbol, interval=self.client.KLINE_INTERVAL_1MINUTE)/1000
    def get_connection_status(self):
        try:
            self.client.ping()
        except Exception as e:
            return False, e
        else:
            return True, 0
    def deleteClient(self):
        del self.client
    '''
    for sorting the array
    '''
    def myFunc(self, e):
        return e['score']
    def get24changes(self, max):
        tickers = self.client.get_ticker()
        high_scores = []
        for ticker in tickers:
            p = ticker['symbol'][:-4]
            sc = float(ticker['priceChangePercent'])
            if len(high_scores) < max:
                if sc > 1:
                    high_scores.append({'asset': p, 'score': sc})
                    high_scores.sort(key=self.myFunc)
            else:
                if sc > high_scores[0]['score']:
                    high_scores[0] = {'asset': p, 'score': sc}
                    high_scores.sort(key=self.myFunc)
                    # print(high_scores)
        return high_scores
    def getVolatility(self, asset):
        symbol = asset + 'USDT'
        interval = self.client.KLINE_INTERVAL_1MINUTE
        intervalMS = 1*60 * 1000
        # get the last data points
        lastData = 2
        timestamp = self.client._get_earliest_valid_timestamp(symbol=symbol, interval=interval)
        unix = int(time.time() * 1000)
        bars = self.client.get_historical_klines(symbol=symbol, interval=interval,
                                            start_str=(unix - (intervalMS * lastData)))
        #print(bars)
        open = float(bars[0][1])
        close = float(bars[0][4])
        diff = close / open
        #print("open: {} close: {} diff: {}".format(open, close, diff))
        return diff
    def check_decimals(self, symbol):
        info = self.client.get_symbol_info(symbol)
        val = info['filters'][2]['stepSize']
        decimal = 0
        is_dec = False
        for c in val:
            if is_dec is True:
                decimal += 1
            if c == '1':
                break
            if c == '.':
                is_dec = True
        return decimal
    '''
    place a market buy order
    '''
    def get_client(self):
        return self.client
    def buy(self, asset, amount):
        symbol = asset + 'USDT'
        #balance = self.getAssetBalance(self.baseAsset)
        if amount == -1:
            balance = self.getAssetBalance(self.baseAsset)
        else:
            balance = amount
        quoteQty = math.trunc(float(balance * 10**2))/10**2
        print("quoteQTY is {}".format(quoteQty))
        order = self.client.create_order(symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=quoteQty)
    '''
    place a market sell order
    '''
    def sell(self, asset, pctg):
        symbol = asset + 'USDT'
        balance = self.getAssetBalance(asset) * pctg
        precision = self.check_decimals(symbol)
        qty = math.trunc(float(balance * 10 ** precision)) / 10 ** precision
        order = self.client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty)
    
    def sell_third(self, asset):
        pass
    
    def get_coin_prices(self, assets):
        inf = self.client.get_all_tickers()
        finalPrices = []
        for element in inf:
            for asset in assets:
                if(element['symbol'] == asset + 'USDT'):
                    finalPrices.append(element)
        return finalPrices
    '''
    start a trade with a take profit and stop loss
    comment out the self.buy/self.sell for testing
    '''
    def trade(self, asset, TP, SL, testing=False, trailing=False):
        symbol = asset + 'USDT'
        success = False
        trade_result = 1
        #profit = (profit+100)/100
        #stop_loss = (100-stop_loss)/100
        interval = 1 #check for price every 1 s
        current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
        start_price = current_price
        highest = current_price
        if trailing:
            print("trailing stop loss placed {}$ bellow the price".format(SL))
        #max_price = current_price * profit
        #min_price = current_price * stop_loss
        print("starting a trade for {}. Current price is {}. will sell at {} or exit at {}".format(symbol, current_price, TP, SL))
        c = time.time()
        #buy
        if not testing:
            try:
                self.buy(asset)
            except Exception as e:
                print(e)
                self.client = Client(self.KEY, self.SECRET, {"timeout": 75})
                try:
                    self.buy()
                except Exception as e:
                    print("Failed to trade!!!")
                    print(e)
                    #Failed to sell
        trading = True
        while trading:
            if time.time() - c > interval:
                #get price
                current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
                #print("price is {}. sell at {}. stop loss at {}".format(current_price, max_price, min_price))
                if trailing:
                    if current_price > highest:
                        highest = current_price
                    if current_price <= highest - SL:
                        if not testing:
                            try:
                                self.sell(asset)
                            except Exception as e:
                                print(e)
                                self.client = Client(self.KEY, self.SECRET, {"timeout": 75})
                                try:
                                    self.sell(asset)
                                except Exception as e:
                                    print("Failed to trade!!!")
                                    print(e)
                                    # Failed to sell
                        trade_result = current_price / start_price
                        if current_price > start_price:
                            success = True
                        else:
                            success = False


                else:
                    if current_price >= TP:
                        #sell
                        if not testing:
                            try:
                                self.sell(asset)
                            except Exception as e:
                                print(e)
                                self.client = Client(self.KEY, self.SECRET, {"timeout": 75})
                                try:
                                    self.sell(asset)
                                except Exception as e:
                                    print("Failed to trade!!!")
                                    print(e)
                                    # Failed to sell

                        print("Success! selling..");
                        print("Sold at: {}".format(current_price))
                        success = True
                        trading = False
                        trade_result = current_price/start_price
                    if current_price <= SL:
                        # sell
                        if not testing:
                            try:
                                self.sell(asset)
                            except Exception as e:
                                print(e)
                                self.client = Client(self.KEY, self.SECRET, {"timeout": 75})
                                try:
                                    self.sell(asset)
                                except Exception as e:
                                    print("Failed to trade!!!")
                                    print(e)
                                    # Failed to sell
                        print("Failure! selling..");
                        print("Sold at: {}".format(current_price))
                        success = False
                        trading = False
                        trade_result = current_price / start_price
                    c = time.time()
        return trade_result, success