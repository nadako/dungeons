import pyglet

from description import get_name
from fight import Fighter
from health import Health
from inventory import Inventory
from item import Item


class HUD(object):

    def __init__(self, batch, group=None):
        self._label = pyglet.text.Label(font_name='eight2empire', anchor_y='bottom', batch=batch, group=group)
        self._player = None

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, value):
        if value is not self._player:
            if self._player is not None:
                self._player.unlisten('health_update', self._update_hud)
                self._player.unlisten('pickup', self._update_hud)
                self._player.unlisten('drop', self._update_hud)

            self._player = value
            if value is not None:
                value.listen('health_update', self._update_hud)
                value.listen('pickup', self._update_hud)
                value.listen('drop', self._update_hud)
                self._update_hud()

    def _update_hud(self, *args):
        item_names = []
        for item in self._player.get(Inventory).items:
            name = get_name(item)
            item_component = item.get(Item)
            if item_component.quantity > 1:
                name += ' (%d)' % item_component.quantity
            item_names.append(name)
        inventory = ', '.join(item_names) or 'nothing'
        fighter = self._player.get(Fighter)
        health = self._player.get(Health)
        text = 'HP: %d/%d, ATK: %d, DEF: %d (INV: %s)' % (health.health, health.max_health, fighter.attack, fighter.defense, inventory)
        self._label.text = text

    def delete(self):
        self.player = None
        self._label.delete()
