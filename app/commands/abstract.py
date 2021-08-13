import re
from abc import abstractmethod
from collections import defaultdict

from telebot import types

from app.generic import chunkify_by_size
from app.user_models import ACCESS_LEVEL, User





class Cmd():
    func_btn_map = {

    }
    _re_set = set()
    keyboards = defaultdict(list)
    admin = None
    ctx = None
    change_access_level_cmd = "change_access_level"

    @abstractmethod
    def dict_of_methods(self):
        pass

    def __init__(self, bot, app, logger, admin):
        if Cmd.admin is None:
            Cmd.admin = admin
        self.bot = bot
        self.app = app
        if Cmd.ctx is None:
            Cmd.ctx = app.app_context
        self.l = logger
        self.admin = admin
        self.markup_back_to_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        self.markup_back_to_menu.row(self.ru_back_to_menu)
        Cmd.func_btn_map.update(self.dict_of_methods())
        self.init_fields()
        self.init_keyboards()
        bot.message_handlers.clear()
        self.add_handlers(bot)

        bot.add_message_handler(bot_handler_dict(self.back_to_menu_btn_pushed, Cmd.re_back_to_menu,
                                                  lambda msg: Cmd.is_allowed(msg, ACCESS_LEVEL.USER)))



    #---------ALL HANDLERS INITIALIZATION------

    @staticmethod
    def get_keyboard(access_level):
        return Cmd.keyboards[access_level]

    def init_fields(self):
        for method, params in Cmd.func_btn_map.items():
            en, ru, access_level = params
            Cmd._re_set.add(self._regex(method))
            setattr(self, f"re_{method.__name__}", self._regex(method))
            setattr(self, f"access_level_{method.__name__}", access_level)

    @staticmethod
    def init_keyboards():
        keyboards = Cmd.keyboards
        keyboards.clear()
        for method, params in Cmd.func_btn_map.items():
            en, ru, access_level = params
            if not ru:
                continue
            if access_level == ACCESS_LEVEL.USER:
                keyboards[ACCESS_LEVEL.USER].append(ru)
                keyboards[ACCESS_LEVEL.MANAGER].append(ru)
                keyboards[ACCESS_LEVEL.ADMIN].append(ru)
            elif access_level == ACCESS_LEVEL.MANAGER:
                keyboards[ACCESS_LEVEL.MANAGER].append(ru)
                keyboards[ACCESS_LEVEL.ADMIN].append(ru)
            else:
                keyboards[ACCESS_LEVEL.ADMIN].append(ru)

    def add_handlers(self, bot):
        for method, params in Cmd.func_btn_map.items():
            en, ru, access_level = params
            bot.add_message_handler(bot_handler_dict(method, self._regex(method), Cmd._access_level_lambda(access_level)))

    def _regex(self, func):
        if not self.func_btn_map:
            raise Exception("Function-Button map is empty")
        en, ru, _ = self.func_btn_map[func]
        if ru:
            return _re(en, ru)
        else:
            return _re_no_key(en)

    @staticmethod
    def _access_level_lambda(access_level):
        return lambda msg: Cmd.is_allowed(msg, access_level)

    #------ACCESS LEVELS AND GENERATE MARKUP FOR EACH LEVEL----------

    @staticmethod
    def get_markup_for_access_level(access_level):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in chunkify_by_size(Cmd.get_keyboard(access_level), 3):
            markup.row(*row)
        return markup

    @staticmethod
    def is_allowed(msg, min_access_level):
        return msg.chat.title is None and Cmd.access_level_corresponds(msg, min_access_level)

    def access_level_by_uid(self, user_id):
        with Cmd.ctx():
            user = User.query.filter_by(id=user_id).first()
            return user.access_level

    def access_level_by_msg(self, msg):
        if isinstance(msg, int):
            return self.access_level_by_uid(msg)
        else:
            return self.access_level_by_uid(msg.from_user.id)

    @staticmethod
    def access_level_corresponds(msg, minimal_access_level):
        if msg.from_user.id == int(Cmd.admin) and msg.text == f"/{Cmd.change_access_level_cmd}":
            return True
        with Cmd.ctx():
            user = User.query.filter_by(id=msg.from_user.id).first()
            if user is None:
                return False
            else:
                return user.access_level.value <= minimal_access_level.value

    #------------BACK BUTTON AND UNEXPECTED COMMANDS HANDLER-----------

    ru_back_to_menu = "❌ В меню"
    re_back_to_menu = f"^(/reset|{ru_back_to_menu})$"
    access_level_back_to_menu = ACCESS_LEVEL.USER

    def back_to_menu_btn_pushed(self, msg):
        if msg.content_type == "text" and re.match(self.re_back_to_menu, msg.text):
            self.bot.clear_step_handler_by_chat_id(chat_id=msg.chat.id)
            self.bot.send_message(msg.chat.id, "Операция отменена",
                                  reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
            return True

    def unexpected_cmd_typed(self, msg):
        if msg.content_type == "text":
            for _re in Cmd._re_set:
                if re.match(_re, msg.text):
                    return True


def _re(en_cmd, ru_cmd):
    return f"^(/{en_cmd}|{ru_cmd})$"


def _re_no_key(en_cmd):
    return f"^(/{en_cmd})$"


def bot_handler_dict(function, regexp, func, commands=None, content_types=None):
    return {'function': function,
            'filters': {'commands': commands,
                        'regexp': regexp,
                        'func': func,
                        'content_types': content_types}}

TRY_AGAIN = 0
def input_method(smth=None):
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            cmd = args[0]
            bot = cmd.bot
            log = cmd.l
            msg = args[1]

            if cmd.back_to_menu_btn_pushed(msg):
                return

            if cmd.unexpected_cmd_typed(msg):
                bot.register_next_step_handler(msg, getattr(cmd, func.__name__))
                bot.send_message(msg.chat.id, "Вы ввели команду, а не данные. Повторите ввод")

                return
            try:
                return_value = func(*args, **kwargs)
            except Exception as e:
                log.error(e)
                bot.send_message(msg.chat.id, "Что-то пошло не так. Повторите ввод")
                return_value = TRY_AGAIN

            if return_value == TRY_AGAIN:
                bot.register_next_step_handler(msg, getattr(cmd, func.__name__))
                return
            return return_value

        return wrapper

    return actual_decorator
