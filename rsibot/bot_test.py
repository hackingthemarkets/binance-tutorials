# Importing the libraries...

import ccxt
import pandas as pd
pd.set_option('display.max_rows', None)
from datetime import datetime
from ta.trend import MACD
from ta.momentum import RSIIndicator
import warnings
warnings.filterwarnings('ignore')
import  schedule as schedule
import time

# Connection to the exchange for data retreival and order execution
exchange = ccxt.binance()

# For live implementation add your API keys:
# exchange = ccxt.binance({"apiKey": '<YOUR_API_KEY>',"secret": '<YOUR_SECRET_KEY>' })

# Function for data retreival and DataFrame processing
def technical_signals(df):
    '''
    This function will implement the technical indicators to the market DataFrame.
    The second part, will define the logics with a boolean final.
    '''
    # ---> Example of manual calculation of indicator

    # Manual MACD
    # ShortEMA = df["close"].ewm(span=12, adjust=False).mean() 
    # LongEMA = df["close"].ewm(span=26, adjust=False).mean() 
    # MACD = ShortEMA - LongEMA
    # Signal = MACD.ewm(span=9, adjust=False).mean()
    # df['MACD'] = MACD
    # df['Signal'] = Signal

    # Get Indicators using libary MACD & RSI for the example.
    # MACD
    indicator_macd = MACD(df['close'])
    df['MACD'] = indicator_macd.macd()
    df['Signal']= indicator_macd.macd_signal()
    df['MACD Histogram']= indicator_macd.macd_diff()
    df['MACD_Signal'] = False
   
    # RSI
    indicator_rsi = RSIIndicator(df['close'], window=14)
    df['RSI_Signal'] = False
    df['RSI'] = indicator_rsi.rsi()
    # As many indicators, calculations, etc as required...

    # Technical indicator strategy logics. We will use simple MACD to detect signals:
    # Crossover MACD over Signal Below 0 == Buy signal
    # Crossunder MACD under Signal Above 0 == Sell Signal
    for current in range(1, len(df.index)):
        previous = current - 1
        if (df['MACD'][current] > df['Signal'][current]) and (df['MACD'][previous] <  df['Signal'][previous]) and (df['MACD'][current]<0):
            df['MACD_Signal'][current] = True
        elif (df['MACD'][current] < df['Signal'][current]) and (df['MACD'][previous] >  df['Signal'][previous]):
            df['MACD_Signal'][current] = False
        else:
            df['MACD_Signal'][current] = df['MACD_Signal'][previous]
    return df

# Defines if we're in the market or not, to avoid submit orders once we've submited one on the same direction.
in_position = False
def reading_market(df):
    '''
    Function to analyze the market looking for signals according to our logics.
    '''
    global in_position

    print("Looking for signals...")
    print(df.tail(4))
    last_row = len(df.index) - 1
    previous_row = last_row - 1

    if not df['MACD_Signal'][previous_row] and df['MACD_Signal'][last_row]:
        print("Uptrend activated according MACD, BUY SIGNAL triggered")
        if not in_position:
            order_buy = 'Here goes BUY order' #exchange.create_market_buy_order('BTC/USDT', 1)
            print(order_buy)
            in_position = True
        else:
            print("Already in position, skip BUY signal")
    
    if df['MACD_Signal'][previous_row] and not df['MACD_Signal'][last_row]:
        if in_position:
            print("Downtrend activated, SELL SIGNAL triggered")
            order_sell = 'Here goes SELL order' # exchange.create_market_sell_order('BTC/USDT', 1)
            print(order_sell)
            in_position = False
        else:
            print("Not in position, skip SELL Signal")

def execute_connection(symbol='BTC/USDT', timeframe='1m'):
    '''
    Function for data retreival, processing, and cleaning into dataframe to be used 
    later for technical indicators implementation
    '''
    raw_data = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    # since the return is on a list format. To see ---> print(raw_data)
    
    # Converting data into a dataframe "[:-1]" since we will check the last closed bar
    df = pd.DataFrame(raw_data[:-1], columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    # Converting date into a readable date format
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    print(f"Executing connection and data processing at... {datetime.now().isoformat()}")
    #print(df)
    complete_df = technical_signals(df)
    reading_market(complete_df)

# Example of data
#execute_connection(symbol='BTC/USDT', timeframe='15m')

# Running and execution
schedule.every(10).seconds.do(execute_connection)

while True:
    schedule.run_pending()
    time.sleep(1)

