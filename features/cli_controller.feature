Feature: CLI

  Scenario: provider hierarchy
    Given create "environment" "testenv" via cli
    Given create "provider_type" "testprovider_type" via cli
    Then create provider in env "testenv" of type "testprovider_type" with native_id "testprovider" via cli
    Then create "region" "testregion" under "provider_id" "testenv:testprovider_type:testprovider" via cli
    Then create "zone" "testzone" under "region_id" "testenv:testprovider_type:testprovider:testregion" via cli
    Then create "zone" "testzone2" under "region_id" "testenv:testprovider_type:testprovider:testregion" via cli
    Then create "partition" "testpartition" under "region_id" "testenv:testprovider_type:testprovider:testregion" via cli
    Then create "cidr" "10.10.0.0/16" "network" "testnet" under "partition_id" "testenv:testprovider_type:testprovider:testregion:testpartition" via cli
    Then allocate subnet "testenv:testprovider_type:testprovider:testregion:testpartition:testnet" from vpc_cidr "10.10.0.0/16" with "12" additional bits named "testsubnet0" via cli

  Scenario: application hierarchy
    Given create "application" "testapp" via cli
    Given create "language" "json" via cli
    Then create textresource "config_template" "testcfgtmpl" under "language_id" "json" with doc "{}" via cli
    Then create "stack" "teststack" under "application_id" "testapp" via cli
    Then create "service" "testservice" under "stack_id" "testapp:teststack" via cli
    Then create config for resource "service" named "testsvccfg" from template "testcfgtmpl" can be created for "testapp:teststack:testservice" tagged "tag" via cli
    Then create config for resource "stack" named "teststackcfg" from template "testcfgtmpl" can be created for "testapp:teststack" tagged "tag" via cli


  Scenario: deployment
    Given create "deployment_target_type" "k8s" via cli
    And create deployment_target "testdt" of type "k8s" in "testenv:testprovider_type:testprovider:testregion:testpartition" via cli
    Then create "deployment_target_bin" with parent id "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" in parent field "deployment_target_id" named "bin0" via cli
    Then create deployment at "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0" for "testapp:teststack:testservice" tagged "default" with defaults "{}" via cli
    Then create config for resource "deployment" named "testdepcfg" from template "testcfgtmpl" can be created for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default" tagged "tag" via cli


  Scenario: cicd
    Given create "repo_type" "ecr" via cli
    Given create "repo_type" "helm" via cli
    Given create "repo_type" "s3" via cli
    Given create "repo_type" "git" via cli
    Then create "repo" with parent id "git" in parent field "repo_type_id" named "testsvcreposrc" via cli
    Then create "repo" with parent id "ecr" in parent field "repo_type_id" named "testsvcrepobuildartifact" via cli
    Then create "repo" with parent id "helm" in parent field "repo_type_id" named "testsvcreporeleaseartifact" via cli
    Then create build for "testapp:teststack:testservice" from job "123" tagged "v1.0" via cli
    Then create release for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default" from build "testapp:teststack:testservice:123" from job "456" via cli
    Then create build_artifact for "testapp:teststack:testservice:123" from "git:testsvcreposrc" uploaded to "ecr:testsvcrepobuildartifact" named "test_build_artifact_ecr" in path "some_output_path" via cli
    Then create release_artifact for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default:456" from "ecr:testsvcrepobuildartifact" uploaded to "helm:testsvcreporeleaseartifact" named "test_release_artifact_helm" in path "some_output_path" via cli


  Scenario: cleanup
    Then delete "deployment_config" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default:testcfgtmpl:testdepcfg:tag" via cli
    When delete "service_config" "testapp:teststack:testservice:testcfgtmpl:testsvccfg:tag" via cli
    When delete "stack_config" "testapp:teststack:testcfgtmpl:teststackcfg:tag" via cli
    When delete "config_template" "testcfgtmpl" via cli

    Then delete "release_artifact" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default:456:test_release_artifact_helm" via cli
    Then delete "release" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default:456" via cli
    Then delete "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0:testapp:teststack:testservice:default" via cli
    Then delete "deployment_target_bin" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:bin0" via cli
    Then delete "deployment_target" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" via cli
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone" via cli
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone2" via cli
    Then delete "subnet" "testenv:testprovider_type:testprovider:testregion:testpartition:testnet:testsubnet0" via cli
    Then delete "network" "testenv:testprovider_type:testprovider:testregion:testpartition:testnet" via cli
    Then delete "partition" "testenv:testprovider_type:testprovider:testregion:testpartition" via cli
    Then delete "region" "testenv:testprovider_type:testprovider:testregion" via cli
    Then delete "provider" "testenv:testprovider_type:testprovider" via cli
    And delete "build_artifact" "testapp:teststack:testservice:123:test_build_artifact_ecr" via cli
    And delete "build" "testapp:teststack:testservice:123" via cli
    And delete "service" "testapp:teststack:testservice" via cli
    And delete "stack" "testapp:teststack" via cli
    And delete "application" "testapp" via cli
    Then delete "environment" "testenv" via cli
    Then delete "repo" "ecr:testsvcrepobuildartifact" via cli
    Then delete "repo" "git:testsvcreposrc" via cli
    Then delete "repo" "helm:testsvcreporeleaseartifact" via cli
