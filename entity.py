from collections import defaultdict


class Entity(object):

    def __init__(self, *components):
        self.level = None
        self._components = {}
        self._event_handlers = defaultdict(set)
        for component in components:
            self.add(component)

    def add(self, component):
        assert isinstance(component, Component)
        if self.has(component):
            raise RuntimeError('Trying to add duplicate component with name %s: %r' % (component.COMPONENT_NAME, component))
        self._components[component.COMPONENT_NAME] = component
        component.owner = self

    def remove(self, component):
        if not self.has(component):
            raise RuntimeError('Trying to remove component that is not added: %s' % component.COMPONENT_NAME)
        else:
            component = self._components.pop(component.COMPONENT_NAME)
            component.owner = None

    def get(self, component):
        return self._components.get(component.COMPONENT_NAME)

    def has(self, component):
        return component.COMPONENT_NAME in self._components

    def listen(self, event_name, handler):
        self._event_handlers[event_name].add(handler)

    def unlisten(self, event_name, handler):
        if event_name in self._event_handlers:
            self._event_handlers[event_name].remove(handler)

    def event(self, event_name, *data):
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                handler(self, *data)
        for componment in self._components.values():
            method = getattr(componment, 'on_' + event_name, None)
            if method:
                method(*data)


class Component(object):

    COMPONENT_NAME = None # override for class

    owner = None # set when added to entity
