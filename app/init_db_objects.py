import datetime

from app import db
from app.models import Category, Currency, CurrencyRate
from app.user_models import User, ACCESS_LEVEL
from config import Config


class InitDB():
    def __init__(self, app):
        self.app = app

    def init_all(self):
        self.init_admin()
        self.init_categories()
        self.init_currencies()
        self.do()
        print("All necessary db objects successfully written!")

    def init_admin(self):
        with self.app.app_context():
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
        with self.app.app_context():
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
        with self.app.app_context():
            from app.api_client import ExchangeRates
            ExchangeRates.init("", Config.CURRENCY_API_KEY)
            ExchangeRates.get("eur","usd") #load
            currencies_db = Currency.get_all()
            if len(currencies_db) == 0:
                for iso, rate in ExchangeRates._instance.rates_cache.items():
                    c = Currency()
                    c.iso = iso.lower()
                    if iso.lower() == Config.MAIN_CURRENCY:
                        c.default = True
                    db.session.add(c)
                    cr = CurrencyRate()
                    cr.iso = iso.lower()
                    cr.date = datetime.date.today()
                    cr.rate = rate

                    db.session.add(cr)
        return self

    def do(self):
        db.session.commit()
