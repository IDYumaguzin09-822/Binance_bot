import configparser
import sys

import requests.exceptions
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import time

from loguru import logger

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# api_key = config['Binance']['api_key']
# api_secret = config['Binance']['api_secret']

api_key = "Om9RQuqGtEMHarUtRO2BfRc5ebdC4K66ArsCN2uModF4zECaVDe1oHaNn5Pz0b8N"
api_secret = "V7dszhbOT6dTdyFlXjFIPA5j1CdaClPwTxPCmAuXMQbyKaAWi3g9w48rugXcbDy8"

# logger.add('debugBinanceApp.log', format="{time} {level} {message}", level="DEBUG")


def create_new_order(client, symbol, qty):
    # choose quantity or quoteOrderQty to filter your order
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        # quantity=qty,
        quoteOrderQty=qty
    )
    print(
        "Symbol: {}, Price: {}, Quantity: {}, CummulQuoteQty: {}, Status: {}, Type: {}, Side: {},\
         Buy Price: {}, Commission: {}".format(
            order['symbol'], order['price'],
            order['origQty'], order['cummulativeQuoteQty'],
            order['status'], order['type'],
            order['side'], order['fills'][0]['price'], order['fills'][0]['commission']))
    logger.info(order)
    return order['origQty'], order['fills'][0]['price']


def view_my_balance(client):
    info = client.get_account()
    logger.info(info)
    for asset in info['balances']:
        print("{}: {} is free and {} is locked".format(asset['asset'], asset['free'], asset['locked']))
    print()


def view_all_tickers(client):
    prices = client.get_all_tickers()
    logger.info(prices)
    for symbol in prices:
        print("{}: {}".format(symbol['symbol'], symbol['price']))
    print()


def view_coin_ticker(client, symbol):
    # Выводит текущую цену крипы
    prices = client.get_ticker(symbol=symbol)
    print("{}: {}".format(prices['symbol'], prices['lastPrice']))


def view_all_orders_by_sym(client, symbol):
    orders = client.get_all_orders(symbol=symbol)
    for order in orders:
        print("{} {} {} order: {}, price: {}, quantity: {}, cumQuoteQty: {}".format(order['status'], order['side'],
                                                                                    order['type'], order['symbol'],
                                                                                    order['price'], order['origQty'],
                                                                                    order['cummulativeQuoteQty']))
    print()


def view_symbol_info(client, symbol):
    # Показывает полную информацию о ккрипте
    res = client.get_exchange_info()
    print("-" * 20)
    for symb in res['symbols']:
        if symb['symbol'] == symbol:
            print(symb)
    print("-" * 20)


def create_sell_order(client, buy_price, symbol, qty):
    print('Sell func')
    while True:
        print('во внешнем цикле')
        coin = client.get_ticker(symbol=symbol)
        logger.info(coin)
        # if float(coin['lastPrice']) <= float(coin['highPrice']) * 0.98:
        if True:
            while True:
                print('внутренний цикл')
                depth = client.get_order_book(symbol=symbol)
                print(depth['bids'])
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=qty,
                    # quoteOrderQty=qty
                )
                logger.info(order)
                print(order)
                print("Статус:", order['status'])
                print(client.response.headers['x-mbx-used-weight'])
                if order['status'] == 'FILLED':
                    break
            break
        break


def stuff(client, symbol):
    # Показывает глубину стаканов что-ли
    depth = client.get_order_book(symbol=symbol)
    print(depth)

    # Для отмены открытого ордера
    result = client.cancel_order(symbol=symbol, orderId='5236')
    print(result)

    # Для получения открытых ордеров для текущей пары
    orders = client.get_open_orders(symbol=symbol)
    for order in orders:
        print(order)
    print()

    # Выводит bids and asks
    while True:
        depth = client.get_order_book(symbol=symbol)
        print(depth)


@logger.catch
def main(symbol, quote_order_quantity):
    try:
        print("Finally, I'm here")
        client = Client(api_key, api_secret, testnet=True)
        view_my_balance(client)

        # create_new_order(client, symbol, quantity)
        # t0 = time.time()
        # qty, buy_price = create_new_order(client, symbol, quote_order_quantity)
        # print("Order create time:", time.time() - t0)
        buy_price = 0
        qty = 100
        create_sell_order(client, buy_price, symbol, qty)
        # view_my_balance(client)
        # view_all_tickers(client)
        # view_coin_ticker(client, symbol)

        # view_all_orders_by_sym(client, symbol)
        print(quote_order_quantity)
        view_symbol_info(client, symbol)

        print(client.response.headers['x-mbx-used-weight'])
        logger.info("Weight:" + client.response.headers['x-mbx-used-weight'])
    except requests.exceptions.ConnectionError:
        logger.error("-1, Connection Error")
    except requests.exceptions.ReadTimeout:
        logger.error("-1, Read Timeout Error")


def binance_start(coin, btc_count):
    print("Now, I'm here!")
    symbol = coin + 'USDT'
    print(symbol)
    quote_order_quantity = btc_count
    t0 = time.time()
    main(symbol, quote_order_quantity)
    t1 = time.time()
    print("Время работы:", t1 - t0)


if __name__ == '__main__':
    binance_start('BNB', 1)
