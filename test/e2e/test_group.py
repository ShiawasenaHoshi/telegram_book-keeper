from __future__ import annotations

import asyncio
import time

from helpers import push_update


async def test_group_messages_are_ignored(user) -> None:
  before = len(await user.messages())
  push_update(
    user.user_id,
    {
      "message": {
        "message_id": 1,
        "date": int(time.time()),
        "chat": {"id": -100_900_002, "type": "group", "title": "E2E"},
        "from": {"id": user.user_id, "is_bot": False, "first_name": "Test"},
        "text": "/help",
      }
    },
  )
  await asyncio.sleep(2)
  assert len(await user.messages()) == before
