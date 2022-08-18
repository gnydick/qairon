-- allocation
alter table allocation
    drop constraint allocation_deployment_proc_id_fkey;


-- build
alter table build
    drop constraint build_service_id_fkey;


-- release
alter table release
    drop constraint release_build_id_fkey;



alter table release
    drop constraint release_deployment_id_fkey;


-- deployment
alter table deployment
    drop constraint deployment_deployment_target_id_fkey;


alter table deployment
    drop constraint deployment_current_release_id_fkey;


alter table deployment
    drop constraint deployment_service_id_fkey;


-- deployment_config
alter table deployment_config
    drop constraint deployment_config_deployment_id_fkey;


-- deployment_target
alter table deployment_target
    drop constraint deployment_target_partition_id_fkey;


alter table deployment_target
    drop constraint deployment_target_deployment_target_type_id_fkey;


-- deployment_proc
alter table deployment_proc
    drop constraint deployment_proc_deployment_id_fkey;


-- deployments_zones
alter table deployments_zones
    drop constraint deployments_zones_deployment_id_fkey;


alter table deployments_zones
    drop constraint deployments_zones_zone_id_fkey;


-- fleet
alter table fleet
    drop constraint fleet_deployment_target_id_fkey;


-- network
alter table network
    drop constraint network_partition_id_fkey;


-- partition
alter table partition
    drop constraint partition_region_id_fkey;


-- region
alter table region
    drop constraint region_provider_id_fkey;


-- release
alter table release
    drop constraint release_deployment_id_fkey;


-- service
alter table service
    drop constraint service_stack_id_fkey;


-- subnet
alter table subnet
    drop constraint subnet_network_id_fkey;


-- subnets_fleets
alter table subnets_fleets
    drop constraint subnets_fleets_fleet_id_fkey;


-- zone
alter table zone
    drop constraint zone_region_id_fkey;



---- build_artifact
-- build_id
alter table build_artifact
    drop constraint build_artifact_build_id_fkey;


-- input_repo_id
alter table build_artifact
    drop constraint build_artifact_input_repo_id_fkey;


-- output_repo_id
alter table build_artifact
    drop constraint build_artifact_output_repo_id_fkey;



---- release_artifact
-- release_id
alter table release_artifact
    drop constraint release_artifact_release_id_fkey;


-- input_repo_id
alter table release_artifact
    drop constraint release_artifact_input_repo_id_fkey;


-- output_repo_id
alter table release_artifact
    drop constraint release_artifact_output_repo_id_fkey;

