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


class AbstractOutputController(ABC):

    def serialize_row(self, row, output_fields=None):
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
    def serialize_rows(self, batches, output_fields=None):
        if type(batches) == dict:
            cleaned = self.serialize_row(batches, output_fields)
            yield cleaned
        else:
            for batch in batches:
                if type(batch) == dict:
                    yield self.serialize_row(batch, output_fields)
                elif type(batch) == list:
                    for row in batch:
                        yield self.serialize_row(row, output_fields)

    def handle(self, q, data, output_fields=None, output_format=None):
        if not q:
            if type(data) == dict:
                result_stream = self.serialize_row(data, output_fields)
                self._output_(result_stream, output_format)
            elif isinstance(data, Iterable):
                self._output_(self.serialize_rows(data), output_format)


class PrintingOutputController(AbstractOutputController):

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

            if output_format == 'json':
                json.dump(data, sys.stdout)
            elif output_format == 'plain':
                print(' '.join(str(x) for x in data.values()))



class StringIOOutputController(AbstractOutputController):

    def __init__(self, stringIO):
        self.stringIO = stringIO

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

            if output_format == 'json':
                json.dump(data, self.stringIO)
            elif output_format == 'plain':
                self.stringIO.write(' '.join(str(x) for x in data.values()))



class IterableOutputController(AbstractOutputController):

    def __init__(self, iterable):
        self.iterable = iterable

    def _output_(self, data, output_format=None):
        if output_format is None:
            output_format = 'json'

            if output_format == 'json':
                for x in data:
                    self.iterable.append(json.dumps(x))
            elif output_format == 'plain':
                self.iterable.append(' '.join(str(x) for x in data.values()))


