import collections
import enum

from app import db


class ACCESS_LEVEL(enum.Enum):
    ADMIN = 1
    MANAGER = 2
    USER = 3


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_level = db.Column(db.Enum(ACCESS_LEVEL), nullable=False)
    bot_state = db.relationship('UserBotState', backref='user', uselist=False)

    @staticmethod
    def add(id, access_level):
        if not User.query.filter_by(id=id).first():
            u = User()
            u.id = id
            u.access_level = access_level
            db.session.add(u)
            db.session.commit()
            return u

    def is_in_state(self, state):
        if self.bot_state == None:
            idle = UserBotState.update(self.id)
            return idle == state
        return self.bot_state.is_equal(state)

    def update_state(self, state):
        if not self.is_in_state(state):
            return UserBotState.update(self.id, state)

    def idle(self):
        self.update_state(IDLE)

    @staticmethod
    def get(msg):
        return User.query.filter_by(id=msg.from_user.id).first()


IDLE = "idle"


class UserBotState(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    state = db.Column(db.String(48))

    def is_equal(self, state):
        str_state = state
        if isinstance(state, collections.Callable):
            str_state = state.__name__
        return self.state == str_state

    @staticmethod
    def update(user_id, state=IDLE):
        str_state = state
        if isinstance(state, collections.Callable):
            str_state = state.__name__
        u_state = UserBotState.query.filter_by(user_id=user_id).first()
        if u_state:
            if u_state.state == str_state:
                return u_state
            else:
                update = True
        else:
            update = False
            u_state = UserBotState()
            u_state.user_id = user_id
        u_state.state = str_state
        if not update:
            db.session.add(u_state)
        db.session.commit()
        return u_state
