import datetime
import os

from app import db
from app.models import Category, Currency, CurrencyRate
from app.user_models import User, ACCESS_LEVEL
from config import Config


class InitDB():
    def __init__(self, app):
        self.app = app

    def init_all(self):
        with self.app.app_context():
            self.init_admin()
            self.init_categories()
            self.init_currencies()
            self.do()
        print("All necessary db objects successfully written!")

    def init_admin(self):
        if not db.session.execute(
            db.select(User).filter_by(id=Config.TG_ADMIN_ID)
        ).scalar_one_or_none():
            a = User()
            a.id = Config.TG_ADMIN_ID
            a.name = "superadmin"
            a.access_level = ACCESS_LEVEL.ADMIN
            db.session.add(a)
        return self

    def init_categories(self):
        categories = {
            1: Category()._construct(1, "income", "Доход", 1, "💰"),
            2: Category()._construct(2, "transport", "Транспорт", 2, "🚕"),
            3: Category()._construct(3, "supermarkets", "Супермаркеты", 3, "🏪"),
            4: Category()._construct(4, "cafe", "Кафе", 4, "🍽"),
            5: Category()._construct(5, "household", "Хозяйство", 5, "🛠"),
            6: Category()._construct(6, "evolution", "Развитие", 6, "🧩"),
            7: Category()._construct(7, "entertainment", "Развлечения", 7, "🎉"),
            8: Category()._construct(8, "goods", "Вещи", 8, "💍"),
            9: Category()._construct(9, "service", "Банки,гос,связь", 9, "🏛"),
            10: Category()._construct(10, "gifts", "Подарки", 10, "🎁"),
            11: Category()._construct(11, "donation", "Донаты", 11, "📥"),

            13: Category()._construct(13, "investments", "Инвестиции", 13, "📊"),
            14: Category()._construct(14, "health", "Здоровье", 14, "🍏"),
            15: Category()._construct(15, "beauty", "Красота", 12, "💄"),

            12: Category()._construct(12, "other", "Другое", 15, "❔"),

        }
        ids = [c.id for c in db.session.execute(db.select(Category)).scalars().all()]
        for id, category in categories.items():
            if id not in ids:
                db.session.add(category)
        return self

    def init_currencies(self):
        if Currency.get_all():
            return self
        if Config.CURRENCY_API_KEY:
            from app.api_client import ExchangeRates
            ExchangeRates.init("", Config.CURRENCY_API_KEY)
            ExchangeRates.get(Config.MAIN_CURRENCY, "usd")
            rates = ExchangeRates._instance.rates_cache.items()
        elif os.environ.get("OFFLINE_RATES") == "1":
            from app.reference_currency_data import REFERENCE_RATES
            rates = REFERENCE_RATES.items()
        else:
            raise RuntimeError(
                "CURRENCY_API_KEY is not set and OFFLINE_RATES is not enabled"
            )
        self._seed_currencies(rates)
        return self

    def _seed_currencies(self, rates):
        main = Config.MAIN_CURRENCY.lower()
        today = datetime.date.today()
        for iso, rate in rates:
            iso_lower = iso.lower()
            c = Currency()
            c.iso = iso_lower
            c.default = iso_lower == main
            db.session.add(c)
            cr = CurrencyRate()
            cr.iso = iso_lower
            cr.date = today
            cr.rate = rate
            db.session.add(cr)

    def do(self):
        db.session.commit()
