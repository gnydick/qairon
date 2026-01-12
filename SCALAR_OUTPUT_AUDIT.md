# Scalar Output Expectations Audit

This document traces the actual code flow for output handling and identifies issues.

---

## Current Architecture

### 1. Entry Point: `handle()` (line 66-73)

```python
def handle(self, data, **kwargs):
    q = kwargs.get('q', False)
    if q is False:
        if type(data) == dict:
            results = simplify_row(data, **kwargs)
        elif isinstance(data, Iterable):
            results = simplify_rows(data, **kwargs)
        self._output_(results, **kwargs)
```

### 2. Current `simplify_row()` (line 25-46)

Currently mixes two responsibilities:
- Transforms JSON:API to flat format
- Filters fields based on `output_fields` kwarg

```python
def simplify_row(row, **kwargs):
    # Extract relationship IDs into attributes
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

    for key in [x for x in keys if x not in ['id']]:
        output[key] = row['attributes'][key]
    return output
```

### 3. Current `_output_()` methods

Only handles format (json/plain), not field filtering.

---

## Issues with Current Design

1. **`simplify_row()` does too much** - transforms AND filters
2. **`resource` not included** - JSON:API `type` is dropped unless explicitly requested
3. **Field filtering in wrong place** - should be in output controller
4. **Inconsistent output** - different kwargs produce different shapes

---

## Proposed Architecture: Clean Separation of Concerns

### Layer 1: `simplify_row()` - Pure Transformation

**Single responsibility:** Transform JSON:API format to complete flat format.

```python
def simplify_row(row):
    """
    Transform JSON:API format to flat dict format.
    Always returns complete data - no filtering.
    """
    # Extract relationship IDs into attributes
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
```

**Output format (always):**
```python
{
    'resource': 'deployment',      # from row['type']
    'id': 'env:app:stack:svc:tag', # from row['id']
    'attr1': 'value1',             # from row['attributes']
    'attr2': 'value2',
    ...
}
```

### Layer 2: `simplify_rows()` - Batch Transformation

```python
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
```

### Layer 3: `handle()` - Orchestration

```python
def handle(self, data, **kwargs):
    q = kwargs.get('q', False)
    if q is False:
        if type(data) == dict:
            results = simplify_row(data)
        elif isinstance(data, Iterable):
            results = simplify_rows(data)
        self._output_(results, **kwargs)
```

### Layer 4: `_output_()` - Formatting & Field Selection

**All presentation logic moves here:**

```python
def _output_(self, data, **kwargs):
    output_format = kwargs.get('output_format', 'json')
    output_fields = kwargs.get('output_fields', None)

    if output_format == 'json':
        if output_fields:
            data = self._filter_fields(data, output_fields)
        print(json.dumps(data))

    elif output_format == 'plain':
        if output_fields:
            data = self._filter_fields(data, output_fields)
        if type(data) == dict:
            print(' '.join(str(x) for x in data.values()))
        elif isinstance(data, Iterable):
            for row in data:
                print(' '.join(str(x) for x in row.values()))

def _filter_fields(self, data, fields):
    """Filter dict or iterable to only include specified fields."""
    if type(data) == dict:
        return {k: v for k, v in data.items() if k in fields}
    else:
        return ({k: v for k, v in row.items() if k in fields} for row in data)
```

---

## Benefits of New Architecture

1. **`simplify_row()` is simpler** - no kwargs, always complete output
2. **Consistent data shape** - every row has `resource`, `id`, and all attributes
3. **Output controllers own presentation** - field filtering, formatting
4. **Easier testing** - each layer has single responsibility
5. **List and scalar output identical format** - just different cardinality

---

## Test Workarounds That Can Be Removed

After implementing new architecture, these workarounds become unnecessary:

| Line | Current Workaround | After Fix |
|------|-------------------|-----------|
| 327 | `output_obj['resource'] = 'dependency_case'` | Output already has `resource` |
| 338 | `output_obj['resource'] = resource` | Output already has `resource` |
| 349 | `output_obj['resource'] = resource` | Output already has `resource` |
| 360 | `output_obj['resource'] = resource` | Output already has `resource` |
| 372 | `output_obj['resource'] = resource` | Output already has `resource` |

**Note:** The `resource_dict['id'] = ...` patches to INPUT are still needed since tests need to construct expected `id` for comparison.

---

## Missing Method

### `get_instance()` on QCLIController

**Location:** `features/steps/cli.py` lines 294, 305

```python
environment = context.cli.get_instance('environment', expected_env_id)
k8s_cluster = context.cli.get_instance('k8s_cluster', expected_cluster_id)
```

**Issue:** `QCLIController` does not have `get_instance()` method.

**Fix:**
```python
def get_instance(self, resource, resource_id):
    """Returns a single simplified dict (not a stream)."""
    row = self.rest.get_instance(resource, resource_id)
    return simplify_row(row)
```

**Note:** `get_instance()` returns a single dict, not a stream. This is a legitimate exception to the streaming pattern - the method name explicitly indicates scalar return.

---

## Other Files with Scalar Expectations

These files call `rest.get_instance()` directly and expect scalar dict:

| File | Line | Code |
|------|------|------|
| `subnets.py` | 17 | `rest.get_instance('network', ...)['attributes']` |
| `baking_builder.py` | 18-26 | `simplify_row(self.rest.get_instance(...))` |
| `aws.py` | 48-62 | `rest.get_instance('config_template', ...)['attributes']` |
| `dependencies.py` | 23-24 | `self.rest.get_instance(...)` |

These work correctly because `rest.get_instance()` returns scalar dict.

---

## Implementation Checklist

- [ ] Refactor `simplify_row()` to always return complete format (no kwargs)
- [ ] Update `simplify_rows()` to not pass kwargs
- [ ] Update `handle()` to not pass kwargs to simplify functions
- [ ] Add `_filter_fields()` helper to output controllers
- [ ] Move field filtering to `_output_()` methods
- [ ] Add `get_instance()` to `QCLIController`
- [ ] Update tests to remove `output_obj['resource']` workarounds

---

## Testing Checklist

After implementation:
- [ ] `behave features/cli.feature` passes
- [ ] `behave features/rest_api.feature` passes
- [ ] All output includes `resource` field by default
- [ ] `output_fields=['id']` filters to just id
- [ ] Plain format with filtered fields outputs correct values
- [ ] `context.cli.get_instance()` works