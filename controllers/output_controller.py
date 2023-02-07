import itertools
import json
import types


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


def __serialize_rows__(rows, output_fields=None):
    serialized = list()
    for row in rows:
        serialized.append(__serialize_row__(row, output_fields))
    yield serialized


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


def serialize(batches, output_fields=None):
    if type(batches) == dict:
        cleaned = __serialize_row__(batches, output_fields)
        yield cleaned
    elif type(batches) is types.GeneratorType:
        for batch in batches:
            if type(batch) == dict:
                cleaned = __serialize_row__(batch, output_fields)
            elif type(batch) == list:
                cleaned = __serialize_rows__(batch, output_fields)
            yield cleaned

    else:
        wrapper = __serialize_rows__(batches, output_fields)
        for cleaned in wrapper:
            yield cleaned


def __output__(batch, output_format):
    if output_format is None:
        output_format = 'json'
    if output_format == 'json':
        print(json.dumps(batch))
    elif output_format == 'plain':
        if type(batch) == dict:
            print(' '.join(str(x) for x in batch.values()))
        elif type(batch) == list:
            for row in batch:
                print(' '.join(str(x) for x in row.values()))


def output(q, rows, output_fields=None, output_format=None):
    if not q:
        wrapper = serialize(rows, output_fields)
        for cleaned in wrapper:
            if type(cleaned) is types.GeneratorType:
                for batch in cleaned:
                    __output__(batch, output_format)
            elif type(cleaned) is dict:
                __output__(cleaned, output_format)
