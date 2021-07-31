from controllers import RestController
from controllers.bakers import HelmBakerController


class BakerController:

    def __init__(self, release_id):
        self.rest = RestController()
        self.release_id = release_id
        self.release = self.rest.get_instance('release', release_id)
        self.build = self.rest.get_instance('build', self.release['build_id'])
        self.deployment = self.rest.get_instance('deployment', self.release['deployment_id'])
        self.deployment_target = self.rest.get_instance('deployment_target',
                                                        self.deployment['deployment_target_id'])
        if self.deployment_target['deployment_target_type_id'] in ['eks', 'k8s', 'minikube']:
            self.baker = HelmBakerController(self)

    def bake(self):
        self.baker.bake()
