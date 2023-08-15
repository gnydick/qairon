#!/usr/bin/env python3
import io
import sys
from pathlib import Path
PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)
from controllers import QCLIController, PrintingOutputController, StringIOOutputController, IterableOutputController



### JSON

## stdout
# # this will print to stdout, just like when running the plugins script
# poc = PrintingOutputController()
# plugins = CLIController(poc)
# # plugins.list('deployment')
# plugins.get('service', 'withme:services:authentication-server_plugins')

## StringIO
# this will return a single string that will be parseable. e.g.
#  * if you request json and there are multiple rows, you will get a json array
#  * if you request json and there is a single row, you will get a json object
file_like_string_io = io.StringIO()

soc = StringIOOutputController(file_like_string_io)
qcli = QCLIController(soc)
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
qcli = QCLIController(ioc)

qcli.list('deployment')
for row in results:
    print(row)

### Plain
## stdout

poc = PrintingOutputController()
qcli = QCLIController(poc)
qcli.list('deployment')
# plugins.get('service', 'withme:services:authentication-server_plugins', output_format='plain')

## StringIO
file_like_string_io = io.StringIO()

soc = StringIOOutputController(file_like_string_io)
qcli = QCLIController(soc)
qcli.list('deployment', output_format='plain')
result = file_like_string_io.getvalue()
file_like_string_io.flush()
file_like_string_io.seek(0)
print(result)

## Iterable
results = []
ioc = IterableOutputController(results)
qcli = QCLIController(ioc)

qcli.list('deployment', output_format='plain')
for row in results:
    print(row)
