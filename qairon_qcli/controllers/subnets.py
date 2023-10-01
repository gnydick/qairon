import json

from qairon_qcli.controllers.output_controller import IterableOutputController


class SubnetController:

    def __init__(self, network_id):
        results = []
        ioc = IterableOutputController(results)
        self.network_id = network_id

    def allocate_subnet(self, additional_mask_bits, name):
        from .rest_controller import RestController
        rest = RestController()
        import ipaddress as ip
        network = rest.get_instance('network', resource_id=self.network_id)['attributes']
        response = rest._get_all_('network', self.network_id, path='subnets')
        collect = [x for x in response]
        subnets = collect[0]
        if type(subnets) is None:
            pass
        else:
            used_sbns = list(map(lambda x: ip.IPv4Network(x['attributes']['cidr']), subnets))
            n = ip.IPv4Network(network['cidr'])
            psns = list(n.subnets(int(additional_mask_bits)))

            for sbn in used_sbns:
                psns = list(filter(lambda x: not sbn.overlaps(x), psns))

            subnet_cidr = str(psns[0].compressed)

            return subnet_cidr
