import unittest

import matplotlib.pyplot

from app.charts import expenses_pie


class ChartCase(unittest.TestCase):
    def test_expenses_pie(self):
        expenses = {9: ['🏛 Банки,гос,связь', 367500.0, 12.4], 3: ['🏪 Супермаркеты', 322500.0, 17.9],
                    2: ['🚕 Транспорт', 315000.0, 10.6], 8: ['💍 Вещи', 285000.0, 9.6],
                    11: ['📥 Донаты', 277500.0, 9.3], 12: ['❔ Другое', 262500.0, 8.8],
                    5: ['🛠 Хозяйство', 255000.0, 8.6], 4: ['🍽 Кафе', 255000.0, 8.6],
                    6: ['🧩 Развитие', 247500.0, 14.0], 7: ['🎉 Развлечения', 210000.0, 0.1],
                    10: ['🎁 Подарки', 172500.0, 0.1]}
        matplotlib.pyplot.savefig = lambda filename: matplotlib.pyplot.show()
        path = expenses_pie(expenses)
        self.assertIsNotNone(path)
