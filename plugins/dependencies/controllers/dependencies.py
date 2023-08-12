from controllers import RestController


class DependencyController:

    def __init__(self):
        pass

    rest = RestController()

    def add_related(self, dependency_id, related_id, resource=None, **kwargs):
        self.rest.add_to_many_to_many('dependency', dependency_id, 'related', 'relateds', related_id)

    def get_related(self, related_id, **kwargs):
        (type, resource_id) = related_id.split(":")
        return self.rest.get_instance(type.lower(), resource_id, **kwargs)
