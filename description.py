from entity import Component


class Description(Component):

    COMPONENT_NAME = 'description'

    def __init__(self, name):
        self.name = name


def get_name(entity):
    desc = entity.get(Description)
    if desc:
        return desc.name
    else:
        return 'Something'
