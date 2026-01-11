from sqlalchemy import *

from db import db


deps_to_zones = Table('deployments_zones', db.metadata,
                      Column('deployment_id', String, ForeignKey('deployment.id')),
                      Column('zone_id', String, ForeignKey('zone.id')),
                      Index('ix_deps_to_zones_deployment_id', 'deployment_id'),
                      Index('ix_deps_to_zones_zone_id', 'zone_id')
                      )

subnets_to_fleets = Table('subnets_fleets', db.metadata,
                          Column('subnet_id', String, ForeignKey('subnet.id'), nullable=False),
                          Column('fleet_id', String, ForeignKey('fleet.id'), nullable=False),
                          Index('ix_subnets_to_fleets_subnet_id', 'subnet_id'),
                          Index('ix_subnets_to_fleets_fleet_id', 'fleet_id')
                          )

target_to_fleets = Table('target_fleets', db.metadata,
                              Column('deployment_target_id', String,
                                     ForeignKey('deployment_target.id'), nullable=False),
                              Column('fleet_id', String, ForeignKey('fleet.id'), nullable=False),
                              Index('ix_target_to_fleets_deployment_target_id', 'deployment_target_id'),
                              Index('ix_target_to_fleets_fleet_id', 'fleet_id')
                              )

svcs_to_repos = Table('services_repos', db.metadata,
                      Column('service_id', String, ForeignKey('service.id'), nullable=False),
                      Column('repo_id', String, ForeignKey('repo.id'), nullable=False),
                      Index('ix_services_repos_to_service_id', 'service_id'),
                      Index('ix_services_repos_to_repo_id', 'repo_id')
                      )

deployment_current_release = Table('deployment_current_release', db.metadata,
                                   Column('deployment_id', String, ForeignKey('deployment.id'),
                                          primary_key=True, nullable=False),
                                   Column('release_id', String, ForeignKey('release.id'),
                                          primary_key=True, nullable=False),
                                   Index('ix_deployment_current_release_release_id', 'release_id')
                                   )
