import itertools
import json
import sys

from json_stream import streamable_list
from json_stream.writer import StreamableList


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


def serialize_row(row, output_fields=None):
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


@streamable_list
def serialize_rows(batches, output_fields=None):
    if type(batches) == dict:
        cleaned = serialize_row(batches, output_fields)
        yield cleaned
    else:
        for batch in batches:
            if type(batch) == dict:
                yield serialize_row(batch, output_fields)
            elif type(batch) == list:
                for row in batch:
                    yield serialize_row(row, output_fields)


def __output__(batch, output_format):
    if output_format is None:
        output_format = 'json'
    if output_format == 'json':
        if type(batch) is StreamableList:
            json.dump(batch, sys.stdout)
        else:
            print(json.dumps(batch))
    elif output_format == 'plain':
        if type(batch) == dict:
            print(' '.join(str(x) for x in batch.values()))
        else:
            for row in batch:
                print(' '.join(str(x) for x in row.values()))


def output(q, data, output_fields=None, output_format=None):
    if not q:
        if type(data) is StreamableList:
            result_stream = serialize_rows(data, output_fields)
            __output__(result_stream, output_format)
        if type(data) == list:
            result_stream = serialize_rows(data, output_fields)
            __output__(result_stream, output_format)
        elif type(data) == dict:
            __output__(serialize_row(data), output_format)
