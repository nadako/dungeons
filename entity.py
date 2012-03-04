class Component(object):
    pass


class EntityManager(object):

    def __init__(self):
        self.entities = []
        self.components = {}
        self.next_id = 1

    def create_entity(self):
        id = self.next_id
        self.next_id += 1
        self.entities.append(id)
        return id

    def delete_entity(self, id):
        self.entities.remove(id)
        for store in self.components.itervalues():
            store.pop(id, None)

    def get_proxy(self, id):
        return EntityProxy(self, id)

    def get_component_class(self, component):
        component_class = None
        for cls in component.__class__.__mro__:
            if cls is Component:
                break
            component_class = cls
        else:
            raise RuntimeError('Component %r doesnt derive from Component' % component)
        return component_class

    def add_component(self, id, component):
        component_class = self.get_component_class(component)
        store = self.components.get(component_class)
        if store is None:
            store = self.components[component_class] = {}
        store[id] = component

    def remove_component(self, id, component_class):
        store = self.components.get(component_class)
        if store is not None:
            store.pop(id, None)

    def has_component(self, id, component_class):
        store = self.components.get(component_class)
        if store is not None:
            return id in store
        else:
            return False

    def get_component(self, id, component_class):
        store = self.components.get(component_class)
        if store is not None:
            return store.get(id)
        return None

    def iter_components(self, component_class):
        store = self.components.get(component_class)
        if store is None:
            return iter(())
        return store.iteritems()


class EntityProxy(object):

    __slots__ = ('manager', 'id')

    def __init__(self, manager, id):
        self.manager = manager
        self.id = id

    def delete(self):
        self.manager.delete(self.id)
        self.manager = None
        self.id = None

    def add(self, *components):
        for component in components:
            self.manager.add_component(self.id, component)

    def remove(self, *component_classes):
        for cls in component_classes:
            self.manager.remove_component(self.id, cls)

    def has(self, component_class):
        return self.manager.has_component(self.id, component_class)

    def get(self, component_class):
        return self.manager.get_component(self.id, component_class)

    def __iter__(self):
        for store in self.manager.components.values():
            if self.id in store:
                yield store[self.id]
