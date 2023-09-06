from abc import ABC, abstractmethod


class AbstractBakingController(ABC):

    def __init__(self, metadata):
        self.rest = metadata.rest
        self.deployment_id = metadata.deployment_id
        self.build_id = metadata.build_id
        self.release_job_number = metadata.release_job_number
        self.build = metadata.__build__
        self.deployment = metadata.__deployment__
        self.deployment_target = metadata.__deployment_target__
        self.configs = metadata.__configs__

    @abstractmethod
    def bake(self):
        raise NotImplementedError
