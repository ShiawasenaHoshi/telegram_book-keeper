import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, desc, and_, exists
from sqlalchemy.sql import label

from app import db


def default_dates(from_date=None, to_date=None):
    dt = datetime.datetime
    if not from_date:
        today = dt.today()
        from_date = dt(today.year, today.month, 1)
    if not to_date:
        if from_date:
            to_date = from_date + relativedelta(months=1)
        else:
            today = dt.today()
            to_date = dt(today.year, today.month, 1) + relativedelta(months=1)
    if to_date < from_date:
        raise Exception("to_date less than from_date")
    return from_date, to_date


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    currency_iso = db.Column(db.String(3), db.ForeignKey('currency.iso'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    msg_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(128), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    @staticmethod
    def add(timestamp, amount, currency_iso, user_id, msg_id, description, category_id):
        tx = Transaction()
        tx.timestamp = timestamp
        tx.amount = amount
        if currency_iso:
            tx.currency_iso = currency_iso
        else:
            tx.currency_iso = Currency.get_default()
        tx.user_id = user_id
        tx.msg_id = msg_id
        tx.description = description
        tx.category_id = category_id
        db.session.add(tx)
        db.session.commit()
        return tx

    @staticmethod
    def remove_by_msg(user_id, msg_id):
        tx = Transaction.query.filter_by(user_id=user_id, msg_id=msg_id).first()
        if tx:
            db.session.delete(tx)
            db.session.commit()
        return tx

    @staticmethod
    def edit_by_msg(user_id, msg_id, amount, currency_iso, description):
        tx = Transaction.query.filter_by(user_id=user_id, msg_id=msg_id).first()
        if tx:
            tx.amount = amount
            if currency_iso:
                tx.currency_iso = currency_iso
            if description:
                tx.description = description
            if tx:
                db.session.commit()
                tx = Transaction.query.filter_by(user_id=user_id, msg_id=msg_id).first()
        return tx

    @staticmethod
    def tx_summary(category_id):
        today = datetime.date.today()
        month_start, month_end = default_dates(datetime.date(today.year, today.month, 1))
        month_summary = Transaction.summary(month_start, month_end)

        tomorrow = today + datetime.timedelta(days=1)
        day_summary = Transaction.summary(today, tomorrow)
        return {
            "month_income": month_summary["total_income"],
            "month_expense": month_summary["total_expense"],
            "month_category_expense": month_summary["expenses"][category_id]["sum"] if category_id in month_summary[
                "expenses"] else 0,
            "month_expenses": month_summary["expenses"],
            "day_income": day_summary["total_income"],
            "day_expense": day_summary["total_expense"],
            "day_category_expense": day_summary["expenses"][category_id]["sum"] if category_id in day_summary[
                "expenses"] else 0,
            "balance": month_summary["balance"],
            "start_balance": month_summary["start_balance"] if "start_balance" in month_summary else 0
        }

    @staticmethod
    def report(from_date=None, to_date=None):
        from_date, to_date = default_dates(from_date, to_date)
        subq1 = db.session.query(Transaction.id).filter(Transaction.timestamp >= from_date,
                                                        Transaction.timestamp < to_date).subquery()

        subq3 = db.session.query(Transaction.id,
                                 Transaction.timestamp,
                                 Transaction.category_id,
                                 Transaction.currency_iso,
                                 Transaction.description,
                                 Transaction.amount,
                                 CurrencyRate.rate,
                                 label('converted_amount', Transaction.amount * CurrencyRate.rate)) \
            .filter(Transaction.id.in_(subq1)) \
            .join(CurrencyRate, (Transaction.currency_iso == CurrencyRate.iso) & (
                func.date_trunc('day', Transaction.timestamp) == CurrencyRate.date)) \
            .subquery()
        res = db.session.query(subq3.c.timestamp,
                               subq3.c.converted_amount,
                               func.concat(subq3.c.amount, " ", subq3.c.currency_iso).label('amount_in_currency'),
                               subq3.c.description,
                               func.concat(Category.utf_icon, " ", Category.description).label('cat_title')) \
            .join(Category, subq3.c.category_id == Category.id) \
            .order_by(subq3.c.timestamp) \
            .all()

        return res

    @staticmethod
    def summary(from_date=None, to_date=None):
        from_date, to_date = default_dates(from_date, to_date)

        subq1 = db.session.query(Transaction.id).filter(Transaction.timestamp >= from_date,
                                                        Transaction.timestamp < to_date).subquery()

        subq2 = db.session.query(Transaction.id,
                                 Transaction.category_id,
                                 Transaction.currency_iso,
                                 Transaction.amount,
                                 CurrencyRate.rate,
                                 label('converted_amount', Transaction.amount * CurrencyRate.rate)) \
            .filter(Transaction.id.in_(subq1)) \
            .join(CurrencyRate, (Transaction.currency_iso == CurrencyRate.iso) & (
                func.date_trunc('day', Transaction.timestamp) == CurrencyRate.date)) \
            .subquery()
        subq3 = db.session.query(subq2.c.category_id, func.sum(subq2.c.converted_amount).label('sum')) \
            .group_by(subq2.c.category_id) \
            .order_by(desc("sum")) \
            .subquery()
        total = db.session.query(subq3.c.category_id, Category.description, Category.utf_icon, subq3.c.sum) \
            .join(Category, subq3.c.category_id == Category.id) \
            .all()

        total = {cat[0]: (cat[1], cat[2], round(cat[3], 1)) for cat in total}

        expenses = {id: {"description": data[0], "icon": data[1], "sum": data[2]} for id, data in total.items() if
                    id != CAT_INCOME}
        sum_expenses = sum([cat["sum"] for cat in expenses.values()])
        for id in expenses.keys():
            expenses[id]["percentage"] = round(100 * expenses[id]["sum"] / sum_expenses, 1)

        if CAT_INCOME in total:
            total_income = total[CAT_INCOME][2]
            balance = total_income - sum_expenses
        else:
            total_income = 0
            balance = sum_expenses * -1

        result = {
            "total_income": round(total_income, 1),
            "total_expense": round(sum_expenses, 1),
            "expenses": expenses,
            "balance": round(balance, 1)
        }

        start_balance = MonthStartBalance.query.filter_by(year=from_date.year, month=from_date.month).first()
        if start_balance:
            result["start_balance"] = round(start_balance.balance, 1)

        return result

    __table_args__ = (
        db.Index('ix_tx_timestamp', timestamp),
        db.Index('ix_cat_id', category_id),
        db.Index('ix_user_msg', user_id, msg_id),
    )


currency_set = None


class Currency(db.Model):
    iso = db.Column(db.String(3), primary_key=True)
    default = db.Column(db.Boolean, default=False)

    @staticmethod
    def set_default(iso):
        a = Currency.query.filter_by(default=True).first()
        a.default = False
        b = Currency.query.filter_by(iso=iso).first()
        b.default = True
        db.session.commit()

    @staticmethod
    def get_default():
        return Currency.query.filter_by(default=True).first().iso

    def get_last_rate(self):
        pass

    @staticmethod
    def get_all():
        currencies = db.session.query(Currency.iso).all()
        currencies_set = set(c.iso for c in currencies)
        return currencies_set  # todo cache


class CurrencyRate(db.Model):
    iso = db.Column(db.String(3), db.ForeignKey('currency.iso'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    rate = db.Column(db.Float, nullable=False)

    @staticmethod
    def set(iso, rate, date=None):
        # todo check existence
        cr = CurrencyRate()
        cr.iso = iso
        cr.date = date if date else datetime.date.today()
        cr.rate = rate
        db.session.add(cr)
        db.session.commit()

    @staticmethod
    def get(iso, date=None):
        if not date:
            date = datetime.date.today()
        result = CurrencyRate.query.filter_by(iso=iso, date=date).first()
        return result.rate if result else None

    @staticmethod
    def get_not_existed_rates_for_dates(from_date=None, to_date=None):
        from_date, to_date = default_dates(from_date, to_date)
        subq1 = db.session.query(
            Transaction.currency_iso,
            label('tx_date', func.date_trunc('day', Transaction.timestamp))
        ) \
            .filter(Transaction.timestamp >= from_date, Transaction.timestamp < to_date).subquery()
        subq2 = db.session.query(subq1.c.currency_iso, subq1.c.tx_date) \
            .distinct(subq1.c.currency_iso, subq1.c.tx_date).subquery()
        result = db.session.query(subq2.c.currency_iso, subq2.c.tx_date) \
            .filter(
            ~exists().where(
                and_(subq2.c.currency_iso == CurrencyRate.iso, subq2.c.tx_date == CurrencyRate.date))).all()
        return result


class MonthStartBalance(db.Model):
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False)

    @staticmethod
    def is_exist_for_current_month():
        today = datetime.date.today()
        b = MonthStartBalance.query.filter_by(year=today.year, month=today.month).first()
        return b

    @staticmethod
    def update(year=None, month=None):
        if year and month:
            from_date = datetime.date(year, month, 1)
        elif not year and not month:
            today = datetime.date.today()
            first = today.replace(day=1)
            from_date = first - datetime.timedelta(days=1)  # previous_month
            year = from_date.year
            month = from_date.month
            from_date = datetime.date(year, month, 1)
        else:
            raise Exception(f"{'year' if month else 'month'} is None, but {'year' if year else 'month'} isn't None")
        report = Transaction.summary(from_date=from_date)

        month_start_balance = MonthStartBalance.query.filter_by(year=year, month=month).first()
        if month_start_balance:
            next_month_balance = month_start_balance.balance + report['balance']
        else:
            next_month_balance = report['balance']
        to_date = from_date + relativedelta(months=1)
        next = MonthStartBalance.query.filter_by(year=to_date.year, month=to_date.month).first()
        if not next:
            next = MonthStartBalance()
            next.year = to_date.year
            next.month = to_date.month
            db.session.add(next)
        next.balance = next_month_balance
        db.session.commit()
        return next

    @staticmethod
    def update_all():
        # todo update from older to newer txs
        pass


CAT_INCOME = 1


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(16))
    description = db.Column(db.String(128))
    utf_icon = db.Column(db.String(3))
    ui_order = db.Column(db.Integer, default=id)

    def _construct(self, id, short_name, description, ui_order, utf_icon):
        self.id = id
        self.short_name = short_name
        self.description = description
        self.utf_icon = utf_icon
        self.ui_order = ui_order
        return self

    @staticmethod
    def get(id):
        return Category.query.filter_by(id=id).first()
