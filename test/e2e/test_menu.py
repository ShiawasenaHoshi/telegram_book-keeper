from __future__ import annotations

import pytest
from telemulator import BotSilentError


async def test_back_to_menu_cancels_input(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  screen = await user.send("❌ В меню")
  assert "Операция отменена" in screen.text
  await user.send("100", expect_reply=False)
  assert db.execute('SELECT count(*) FROM "transaction"').fetchone() == (0,)


async def test_reset_cancels_input(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  screen = await user.send("/reset")
  assert "Операция отменена" in screen.text
  await user.send("100", expect_reply=False)
  assert db.execute('SELECT count(*) FROM "transaction"').fetchone() == (0,)


async def test_a_stranger_gets_no_answer(stranger) -> None:
  with pytest.raises(BotSilentError):
    await stranger.send("/help", timeout=5.0)
