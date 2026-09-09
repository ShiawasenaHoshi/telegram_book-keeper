from __future__ import annotations


async def test_a_transport_transaction_is_stored(user, db) -> None:
  await user.send("🚕 Транспорт")
  await user.send("50")
  assert db.execute('SELECT count(*) FROM "transaction"').fetchone() == (1,)


async def test_income_shows_a_different_summary_header(user) -> None:
  await user.send("💰 Доход", expect_reply=False)
  messages = await user.messages()
  assert any("ДОХОД" in m.text.upper() for m in messages)


async def test_a_transaction_with_explicit_currency(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  await user.send("100 usd lunch")
  row = db.execute('SELECT currency_iso FROM "transaction"').fetchone()
  assert row[0] == "usd"
