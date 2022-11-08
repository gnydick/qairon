from sqlalchemy import *

from db import db
import datetime

deps_to_zones = Table('deployments_zones', db.metadata,
                      Column('deployment_id', String, ForeignKey('deployment.id', onupdate='CASCADE')),
                      Column('zone_id', String, ForeignKey('zone.id', onupdate='CASCADE')),
                      Index('ix_deps_to_zones_deployment_id', 'deployment_id'),
                      Index('ix_deps_to_zones_zone_id', 'zone_id')
                      )

subnets_to_fleets = Table('subnets_fleets', db.metadata,
                          Column('subnet_id', String, ForeignKey('subnet.id', onupdate='CASCADE')),
                          Column('fleet_id', String, ForeignKey('fleet.id', onupdate='CASCADE')),
                          Index('ix_subnets_to_fleets_subnet_id', 'subnet_id'),
                          Index('ix_subnets_to_fleets_fleet_id', 'fleet_id')
                          )

target_bins_to_fleets = Table('target_bins_fleets', db.metadata,
                          Column('deployment_target_bin_id', String, ForeignKey('deployment_target_bin.id', onupdate='CASCADE')),
                          Column('fleet_id', String, ForeignKey('fleet.id', onupdate='CASCADE')),
                          Index('ix_target_bins_to_fleets_deployment_target_bin_id', 'deployment_target_bin_id'),
                          Index('ix_target_bins_to_fleets_fleet_id', 'fleet_id')
                          )



svcs_to_repos = Table('services_repos', db.metadata,
                      Column('service_id', String, ForeignKey('service.id', onupdate='CASCADE')),
                      Column('repo_id', String, ForeignKey('repo.id', onupdate='CASCADE'))
                      )
