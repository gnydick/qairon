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
    HEADERS = {'Content-Type': 'application/vnd.api+json', 'Accept': 'application/vnd.api+json'}

    def add_to_many_to_many(self, owner_res, owner_res_id, singular_resource, plural_resource, col_res_id):
        owner = self.get_collection(owner_res, owner_res_id, plural_resource)
        collection = dict()
        collection['data'] = list([x for x in
                                   owner])
        collection['data'].append({'type': singular_resource, 'id': col_res_id})
        return self._put_rest_(owner_res, owner_res_id, plural_resource, json=collection)

    def del_from_many_to_many(self, owner_res, owner_res_id, singular_resource, plural_resource, col_res_id):
        owner = self.get_collection(owner_res, owner_res_id, plural_resource)
        collection = dict()
        collection['data'] = list(filter(lambda x: x['id'] != col_res_id, owner))
        # collection['data'] = [{'type': singular_resource, 'id': x} for x in collection['data']]

        return self._put_rest_(owner_res, owner_res_id, plural_resource, json=collection)

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
        from .subnets import SubnetController
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

    def _get_list_(self, resource, params={}, headers=HEADERS):
        res_url = self.URL + resource
        response = requests.get(res_url, params=params, headers=headers)
        return response

    def _get_record_(self, resource, resource_id=None, field=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        if field is not None:
            res_url += '/' + field
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

        data_post_data = {'data': {'attributes': post_data, 'type': args_dict['resource']}}
        return self._post_rest_(args_dict['resource'], json=data_post_data)

    def _delete_rest_(self, resource, resource_id, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.delete(res_url, headers=headers)

    def delete_resource(self, resource, resource_id, command=None):
        return self._delete_rest_(resource, resource_id)

    def _post_rest_(self, resource, resource_id=None, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
        return requests.post(res_url, data=data, json=json, params=params, headers=headers)

    def update_resource(self, resource, resource_id, json={}, q=False):
        return self._put_rest_(resource, resource_id, data=None, json=json)

    def _put_rest_(self, resource, resource_id, collection, data=None, json=None, params={}, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id + '/relationships/' + collection
        return requests.patch(res_url, data, json=json, params=params, headers=headers)

    def get_instance(self, resource, resource_id, included=None):
        if included:
            params = {'include': included }
        else:
            params=None
        response = self._get_record_(resource, resource_id, params=params)
        results = response.json()
        return __handle_return_data__(results, included)['data']

    def pretty_get_instance(self, resource, resource_id):
        return json.dumps(self.get_instance(resource, resource_id), indent=4, sort_keys=True)

    def get_field(self, resource, resource_id, field, included=None, resperpage=None, page=None):
        params = {'page[size]': resperpage, 'page[number]': page}
        if included:
            params['include'] = included
        response = self._get_record_(resource, resource_id, field=field, params=params)
        results = response.json()
        return __handle_return_data__(results, included)['data']

    def get_field_query(self, resource, field, query, resperpage=None, page=None):
        params = {'page[size]': resperpage, 'page[number]': page, 'include': field}
        rows = self._query_(resource, query=query, field=field, params=params)
        return rows

    def _get_all_(self, resource, resource_id, path, headers=HEADERS):
        res_url = self.URL + resource
        if resource_id is not None:
            res_url += '/' + resource_id
            if path is not None:
                res_url += '/' + path

            params = {'page[size]': 1}
            response = requests.get(res_url, headers=headers)
            rdata = response.json()
            total = rdata['meta']['total']

            # this section loops through the pages, yielding page (batch of rows) to the caller
            for page in range(1, int(total / 200 + 2)):
                params = {'page[num]': page, 'page[size]': 100}
                response = requests.get(res_url, params=params, headers=headers)
                results = response.json()
                if 'data' not in results:
                    exit(255)
                else:
                    data = results['data']
                    yield data

    def get_collection(self, resource, resource_id, collection, resperpage=None, page=None):
        # receiving the yield for the pages (batches of rows)
        batches = self._get_all_(resource, resource_id, collection)

        # loop over each batch
        for batch in batches:
            # loop over each row of each batch
            for member in batch:
                # stream each line back to the caller to loop over
                yield member

    def query(self, resource, query, output_fields=None, resperpage=None, page=None,
              **kwargs):
        return self._query_(resource, query, output_fields=output_fields, resperpage=resperpage, page=page)

    def list(self, resource):
        return self._query_(resource)

    def _query_(self, resource, query=None, resperpage=None, page=None,
                **kwargs):
        params = {'page[size]': resperpage, 'page[number]': page}
        if query is not None:
            filters = json.loads(query)
            params['filter[objects]'] = query
        response = self._get_list_(resource, params=params)
        results = response.json()
        if 'data' not in results:
            exit(255)
        else:
            return results['data']

    def _complex_list_(self, resource, filters, output_fields=None, resperpage=100):
        params = dict(results_per_page=resperpage)
        params['q'] = json.dumps(dict(filters=filters))
        response = self._get_record_(resource, params=params)
        results = []
        if type(output_fields) == str:
            output_fields = [output_fields]
        elif output_fields is None:
            output_fields = ['id']

        json_results = response.json()
        if 'data' not in json_results:
            exit(255)
        else:
            for obj in json_results['data']:
                row = []
                for field in output_fields:
                    row.append(obj[field])

                results.append(row)
            return results

    def qairon_wrapped_deployment_search(self, prefix, parsed_args):
        return self._get_search_(prefix, 'deployment')

    def _clone_config_for_dep_clone_(self, configs, new_dep_id):
        for config in configs:
            config.pop('id')
            config['deployment_id'] = new_dep_id
            config['resource'] = 'config'
            self.create_resource(config)


def __handle_return_data__(results, included):
    if 'data' not in results:
        exit(255)
    else:
        result = results
        if included:
            result['included'] = results['included']
        return result
