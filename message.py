import pyglet

from description import get_name
from entity import Component
from item import Item


class MessageLog(pyglet.event.EventDispatcher):

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
        self.dispatch_event('on_messages_update')

    def mark_as_seen(self):
        if self.new_message_indexes:
            self.new_message_indexes[:] = []
            self.dispatch_event('on_messages_update')

MessageLog.register_event_type('on_messages_update')


class LastMessagesView(object):

    def __init__(self, message_log, width, y, batch, group=None):
        self.message_log = message_log
        self.message_log.set_handler('on_messages_update', self.on_messages_update)
        self.layout = pyglet.text.layout.TextLayout(self.prepare_document(), width=width, multiline=True, batch=batch, group=group)
        self.layout.anchor_y = 'top'
        self.layout.y = y

    def on_messages_update(self):
        self.layout.document = self.prepare_document()

    def prepare_document(self):
        parts = ['{font_name "eight2empire"}']
        for text, new in self.message_log.get_latest():
            parts.append('{color (255, 255, 0, %d)}>>' % (new and 255 or 0))
            parts.append(text)
            parts.append('{}\n')
        return pyglet.text.decode_attributed(''.join(parts))

    def delete(self):
        self.message_log.remove_handler('on_messages_update', self.on_messages_update)
        self.layout.delete()


class MessageLogger(Component):

    COMPONENT_NAME = 'message_logger'

    def __init__(self, message_log):
        self._message_log = message_log

    def message(self, text, color=(255, 255, 255, 255)):
        if color:
            text = '{color (%d, %d, %d, %d)}%s' % (color + (text,))
        self._message_log.add_message(text)

    def on_take_damage(self, damage, source):
        self.message('%s hits you for %d hp' % (get_name(source), damage))

    def on_do_damage(self, damage, target):
        self.message('You hit %s for %d hp' % (get_name(target), damage))

    def on_die(self):
        self.message('You die')

    def on_kill(self, target):
        self.message('%s dies' % get_name(target))

    def on_bump(self, entity):
        self.message('You bump into %s' % get_name(entity))

    def on_drop(self, item):
        if item:
            self.message('Dropped up %s' % get_name(item))
        else:
            self.message('Nothing to drop')

    def on_pickup(self, item):
        if item:
            self.message('Picked up %d %s' % (item.get(Item).quantity, get_name(item)))
        else:
            self.message('Nothing to pickup here')

    def on_door_open(self, door):
        self.message('You open the door')
