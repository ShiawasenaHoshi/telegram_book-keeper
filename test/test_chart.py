import unittest

import matplotlib.pyplot

from app.charts import expenses_pie


class ChartCase(unittest.TestCase):
    def test_expenses_pie(self):
        expenses = {7: {'description': 'Развлечения', 'icon': '🎉', 'sum': 337500.0, 'percentage': 11.7},
                    4: {'description': 'Кафе', 'icon': '🍽', 'sum': 285000.0, 'percentage': 9.9},
                    9: {'description': 'Банки,гос,связь', 'icon': '🏛', 'sum': 285000.0, 'percentage': 9.9},
                    12: {'description': 'Другое', 'icon': '❔', 'sum': 277500.0, 'percentage': 9.6},
                    5: {'description': 'Хозяйство', 'icon': '🛠', 'sum': 270000.0, 'percentage': 9.4},
                    2: {'description': 'Транспорт', 'icon': '🚕', 'sum': 262500.0, 'percentage': 9.1},
                    8: {'description': 'Вещи', 'icon': '💍', 'sum': 262500.0, 'percentage': 9.1},
                    10: {'description': 'Подарки', 'icon': '🎁', 'sum': 247500.0, 'percentage': 8.6},
                    6: {'description': 'Развитие', 'icon': '🧩', 'sum': 225000.0, 'percentage': 7.8},
                    3: {'description': 'Супермаркеты', 'icon': '🏪', 'sum': 225000.0, 'percentage': 7.8},
                    11: {'description': 'Донаты', 'icon': '📥', 'sum': 202500.0, 'percentage': 7.0}}
        matplotlib.pyplot.savefig = lambda filename: matplotlib.pyplot.show()
        path = expenses_pie(expenses)
        self.assertIsNotNone(path)
