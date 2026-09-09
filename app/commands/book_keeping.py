import datetime

from telebot.apihelper import ApiTelegramException

from app import db
from app.api_client import ExchangeRates
from app.charts import expenses_pie
from app.commands.abstract import Cmd, input_method, bot_handler_dict
from app.models import Transaction, Category, CurrencyRate, Currency, MonthStartBalance, default_dates, CAT_INCOME
from app.user_models import ACCESS_LEVEL, User
from app.report.generator import generate_report
from config import Config


class BookKeepingCmd(Cmd):
    def __init__(self, bot, app, logger, admin):
        super().__init__(bot, app, logger, admin)

        bot.add_edited_message_handler(bot_handler_dict(self.edit_transaction, None,
                                                         lambda msg: Cmd.is_allowed(msg, ACCESS_LEVEL.USER)))

        bot.add_message_handler(bot_handler_dict(self.delete_transaction, self.re_delete_transaction,
                                                  lambda msg: Cmd.is_allowed(msg,
                                                                             ACCESS_LEVEL.USER) and msg.reply_to_message))

    def edit_transaction(self, msg):
        amount, currency_iso, description = self.parse_tx_msg(msg)
        with Cmd.ctx():
            tx = Transaction.edit_by_msg(msg.chat.id, msg.message_id, amount, currency_iso, description)
            if tx:
                cat = Category.get(tx.category_id)
                tx_str = f"{tx.amount} {tx.currency_iso} ({cat.description}) {tx.description}"
                self.bot.reply_to(msg, f"Транзакция изменена. Теперь в базе: {tx_str}",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
            else:
                self.bot.reply_to(msg, f"Транзакция отсутствует в базе",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
        self.l.info(f"Uid_{msg.from_user.id} has sended data: {msg.text}")

    re_delete_transaction = f"^(delete|del|rm|удалить|удали)$"

    def delete_transaction(self, msg):
        with Cmd.ctx():
            tx = Transaction.remove_by_msg(msg.reply_to_message.chat.id, msg.reply_to_message.id)
            if tx:
                cat = Category.get(tx.category_id)
                tx_str = f"{tx.amount} {tx.currency_iso} ({cat.utf_icon} {cat.description}) {tx.description}"
                self.bot.reply_to(msg.reply_to_message, f"Запись удалена из базы: {tx_str}",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
            else:
                self.bot.reply_to(msg.reply_to_message, f"Запись уже удалена из базы ранее",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))

    def dict_of_methods(self):
        with Cmd.ctx():
            cats = db.session.execute(
                db.select(Category).order_by(Category.ui_order)
            ).scalars().all()
            result = {}

            def tx_lambda(cat_id):
                return lambda msg: self.add_transaction(msg, cat_id)

            for cat in cats:
                result[tx_lambda(cat.id)] = (cat.short_name, f"{cat.utf_icon} {cat.description}", ACCESS_LEVEL.USER)

            result[self.set_default_currency] = ("set_default_currency", "🔧 Уст. валюту", ACCESS_LEVEL.ADMIN)
            result[self.summary] = ("summary", "📊 Отчет", ACCESS_LEVEL.USER)
            return result

    def set_default_currency(self, msg):
        msg = self.bot.send_message(msg.chat.id,
                                    'Напишите iso валюты',
                                    reply_markup=self.markup_back_to_menu)
        self.bot.register_next_step_handler(msg, self.waiting_for_data_default_currency)

    @input_method()
    def waiting_for_data_default_currency(self, msg):
        iso = msg.text.strip()
        with Cmd.ctx():
            Currency.set_default(iso)
        self.bot.reply_to(msg, f"{iso} теперь валюта по умолчанию",
                          reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
        self.l.info(f"Uid_{msg.from_user.id} has sended data: {msg.text}")

    def add_transaction(self, msg, cat_id):
        with Cmd.ctx():
            summary = Transaction.tx_summary(category_id=cat_id)
            summary_text = ''
            cat = Category.get(cat_id)
            cat_text = f"{cat.utf_icon} {cat.description}"
            if cat_id == CAT_INCOME:
                summary_text += f"{cat_text.upper()} ЗА СЕГОДНЯ: {summary['day_income']}\n\n"
            else:
                summary_text += f"РАСХОДЫ НА {cat_text.upper()}: \n- за сегодня: {summary['day_category_expense']}\n- за месяц: {summary['month_category_expense']}\n\n"
            summary_text += f"ВСЕГО ПОТРАЧЕНО СЕГОДНЯ: {summary['day_expense']}\n\n"
            summary_text += f"СВОДКА ЗА МЕСЯЦ. \n- стартовый баланс {summary['start_balance']} \n- Σ приход: {summary['month_income']}\n- Σ расход: {summary['month_expense']}\n\n" \
                            f"БАЛАНС: {round(summary['balance'] + summary['start_balance'], 1)}"
        self.bot.send_message(msg.chat.id, summary_text)
        msg = self.bot.send_message(msg.chat.id,
                                    'Напишите сумму транзакции',
                                    reply_markup=self.markup_back_to_menu)
        self.bot.register_next_step_handler(msg, lambda msg: self.waiting_for_data_transaction(msg, cat_id, summary))

    def parse_tx_msg(self, msg):
        temp = msg.text.strip()
        while "  " in temp:
            temp = temp.replace("  ", " ")
        data = temp.split(" ", 1)
        amount = float(data[0])

        if len(data) > 1:
            description = data[1]
            currency_iso = description[:3]
            with Cmd.ctx():
                if currency_iso in Currency.get_all():
                    description = description[3:].strip()
                else:
                    currency_iso = None
        else:
            description = ""
            currency_iso = None
        return amount, currency_iso, description

    @input_method()
    def waiting_for_data_transaction(self, msg, cat_id, summary):
        if cat_id and summary:
            try:
                timestamp = datetime.datetime.fromtimestamp(msg.date)
                amount, currency_iso, description = self.parse_tx_msg(msg)
                rate = self.fetch_currency_rate(currency_iso)
                with Cmd.ctx():
                    Transaction.add(timestamp, amount, currency_iso, msg.chat.id, msg.message_id, description, cat_id)
                tx_changes = f"+ {round(amount * rate)} {Config.MAIN_CURRENCY}"

                expenses_text = "\n".join(
                    [f"{val['icon']} {val['description']}: {val['sum']} {Config.MAIN_CURRENCY} {tx_changes if id == cat_id else ''}" for
                     id, val in
                     summary["month_expenses"].items()])
                if cat_id == CAT_INCOME:
                    with Cmd.ctx():
                        c = Category.get(cat_id)
                        expenses_text = f"{c.utf_icon} {c.description}: {summary['month_income']} {tx_changes} \n" + expenses_text
                elif cat_id not in summary["month_expenses"].keys():
                    with Cmd.ctx():
                        c = Category.get(cat_id)
                        expenses_text = f"{c.utf_icon} {c.description}: 0 {tx_changes} \n" + expenses_text
                self.bot.reply_to(msg, f"Транзакция записана\n{expenses_text}",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
                self.l.info(f"Uid_{msg.from_user.id} has sended data: {msg.text}")
            except Exception as e:
                self.l.info(e)
                self.bot.send_message(msg.chat.id, f"Что-то пошло не так. Повторите ввод. (Ошибка: {e})")
                self.bot.register_next_step_handler(msg, lambda msg: self.waiting_for_data_transaction(msg, cat_id, summary))
        else:
            self.bot.clear_step_handler_by_chat_id(chat_id=msg.chat.id)
            self.bot.send_message(msg.chat.id,
                                  "Что-то пошло не так. Попробуйте снова нажать кнопку категории и отправить транзакцию",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))

    def fetch_currency_rate(self, iso=None):
        if iso == Config.MAIN_CURRENCY:
            rate = 1
        else:
            with Cmd.ctx():
                if not iso:
                    iso = Currency.get_default()
                rate = CurrencyRate.get(iso)
                if rate is None:
                    rate = ExchangeRates.get(Config.MAIN_CURRENCY, iso)
                    CurrencyRate.set(iso, rate)
                    self.l.info(f"Today's {iso.upper()} rate set to {rate}")
        return rate

    def fetch_currencies_rates(self):
        with Cmd.ctx():
            for iso in Currency.get_all():
                if CurrencyRate.get(iso) is None:
                    if iso == Config.MAIN_CURRENCY:
                        rate = 1
                    else:
                        rate = ExchangeRates.get(Config.MAIN_CURRENCY, iso)
                    CurrencyRate.set(iso, rate)
                    self.l.info(f"Today's {iso.upper()} rate set to {rate}")

    def summary(self, msg_or_user_id, from_date=None, to_date=None):
        if isinstance(msg_or_user_id, int):
            user_id = msg_or_user_id
        else:
            user_id = msg_or_user_id.chat.id
        if not from_date or not to_date:
            from_date, to_date = default_dates()
        month_year = from_date.strftime("%m.%y")
        self.fetch_currencies_rates()
        with Cmd.ctx():
            not_existed_rates = CurrencyRate.get_not_existed_rates_for_dates()
            if not_existed_rates:
                text = "Ошибка: нет курса валют на следующие дни\n"
                text += "\n".join(f"{ner[0]}: {ner[1].strftime('%Y.%m.%d')}" for ner in not_existed_rates)
                self.bot.send_message(user_id, text)
            else:
                summary = Transaction.summary(from_date, to_date)
                text = f"ОТЧЕТ ЗА {month_year.upper()}\n" \
                       f"Приход: {summary['total_income']}\n" \
                       f"Расход: {summary['total_expense']}\n"

                balance = summary['balance']
                if "start_balance" in summary:
                    text += f"С прошлого месяца: {summary['start_balance']}\n"
                    balance = round(balance + summary["start_balance"], 1)

                text += f"Баланс: {balance}"

                self.bot.send_message(user_id, text)
                path = expenses_pie(summary["expenses"])
                f = open(path, 'rb')
                self.bot.send_photo(user_id, f, None)
                expenses_text = "РАСХОД ПО КАТЕГОРИЯМ\n"
                expenses_text += "\n".join(
                    [
                        f"{e['icon']} {e['description']}: {e['sum']} {Config.MAIN_CURRENCY} ({e['percentage'] if e['percentage'] >= 0.1 else '>0.1'}%)"
                        for e in summary["expenses"].values()])

                self.bot.send_message(user_id, expenses_text)

                data = Transaction.report(from_date, to_date)
                path = generate_report(data)
                try:
                    f = open(path, 'rb')
                    self.bot.send_document(user_id, f, None,
                                           reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(user_id)))
                except BaseException as be:
                    self.l.error(be, exc_info=True)

    def month_start_balance_check(self):
        with Cmd.ctx():
            b = MonthStartBalance.is_exist_for_current_month()
            if not MonthStartBalance.is_exist_for_current_month():
                self.l.info("Sending last month's summary to all users")
                last_month = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
                from_date, to_date = default_dates(datetime.date(last_month.year, last_month.month, 1))
                for u in db.session.execute(db.select(User)).scalars().all():
                    try:
                        self.bot.send_message(u.id, "ОТЧЕТ ЗА ПРОШЛЫЙ МЕСЯЦ")
                        self.summary(u.id, from_date, to_date)
                    except ApiTelegramException as ate:
                        self.l.error(f"uid{u.id}: {ate}")
                    except BaseException as be:
                        self.l.error(be, exc_info=True)
                self.l.info("Defining month's start balance")
                b = MonthStartBalance.update()
            self.l.info(f"Month's start balance defined as {b.balance} {Config.MAIN_CURRENCY}")
