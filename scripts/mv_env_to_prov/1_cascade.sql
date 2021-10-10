
-- allocation
alter table allocation drop constraint allocation_deployment_proc_id_fkey;

alter table allocation
    add constraint allocation_deployment_proc_id_fkey
        foreign key (deployment_proc_id) references deployment_proc
            on update cascade;


-- deployment
alter table deployment drop constraint deployment_deployment_target_id_fkey;

alter table deployment
    add constraint deployment_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target
            on update cascade;

alter table deployment drop constraint deployment_current_release_id_fkey;

alter table deployment
    add constraint deployment_current_release_id_fkey
        foreign key (current_release_id) references release
            on update cascade;


-- deployment_config
alter table deployment_config drop constraint deployment_config_deployment_id_fkey;

alter table deployment_config
    add constraint deployment_config_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- deployment_target
alter table deployment_target drop constraint deployment_target_partition_id_fkey;

alter table deployment_target
    add constraint deployment_target_partition_id_fkey
        foreign key (partition_id) references partition
            on update cascade;


-- deployment_proc
alter table deployment_proc drop constraint deployment_proc_deployment_id_fkey;

alter table deployment_proc
    add constraint deployment_proc_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- deployments_zones
alter table deployments_zones drop constraint deployments_zones_deployment_id_fkey;

alter table deployments_zones
    add constraint deployments_zones_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

alter table deployments_zones drop constraint deployments_zones_zone_id_fkey;

alter table deployments_zones
    add constraint deployments_zones_zone_id_fkey
        foreign key (zone_id) references zone
            on update cascade;

-- fleet
alter table fleet drop constraint fleet_deployment_target_id_fkey;

alter table fleet
    add constraint fleet_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target
            on update cascade;

-- network
alter table network drop constraint network_partition_id_fkey;

alter table network
    add constraint network_partition_id_fkey
        foreign key (partition_id) references partition
            on update cascade;


-- partition
alter table partition drop constraint partition_region_id_fkey;

alter table partition
    add constraint partition_region_id_fkey
        foreign key (region_id) references region
            on update cascade;


-- provider
alter table provider drop constraint provider_environment_id_fkey;

alter table provider
    add constraint provider_environment_id_fkey
        foreign key (environment_id) references environment
            on update cascade;

-- region
alter table region drop constraint region_provider_id_fkey;

alter table region
    add constraint region_provider_id_fkey
        foreign key (provider_id) references provider
            on update cascade;


-- release
alter table release drop constraint release_deployment_id_fkey;

alter table release
    add constraint release_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- subnet
alter table subnet drop constraint subnet_network_id_fkey;

alter table subnet
    add constraint subnet_network_id_fkey
        foreign key (network_id) references network
            on update cascade;

-- subnets_fleets
alter table subnets_fleets drop constraint subnets_fleets_fleet_id_fkey;

alter table subnets_fleets
    add constraint subnets_fleets_fleet_id_fkey
        foreign key (fleet_id) references fleet
            on update cascade;


-- zone
alter table zone drop constraint zone_region_id_fkey;

alter table zone
    add constraint zone_region_id_fkey
        foreign key (region_id) references region
            on update cascade;


