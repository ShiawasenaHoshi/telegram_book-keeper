from __future__ import annotations

import asyncio

from helpers import edited_message, push_update


async def test_a_transaction_is_edited_by_editing_the_message(user, db) -> None:
  await user.send("🏪 Супермаркеты")
  await user.send("100")
  msg_id = db.execute('SELECT msg_id FROM "transaction"').fetchone()[0]

  update_id = push_update(user.user_id, edited_message(user.user_id, msg_id, "200 edited"))
  await user._http.get(
    f"/user/chats/{user.bot_id}/acks/{update_id}",
    params={"timeout": 10.0},
  )
  await asyncio.sleep(0.5)
  messages = await user.messages()
  assert any("изменена" in m.text.lower() for m in messages)
  amount = db.execute('SELECT amount FROM "transaction"').fetchone()[0]
  assert amount == 200.0


async def test_editing_a_missing_transaction_is_reported(user) -> None:
  update_id = push_update(user.user_id, edited_message(user.user_id, 999_999, "200 x"))
  await user._http.get(
    f"/user/chats/{user.bot_id}/acks/{update_id}",
    params={"timeout": 10.0},
  )
  messages = await user.messages()
  assert any("отсутствует" in m.text.lower() for m in messages)
