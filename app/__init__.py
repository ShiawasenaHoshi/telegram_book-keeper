import logging
import sys
import traceback

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    try:
        app = Flask(__name__)
        app.config.from_object(config_class)

        db.init_app(app)
        migrate.init_app(app, db)
        with app.app_context():
            if not config_class.DB_INTERACT and not config_class.TESTING :
                from flask_migrate import upgrade as _upgrade
                _upgrade()
                from app.init_db_objects import InitDB
                InitDB(app).init_all()

        app.logger.setLevel(logging.INFO)
        if (len(sys.argv) > 1 and sys.argv[1] == 'db'):
            return app
        if not config_class.DB_INTERACT and not config_class.TESTING and config_class.TG_TOKEN and config_class.TG_ADMIN_ID:

            from app.user_models import ACCESS_LEVEL, User
            with app.app_context():
                User.add(config_class.TG_ADMIN_ID, ACCESS_LEVEL.ADMIN, "superadmin")
            from app.bot import Bot
            Bot(Config.TG_TOKEN, Config.TG_ADMIN_ID, app).start()
        elif config_class.TESTING:
            print("Test mode")
        else:
            print("App is not configured. Check config.py")
        return app
    except BaseException as e:
        traceback.print_exc()

from app import models, user_models