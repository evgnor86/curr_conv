import extensions


# def start():
#     try:
#         # result = quote of base * amount
#         result = extensions.CurrencyConvertor.get_price(base='USD', quote='RUB', amount='10')
#     except extensions.APIException as e:
#         print(f'{e}')
#     else:
#         print(result)


if __name__ == '__main__':
    # start()
    bot = extensions.TelegramBot()
