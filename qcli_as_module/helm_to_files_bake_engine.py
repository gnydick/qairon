import sys
from pathlib import Path

from qairon_qcli.controllers import QCLIController, IterableOutputController, \
    RestController

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)

results = []
ioc = IterableOutputController(results)
qcli = QCLIController(ioc)
qcli.list('service')
rest = RestController()
from models import *

from db import db
from app import app
import json
with app.app_context():
    session = db.session

    services = session.query(Service).all()
    session.flush()
    session.close()
    for service in services:
        session2 = db.session
        defaults = service.defaults
        print(defaults)
        if defaults is not None:
            if len(defaults) > 0:
                try:
                    defaults = json.loads(defaults)
                    if 'bake' in defaults.keys():
                        if 'output_repos' in defaults['bake'].keys():
                            if len(defaults['bake']['output_repos']) > 1:
                                print("Whoops")
                            elif len(defaults['bake']['output_repos']) == 1:
                                if defaults['bake']['engine'] == 'files':
                                    repo = defaults['bake']['output_repos'][0]
                                    type, name = repo.split(':')
                                    if type != 'helm':
                                        print("Damn!!")
                                    else:
                                        defaults['bake']['engine'] = 'helm'
                                        print("BEFORE:", service)
                                        service.defaults = json.dumps(defaults, indent=4)
                                        print("AFTER:", service)
                                        session2.add(service)
                                        session2.commit()
                                        session2.flush()
                                        session2.close()

                                        # rest.update_resource('service', result['id'], json=json.dumps(result))
                                        pass


                except Exception as e:
                    pass
