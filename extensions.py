import json
import requests

import config


class APIException(Exception):
    def __init__(self, message):
        super().__init__(message)


class CurrencyConvertor:

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
