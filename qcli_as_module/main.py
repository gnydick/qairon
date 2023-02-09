import io
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)

from qairon.qcli import CLIController

## stdout
# this will print to stdout just by running the command
qcli = CLIController()
qcli.get('service', 'withme:services:authentication-server')

## StringIO
file_like_string_io = io.StringIO()

qcli = CLIController(file_like_string_io)
qcli.get('service', 'withme:services:authentication-server')
result = file_like_string_io.getvalue()
print(result)

## Iterable
iterable = []
qcli = CLIController(iterable)

qcli.get('service', 'withme:services:authentication-server')
for row in foo:
    print(row)

# qcli.query('service', query='[{"name":"id", "op":"like", "val":"withme:services:%"}]')
