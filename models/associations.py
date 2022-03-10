from sqlalchemy import *

from db import db
import datetime

deps_to_zones = Table('deployments_zones', db.metadata,
                      Column('deployment_id', String, ForeignKey('deployment.id')),
                      Column('zone_id', String, ForeignKey('zone.id'))
                      )

subnets_to_fleets = Table('subnets_fleets', db.metadata,
                          Column('subnet_id', String, ForeignKey('subnet.id')),
                          Column('fleet_id', String, ForeignKey('fleet.id'))
                          )



svcs_to_repos = Table('services_repos', db.metadata,
                      Column('service_id', String, ForeignKey('service.id')),
                      Column('repo_id', String, ForeignKey('repo.id'))
                      )
