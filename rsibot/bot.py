from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import config, requests, websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/ethbrl@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 65
RSI_OVERSOLD = 35

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNALPEDIOD = 9
MACD_START = MACD_SLOW + MACD_SIGNALPEDIOD

TRADE_SYMBOL = 'ETHBRL'
TRADE_QUANTITY = 0.05

MINIMUM_GAIN = 0.10

closes = []
in_position = False
bought = 0

# client = Client(config.API_KEY, config.API_SECRET, tld='us')

def telegram_send(bot_message):
    
    bot_token = config.TELEGRAM_TOKEN
    bot_chatID = config.TELEGRAM_ID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()

def save_transaction_history(side, quantity, last_price, gain):
  message = "Operation: {} Quantity: {} Value: {} Gain: {}%\n".format(side, quantity, last_price, gain)

  f = open("negociations.txt", mode="a+", newline="\n")
  f.write(message)
  f.close()

  telegram_send(message)

def order(side, quantity, symbol, last_price, gain=0 , order_type=ORDER_TYPE_MARKET):
    try:
        # order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        save_transaction_history(side, quantity, last_price, gain)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def calc_gain(sold, bought):
  diff = sold - bought
  return float("{:.2f}".format((diff / bought) * 100))


def on_open(ws):
    message = "opened connection"
    print(message)
    telegram_send(message)

def on_close(ws):
    print('closed connection')
    print('opening connection again')
    telegram_send('opening connection again')
    open_socket()

def on_message(ws, message):
    global closes, in_position, bought
    json_message = json.loads(message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = float(candle['c'])

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(close)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            if len(closes) > MACD_START:
              macd, macdsignal, macdhist = talib.MACD(np_closes, MACD_FAST, MACD_SLOW, MACD_SIGNALPEDIOD)
            else:
              macd, macdsignal, macdhist = (10, 0, 10)
            last_rsi = rsi[-1]
            last_macd = macd[-1]
            last_macdsignal = macdsignal[-1]
            macd_signal = abs(last_macd - last_macdsignal)
            print("the current RSI is {} and MACD is {} ".format(last_rsi, macd_signal))
            
            if last_rsi >= RSI_OVERBOUGHT and (-1.5 <= macd_signal <= 1.5):
                if in_position:
                    gain = calc_gain(close, bought)
                    if gain >= MINIMUM_GAIN:
                      print("Overbought! Sell! Sell! Sell!")
                      order_succeeded = order("SELL", TRADE_QUANTITY, TRADE_SYMBOL, close, gain)
                      if order_succeeded:
                          bought = 0
                          in_position = False
                    else:
                      print("Overbought! But not profitable, nothing to do.")
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi <= RSI_OVERSOLD and (-1.5 <= macd_signal <= 1.5):
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    order_succeeded = order("BUY", TRADE_QUANTITY, TRADE_SYMBOL, close)
                    
                    if order_succeeded:
                        bought = close
                        in_position = True

def open_socket():                
  ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
  ws.run_forever()

open_socket()