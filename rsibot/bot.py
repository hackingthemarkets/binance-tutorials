import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethbrl@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 60
RSI_OVERSOLD = 50
TRADE_SYMBOL = 'ETHBRL'
TRADE_QUANTITY = 0.05
MINIMUM_GAIN = 0.30

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def save_transaction_history(side, quantity, last_price, gain):
  f = open("negociacoes.txt", mode="a+", newline="\n")
  f.write("Operation: " + str(side) + " Quantity: " + str(quantity) + " Value: " + str(last_price)+ " Gain: " + str(gain) + "\n" )
  f.close()


def order(side, quantity, symbol, last_price, gain=0 , order_type=ORDER_TYPE_MARKET):
    try:
        # print("sending order")
        # order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        save_transaction_history(side, quantity, last_price, gain)
        # print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def gain(sold, bought):
  diff = float(sold) - float(bought)
  gain = (diff / bought) * 100
  return gain

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    bought = 0
    # print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))
            
            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    sold = close
                    gain = gain(sold, bought)
                    if gain >= MINIMUM_GAIN:
                      print("Overbought! Sell! Sell! Sell!")
                      # put binance sell logic here
                      order_succeeded = order("SELL", TRADE_QUANTITY, TRADE_SYMBOL, close, gain)
                      if order_succeeded:
                          in_position = False
                    else:
                      print("Overbought! But not profitable, nothing to do.")
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    bought = float(last_price)
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order("BUY", TRADE_QUANTITY, TRADE_SYMBOL, last_price)
                    
                    if order_succeeded:
                        in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
