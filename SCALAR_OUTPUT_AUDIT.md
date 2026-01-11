# Scalar Output Expectations Audit

This document traces the actual code flow for output handling and identifies issues.

---

## Output Controller Code Flow

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

- Receives JSON:API data (`{id, type, attributes: {...}, relationships: {...}}`)
- Calls `simplify_row()` or `simplify_rows()` to flatten
- Passes result to `_output_()`

### 2. Transformation: `simplify_row()` (line 25-46)

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

**With `output_fields=['id']`:**
- `keys = ['id']`
- `output['id'] = row['id']`
- Loop adds nothing (excludes 'id')
- Result: `{'id': 'composite:id:value'}`

**With `output_fields` not specified (default):**
- `keys = row['attributes'].keys()`
- `output['id'] = row['id']`
- Loop adds all attributes
- Result: `{'id': '...', 'attr1': '...', 'attr2': '...', ...}`
- **NOTE: `type` (resource) is NOT included**

**With `output_fields=['id', 'type']`:**
- `output['id'] = row['id']`
- `output['type'] = row['type']`
- Result: `{'id': '...', 'type': '...'}`

### 3. Output: `_output_()` methods

**Plain format (line 85-90):**
```python
elif output_format == 'plain':
    if type(data) == dict:
        print(' '.join(str(x) for x in data.values()))
    elif isinstance(data, Iterable):
        for row in data:
            print(' '.join(str(x) for x in row.values()))
```

- Joins all dict VALUES with spaces
- With `output_fields=['id']`: outputs just the id string
- With default fields: outputs `id attr1 attr2 ...` space-separated

**JSON format (line 82-84):**
```python
if output_format == 'json':
    output = json.dumps(data)
    print(output)
```

- Dumps entire dict as JSON
- With default fields: `{"id": "...", "attr1": "...", ...}` (no `resource`)

---

## Issue Summary

### Issue 1: `resource` Not Included in Default Output

**Location:** `simplify_row()` lines 40-42

**Current behavior:**
```python
else:
    keys = row['attributes'].keys()
    output['id'] = row['id']
    # type/resource is NOT added
```

**Expected:** Default output should include `resource` (from JSON:API `type`)

### Issue 2: `type` vs `resource` Naming

**Location:** `simplify_row()` lines 38-39

**Current behavior:**
```python
if 'type' in keys:
    output['type'] = row['type']
```

- Field is called `type` (JSON:API terminology)
- Tests expect field called `resource` (input format terminology)

---

## Test Workarounds in `features/steps/cli.py`

### Plain Format Tests (Working)

These tests use `output_format='plain', output_fields=['id']` to get just the id:

| Line | Call | Output |
|------|------|--------|
| 9 | `create(..., output_format='plain', output_fields=['id'])` | `id` value only |
| 22 | `create(..., output_format='plain', output_fields=['id'])` | `id` value only |
| etc. | ... | ... |

**Flow:**
1. `simplify_row()` with `output_fields=['id']` -> `{'id': 'value'}`
2. `_output_()` plain -> `' '.join(['value'])` -> `'value'`

### JSON Format Tests (Need Workarounds)

These tests get full JSON output and must patch `resource`:

| Line | Patch to OUTPUT | Patch to INPUT |
|------|-----------------|----------------|
| 327 | `output_obj['resource'] = 'dependency_case'` | - |
| 338-339 | `output_obj['resource'] = resource` | `resource_dict['id'] = ':'.join([value1, value2, name])` |
| 349-350 | `output_obj['resource'] = resource` | `resource_dict['id'] = ':'.join([value1, value2, value3])` |
| 360-361 | `output_obj['resource'] = resource` | `resource_dict['id'] = ':'.join([value1, value2, value3])` |
| 372-373 | `output_obj['resource'] = resource` | `resource_dict['id'] = ':'.join([value1, value2])` |

**Flow:**
1. `simplify_row()` default -> `{'id': '...', 'attr1': '...', ...}` (no `resource`)
2. `_output_()` json -> `{"id": "...", "attr1": "...", ...}`
3. Test parses JSON, adds `resource` manually

---

## Missing Method

### `get_instance()` on QCLIController

**Location:** `features/steps/cli.py` lines 294, 305

```python
environment = context.cli.get_instance('environment', expected_env_id)
k8s_cluster = context.cli.get_instance('k8s_cluster', expected_cluster_id)
```

**Issue:** `QCLIController` does not have `get_instance()` method. Only `RestController` has it.

**Note:** `get_instance()` returns a single dict, not a stream. This is a legitimate exception to the streaming pattern - the method name explicitly indicates scalar return.

---

## Proposed Fixes

### Fix 1: Add `resource` to Default Output

In `simplify_row()`, change:

```python
else:
    keys = row['attributes'].keys()
    output['id'] = row['id']
```

To:

```python
else:
    keys = row['attributes'].keys()
    output['resource'] = row['type']  # ADD THIS
    output['id'] = row['id']
```

### Fix 2: Rename `type` to `resource` When Requested

Change lines 38-39:

```python
if 'type' in keys:
    output['type'] = row['type']
```

To:

```python
if 'type' in keys or 'resource' in keys:
    output['resource'] = row['type']
```

### Fix 3: Add `get_instance()` to QCLIController

```python
def get_instance(self, resource, resource_id):
    """Returns a single simplified dict (not a stream)."""
    row = self.rest.get_instance(resource, resource_id)
    return simplify_row(row)
```

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

## Testing Checklist

After fixes:
- [ ] `behave features/cli.feature` passes
- [ ] `behave features/rest_api.feature` passes
- [ ] Default JSON output includes `resource` field
- [ ] Plain format with `output_fields=['id']` outputs just id
- [ ] Remove test workarounds that add `resource` to output
- [ ] `context.cli.get_instance()` works