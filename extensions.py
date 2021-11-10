import json
import requests
import telebot

import config


class APIException(Exception):
    def __init__(self, message):
        super().__init__(message)


class CurrencyConvertor:
    """
    Class for currency convert API service: https://free.currconv.com/api/v7/convert
    """

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> str:

        available_currencies = ('RUB', 'EUR', 'USD', 'GBP', 'AUD', 'JPY')

        if any([base.upper() not in available_currencies, quote.upper() not in available_currencies]):
            raise APIException(f'Base or quote currency not int available currencies: {available_currencies}')

        try:
            amount = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f'Amount must be a number (integer or float) but not {amount}')

        params = {
            'apiKey': config.CURR_CONV_API_KEY,
            'q': f'{base}_{quote}'
        }

        try:
            api_result = requests.get(url=config.CURR_CONV_API_URL, params=params)
        except ConnectionError:
            raise APIException(f'Connection error to {config.CURR_CONV_API_URL}')
        else:
            if api_result.status_code == 200:
                response = json.loads(api_result.content)['results'][params['q']]['val']
                try:
                    response = float(response)
                except ValueError:
                    raise APIException(f'Something wrong, in API response wrong or empty value: "{response}"')
                else:
                    return f'{response * amount}'
            else:
                raise APIException(f'Something wrong, API response code is {api_result.status_code}')


class TelegramBot:
    """
    Class for Telegram bot service

    Note:
    With class-based notations don't work @<bot_object>.<handler>
    I'm use <bot_object>.register_<handler> as alternative
    """
    def __init__(self):
        self._bot_name = config.TELEGRAM_BOT_NAME
        self._token = config.TELEGRAM_BOT_TOKEN
        self._bot = None

        try:
            self._bot = telebot.TeleBot(self._token)
        except Exception as e:
            raise APIException('Something wrong... {e.message}')
        else:
            self._bot.register_message_handler(self.start, commands=['start'])
            self._bot.register_message_handler(self.help, commands=['help'])
            self._bot.register_message_handler(self.parser, content_types=['text'])

        self._bot.infinity_polling()

    def start(self, message):
        self._bot.send_message(message.chat.id, f"Welcome, {message.chat.username} \nSend /help for usage help")

    def help(self, message):
        help_msg = 'Send: convert <amount_base> <base_currency> <quote_currency>\n' \
                   'Example: convert 100 USD RUB\n' \
                   'Result: 7070.0 RUB\n' \
                   ''
        self._bot.send_message(message.chat.id, f"{help_msg}")

    def parser(self, message):
        try:
            result = ''
            command, amount, base, quote = message.text.split()

            if command == 'convert':
                # result = quote of base * amount
                result = CurrencyConvertor.get_price(base=base, quote=quote, amount=amount)
                result = f"Result: {result} {quote}"
            else:
                result = 'Wrong input, send /help for usage help'

        except APIException as e:
            print(f'{e}')
            self._bot.send_message(message.chat.id, f"Error: {e}")

        else:
            self._bot.send_message(message.chat.id, result)
