from controllers import RestController
from controllers.output_controller import simplify_row, simplify_rows

from .bakers import HelmBakerController


class BakerBuilder:

    def __init__(self, deployment_id, build_id, release_job_number):
        
        self.rest = RestController()
        self.deployment_id = deployment_id
        self.build_id = build_id
        self.release_job_number = release_job_number

        self.__build__ = simplify_row(self.rest.get_instance('build', build_id))
        self.__deployment__ = simplify_row(self.rest.get_instance('deployment', deployment_id))

        # simplify_rows is a yield, must wrap to cache results
        self.__configs__ = [x for x in simplify_rows(self.rest.get_field('deployment', deployment_id, 'configs'))]
        self.__svc_configs__ = [x for x in simplify_rows(self.rest.get_field('service', self.__deployment__['service_id'], 'configs'))]
        self.__deployment_target_bin__ = simplify_row(self.rest.get_instance('deployment_target_bin',
                                                                             self.__deployment__['deployment_target_bin_id']))
        self.__deployment_target__ = simplify_row(self.rest.get_instance('deployment_target',
                                                                         self.__deployment_target_bin__['deployment_target_id']))

    def build(self):
        if self.__deployment_target__['type_id'] in ['eks', 'k8s', 'minikube']:
            return HelmBakerController(self)
        elif self.__deployment_target__['type_id'] in ['glbuild']:
            return GlBuildBaker(self)
