import unittest

from freezegun import freeze_time

from app import create_app
from app import db
from app.commands.book_keeping import BookKeepingCmd
from test._test_classes import TestBot, TestMessage
from test._test_config import TestConfig
from test.test_models import DBCase


class CommandsCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.dc = dc = DBCase()
        dc.setUp()

        self.l = self.app.logger
        self.admin = 0

    def tearDown(self):
        self.dc.tearDown()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_summary(self):
        def send_msg_func(uid, text):
            print(f"{uid}:{text}")

        def send_doc_func(aid, data):
            print(f"{aid}:{data}")

        bot = TestBot(send_msg_func, send_doc_func)
        bkc = BookKeepingCmd(bot, self.app, self.l, self.admin)
        test_year = DBCase.test_year
        test_month = DBCase.test_month
        iso = "usd"
        self.dc.generate_tx_users(test_year, test_month, iso)
        freezer = freeze_time(f"{DBCase.test_year}-{DBCase.test_month}-15 12:00:01")
        freezer.start()
        bkc.summary(TestMessage())
        self.dc.generate_currency_rates(test_year, test_month, iso)
        bkc.summary(TestMessage())
        freezer.stop()
