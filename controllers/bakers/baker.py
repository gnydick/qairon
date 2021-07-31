from abc import ABC, abstractmethod

from controllers import RestController


class AbstractBakerController(ABC):

    def __init__(self, release_id):
        self.rest = RestController()
        self.release_id = release_id
        self.release = self.rest.get_instance('release', release_id)
        self.build = self.rest.get_instance('build', self.release['build_id'])
        self.deployment = self.rest.get_instance('deployment', self.release['deployment_id'])


        self.deployment_target = self.rest.get_instance('deployment_target',
                                                        self.deployment['deployment_target_id'])

    @abstractmethod
    def bake(self):
        raise NotImplementedError
