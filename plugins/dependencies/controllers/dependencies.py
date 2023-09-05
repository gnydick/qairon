import json

from controllers import RestController
from controllers.output_controller import simplify_row


class CardinalityException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args)


class DependencyController:

    def __init__(self):
        self.rest = RestController()

    def get_related(self, dependency_id):
        results = []
        filters = [dict(name='dependency_id', op='eq', val=dependency_id)]
        rows =  self.rest.query('related', query=json.dumps(filters))
        for row in rows:
            newrow = simplify_row(row[0])
            obj = self.rest.get_instance(newrow['related_type'].lower(), newrow['object_id'])
            results.append(obj)
        return results


