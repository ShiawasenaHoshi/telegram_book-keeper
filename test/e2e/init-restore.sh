#!/bin/bash
set -euo pipefail
pg_restore -U postgres -d postgres --no-owner --no-acl /seed.dump
# Keep category, currency and currency_rate from the dump; drop rows the bot would
# walk at startup (monthly broadcast to every user) and per-scenario application data.
psql -v ON_ERROR_STOP=1 -U postgres -d postgres <<'SQL'
TRUNCATE "transaction", receipt, month_start_balance, "user" RESTART IDENTITY CASCADE;
DELETE FROM currency_rate WHERE date = CURRENT_DATE;
SQL
