import unittest

from app.api_client import get_tinkoff_currency_rate


class ApiClientCase(unittest.TestCase):
    def test_get_tinkoff_currency_rate(self):
        result = get_tinkoff_currency_rate("rub", "usd")
        self.assertTrue(isinstance(result, float))
        self.assertTrue(result > 0)
