import pyglet


class MessageLog(object):

    def __init__(self, num_latest=5):
        self.num_latest = num_latest
        self.messages = []
        self.new_message_indexes = []

    def get_latest(self):
        result = []
        total = len(self.messages)
        for i in xrange(max(0, total - self.num_latest), total):
            result.append((self.messages[i], i in self.new_message_indexes))
        return result

    def add_message(self, text):
        idx = len(self.messages)
        self.messages.append(text)
        self.new_message_indexes.append(idx)
        self.on_update()

    def mark_as_seen(self):
        self.new_message_indexes[:] = []
        self.on_update()

    @staticmethod
    def on_update():
        raise NotImplementedError()


class LastMessagesView(object):

    def __init__(self, message_log, width, y):
        self.message_log = message_log
        self.message_log.on_update = self.on_message_log_update
        self.layout = pyglet.text.layout.TextLayout(self.prepare_document(), width=width, multiline=True)
        self.layout.anchor_y = 'top'
        self.layout.y = y

    def on_message_log_update(self):
        self.layout.document = self.prepare_document()

    def prepare_document(self):
        parts = ['{font_name "eight2empire"}']
        for text, new in self.message_log.get_latest():
            if new:
                parts.append('{color (255, 255, 0, 255)}>>')
            parts.append(text)
            parts.append('{}\n')
        return pyglet.text.decode_attributed(''.join(parts))

    def draw(self):
        self.layout.draw()
