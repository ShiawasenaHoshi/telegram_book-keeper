from __future__ import annotations

import os
import time
from typing import Any

import httpx

TM_BASE_URL = os.environ["TM_BASE_URL"]
BOT_TOKEN = os.environ["BOT_TOKEN"]


def push_update(chat_id: int, update: dict[str, Any]) -> int:
  response = httpx.post(
    f"{TM_BASE_URL}/admin/{BOT_TOKEN}/updates",
    json={"chat_id": chat_id, "update": update},
    timeout=10,
  )
  response.raise_for_status()
  return response.json()["update_id"]


def edited_message(
  chat_id: int, message_id: int, text: str
) -> dict[str, Any]:
  now = int(time.time())
  return {
    "edited_message": {
      "message_id": message_id,
      "date": now,
      "edit_date": now,
      "chat": {"id": chat_id, "type": "private"},
      "from": {"id": chat_id, "is_bot": False, "first_name": "Test"},
      "text": text,
    }
  }


def forwarded_message(
  admin_id: int, forward_from_id: int, *, first_name: str = "Forwarded"
) -> dict[str, Any]:
  return {
    "message": {
      "message_id": 50,
      "date": int(time.time()),
      "chat": {"id": admin_id, "type": "private"},
      "from": {"id": admin_id, "is_bot": False, "first_name": "Admin"},
      "forward_from": {
        "id": forward_from_id,
        "is_bot": False,
        "first_name": first_name,
      },
      "text": "hello",
    }
  }
