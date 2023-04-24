import unittest

from app.api_client import ExchangeRates


class ApiClientCase(unittest.TestCase):
    def test_get_tinkoff_currency_rate(self):
        ExchangeRates.init("rub")
        result = ExchangeRates.get("rub", "usd")
        self.assertTrue(isinstance(result, float))
        self.assertTrue(result > 0)

    def test_get_exchangerate_rate(self):
        ExchangeRates.init("eur")
        result = ExchangeRates.get("eur", "gel")
        self.assertTrue(isinstance(result, float))
        self.assertTrue(result > 0)