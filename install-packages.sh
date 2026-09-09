#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends libpq-dev gcc python3-dev
pip install -r /tmp/requirements.txt
apt-get clean
rm -rf /var/lib/apt/lists/*
