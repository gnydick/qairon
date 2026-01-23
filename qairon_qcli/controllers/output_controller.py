import itertools
import json

from abc import ABC

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


def simplify_row(row):
    """Transform JSON:API format to flat dict format. Always returns complete data."""
    if 'relationships' in row:
        for k, v in row['relationships'].items():
            if type(v['data']) == dict:
                row['attributes'][k + '_id'] = v['data']['id']

    output = dict()
    output['resource'] = row['type']
    output['id'] = row['id']

    for key in row['attributes'].keys():
        output[key] = row['attributes'][key]

    return output


@streamable_list
def simplify_rows(batches):
    """Transform batches of JSON:API data to flat format."""
    if type(batches) == dict:
        yield simplify_row(batches)
    else:
        for batch in batches:
            if type(batch) == dict:
                yield simplify_row(batch)
            elif type(batch) == list:
                for row in batch:
                    yield simplify_row(row)


def _filter_fields(data, fields):
    """Filter dict to only include specified fields."""
    return {k: v for k, v in data.items() if k in fields}


class AbstractOutputController(ABC):

    def handle(self, data, **kwargs):
        q = kwargs.get('q', False)
        if q is False:
            results = simplify_rows(data)
            self._output_(results, **kwargs)


class PrintingOutputController(AbstractOutputController):

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format') or 'json'
        output_fields = kwargs.get('output_fields')

        # Materialize the iterable to a list so we can check length
        rows = list(data)

        # Apply field filtering if specified
        if output_fields:
            rows = [_filter_fields(row, output_fields) for row in rows]
        if output_format == 'json':
            # Single item: output as scalar dict, multiple: output as list
            if len(rows) == 1:
                print(json.dumps(rows[0]))
            else:
                print(json.dumps(rows))
        elif output_format == 'plain':
            for row in rows:
                print(' '.join(row[x] for x in output_fields))


class StringIOOutputController(AbstractOutputController):

    def __init__(self, string_io):
        self.string_io = string_io

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format') or 'json'
        output_fields = kwargs.get('output_fields')

        # Materialize the iterable to a list so we can check length
        rows = list(data)

        # Apply field filtering if specified
        if output_fields:
            rows = [_filter_fields(row, output_fields) for row in rows]

        if output_format == 'json':
            # Single item: output as scalar dict, multiple: output as list
            if len(rows) == 1:
                json.dump(rows[0], self.string_io)
            else:
                json.dump(rows, self.string_io)
        elif output_format == 'plain':
            for row in rows:
                self.string_io.write(' '.join(str(x) for x in row.values()))


class IterableOutputController(AbstractOutputController):

    def __init__(self, iterable):
        self.iterable = iterable

    def _output_(self, data, **kwargs):
        output_format = kwargs.get('output_format') or 'json'
        output_fields = kwargs.get('output_fields')

        # Materialize the iterable to a list so we can check length
        rows = list(data)

        # Apply field filtering if specified
        if output_fields:
            rows = [_filter_fields(row, output_fields) for row in rows]

        if output_format == 'json':
            for row in rows:
                self.iterable.append(json.dumps(row))
        elif output_format == 'plain':
            for row in rows:
                self.iterable.append(' '.join(str(x) for x in row.values()))

    @streamable_list
    def read_as_json(self):
        for row in self.iterable:
            yield json.loads(row)
        self.iterable.clear()
