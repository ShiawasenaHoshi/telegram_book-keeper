import requests
import json


class ExchangeRates():
    _instance = None
    _rates_method = None
    _currency_api_key = None

    def __init__(self):
        self.rates_cache = None

    @classmethod
    def init(cls, provider, currency_api_key):
        if cls._instance is None:
            cls._instance = ExchangeRates()
            cls._currency_api_key = currency_api_key
            if provider == "tinkoff":
                cls._rates_method = cls._instance._get_tinkoff_currency_rate
            else:
                cls._rates_method = cls._instance._get_exchangerate_rate

    @classmethod
    def get(cls, iso_default, iso_to):
        if not cls._instance:
            raise Exception("ExchangeRates is not initialized")
        return cls._instance._rates_method(iso_default, iso_to)

    def _get_tinkoff_currency_rate(self, iso_default, iso_to):
        url = f"https://api.tinkoff.ru/v1/currency_rates?from={iso_to.upper()}&to={iso_default.upper()}"
        headers = {"Sec-Ch-Ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\"", "Sec-Ch-Ua-Mobile": "?0",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                   "Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*",
                   "Origin": "https://www.tinkoff.ru", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors",
                   "Sec-Fetch-Dest": "empty", "Referer": "https://www.tinkoff.ru/",
                   "Accept-Encoding": "gzip, deflate", "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                   "Connection": "close"}
        response = requests.get(url, headers=headers)

        parsed = json.loads(response.text)
        for rate in parsed["payload"]["rates"]:
            if rate["category"] == "SavingAccountTransfers":
                return rate["sell"]
        raise Exception("There is no category \"SavingAccountTransfers\" in tinkoff's response")

    def _get_exchangerate_rate(self, iso_default, iso_to):
        if not self.rates_cache:
            url = f'https://api.currencyapi.com/v3/latest?base_currency={iso_default.upper()}'
            headers = {"apikey": self._currency_api_key}
            response = requests.get(url, headers=headers)
            data = response.json()
            self.rates_cache = {}
            for iso, rate in data["data"].items():
                self.rates_cache[iso.upper()] = 1.0 / rate["value"]
        if iso_to.upper() in self.rates_cache:
            return self.rates_cache[iso_to.upper()]
        else:
            return 0
