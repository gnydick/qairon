import json

from qairon.models import Network, Subnet


class SubnetController:

    def __init__(self, network_id):
        self.network_id = network_id

    def allocate_subnet(self, additional_mask_bits, name):
        from .rest_controller import RestController
        rest = RestController()
        import ipaddress as ip
        net = rest.get_instance('network', resource_id=self.network_id)
        network = Network(**net)
        if type(net) is None:
            pass
        else:
            used_sbns = list(map(lambda x: ip.IPv4Network(x['cidr']), network.subnets))
            n = ip.IPv4Network(network.cidr)
            psns = list(n.subnets(int(additional_mask_bits)))

            for sbn in used_sbns:
                psns = list(filter(lambda x: not sbn.overlaps(x), psns))

            subnet_cidr = str(psns[0].compressed)

            return subnet_cidr
