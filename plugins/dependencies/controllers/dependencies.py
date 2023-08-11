from controllers import RestController


class DependencyController:

    def __init__(self):
        pass

    rest = RestController()

    def add_related(self, dependency_id, related_id, resource=None, command=None, q=False):
        self.rest.add_to_many_to_many('dependency', dependency_id, 'related', 'relateds', related_id)
