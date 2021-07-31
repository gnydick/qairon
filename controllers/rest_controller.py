import json
import os
import re

import requests

from .schema import QaironSchema


class RestController:
    global schema
    schema = QaironSchema()
    global endpoint
    endpoint = os.getenv("QAIRON_ENDPOINT", "http://localhost:5001")

    def __init__(self):
        pass

    URL = '%s/api/rest/v1/' % endpoint
    HEADERS = {'Content-Type': 'application/json'}

    def add_to_many_to_many(self, owner_res, owner_res_id, col_res, col_res_id):
        owner = self.get_instance(owner_res, owner_res_id)
        collection = [{'id': x['id']} for x in owner[col_res]]
        collection.append({"id": col_res_id})
        attr = {col_res: collection}
        return self._put_rest_(owner_res, owner_res_id, json=attr)

    def del_from_many_to_many(self, owner_res, owner_res_id, col_res, col_res_id):
        owner = self.get_instance(owner_res, owner_res_id)
        collection = list(filter(lambda x: x['id'] != col_res_id, owner[col_res]))
        attr = {col_res: collection}
        return self._put_rest_(owner_res, owner_res_id, json=attr)

    def resource_get_search(self, prefix, resource, **kwargs):
        return self._get_search_(prefix, resource=resource, **kwargs)

    def resource_get_attr_search(self, prefix, parsed_args, resource, attribute, **kwargs):
        return self._get_attr_search_(prefix, parsed_args, resource=resource, attribute=attribute, **kwargs)

    def __collection_for_resource_completer__(self, prefix, parsed_args, plural):
        results = self._get_members_of_collection_(prefix, parsed_args, plural)
        return results

    def add_service_config_for_service_completer(self, prefix, parsed_args, **kwargs):
        current_service_config_templates = self.__collection_for_resource_completer__(prefix, parsed_args,
                                                                                      'service_config_templates')
        filters = [dict(name='id', op='not_in', val=current_service_config_templates)]
        filtered_service_config_templates = [x[0] for x in self._complex_list_('service_config_template', filters)]
        return filtered_service_config_templates

    def del_service_config_for_service_completer(self, prefix, parsed_args, **kwargs):
        return self.__collection_for_resource_completer__(prefix, parsed_args, 'service_config_templates')

    def add_zone_for_deployment_completer(self, prefix, parsed_args, **kwargs):
        current_zones = self.__collection_for_resource_completer__(prefix, parsed_args, 'zones')
        filters = [dict(name='id', op='not_in', val=current_zones)]
        filtered_zones = [x[0] for x in self._complex_list_('zone', filters)]
        return filtered_zones

    def del_zone_for_deployment_completer(self, prefix, parsed_args, **kwargs):
        return self.__collection_for_resource_completer__(prefix, parsed_args, 'zones')

    def _get_members_of_collection_(self, prefix, parsed_args, plural, **kwargs):
        url = self.URL + "{resource}/{resource_id}/{plural}".format(
            resource=parsed_args.resource,
            resource_id=parsed_args.owner_id,
            plural=plural)

        headers = {'Content-Type': 'application/json'}
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        results = requests.get(url, headers=headers).json()
        objs = results['objects']
        ids = [x['id'] for x in objs]
        return ids

    def allocate_subnet(self, network_id, additional_mask_bits, name):
        from models import Subnet
        from .subnets import SubnetController
        s = Subnet()
        subnet = s.__dict__
        subc = SubnetController(network_id)
        subnet['resource'] = 'subnet'
        subnet['network_id'] = network_id
        subnet['name'] = name
        subnet['cidr'] = subc.allocate_subnet(additional_mask_bits, name)
        return self.create_resource(subnet)

    def _get_search_(self, prefix, resource=None, **kwargs):
        url = self.URL + "{resource}".format(resource=resource)
        headers = {'Content-Type': 'application/json'}
        filters = [dict(name='id', op='like', val=str(prefix) + '%')]
        params = dict(q=json.dumps(dict(filters=filters)))
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200
        results = requests.get(url, headers=headers).json()
        objs = results['objects']
        ids = [x['id'] for x in objs]
        return ids

    def _get_attr_search_(self, prefix, parsed_args, resource=None, attribute=None,  **kwargs):
        url = self.URL + "{resource}/{id}/{attr}".format(resource=resource, id=parsed_args.owner_id, attr=attribute)
        headers = {'Content-Type': 'application/json'}
        filters = [dict(name='id', op='like', val=str(prefix) + '%')]
        params = dict(q=json.dumps(dict(filters=filters)))
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200
        results = requests.get(url, headers=headers).json()
        objs = results['objects']
        ids = [x['id'] for x in objs]
        return ids

    def _get_rest_(self, resource, resource_id=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        response = requests.get(res_url, params=params, headers=headers)
        return response

    def create_complete_application(self, args_dict):
        pass

    def create_resource(self, args_dict):
        fields = schema.CREATE_FIELDS[args_dict['resource']]
        post_data = {}

        for field in fields:
            if type(field) == str:
                if field in args_dict:
                    value = args_dict[field]
                    if value is not None:
                        post_data[field] = value
            elif type(field) == dict:
                for key in field.keys():
                    if re.match('^-', key):
                        if field[key]['args']['dest'] in args_dict:
                            if args_dict[field[key]['args']['dest']] is not None:
                                post_data[field[key]['args']['dest']] = args_dict[field[key]['args']['dest']]
                    else:
                        if 'args' in field[key]:
                            if field[key]['args']['dest'] in args_dict:
                                post_data[key] = args_dict[key]
                        else:
                            if key in args_dict:
                                post_data[key] = args_dict[key]

        # for opt in ['tag']:
        #     if opt in args_dict:
        #         if args_dict[opt] is not None:
        #             post_data[opt] = args_dict[opt]
        return self._post_rest_(args_dict['resource'], json=post_data)

    def _delete_rest_(self, resource, resource_id):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.delete(res_url)

    def delete_resource(self, resource, resource_id, command=None):
        return self._delete_rest_(resource, resource_id)

    def _post_rest_(self, resource, resource_id=None, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.post(res_url, data=data, json=json, params=params, headers=headers)

    def update_resource(self, resource, resource_id, json={}, q=False):
        return self._put_rest_(resource, resource_id, data=None, json=json)

    def _put_rest_(self, resource, resource_id, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.put(res_url, data, json=json, params=params, headers=headers)

    def get_instance(self, resource, resource_id, **kwargs):
        response = self._get_rest_(resource, resource_id)
        return response.json()

    def pretty_get_instance(self, resource, resource_id, **kwargs):
        return json.dumps(self.get_instance(resource, resource_id), indent=4, sort_keys=True)

    def get_field(self, resource, resource_id, field, **kwargs):
        response = self._get_rest_(resource, resource_id, kwargs)
        return response.json()[field]

    def query(self, resource, search_field, op, value=None, output_fields=None, resperpage=None, page=None,
              format="text",
              **kwargs):
        return self._list_(resource, search_field, op, value, output_fields, resperpage, page, format, **kwargs)

    def list(self, resource):
        return self._list_(resource)

    def _list_(self, resource, search_field=None, op=None, value=None, output_fields=None, resperpage=None, page=None,
               fmt="text", **kwargs):
        params = dict(results_per_page=resperpage, page=page)

        if search_field is not None and op is not None:
            if value is not None:
                filters = [dict(name=search_field, op=op, val=value)]
                params['q'] = json.dumps(dict(filters=filters))
            else:
                filters = [dict(name=search_field, op=op)]
                params['q'] = json.dumps(dict(filters=filters))
        response = self._get_rest_(resource, params=params)
        results = []
        if type(output_fields) == str:
            output_fields = [output_fields]
        elif output_fields is None:
            output_fields = ['id']
        for obj in response.json()['objects']:
            if len(output_fields) > 1:
                row = []
                for field in output_fields:
                    row.append(obj[field])
                results.append(row)
            elif len(output_fields) == 1:
                for field in output_fields:
                    results.append(obj[field])
            if fmt == "json":
                results = json.dumps(results)
        return results

    def _complex_list_(self, resource, filters, output_fields=None, resperpage=100):
        params = dict(results_per_page=resperpage)
        params['q'] = json.dumps(dict(filters=filters))
        response = self._get_rest_(resource, params=params)
        results = []
        if type(output_fields) == str:
            output_fields = [output_fields]
        elif output_fields is None:
            output_fields = ['id']
        for obj in response.json()['objects']:
            row = []
            for field in output_fields:
                row.append(obj[field])

            results.append(row)
        return results

    def qairon_wrapped_deployment_search(self, prefix, parsed_args, **kwargs):
        return self._get_search_(prefix, 'deployment')

    def _clone_config_for_dep_clone_(self, configs, new_dep_id):
        for config in configs:
            config.pop('id')
            config['deployment_id'] = new_dep_id
            config['resource'] = 'config'
            self.create_resource(config)
