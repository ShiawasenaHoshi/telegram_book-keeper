"""Start the bot against the emulator instead of Telegram.

Mounted into the container, never copied into the image: the image must stay
byte-identical to the one that would go to production.
"""

from __future__ import annotations

import os
import sys

# The bot package lives in the image root, and this file runs from /home/bot/e2e.
sys.path.insert(0, "/home/bot")

import telebot.apihelper as apihelper

apihelper.API_URL = os.environ["TM_API_URL"]
apihelper.FILE_URL = os.environ["TM_FILE_URL"]

import bot  # noqa: E402,F401  create_app() starts the polling thread on import
