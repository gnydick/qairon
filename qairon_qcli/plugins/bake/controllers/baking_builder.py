from qairon_qcli.controllers import QCLIController
from qairon_qcli.controllers.output_controller import IterableOutputController

from .baking import FileBakingController


class BakingBuilder:

    def __init__(self, deployment_id, build_id, release_job_number):
        results = []
        self.ioc = IterableOutputController(results)
        self.cli = QCLIController(self.ioc)
        self.deployment_id = deployment_id
        self.build_id = build_id
        self.release_job_number = release_job_number

        self.cli.get('build', build_id)
        self.__build__ = next(self.ioc.read_as_json())

        self.cli.get('deployment', deployment_id)
        self.__deployment__ = next(self.ioc.read_as_json())

        self.cli.get_field('deployment', deployment_id, 'configs')
        self.__configs__ = [x for x in self.ioc.read_as_json()]
        self.cli.get_field('service', self.__deployment__['service_id'], 'configs')
        self.__svc_configs__ = [x for x in self.ioc.read_as_json()]

        self.cli.get('deployment_target', self.__deployment__['deployment_target_id'])
        self.__deployment_target__ = next(self.ioc.read_as_json())

    def build(self):
        return FileBakingController(self)
