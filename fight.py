from entity import Component


class Fighter(Component):

    COMPONENT_NAME = 'fighter'

    def __init__(self, attack, defense):
        self.attack = attack
        self.defense = defense

    def do_attack(self, target):
        target_fighter = target.get(Fighter)
        dmg = max(0, self.attack - target_fighter.defense)
        self.owner.event('do_damage', dmg, target)
        target.event('take_damage', dmg, self.owner)
