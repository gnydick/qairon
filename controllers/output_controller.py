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


def simplify_row(row, **kwargs):
    if 'relationships' in row:
        for k, v in row['relationships'].items():
            if type(v['data']) == dict:
                row['attributes'][k + '_id'] = v['data']['id']

    output = dict()

    output_fields = kwargs.get('output_fields', None)
    if output_fields is not None:
        keys = output_fields
        if 'id' in keys:
            output['id'] = row['id']
        if 'type' in keys:
            output['type'] = row['type']
    else:
        keys = row['attributes'].keys()
        output['id'] = row['id']

    for key in [x for x in keys if x not in  ['id']]:
        output[key] = row['attributes'][key]
    return output


@streamable_list
def simplify_rows(batches, **kwargs):
    output_fields = kwargs.get('output_fields', None)
    if type(batches) == dict:
        cleaned = simplify_row(batches, **kwargs)
        yield cleaned
    else:
        for batch in batches:
            if type(batch) == dict:
                yield simplify_row(batch, **kwargs)
            elif type(batch) == list:
                for row in batch:
                    yield simplify_row(row, **kwargs)


class AbstractOutputController(ABC):

    def handle(self, data, **kwargs):
        q = kwargs.get('q', False)
        if q is False:
            if type(data) == dict:
                results = simplify_row(data, **kwargs)
                self._output_(results, **kwargs)
            elif isinstance(data, Iterable):
                results = simplify_rows(data, **kwargs)
                self._output_(results, **kwargs)


class PrintingOutputController(AbstractOutputController):

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format', None)
        if output_format is None:
            output_format = 'json'
        if output_format == 'json':
            output = json.dumps(data)
            print(output)
        elif output_format == 'plain':
            if type(data) == dict:
                print(' '.join(str(x) for x in data.values()))
            elif isinstance(data, Iterable):
                for row in data:
                    print(' '.join(str(x) for x in row.values()))


class StringIOOutputController(AbstractOutputController):

    def __init__(self, stringIO):
        self.stringIO = stringIO

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format', None)
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

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format', None)
        if output_format is None:
            output_format = 'json'

        if output_format == 'json':
            for row in data:
                self.iterable.append(json.dumps(row))
        elif output_format == 'plain':
            for row in data:
                self.iterable.append(' '.join(str(x) for x in row.values()))

    @streamable_list
    def read_as_json(self):
        for row in self.iterable:
            yield json.loads(row)
        self.iterable.clear()
