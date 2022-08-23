alter table allocation
    add constraint allocation_allocation_type_id_fkey
        FOREIGN KEY (allocation_type_id) REFERENCES allocation_type(id)
            on update cascade;
alter table allocation
    add constraint allocation_deployment_proc_id_fkey
        FOREIGN KEY (deployment_proc_id) REFERENCES deployment_proc(id)
            on update cascade;
alter table build
    add constraint build_service_id_fkey
        FOREIGN KEY (service_id) REFERENCES service(id)
            on update cascade;
alter table build_artifact
    add constraint build_artifact_output_repo_id_fkey
        FOREIGN KEY (output_repo_id) REFERENCES repo(id)
            on update cascade;
alter table build_artifact
    add constraint build_artifact_build_id_fkey
        FOREIGN KEY (build_id) REFERENCES build(id)
            on update cascade;
alter table build_artifact
    add constraint build_artifact_input_repo_id_fkey
        FOREIGN KEY (input_repo_id) REFERENCES repo(id)
            on update cascade;
alter table capacity
    add constraint capacity_allocation_type_id_fkey
        FOREIGN KEY (allocation_type_id) REFERENCES allocation_type(id)
            on update cascade;
alter table capacity
    add constraint capacity_fleet_id_fkey
        FOREIGN KEY (fleet_id) REFERENCES fleet(id)
            on update cascade;
alter table config_template
    add constraint config_template_language_id_fkey
        FOREIGN KEY (language_id) REFERENCES language(id)
            on update cascade;
alter table deployment
    add constraint deployment_service_id_fkey
        FOREIGN KEY (service_id) REFERENCES service(id)
            on update cascade;
alter table deployment
    add constraint deployment_deployment_target_bin_id_fkey
        FOREIGN KEY (deployment_target_bin_id) REFERENCES deployment_target_bin(id)
            on update cascade;
alter table deployment
    add constraint deployment_current_release_id_fkey
        FOREIGN KEY (current_release_id) REFERENCES release(id)
            on update cascade;
alter table deployment_config
    add constraint deployment_config_deployment_id_fkey
        FOREIGN KEY (deployment_id) REFERENCES deployment(id)
            on update cascade;
alter table deployment_config
    add constraint deployment_config_config_template_id_fkey
        FOREIGN KEY (config_template_id) REFERENCES config_template(id)
            on update cascade;
alter table deployment_proc
    add constraint deployment_proc_deployment_id_fkey
        FOREIGN KEY (deployment_id) REFERENCES deployment(id)
            on update cascade;
alter table deployment_proc
    add constraint deployment_proc_proc_id_fkey
        FOREIGN KEY (proc_id) REFERENCES proc(id)
            on update cascade;
alter table deployments_zones
    add constraint deployments_zones_deployment_id_fkey
        FOREIGN KEY (deployment_id) REFERENCES deployment(id)
            on update cascade;
alter table deployments_zones
    add constraint deployments_zones_zone_id_fkey
        FOREIGN KEY (zone_id) REFERENCES zone(id)
            on update cascade;
alter table deployment_target
    add constraint deployment_target_partition_id_fkey
        FOREIGN KEY (partition_id) REFERENCES partition(id)
            on update cascade;
alter table deployment_target
    add constraint deployment_target_deployment_target_type_id_fkey
        FOREIGN KEY (deployment_target_type_id) REFERENCES deployment_target_type(id)
            on update cascade;
alter table deployment_target_bin
    add constraint deployment_target_bin_deployment_target_id_fkey
        FOREIGN KEY (deployment_target_id) REFERENCES deployment_target(id)
            on update cascade;
alter table fleet
    add constraint fleet_deployment_target_id_fkey
        FOREIGN KEY (deployment_target_id) REFERENCES deployment_target(id)
            on update cascade;
alter table fleet
    add constraint fleet_fleet_type_id_fkey
        FOREIGN KEY (fleet_type_id) REFERENCES fleet_type(id)
            on update cascade;
alter table fleet_type
    add constraint fleet_type_provider_type_id_fkey
        FOREIGN KEY (provider_type_id) REFERENCES provider_type(id)
            on update cascade;
alter table network
    add constraint network_partition_id_fkey
        FOREIGN KEY (partition_id) REFERENCES partition(id)
            on update cascade;
alter table partition
    add constraint partition_region_id_fkey
        FOREIGN KEY (region_id) REFERENCES region(id)
            on update cascade;
alter table proc
    add constraint proc_service_id_fkey
        FOREIGN KEY (service_id) REFERENCES service(id)
            on update cascade;
alter table provider
    add constraint provider_provider_type_id_fkey
        FOREIGN KEY (provider_type_id) REFERENCES provider_type(id)
            on update cascade;
alter table provider
    add constraint provider_environment_id_fkey
        FOREIGN KEY (environment_id) REFERENCES environment(id)
            on update cascade;
alter table region
    add constraint region_provider_id_fkey
        FOREIGN KEY (provider_id) REFERENCES provider(id)
            on update cascade;
alter table release
    add constraint release_build_id_fkey
        FOREIGN KEY (build_id) REFERENCES build(id)
            on update cascade;
alter table release
    add constraint release_deployment_id_fkey
        FOREIGN KEY (deployment_id) REFERENCES deployment(id)
            on update cascade;
alter table release_artifact
    add constraint release_artifact_input_repo_id_fkey
        FOREIGN KEY (input_repo_id) REFERENCES repo(id)
            on update cascade;
alter table release_artifact
    add constraint release_artifact_output_repo_id_fkey
        FOREIGN KEY (output_repo_id) REFERENCES repo(id)
            on update cascade;
alter table release_artifact
    add constraint release_artifact_release_id_fkey
        FOREIGN KEY (release_id) REFERENCES release(id)
            on update cascade;
alter table repo
    add constraint repo_repo_type_id_fkey
        FOREIGN KEY (repo_type_id) REFERENCES repo_type(id)
            on update cascade;
alter table service
    add constraint service_stack_id_fkey
        FOREIGN KEY (stack_id) REFERENCES stack(id)
            on update cascade;
alter table service_config
    add constraint service_config_service_id_fkey
        FOREIGN KEY (service_id) REFERENCES service(id)
            on update cascade;
alter table service_config
    add constraint service_config_config_template_id_fkey
        FOREIGN KEY (config_template_id) REFERENCES config_template(id)
            on update cascade;
alter table services_repos
    add constraint services_repos_service_id_fkey
        FOREIGN KEY (service_id) REFERENCES service(id)
            on update cascade;
alter table services_repos
    add constraint services_repos_repo_id_fkey
        FOREIGN KEY (repo_id) REFERENCES repo(id)
            on update cascade;
alter table stack
    add constraint stack_application_id_fkey
        FOREIGN KEY (application_id) REFERENCES application(id)
            on update cascade;
alter table subnet
    add constraint subnet_network_id_fkey
        FOREIGN KEY (network_id) REFERENCES network(id)
            on update cascade;
alter table subnets_fleets
    add constraint subnets_fleets_subnet_id_fkey
        FOREIGN KEY (subnet_id) REFERENCES subnet(id)
            on update cascade;
alter table subnets_fleets
    add constraint subnets_fleets_fleet_id_fkey
        FOREIGN KEY (fleet_id) REFERENCES fleet(id)
            on update cascade;
alter table target_bins_fleets
    add constraint target_bins_fleets_deployment_target_bin_id_fkey
        FOREIGN KEY (deployment_target_bin_id) REFERENCES deployment_target_bin(id)
            on update cascade;
alter table target_bins_fleets
    add constraint target_bins_fleets_fleet_id_fkey
        FOREIGN KEY (fleet_id) REFERENCES fleet(id)
            on update cascade;
alter table zone
    add constraint zone_region_id_fkey
        FOREIGN KEY (region_id) REFERENCES region(id)
            on update cascade;
