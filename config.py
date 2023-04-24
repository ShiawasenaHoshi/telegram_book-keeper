import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv



basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    TG_TOKEN = os.environ.get('TG_TOKEN')
    TG_ADMIN_ID = os.environ.get('TG_ADMIN_ID')

    TESTING = False

    if os.environ.get('DB_INTERACT') == '1':
        DB_INTERACT = True
    else:
        DB_INTERACT = False

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI') or 'postgresql://postgres:postgres@postgres:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BOT_INTERVAL = int(os.environ.get('BOT_INTERVAL')) if os.environ.get('BOT_INTERVAL') else 3
    BOT_TIMEOUT = int(os.environ.get('BOT_TIMEOUT')) if os.environ.get('BOT_INTERVAL') else 30

    if os.environ.get('WEBHOOK_ENABLE') == '1':
        WEBHOOK_ENABLE = True
    else:
        WEBHOOK_ENABLE = False
    WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
    WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT') or 8443  # 443, 80, 88 or 8443 (port need to be 'open')
    WEBHOOK_LISTEN = os.environ.get('WEBHOOK_LISTEN') or '0.0.0.0'  # In some VPS you may need to put here the IP addr

    WEBHOOK_SSL_CERT = os.environ.get(
        'WEBHOOK_SSL_CERT') or basedir + '/webhook_cert.pem'  # Path to the ssl certificate
    WEBHOOK_SSL_PRIV = os.environ.get(
        'WEBHOOK_SSL_PRIV') or basedir + '/webhook_pkey.pem'  # Path to the ssl private key

    WEBHOOK_URL_BASE = os.environ.get('WEBHOOK_URL_BASE') or "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = os.environ.get('WEBHOOK_URL_PATH') or "/%s/" % (TG_TOKEN)

    MAIN_CURRENCY = os.environ.get('MAIN_CURRENCY') or 'eur'

    TEMP_FOLDER = tempfile.gettempdir()

    RECEIPTS_FOLDER = Path("receipts")
