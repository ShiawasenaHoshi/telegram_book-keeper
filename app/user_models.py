import enum

from app import db


class ACCESS_LEVEL(enum.Enum):
    ADMIN = 1
    USER = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240), nullable=False)
    access_level = db.Column(db.Enum(ACCESS_LEVEL), nullable=False)

    @staticmethod
    def add(id, name, access_level):
        if not db.session.execute(db.select(User).filter_by(id=id)).scalar_one_or_none():
            u = User()
            u.id = id
            u.name = name
            u.access_level = access_level
            db.session.add(u)
            db.session.commit()
            return u

    @staticmethod
    def get(msg):
        return db.session.get(User, msg.from_user.id)
