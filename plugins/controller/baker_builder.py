from controllers import RestController
from .bakers import HelmBakerController


class BakerBuilder:

    def build(self, deployment_id, build_id, release_job_number):
        self.rest = RestController()
        self.deployment_id = deployment_id
        self.build_id = build_id
        self.release_job_number = release_job_number
        self.build = self.rest.get_instance('build', build_id)
        self.deployment = self.rest.get_instance('deployment', deployment_id)
        self.deployment_target = self.rest.get_instance('deployment_target',
                                                        self.deployment['deployment_target_id'])
        if self.deployment_target['deployment_target_type_id'] in ['eks', 'k8s', 'minikube']:
            return HelmBakerController(self)
