from __future__ import annotations


async def test_a_transaction_is_stored_in_the_chosen_category(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  await user.send("100")

  stored = db.execute(
    'SELECT amount, currency_iso FROM "transaction"'
  ).fetchall()
  assert len(stored) == 1


async def test_a_transaction_is_deleted_by_answering_it(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  await user.send("100")
  message_id = db.execute('SELECT msg_id FROM "transaction"').fetchone()[0]

  screen = await user.send("delete", reply_to_message_id=message_id)

  assert "удалена" in screen.text.lower()
  assert db.execute('SELECT count(*) FROM "transaction"').fetchone() == (0,)
