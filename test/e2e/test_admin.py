from __future__ import annotations

import asyncio

from helpers import forwarded_message, push_update


async def test_default_currency_can_be_changed(admin, db) -> None:
  await admin.send("🔧 Уст. валюту")
  screen = await admin.send("usd")
  assert "usd" in screen.text.lower()
  default = db.execute('SELECT iso FROM currency WHERE "default" IS TRUE').fetchone()
  assert default[0] == "usd"


async def test_user_list_is_shown(admin, db) -> None:
  peer_id = 909_150
  db.execute(
    'INSERT INTO "user" (id, name, access_level) VALUES (%s, %s, %s)',
    (peer_id, "peer", "USER"),
  )
  screen = await admin.send("🧑‍💻 Список пользователей")
  assert str(peer_id) in screen.text


async def test_access_level_can_be_changed(admin, db) -> None:
  await admin.send("🧞‍♂️ Уровень доступа")
  screen = await admin.send("2")
  assert "изменен" in screen.text.lower()
  level = db.execute(
    'SELECT access_level FROM "user" WHERE id = %s', (admin.user_id,)
  ).fetchone()[0]
  assert level == "USER"


async def test_a_forwarded_message_adds_a_user(admin, db) -> None:
  new_id = 909_201
  await admin.send("🙋 Добавить пользователя")
  update_id = push_update(
    admin.user_id, forwarded_message(admin.user_id, new_id, first_name="Newbie")
  )
  await admin._http.get(
    f"/user/chats/{admin.bot_id}/acks/{update_id}",
    params={"timeout": 10.0},
  )
  await asyncio.sleep(0.5)
  messages = await admin.messages()
  assert any("добавлен" in m.text.lower() for m in messages)
  assert db.execute('SELECT count(*) FROM "user" WHERE id = %s', (new_id,)).fetchone() == (1,)
