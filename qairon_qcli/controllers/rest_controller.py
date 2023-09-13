import json
import logging
import os
import re

import requests
from json_stream import streamable_list
from qairon_qcli.controllers.subnets import SubnetController

from .schema import QaironSchema


class RestController:
    # global schema
    schema = QaironSchema()
    global endpoint
    endpoint = os.getenv("QAIRON_ENDPOINT", "http://localhost:5001")

    def __init__(self):
        pass

    URL = '%s/api/rest/v1/' % endpoint
    HEADERS = {'Content-Type': 'application/vnd.api+json', 'Accept': 'application/vnd.api+json'}

    def add_to_many_to_many(self, owner_res, owner_res_id, singular_resource, plural_resource, col_res_id):
        owner = self._get_all_(owner_res, owner_res_id, path=plural_resource)
        collection = dict()
        collection['data'] = []
        for wrapper in owner:
            for wraps in wrapper:
                collection['data'].append({'id': wraps['id'], 'type': singular_resource})
        collection['data'].append({'type': singular_resource, 'id': col_res_id})
        response = self._put_rest_(owner_res, owner_res_id, plural_resource, json=collection)
        if response.status_code == 204:
            return self.get_field(owner_res, owner_res_id, plural_resource)

    def del_from_many_to_many(self, owner_res, owner_res_id, singular_resource, plural_resource, col_res_id):
        owner = self._get_all_(owner_res, owner_res_id, path=plural_resource)
        collection = dict()
        for wrapper in owner:
            collection['data'] = list(filter(lambda x: x.get('id') != col_res_id, wrapper))
        response = self._put_rest_(owner_res, owner_res_id, plural_resource, json=collection)
        if response.status_code == 204:
            return self.get_field(owner_res, owner_res_id, plural_resource)

    def resource_get_search(self, prefix, resource):
        return self._get_search_(prefix, resource=resource)

    def resource_get_attr_search(self, prefix, parsed_args, resource, attribute):
        return self._get_attr_search_(prefix, parsed_args, resource=resource, attribute=attribute)

    def __collection_for_resource_completer__(self, prefix, parsed_args, plural):
        results = self._get_members_of_collection_(prefix, parsed_args, plural)
        return results

    def add_service_config_for_service_completer(self, prefix, parsed_args):
        current_service_config_templates = self.__collection_for_resource_completer__(prefix, parsed_args,
                                                                                      'service_config_templates')
        filters = [dict(name='id', op='not_in', val=current_service_config_templates)]
        filtered_service_config_templates = [x[0] for x in self._complex_list_('service_config_template', filters)]
        return filtered_service_config_templates

    def del_service_config_for_service_completer(self, prefix, parsed_args):
        return self.__collection_for_resource_completer__(prefix, parsed_args, 'service_config_templates')

    def add_zone_for_deployment_completer(self, prefix, parsed_args):
        current_zones = self.__collection_for_resource_completer__(prefix, parsed_args, 'zones')
        filters = [dict(name='id', op='not_in', val=current_zones)]
        filtered_zones = [x[0] for x in self._complex_list_('zone', filters)]
        return filtered_zones

    def del_zone_for_deployment_completer(self, prefix, parsed_args):
        return self.__collection_for_resource_completer__(prefix, parsed_args, 'zones')

    def _get_members_of_collection_(self, prefix, parsed_args, plural):
        url = self.URL + "{resource}/{resource_id}/{plural}".format(
            resource=parsed_args.resource,
            resource_id=parsed_args.owner_id,
            plural=plural)

        headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        }
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        results = requests.get(url, headers=headers).json()
        if 'data' not in results:
            exit(255)
        else:
            objs = results['data']
            ids = [x['id'] for x in objs]
            return ids

    def allocate_subnet(self, network_id, additional_mask_bits, name):

        # s = Subnet()
        subnet = dict()
        subc = SubnetController(network_id)
        subnet['resource'] = 'subnet'
        subnet['network_id'] = network_id
        subnet['name'] = name
        subnet['cidr'] = subc.allocate_subnet(additional_mask_bits, name)
        return self.create_resource(subnet)

    def _get_search_(self, prefix, resource=None):
        url = self.URL + "{resource}".format(resource=resource)
        headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        }
        filters = [dict(name='id', op='like', val=str(prefix) + '%')]
        params = {'filter[objects]': json.dumps(filters)}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200
        results = response.json()
        if 'data' not in results:
            exit(255)
        else:
            objs = results['data']
            ids = [x['id'] for x in objs]
            return ids

    def _get_attr_search_(self, prefix, parsed_args, resource=None, attribute=None):
        url = self.URL + "{resource}/{id}/{attr}".format(resource=resource, id=parsed_args.owner_id, attr=attribute)
        headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        }
        filters = [dict(name='id', op='like', val=str(prefix) + '%')]
        params = {'filter[objects]': json.dumps(filters)}
        response = requests.get(url, params=params, headers=headers)
        assert response.status_code == 200
        results = requests.get(url, headers=headers).json()
        if 'data' not in results:
            exit(255)
        else:
            objs = results['data']
            ids = [x['id'] for x in objs]
            return ids

    def _get_record_(self, resource, resource_id=None, field=None, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        if field is not None:
            res_url += '/' + field
        response = requests.get(res_url, headers=headers)
        return response

    def create_complete_application(self, args_dict):
        pass

    def create_resource(self, args_dict):
        fields = QaironSchema.CREATE_FIELDS[args_dict['resource']]
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

        data_post_data = {'data': {'attributes': post_data, 'type': args_dict['resource']}}
        return self._post_rest_(args_dict['resource'], json=data_post_data)

    def _delete_rest_(self, resource, resource_id, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.delete(res_url, headers=headers)

    def delete_resource(self, resource, resource_id):
        return self._delete_rest_(resource, resource_id)

    def _post_rest_(self, resource, resource_id=None, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.post(res_url, data=data, json=json, params=params, headers=headers)

    def patch_resource(self, resource, resource_id, json={}, **kwargs):
        return self._patch_rest_(resource, resource_id, data=None, json=json)

    def update_resource(self, resource, resource_id, json={}, **kwargs):
        return self._put_rest_(resource, resource_id, data=None, json=json)

    def _patch_rest_(self, resource, resource_id, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.patch(res_url, data, json=json, params=params, headers=headers)

    def _put_rest_(self, resource, resource_id, collection, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id + '/relationships/' + collection
        return requests.patch(res_url, data, json=json, params=params, headers=headers)

    def get_instance(self, resource, resource_id):
        response = self._get_record_(resource, resource_id)
        results = response.json()
        return results['data']

    def pretty_get_instance(self, resource, resource_id):
        return json.dumps(self.get_instance(resource, resource_id), indent=4, sort_keys=True)

    def get_field(self, resource, resource_id, field):
        response = self._get_record_(resource, resource_id, field=field)
        results = response.json()
        return results['data']

    # this method takes req_params since more complex cli calls use it
    # pagination is only used internally here
    # the req_params passed in is usually a query
    # @streamable_list
    @streamable_list
    def _get_all_(self, resource, resource_id=None, req_params={}, path=None, headers=HEADERS, **kwargs):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
            if path is not None:
                res_url += '/' + path

        # this section loops through the pages, yielding page (batch of rows) to the caller

        req_params['page[size]'] = 100
        response = requests.get(res_url, params=req_params, headers=headers)
        if not (response.status_code >= 200 and response.status_code < 300):
            logging.error("Server Error: %d - %s" % (response.status_code, response.reason))
            raise ValueError
        else:
            rdata = response.json()
            if 'data' not in rdata:
                exit(255)
            else:
                data = rdata['data']
                yield data
                while ('links' in rdata and rdata['links']['next'] is not None):
                    response = requests.get(rdata['links']['next'], params=req_params, headers=headers)
                    rdata = response.json()
                    data = rdata['data']
                    yield data

    def query(self, resource, query=None, **kwargs):
        return self._query_(resource, query=query, **kwargs)

    def list(self, resource):
        return self._get_all_(resource)

    def _query_(self, resource, query, **kwargs):

        req_params = dict()
        if query is not None:
            req_params['filter[objects]'] = query
        response = self._get_all_(resource, req_params=req_params, **kwargs)

        return response

    def qairon_wrapped_deployment_search(self, prefix, parsed_args):
        return self._get_search_(prefix, 'deployment')

    def _clone_config_for_dep_clone_(self, configs, new_dep_id):
        for config in configs:
            config.pop('id')
            config['deployment_id'] = new_dep_id
            config['resource'] = 'config'
            self.create_resource(config)

    def _paginate_(self, result):
        pass
