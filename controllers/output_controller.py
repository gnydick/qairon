import itertools
import json
import os
from subprocess import call

from .rest_controller import RestController


class SerializableGenerator(list):
    """Generator that is serializable by JSON"""

    def __init__(self, iterable):
        tmp_body = iter(iterable)
        try:
            self._head = iter([next(tmp_body)])
            self.append(tmp_body)
        except StopIteration:
            self._head = []

    def __iter__(self):
        return itertools.chain(self._head, *self[:1])


def __serialize_rows__(rows, output_fields=None, included=None):
    for row in rows:
        row_id = row['id']

        if 'relationships' in row:
            for k, v in row['relationships'].items():
                if type(v['data']) == dict:
                    row['attributes'][k + '_id'] = v['data']['id']

        if output_fields:
            keys = output_fields
        else:
            keys = row['attributes'].keys()

        output = {'id': row_id}
        for key in [x for x in keys if x != "id"]:
            output[key] = row['attributes'][key]
        if included:
            if 'included' in row:
                includes = dict()
            for i in row['included']:
                if i['type'] not in includes:
                    includes[i['type']] = []
                includes[i['type']].append(i)
            output['included'] = includes
        yield output


def __serialize_row__(row, output_fields=None, included=None):
    row_id = row['id']

    if 'relationships' in row:
        for k, v in row['relationships'].items():
            if type(v['data']) == dict:
                row['attributes'][k + '_id'] = v['data']['id']

    if output_fields:
        keys = output_fields
    else:
        keys = row['attributes'].keys()

    output = {'id': row_id}
    for key in [x for x in keys if x != "id"]:
        output[key] = row['attributes'][key]
    if included:
        includes = dict()
        for i in row['included']:
            if i['type'] not in includes:
                includes[i['type']] = []
            includes[i['type']].append(i)
        output['included'] = includes
    return output


def serialize(rows, included=None, output_fields=None):
    if type(rows) == list:
        cleaned = __serialize_rows__(rows, output_fields, included)
    elif type(rows) == dict:
        cleaned = __serialize_row__(rows, output_fields, included)
    return cleaned


def __output__(q, rows, included=None, output_fields=None, output_format=None):
    if not q:
        cleaned = serialize(rows, included, output_fields)
        if output_format == None:
            output_format = 'json'
        if output_format == 'json':
            if type(rows) == list:
                output = [x for x in cleaned]
                print(json.dumps(output))
            elif type(rows) == dict:
                print(json.dumps(cleaned))
        elif output_format == 'plain':
            if type(rows) == list:
                for row in cleaned:
                    print(' '.join(str(x) for x in row.values()))
            elif type(rows) == dict:
                output = ['""' if x is None else str(x) for x in cleaned.values()]
                print(' '.join(output))
