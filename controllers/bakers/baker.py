from abc import ABC, abstractmethod

from controllers import RestController


class AbstractBakerController(ABC):

    def __init__(self, metadata):
        self.rest = metadata.rest
        self.release_id = metadata.release_id
        self.release = metadata.release
        self.build = metadata.build
        self.deployment = metadata.deployment
        self.deployment_target = metadata.deployment_target

    @abstractmethod
    def bake(self):
        raise NotImplementedError
