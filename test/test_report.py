from app.models import Transaction
from app.report.generator import generate_report
from test.test_models import DBCase


class ReportCase(DBCase):
    test_year = 2021
    test_month = 12

    def test_generate(self):
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        from_date, to_date = self.generate_tx_users(test_year, test_month, iso)
        self.generate_currency_rates(test_year, test_month, iso)

        data = Transaction.report(from_date, to_date)
        generate_report(data)
        pass
