class LevelObject(object):

    def __init__(self, *components):
        self.level = None

        for component in components:
            self.add_component(component)

    def add_component(self, component):
        assert isinstance(component, Component)
        if self.has_component(component):
            raise RuntimeError('Trying to add duplicate component with name %s: %r' % (component.COMPONENT_NAME, component))
        setattr(self, component.COMPONENT_NAME, component)
        component.owner = self

    def remove_component(self, component):
        if not self.has_component(component):
            raise RuntimeError('Trying to remove component that is not added: %s' % component.COMPONENT_NAME)
        else:
            component = getattr(self, component.COMPONENT_NAME)
            component.owner = None
            delattr(self, component.COMPONENT_NAME)

    def has_component(self, component):
        return hasattr(self, component.COMPONENT_NAME)


class Component(object):

    COMPONENT_NAME = None
    owner = None


class Description(Component):

    COMPONENT_NAME = 'description'

    def __init__(self, name):
        self.name = name
