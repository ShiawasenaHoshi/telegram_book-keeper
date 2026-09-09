from __future__ import annotations


async def test_help_greets_the_user(user) -> None:
  screen = await user.send("/help")
  assert "учета расходов" in screen.text
  assert "🏪 Супермаркеты" in [b for row in (screen.reply_keyboard or []) for b in row]


async def test_start_matches_help(user) -> None:
  screen = await user.send("/start")
  assert "учета расходов" in screen.text
