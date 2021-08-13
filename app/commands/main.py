from app import db
from app.commands.abstract import Cmd, TRY_AGAIN, input_method
from app.user_models import ACCESS_LEVEL, User


class GenericCmd(Cmd):
    def __init__(self, bot, app, logger, admin):
        super().__init__(bot, app, logger, admin)

    def dict_of_methods(self):
        return {
            self.help: ("help", None, ACCESS_LEVEL.USER),
            self.send_welcome: ("start", None, ACCESS_LEVEL.USER),
            self.change_access_level: (Cmd.change_access_level_cmd, "🧞‍♂️ Уровень доступа", ACCESS_LEVEL.ADMIN)
        }

    def send_welcome(self, msg):
        self.help(msg)

    def help(self, msg):
        help_msg = "Здравствуйте! Я есть казна-бот."
        self.bot.send_message(msg.chat.id, help_msg, reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))

    def change_access_level(self, msg):
        msg = self.bot.send_message(msg.chat.id, 'Какой новый уровень доступа? 1 - админ, 2 - менеджер, 3 - работник',
                                    reply_markup=self.markup_back_to_menu)

        self.bot.register_next_step_handler(msg, self.waiting_new_access_level)

    @input_method()
    def waiting_new_access_level(self, msg):
        with Cmd.ctx():
            user = User.get(msg)
            try:
                user.access_level = ACCESS_LEVEL(int(msg.text))
                db.session.commit()
                msg = self.bot.send_message(msg.chat.id, 'Уровень доступа изменен',
                                            reply_markup=Cmd.get_markup_for_access_level(self.access_level_by_msg(msg)))
            except BaseException as be:
                self.bot.send_message(msg.chat.id, 'Что-то пошло не так. Попробуй еще раз')
                return TRY_AGAIN
