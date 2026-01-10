Feature: REST

  Scenario: provider hierarchy
    Given create "environment" "testenv" via rest
    Given create "provider_type" "testprovider_type" via rest
    Then create provider in env "testenv" of type "testprovider_type" with native_id "testprovider" via rest
    Then create "region" "testregion" under "provider_id" "testenv:testprovider_type:testprovider" via rest
    Then create "zone" "testzone" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
    Then create "zone" "testzone2" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
    Then create "partition" "testpartition" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
    Then create "cidr" "10.10.0.0/16" "network" "testnet" under "partition_id" "testenv:testprovider_type:testprovider:testregion:testpartition" via rest
    Then allocate subnet "testenv:testprovider_type:testprovider:testregion:testpartition:testnet" "12" "testsubnet0" via rest

  Scenario: application hierarchy
    Given create "application" "testapp" via rest
    Given create "language" "json" via rest
    Then create textresource "config_template" "testcfgtmpl" under "language_id" "json" with doc "{}" via rest
    Then create "stack" "teststack" under "application_id" "testapp" via rest
    Then create "service" "testservice" under "stack_id" "testapp:teststack" via rest
    Then create config for resource "service" named "testsvccfg" from template "testcfgtmpl" can be created for "testapp:teststack:testservice" tagged "tag" via rest
    Then create config for resource "stack" named "teststackcfg" from template "testcfgtmpl" can be created for "testapp:teststack" tagged "tag" via rest


  Scenario: deployment
    Given create "deployment_target_type" "k8s" via rest
    And create deployment_target "testdt" of type "k8s" in "testenv:testprovider_type:testprovider:testregion:testpartition" via rest
    Then create deployment at "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" for "testapp:teststack:testservice" tagged "default" with defaults "{}" via rest
    Then create config for resource "deployment" named "testdepcfg" from template "testcfgtmpl" can be created for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" tagged "tag" via rest

    When add first - "1" - "zone" to "zones" "testenv:testprovider_type:testprovider:testregion:testzone" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    And add second - "2" - "zone" to "zones" "testenv:testprovider_type:testprovider:testregion:testzone2" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest


  Scenario: cicd
    Given create "repo_type" "ecr" via rest
    Given create "repo_type" "helm" via rest
    Given create "repo_type" "s3" via rest
    Given create "repo_type" "git" via rest
    Then create "repo" with parent id "git" in parent field "repo_type_id" named "testsvcreposrc" via rest
    Then create "repo" with parent id "ecr" in parent field "repo_type_id" named "testsvcrepobuildartifact" via rest
    Then create "repo" with parent id "helm" in parent field "repo_type_id" named "testsvcreporeleaseartifact" via rest
    Then create build for "testapp:teststack:testservice" from job "123" tagged "v1.0" via rest
    Then create release for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" from build "testapp:teststack:testservice:123" from job "456" via rest
    Then create build_artifact for "testapp:teststack:testservice:123" from "git:testsvcreposrc" uploaded to "ecr:testsvcrepobuildartifact" named "test_build_artifact_ecr" in path "some_output_path" via rest
    Then create release_artifact for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default:456" from "ecr:testsvcrepobuildartifact" uploaded to "helm:testsvcreporeleaseartifact" named "test_release_artifact_helm" in path "some_output_path" via rest


  Scenario: cleanup
    Then remove second - "1" - "zone" from "zones" "testenv:testprovider_type:testprovider:testregion:testzone2" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    And  remove first - "0" - "zone" from "zones" "testenv:testprovider_type:testprovider:testregion:testzone" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest

    When delete "deployment_config" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default:testcfgtmpl:testdepcfg:tag" via rest
    When delete "service_config" "testapp:teststack:testservice:testcfgtmpl:testsvccfg:tag" via rest
    When delete "stack_config" "testapp:teststack:testcfgtmpl:teststackcfg:tag" via rest
    When delete "config_template" "testcfgtmpl" via rest

    Then delete "release_artifact" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default:456:test_release_artifact_helm" via rest
    Then delete "release" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default:456" via rest
    Then delete "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    Then delete "deployment_target" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" via rest
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone" via rest
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone2" via rest
    Then delete "subnet" "testenv:testprovider_type:testprovider:testregion:testpartition:testnet:testsubnet0" via rest
    Then delete "network" "testenv:testprovider_type:testprovider:testregion:testpartition:testnet" via rest
    Then delete "partition" "testenv:testprovider_type:testprovider:testregion:testpartition" via rest
    Then delete "region" "testenv:testprovider_type:testprovider:testregion" via rest
    Then delete "provider" "testenv:testprovider_type:testprovider" via rest
    And delete "build_artifact" "testapp:teststack:testservice:123:test_build_artifact_ecr" via rest
    And delete "build" "testapp:teststack:testservice:123" via rest
    And delete "service" "testapp:teststack:testservice" via rest
    And delete "stack" "testapp:teststack" via rest
    And delete "application" "testapp" via rest
    Then delete "environment" "testenv" via rest
    Then delete "repo" "ecr:testsvcrepobuildartifact" via rest
    Then delete "repo" "git:testsvcreposrc" via rest
    Then delete "repo" "helm:testsvcreporeleaseartifact" via rest
