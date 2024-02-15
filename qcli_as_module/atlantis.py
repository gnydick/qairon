#!/usr/bin/env python3
import io
import os
import sys
from pathlib import Path
os.environ['QAIRON_ENDPOINT']='https://qairon.infra.withme.com'
from qairon_qcli.controllers import QCLIController, PrintingOutputController, StringIOOutputController, IterableOutputController

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)

atlantis_deployments = []

ioc = IterableOutputController(atlantis_deployments)
qcli = QCLIController(ioc)
# query by 2 filters
# 1. deployment based on "withme:automation:atlantis" service
# 2. tag is "default"
query = '[{"and":[{"name":"service_id", "op":"eq", "val":"withme:automation:atlantis"},{"name":"tag", "op":"eq", "val":"default"}]}]'

qcli.query('deployment', query=query)


print(atlantis_deployments)
