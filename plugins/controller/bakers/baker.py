from abc import ABC, abstractmethod

from controllers import RestController


class AbstractBakerController(ABC):

    def __init__(self, metadata):
        self.rest = metadata.rest
        self.deployment_id = metadata.deployment_id
        self.build_id = metadata.build_id
        self.release_job_number = metadata.release_job_number
        self.build = metadata.build
        self.deployment = metadata.deployment
        self.deployment_target = metadata.deployment_target

    @abstractmethod
    def bake(self):
        raise NotImplementedError
