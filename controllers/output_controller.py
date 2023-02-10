import itertools
import json
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable

from json_stream import streamable_list


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


def simplify_row(row, output_fields=None):
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
def simplify_rows(batches, output_fields=None):
    if type(batches) == dict:
        cleaned = simplify_row(batches, output_fields)
        yield cleaned
    else:
        for batch in batches:
            if type(batch) == dict:
                yield simplify_row(batch, output_fields)
            elif type(batch) == list:
                for row in batch:
                    yield simplify_row(row, output_fields)


class AbstractOutputController(ABC):

    def handle(self, q, data, output_fields=None, output_format=None):
        if not q:
            if type(data) == dict:
                results = simplify_row(data, output_fields)
                self._output_(results, output_format)
            elif isinstance(data, Iterable):
                results = simplify_rows(data, output_fields)
                self._output_(results, output_format)


class PrintingOutputController(AbstractOutputController):

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

        if output_format == 'json':
            json.dump(data, sys.stdout)
        elif output_format == 'plain':
            if type(data) == dict:
                print(' '.join(str(x) for x in data.values()))
            elif isinstance(data, Iterable):
                for row in data:
                    print(' '.join(str(x) for x in row.values()))






class StringIOOutputController(AbstractOutputController):

    def __init__(self, stringIO):
        self.stringIO = stringIO

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

        if output_format == 'json':
            json.dump(data, self.stringIO)
        elif output_format == 'plain':
            if type(data) == dict:
                self.stringIO.write(' '.join(str(x) for x in data.values()))
            elif isinstance(data, Iterable):
                for row in data:
                    self.stringIO.write(' '.join(str(x) for x in row.values()))


class IterableOutputController(AbstractOutputController):

    def __init__(self, iterable):
        self.iterable = iterable

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

        if output_format == 'json':
            for row in data:
                self.iterable.append(json.dumps(row))
        elif output_format == 'plain':
            for row in data:
                self.iterable.append(' '.join(str(x) for x in row.values()))
