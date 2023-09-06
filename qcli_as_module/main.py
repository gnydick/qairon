import io
import sys
from pathlib import Path

from qairon_qcli.controllers import CLIController, PrintingOutputController, StringIOOutputController, IterableOutputController

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)

### JSON

## stdout
# # this will print to stdout, just like when running the qcli script
# poc = PrintingOutputController()
# qcli = CLIController(poc)
# # qcli.list('deployment')
# qcli.get('service', 'withme:services:authentication-server')

## StringIO
# this will return a single string that will be parseable. e.g.
#  * if you request json and there are multiple rows, you will get a json array
#  * if you request json and there is a single row, you will get a json object
file_like_string_io = io.StringIO()

soc = StringIOOutputController(file_like_string_io)
qcli = CLIController(soc)
qcli.list('deployment')
result = file_like_string_io.getvalue()
file_like_string_io.flush()
file_like_string_io.seek(0)
print(result)

## Iterable
# this will always return indvidual objects e.g.
#  * if you request json and the result is multiple rows, the iterator will receive a Python list of json objects,
#  * not a json array
results = []
ioc = IterableOutputController(results)
qcli = CLIController(ioc)

qcli.list('deployment')
for row in results:
    print(row)

### Plain
## stdout

poc = PrintingOutputController()
qcli = CLIController(poc)
qcli.list('deployment')
# qcli.get('service', 'withme:services:authentication-server', output_format='plain')

## StringIO
file_like_string_io = io.StringIO()

soc = StringIOOutputController(file_like_string_io)
qcli = CLIController(soc)
qcli.list('deployment', output_format='plain')
result = file_like_string_io.getvalue()
file_like_string_io.flush()
file_like_string_io.seek(0)
print(result)

## Iterable
results = []
ioc = IterableOutputController(results)
qcli = CLIController(ioc)

qcli.list('deployment', output_format='plain')
for row in results:
    print(row)
