#!/bin/sh
set -euo pipefail

apk add --no-cache \
  libpq \
  freetype \
  libjpeg-turbo \
  zlib \
  libpng \
  libxml2 \
  libxslt \
  g++ \
  musl-dev \
  postgresql-dev \
  freetype-dev \
  libjpeg-turbo-dev \
  zlib-dev \
  libpng-dev \
  libxml2-dev \
  libxslt-dev

apk upgrade --no-cache

pip install --no-cache-dir -U pip
pip install --no-cache-dir -r /tmp/requirements.txt
