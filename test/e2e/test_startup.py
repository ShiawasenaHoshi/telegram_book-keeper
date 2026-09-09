from __future__ import annotations


def test_month_start_balance_exists_after_bot_startup(db) -> None:
  """month_start_balance_check runs once when the bot container starts."""
  count = db.execute("SELECT count(*) FROM month_start_balance").fetchone()[0]
  assert count >= 1
