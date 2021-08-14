import datetime
import random
import unittest

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from app import create_app
from app import db
from app.init_db_objects import InitDB
from app.models import Transaction, CurrencyRate, MonthStartBalance
from app.user_models import ACCESS_LEVEL, User
from test._test_config import TestConfig


class DBCase(unittest.TestCase):
    test_year = 2021
    test_month = 12

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        InitDB(self.app).init_categories().init_currencies().do()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_basic(self):
        u1 = User.add(1, "user1", ACCESS_LEVEL.USER)
        msg_id = 1
        Transaction.add(datetime.datetime.now(), 100, "usd", u1.id, msg_id, "test tx", 1)
        tx = Transaction.remove_by_msg(u1.id, 1)
        self.assertIsNotNone(tx)
        tx = Transaction.remove_by_msg(u1.id, 1)
        self.assertIsNone(tx)

    def generate_tx_users(self, year, month, iso):
        u1 = User.add(1, "user1", ACCESS_LEVEL.USER)
        msg_id = 1
        from_date = datetime.datetime(year, month, 1, 0, 0, 0)
        to_date = from_date + relativedelta(months=1)

        for i in range(1, 32):
            for x in range(random.randint(1, 30)):
                Transaction.add(
                    datetime.datetime(year, month, i, random.randint(0, 23), random.randint(0, 59),
                                      random.randint(0, 59)),
                    100, iso, u1.id, msg_id, "test tx", random.randint(1, 12))
                msg_id += 1
        return from_date, to_date

    def generate_currency_rates(self, year, month, iso):
        for i in range(1, 32):
            CurrencyRate.set(iso, 75, datetime.date(year, month, i))

    def test_summary(self):
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        from_date, to_date = self.generate_tx_users(test_year, test_month, iso)
        self.generate_currency_rates(test_year, test_month, iso)

        res = Transaction.summary(from_date, to_date)
        self.assertIsNotNone(res)
        self.assertEqual(4, len(res))
        freezer = freeze_time(f"{test_year}-{test_month}-15 12:00:01")
        freezer.start()
        res = Transaction.summary()
        freezer.stop()
        self.assertIsNotNone(res)
        self.assertEqual(4, len(res))

    def test_report(self):
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        from_date, to_date = self.generate_tx_users(test_year, test_month, iso)
        self.generate_currency_rates(test_year, test_month, iso)

        res = Transaction.report(from_date, to_date)
        self.assertIsNotNone(res)
        self.assertEqual(len(Transaction.query.all()), len(res))
        freezer = freeze_time(f"{test_year}-{test_month}-15 12:00:01")
        freezer.start()
        res = Transaction.report()
        freezer.stop()
        self.assertIsNotNone(res)
        self.assertEqual(len(Transaction.query.all()), len(res))

    def test_get_not_existed_rates_for_dates(self):
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        from_date, to_date = self.generate_tx_users(test_year, test_month, iso)

        not_existed_rates = CurrencyRate.get_not_existed_rates_for_dates(from_date, to_date)
        self.assertEqual(31, len(not_existed_rates))
        self.generate_currency_rates(test_year, test_month, iso)
        not_existed_rates = CurrencyRate.get_not_existed_rates_for_dates(from_date, to_date)
        self.assertEqual(0, len(not_existed_rates))

    def test_month_start_balance(self):
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        from_date, to_date = self.generate_tx_users(test_year, test_month, iso)
        self.generate_currency_rates(test_year, test_month, iso)
        b = MonthStartBalance.update(test_year, test_month)
        res = Transaction.summary(from_date, to_date)
        self.assertEqual(b.balance, res['balance'])
        old_balance = 20000
        old_b = MonthStartBalance()
        old_b.year = from_date.year
        old_b.month = from_date.month
        old_b.balance = old_balance
        db.session.add(old_b)
        db.session.commit()
        b = MonthStartBalance.update(test_year, test_month)
        self.assertEqual(b.balance, res['balance'] + old_balance)
        res = Transaction.summary(from_date, to_date)
        self.assertEqual(b.balance, res['balance'] + old_balance)
        self.assertEqual(res['start_balance'], old_balance)

        b = MonthStartBalance.query.filter_by(year=2022, month=1).first()
        self.assertEqual(b.balance, res['balance'] + old_balance)
