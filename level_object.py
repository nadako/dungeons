class LevelObject(object):

    def __init__(self, *components):
        self.level = None

        for component in components:
            self.add_component(component)

    def add_component(self, component):
        assert isinstance(component, Component)
        if self.has_component(component):
            raise RuntimeError('Trying to add duplicate component with name %s: %r' % (component.component_name, component))
        setattr(self, component.component_name, component)
        component.owner = self

    def remove_component(self, name):
        component = getattr(self, name, None)
        if component:
            assert isinstance(component, Component)
            delattr(self, name)
            component.owner = None

    def has_component(self, component):
        return hasattr(self, component.component_name)

    @property
    def name(self):
        if self.has_component(Description):
            return self.description.name
        return 'Something'


class Component(object):

    component_name = None
    owner = None


class Description(Component):

    component_name = 'description'

    def __init__(self, name):
        self.name = name
