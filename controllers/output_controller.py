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


def __serialize_rows__(batch, output_fields=None):
    serialized = list()
    for rows in batch:
        for row in rows:
            serialized.append(__serialize_row__(row, output_fields))
    return serialized


def __serialize_row__(row, output_fields=None):
    row_id = row['id']

    if 'relationships' in row:
        for k, v in row['relationships'].items():
            if type(v['data']) == dict:
                row['attributes'][k + '_id'] = v['data']['id']

    output = dict()
    if output_fields:
        keys = output_fields
        if 'id' in keys:
            output['id'] = row['id']
    else:
        keys = row['attributes'].keys()
        output['id'] = row['id']

    for key in [x for x in keys if x != "id"]:
        output[key] = row['attributes'][key]

    return output


def serialize(rows, output_fields=None):
    if type(rows) == dict:
        cleaned = __serialize_row__(rows, output_fields)
    else:
        cleaned = __serialize_rows__(rows, output_fields)

    return cleaned


def __output__(q, rows, output_fields=None, output_format=None):
    if not q:
        cleaned = serialize(rows, output_fields)
        if output_format is None:
            output_format = 'json'
        if output_format == 'json':
            print(json.dumps(cleaned))
        elif output_format == 'plain':
            if type(cleaned) == dict:
                print(' '.join(str(x) for x in cleaned.values()))
            elif type(cleaned) == list:
                for row in cleaned:
                    print(' '.join(str(x) for x in row.values()))

