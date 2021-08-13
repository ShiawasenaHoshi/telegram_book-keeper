class TestBot():
    def __init__(self, send_message_func=None, send_document_func=None):
        self.message_handlers = []
        self.send_message_func = send_message_func
        self.send_document_func = send_document_func

    def register_next_step_handler(self, message, callback, *args, **kwargs):
        # todo implement
        # chat_id = message.chat.id
        # self.register_next_step_handler_by_chat_id(chat_id, callback, *args, **kwargs)
        pass

    def add_message_handler(self, handler_dict):
        self.message_handlers.append(handler_dict)

    def add_edited_message_handler(self, handler_dict):
        pass

    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None):
        if self.send_message_func:
            self.send_message_func(chat_id, text)

    def send_document(self, chat_id, data, reply_to_message_id=None, caption=None, reply_markup=None,
                      parse_mode=None, disable_notification=None, timeout=None):
        if self.send_document_func:
            self.send_document_func(chat_id, data)


class TestMessage():
    def __init__(self):
        class Chat():
            def __init__(self):
                self.id = 1
        self.chat = Chat()
