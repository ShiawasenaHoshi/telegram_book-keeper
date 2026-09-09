import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render_env import MissingValueError, render


class RenderEnvTest(unittest.TestCase):
    def test_substitutes(self):
        self.assertEqual(render("A=${A}\n", {"A": "one"}), "A=one\n")

    def test_empty_is_error(self):
        with self.assertRaises(MissingValueError):
            render("A=${A}\n", {"A": ""})

    def test_missing_is_error(self):
        with self.assertRaises(MissingValueError):
            render("A=${A}\n", {})


if __name__ == "__main__":
    unittest.main()
