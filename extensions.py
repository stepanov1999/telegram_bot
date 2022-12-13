import requests
import json
from config import currencies, payload, headers



class APIException(Exception):
    pass



class Converter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise APIException("Валюты должны быть разные")

        try:
            quote_ticker = currencies[quote][0]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту <{quote}>")

        try:
            base_ticker = currencies[base][0]
        except KeyError:
            raise APIException(f"Не удалось обработать валюту <{base}>")

        try:
            amount_val = float(amount.replace(',', '.'))
        except ValueError:
            raise APIException(f"Не удалось обработать количество валюты <{amount}>")

        url = f"https://api.apilayer.com/exchangerates_data/convert?to={base_ticker}& \
        from={quote_ticker}&amount={amount_val}"
        response = requests.request("GET", url, headers=headers, data=payload)
        result_json = json.loads(response.content)

        return result_json['result']
