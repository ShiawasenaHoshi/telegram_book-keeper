#!/bin/bash
set -euo pipefail
pg_restore -U postgres -d postgres --no-owner --no-acl /seed.dump
