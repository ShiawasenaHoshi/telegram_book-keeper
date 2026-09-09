from __future__ import annotations

import itertools
import os
import time
from collections.abc import Iterator

import httpx
import psycopg
import pytest
import pytest_asyncio
from telemulator import RemoteUserClient

TM_BASE_URL = os.environ["TM_BASE_URL"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
PG_DSN = os.environ["PG_DSN"]

_user_ids = itertools.count(900_101)

# category, currency and currency_rate are seeded once by InitDB at startup and
# must survive: the bot builds its buttons and regexes from category when Cmd is
# constructed, so an empty table leaves the keyboard pointing at nothing.
APPLICATION_TABLES = ('"transaction"', "receipt", "month_start_balance", '"user"')


def _truncate() -> None:
  with psycopg.connect(PG_DSN, autocommit=True) as conn:
    conn.execute(f"TRUNCATE {', '.join(APPLICATION_TABLES)} RESTART IDENTITY CASCADE")


@pytest.fixture(scope="session", autouse=True)
def bot_is_polling() -> None:
  deadline = time.time() + 120
  while time.time() < deadline:
    journal = httpx.get(f"{TM_BASE_URL}/admin/journal", timeout=5).json()
    calls = journal["calls"] if isinstance(journal, dict) else journal
    if any(call.get("method") == "getUpdates" for call in calls):
      return
    time.sleep(0.5)
  raise AssertionError("the bot never called getUpdates against the emulator")


@pytest.fixture
def db() -> Iterator[psycopg.Connection]:
  with psycopg.connect(PG_DSN, autocommit=True) as conn:
    yield conn


@pytest_asyncio.fixture
async def user(bot_is_polling, db):
  _truncate()
  user_id = next(_user_ids)
  db.execute(
    'INSERT INTO "user" (id, name, access_level) VALUES (%s, %s, %s)',
    (user_id, "e2e", "USER"),
  )
  client = await RemoteUserClient(TM_BASE_URL, user_id, BOT_TOKEN).open()
  try:
    yield client
  finally:
    await client.aclose()
