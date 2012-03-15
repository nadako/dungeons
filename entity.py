class Entity(object):

    def __init__(self, *components):
        self.level = None
        self._components = {}
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


class Component(object):

    COMPONENT_NAME = None # override for class

    owner = None # set when added to entity
