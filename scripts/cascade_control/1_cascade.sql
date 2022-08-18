-- allocation
alter table allocation
    add constraint allocation_deployment_proc_id_fkey
        foreign key (deployment_proc_id) references deployment_proc
            on update cascade;

-- build
alter table build
    add constraint build_service_id_fkey
        foreign key (service_id) references service
            on update cascade;

-- release
alter table release
    add constraint release_build_id_fkey
        foreign key (build_id) references build
            on update cascade;


alter table release
    add constraint release_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;


-- deployment
alter table deployment
    add constraint deployment_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target
            on update cascade;

alter table deployment
    add constraint deployment_current_release_id_fkey
        foreign key (current_release_id) references release
            on update cascade;

alter table deployment
    add constraint deployment_service_id_fkey
        foreign key (service_id) references service
            on update cascade;


-- deployment_config
alter table deployment_config
    add constraint deployment_config_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- deployment_target
alter table deployment_target
    add constraint deployment_target_partition_id_fkey
        foreign key (partition_id) references partition
            on update cascade;


alter table deployment_target
    add constraint deployment_target_deployment_target_type_id_fkey
        foreign key (deployment_target_type_id) references deployment_target_type
            on update cascade;


-- deployment_proc
alter table deployment_proc
    add constraint deployment_proc_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- deployments_zones

alter table deployments_zones
    add constraint deployments_zones_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;


alter table deployments_zones
    add constraint deployments_zones_zone_id_fkey
        foreign key (zone_id) references zone
            on update cascade;

-- fleet

alter table fleet
    add constraint fleet_deployment_target_id_fkey
        foreign key (deployment_target_id) references deployment_target
            on update cascade;

-- network

alter table network
    add constraint network_partition_id_fkey
        foreign key (partition_id) references partition
            on update cascade;


-- partition

alter table partition
    add constraint partition_region_id_fkey
        foreign key (region_id) references region
            on update cascade;


-- region

alter table region
    add constraint region_provider_id_fkey
        foreign key (provider_id) references provider
            on update cascade;


-- release

alter table release
    add constraint release_deployment_id_fkey
        foreign key (deployment_id) references deployment
            on update cascade;

-- service

alter table service
    add constraint service_stack_id_fkey
        foreign key (stack_id) references stack
            on update cascade;

-- subnet

alter table subnet
    add constraint subnet_network_id_fkey
        foreign key (network_id) references network
            on update cascade;

-- subnets_fleets

alter table subnets_fleets
    add constraint subnets_fleets_fleet_id_fkey
        foreign key (fleet_id) references fleet
            on update cascade;


-- zone

alter table zone
    add constraint zone_region_id_fkey
        foreign key (region_id) references region
            on update cascade;



---- build_artifact
-- build_id

alter table build_artifact
    add constraint build_artifact_build_id_fkey
        foreign key (build_id) references build
            on update cascade;

-- input_repo_id

alter table build_artifact
    add constraint build_artifact_input_repo_id_fkey
        foreign key (input_repo_id) references repo
            on update cascade;

-- output_repo_id

alter table build_artifact
    add constraint build_artifact_output_repo_id_fkey
        foreign key (output_repo_id) references repo
            on update cascade;



---- release_artifact
-- release_id

alter table release_artifact
    add constraint release_artifact_release_id_fkey
        foreign key (release_id) references release
            on update cascade;

-- input_repo_id

alter table release_artifact
    add constraint release_artifact_input_repo_id_fkey
        foreign key (input_repo_id) references repo
            on update cascade;

-- output_repo_id

alter table release_artifact
    add constraint release_artifact_output_repo_id_fkey
        foreign key (output_repo_id) references repo
            on update cascade;