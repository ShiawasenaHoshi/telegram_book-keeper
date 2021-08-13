import threading
import time

import flask
import telebot

from app.commands.book_keeping import BookKeepingCmd
from app.commands.main import GenericCmd
from config import Config

import traceback
class Bot(threading.Thread):

    def __init__(self, tg_token, admin_id, app):
        super().__init__()
        self.tg_token = tg_token

        self.app = app
        self.admin = admin_id
        self.l = app.logger
        if Config.WEBHOOK_ENABLE:
            self.bot = telebot.TeleBot(self.tg_token)

    def run(self):
        self.l.info("Bot starting")
        self.use_webhooks(Config.WEBHOOK_ENABLE)

    def use_webhooks(self, use_webhooks):
        app = self.app

        if use_webhooks:
            self.bot = telebot.TeleBot(self.tg_token)
            self.bot.remove_webhook()
            time.sleep(0.1)
            Bot.init_commands(self.bot, app, self.l, self.admin)
            if not Config.WEBHOOK_HOST:
                raise Exception("WEBHOOK_HOST is not defined")

            @app.route('/', methods=['GET', 'HEAD'])
            def index():
                return ''

            @app.route(Config.WEBHOOK_URL_PATH, methods=['POST'])
            def webhook():
                if flask.request.headers.get('content-type') == 'application/json':
                    json_string = flask.request.get_data().decode('utf-8')
                    update = telebot.types.Update.de_json(json_string)
                    self.bot.process_new_updates([update])
                    self.l.debug("hook: " + json_string)
                    return ''
                else:
                    flask.abort(403)

            self.bot.set_webhook(url=Config.WEBHOOK_URL_BASE + Config.WEBHOOK_URL_PATH,
                                 certificate=open(Config.WEBHOOK_SSL_CERT, 'r'))
            self.l.info("Webhook enabled: " + str(use_webhooks))
        else:
            self.l.info("Webhook enabled: " + str(use_webhooks))
            while True:
                try:
                    self.l.info("New bot instance started")
                    self.bot = telebot.TeleBot(self.tg_token)
                    Bot.init_commands(self.bot, app, self.l, self.admin)
                    self.bot.polling(none_stop=True, interval=Config.BOT_INTERVAL, timeout=Config.BOT_TIMEOUT)
                except Exception as ex:  # Error in polling
                    self.l.error("Bot polling failed, restarting in {}sec. Error:\n{}".format(Config.BOT_TIMEOUT, ex), exc_info=True)
                    self.bot.stop_polling()
                    time.sleep(Config.BOT_TIMEOUT)
                else:  # Clean exit
                    self.bot.stop_polling()
                    self.l.info("Bot polling loop finished")
                    break  # End loop

    @staticmethod
    def init_commands(bot, app, logger, admin_uid):
        gc = GenericCmd(bot, app, logger, admin_uid)
        bc = BookKeepingCmd(bot, app, logger, admin_uid)
        bc.month_start_balance_check()

        FETCH_CURRENCIES_TIME = "10:00"

        def fetch_currencies_rates_thread():
            import schedule
            schedule.every().day.at(FETCH_CURRENCIES_TIME).do(bc.fetch_currencies_rates)

            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=fetch_currencies_rates_thread)
        thread.start()
