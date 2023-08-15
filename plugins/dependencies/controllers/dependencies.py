from controllers import RestController
from controllers.output_controller import simplify_row

class CardinalityException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

class DependencyController:

    def __init__(self):
        pass

    rest = RestController()

    def add_related(self, dependency_id, related_id, resource=None, **kwargs):
        dependency_case = simplify_row(self.rest.get_field('dependency', dependency_id, 'dependency_case'))
        allowed_relationship = dependency_case['allowed_relationship']
        current_relateds = self.rest.get_field('dependency', dependency_id, 'relateds')
        if len(current_relateds) > 0 and allowed_relationship == 'OTO':
            raise CardinalityException("One-to-one relationship already has one related")
        else:
            return self.rest.add_to_many_to_many('dependency', dependency_id, 'related', 'relateds', related_id)

    def del_related(self, dependency_id, related_id, resource=None, **kwargs):
        return self.rest.del_from_many_to_many('dependency', dependency_id, 'related', 'relateds', related_id)

    def get_related(self, related_id, **kwargs):
        (type, resource_id) = related_id.split(":")
        return self.rest.get_instance(type.lower(), resource_id, **kwargs)
