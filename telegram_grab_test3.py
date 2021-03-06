import configparser
import re
import time

from telethon import events
from telethon.sync import TelegramClient

from binance_app import binance_start

from loguru import logger

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
username = config['Telegram']['username']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")
logger.add("info.log", format="{time} {level} {message}", level="INFO")


@logger.catch()
def start(btc_count):
    t0 = time.time()
    tg_client = TelegramClient(username, api_id, api_hash)

    @tg_client.on(events.NewMessage(chats="https://t.me/test_channel_by_redtree323"))
    async def message_handler(event):
        # print(event.message)
        message = event.message.to_dict()['message']
        logger.info("Message from Tg: " + str(message))
        reg = re.compile(r"([1A-Z]{2,})", re.M)
        coin_name = reg.findall(message)
        if coin_name:
            logger.info(f"The {str(coin_name[0])} cryptocurrency will be purchased for {btc_count} BTC")
            binance_start(coin_name[0], btc_count)
            await tg_client.disconnect()

    tg_client.start()
    tg_client.run_until_disconnected()
    logger.info("Time: " + str(time.time() - t0))


if __name__ == '__main__':
    start(0.002)
