import io
import sys
from pathlib import Path

from controllers import CLIController, PrintingOutputController, StringIOOutputController, IterableOutputController

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)
#
# ## stdout
# # this will print to stdout just by running the command
poc = PrintingOutputController()
qcli = CLIController(poc)
# qcli.list('deployment')
qcli.get('service', 'withme:services:authentication-server')

# ## StringIO
file_like_string_io = io.StringIO()

soc = StringIOOutputController(file_like_string_io)
qcli = CLIController(soc)
qcli.list('deployment')
result = file_like_string_io.getvalue()
file_like_string_io.flush()
file_like_string_io.seek(0)
print(result)

## Iterable
resutls = []
ioc = IterableOutputController(resutls)
qcli = CLIController(ioc)

qcli.list('deployment')
for row in resutls:
    print(row)
