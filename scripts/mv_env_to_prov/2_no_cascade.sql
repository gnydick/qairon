
-- allocation
alter table allocation drop constraint allocation_deployment_proc_id_fkey;

alter table allocation
    add constraint allocation_deployment_proc_id_fkey
        foreign key (deployment_proc_id) references deployment_proc;


-- deployment
alter table deployment drop constraint deployment_deployment_target_id_fkey;

alter table deployment
    add constraint deployment_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target;

alter table deployment drop constraint deployment_current_release_id_fkey;

alter table deployment
    add constraint deployment_current_release_id_fkey
        foreign key (current_release_id) references release;

alter table deployment drop constraint deployment_service_id_fkey;

alter table deployment
    add constraint deployment_service_id_fkey
        foreign key (service_id) references service;



-- deployment_config
alter table deployment_config drop constraint deployment_config_deployment_id_fkey;

alter table deployment_config
    add constraint deployment_config_deployment_id_fkey
        foreign key (deployment_id) references deployment;

-- deployment_target
alter table deployment_target drop constraint deployment_target_partition_id_fkey;

alter table deployment_target
    add constraint deployment_target_partition_id_fkey
        foreign key (partition_id) references partition;

alter table deployment_target drop constraint deployment_target_deployment_target_type_id_fkey;

alter table deployment_target
    add constraint deployment_target_deployment_target_type_id_fkey
        foreign key (deployment_target_type_id) references deployment_target_type;


-- deployment_proc
alter table deployment_proc drop constraint deployment_proc_deployment_id_fkey;

alter table deployment_proc
    add constraint deployment_proc_deployment_id_fkey
        foreign key (deployment_id) references deployment;

-- deployments_zones
alter table deployments_zones drop constraint deployments_zones_deployment_id_fkey;

alter table deployments_zones
    add constraint deployments_zones_deployment_id_fkey
        foreign key (deployment_id) references deployment;

alter table deployments_zones drop constraint deployments_zones_zone_id_fkey;

alter table deployments_zones
    add constraint deployments_zones_zone_id_fkey
        foreign key (zone_id) references zone;

-- fleet
alter table fleet drop constraint fleet_deployment_target_id_fkey;

alter table fleet
    add constraint fleet_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target;

-- network
alter table network drop constraint network_partition_id_fkey;

alter table network
    add constraint network_partition_id_fkey
        foreign key (partition_id) references partition;


-- partition
alter table partition drop constraint partition_region_id_fkey;

alter table partition
    add constraint partition_region_id_fkey
        foreign key (region_id) references region;


-- region
alter table region drop constraint region_provider_id_fkey;

alter table region
    add constraint region_provider_id_fkey
        foreign key (provider_id) references provider;


-- release
alter table release drop constraint release_deployment_id_fkey;

alter table release
    add constraint release_deployment_id_fkey
        foreign key (deployment_id) references deployment;

-- service
alter table service drop constraint service_stack_id_fkey;

alter table service
    add constraint service_stack_id_fkey
        foreign key (stack_id) references stack;

-- subnet
alter table subnet drop constraint subnet_network_id_fkey;

alter table subnet
    add constraint subnet_network_id_fkey
        foreign key (network_id) references network;

-- subnets_fleets
alter table subnets_fleets drop constraint subnets_fleets_fleet_id_fkey;

alter table subnets_fleets
    add constraint subnets_fleets_fleet_id_fkey
        foreign key (fleet_id) references fleet;


-- zone
alter table zone drop constraint zone_region_id_fkey;

alter table zone
    add constraint zone_region_id_fkey
        foreign key (region_id) references region;


