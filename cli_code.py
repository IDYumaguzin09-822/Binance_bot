import click
from telegram_grab_test3 import start


@click.command()
@click.option('-c', '--btc-count', help='Количество BTC, на которые Вы хотите купить pump-крипту')
def main(btc_count):
    start(btc_count)


if __name__ == '__main__':
    main()
