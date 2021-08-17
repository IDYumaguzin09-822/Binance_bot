import configparser

import requests.exceptions
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import time

from loguru import logger

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

api_key = config['Binance']['api_key']
api_secret = config['Binance']['api_secret']


def create_new_order(client, symbol, qty):
    # choose quantity or quoteOrderQty to filter your order
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        # quantity=qty,
        quoteOrderQty=qty
    )
    logger.info(
        "Symbol: {}, Price: {}, Quantity: {}, CummulQuoteQty: {}, Status: {},"
        " Type: {}, Side: {}, Buy Price: {}, Commission: {}".format(
            order['symbol'], order['price'],
            order['origQty'], order['cummulativeQuoteQty'],
            order['status'], order['type'],
            order['side'], order['fills'][0]['price'], order['fills'][0]['commission']))
    logger.debug(order)
    return order['origQty'], float(order['fills'][0]['price'])


def view_my_balance(client):
    info = client.get_account()
    logger.debug(info)
    for asset in info['balances']:
        print("{}: {} is free and {} is locked".format(asset['asset'], asset['free'], asset['locked']))
    print()


def view_all_tickers(client):
    prices = client.get_all_tickers()
    logger.debug(prices)
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
    logger.info("Sell order function")
    while True:
        coin = client.get_ticker(symbol=symbol)
        logger.debug(coin)
        last_price = float(coin['lastPrice'])
        high_price = float(coin['highPrice'])
        if (last_price >= buy_price * 1.4) or (last_price <= high_price * 0.98):
            while True:
                order = client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=qty,
                    # quoteOrderQty=qty
                )
                logger.info(order)
                logger.info("Статус:" + order['status'])
                if order['status'] == 'FILLED':
                    break
        logger.info("Wait...")


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
        client = Client(api_key, api_secret, testnet=True)

        t0 = time.time()
        qty, buy_price = create_new_order(client, symbol, quote_order_quantity)
        logger.info("BUY Order create time: " + str(time.time() - t0))

        t0 = time.time()
        create_sell_order(client, buy_price, symbol, qty)
        logger.info("SELL Order create time: " + str(time.time() - t0))

        view_my_balance(client)
        # view_all_tickers(client)
        # view_coin_ticker(client, symbol)

        # view_all_orders_by_sym(client, symbol)
        # view_symbol_info(client, symbol)

        logger.info("Weight:" + client.response.headers['x-mbx-used-weight'])
    except requests.exceptions.ConnectionError:
        logger.error("-1, Connection Error")
    except requests.exceptions.ReadTimeout:
        logger.error("-1, Read Timeout Error")
    except KeyboardInterrupt:
        logger.error("-1, Keyboard Interrupt")


def binance_start(coin, btc_count):
    symbol = coin + 'USDT'
    logger.info("Symbol: " + symbol)
    quote_order_quantity = btc_count
    t0 = time.time()
    main(symbol, quote_order_quantity)
    logger.info("Время работы: " + str(time.time() - t0))


if __name__ == '__main__':
    binance_start('BNB', 1)
