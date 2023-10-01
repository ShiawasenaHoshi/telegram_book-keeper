import unittest

from app.api_client import ExchangeRates
from test._test_config import TestConfig


class ApiClientCase(unittest.TestCase):
    def test_get_tinkoff_currency_rate(self):
        ExchangeRates.init("rub")
        result = ExchangeRates.get("rub", "usd")
        self.assertTrue(isinstance(result, float))
        self.assertTrue(result > 0)

    def test_get_exchangerate_rate(self):
        ExchangeRates.init("eur", TestConfig.CURRENCY_API_KEY)
        result = ExchangeRates.get("eur", "gel")
        self.assertTrue(isinstance(result, float))
        self.assertTrue(result > 0)