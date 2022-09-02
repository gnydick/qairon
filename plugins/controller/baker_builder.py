from controllers import RestController
from .bakers import HelmBakerController


class BakerBuilder:

    def __init__(self, deployment_id, build_id, release_job_number):
        self.rest = RestController()
        self.deployment_id = deployment_id
        self.build_id = build_id
        self.release_job_number = release_job_number
        self.__build__ = self.rest.get_instance('build', build_id)
        self.__deployment__ = self.rest.get_instance('deployment', deployment_id)
        self.__configs__ = self.rest.get_field('deployment', deployment_id, 'configs')
        self.__deployment_target_bin__ = self.rest.get_instance('deployment_target_bin',
                                                            self.__deployment__['deployment_target_bin_id'])
        self.__deployment_target__ = self.rest.get_instance('deployment_target',
                                                        self.__deployment_target_bin__['deployment_target_id'])

    def build(self):
        if self.__deployment_target__['deployment_target_type_id'] in ['eks', 'k8s', 'minikube']:
            return HelmBakerController(self)
        elif self.__deployment_target__['deployment_target_type_id'] in ['glbuild']:
            return GlBuildBaker(self)
