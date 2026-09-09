from app import db
from app.commands.abstract import Cmd, input_method
from app.user_models import ACCESS_LEVEL, User


class UserCmd(Cmd):
    def dict_of_methods(self):
        return {
            self.add: ("user_add", "🙋 Добавить пользователя", ACCESS_LEVEL.ADMIN),
            self.ls: ("user_ls", "🧑‍💻 Список пользователей", ACCESS_LEVEL.ADMIN),
        }

    def add(self, msg):

        msg = self.bot.send_message(msg.chat.id,
                                    'Для добавления пользователя пришлите его ID, контакт или одно из его сообщений',
                                    reply_markup=self.markup_back_to_menu)
        self.bot.register_next_step_handler(msg, self.waiting_user_add)

    @staticmethod
    def _forwarded_sender(msg):
        if msg.forward_from is not None:
            return msg.forward_from
        origin = getattr(msg, 'forward_origin', None)
        if origin is not None and getattr(origin, 'type', None) == 'user':
            return origin.sender_user
        return None

    @input_method()
    def waiting_user_add(self, msg):
        forwarded = self._forwarded_sender(msg)
        if forwarded is not None:
            self.add_forwarded(msg, forwarded)
        elif msg.content_type == 'contact':
            self.add_contact(msg)
        else:
            pass  # todo validate and add user by ID
        # todo change name of added user

    def add_forwarded(self, msg, forwarded):
        with Cmd.ctx():
            if forwarded.first_name and forwarded.last_name:
                name = "{0} {1}".format(forwarded.first_name, forwarded.last_name)
            elif forwarded.first_name:
                name = forwarded.first_name
                if forwarded.username:
                    name = name + " " + forwarded.username
            elif forwarded.username:
                name = forwarded.username
            else:
                name = str(forwarded.id)
            user = User.add(forwarded.id, name, ACCESS_LEVEL.USER)
            if user:
                self.bot.send_message(msg.chat.id, f'Пользователь {name} добавлен',
                                      reply_markup=Cmd.get_markup_for_access_level(
                                          self.access_level_by_msg(msg.chat.id)))

    def add_contact(self, msg):
        if msg.contact.user_id is None:
            self.bot.reply_to(msg, 'Пользователь не добавлен: отсутствует ID')
        else:
            with self.app.app_context():
                if msg.contact.first_name and msg.contact.last_name:
                    name = f"{msg.contact.first_name} {msg.contact.last_name}"
                elif msg.contact.first_name:
                    name = msg.contact.first_name
                elif msg.contact.username:
                    name = msg.contact.username
                else:
                    name = str(msg.contact.user_id)
                user = User.add(msg.contact.user_id, name, ACCESS_LEVEL.USER)
                if user:
                    self.bot.send_message(msg.chat.id, f'Пользователь {name} добавлен',
                                          reply_markup=Cmd.get_markup_for_access_level(
                                              self.access_level_by_msg(msg.chat.id)))

    def ls(self, msg):
        with Cmd.ctx():
            users = db.session.execute(db.select(User)).scalars().all()
            ls_msg = "\n".join([f'{str(user.id)}: {user.name}' for user in users])
            self.bot.send_message(msg.chat.id, ls_msg)
