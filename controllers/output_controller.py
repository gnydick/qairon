import _io
import json

import itertools
import sys
from json_stream import streamable_list
from json_stream.writer import StreamableList
from collections.abc import Iterable

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


class OutputController:

    def __init__(self, output_stream):
        self.output_stream = output_stream

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

    def _output_(self, batch, output_format=None):
        if output_format is None:
            output_format = 'json'
        if output_format == 'json':
            if type(batch) is StreamableList:
                for row in batch:
                    value = json.dumps(row)
                    self.__write_or_append__(value)
            else:
                value = json.dumps(batch)
                self.__write_or_append__(value)
        elif output_format == 'plain':
            if type(batch) == dict:
                value = ' '.join(str(x) for x in batch.values())
                self.__write_or_append__(value)
            else:
                for row in batch:
                    value = ' '.join(str(x) for x in row.values())
                    self.__write_or_append__(value)

    def write(self, q, data, output_fields=None, output_format=None):
        if not q:
            if type(data) == dict:
                result_stream = self.serialize_row(data, output_fields)
                self._output_(result_stream, output_format)
            elif isinstance(self.output_stream, Iterable):
                self._output_(self.serialize_rows(data), output_format)

    def __write_or_append__(self, value):
        if isinstance(self.output_stream, _io.TextIOWrapper) or isinstance(self.output_stream, _io.StringIO):
            self.output_stream.write(value)
        elif isinstance(self.output_stream, Iterable):
            self.output_stream.append(value)