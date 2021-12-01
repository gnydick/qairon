Feature: full test

  Scenario: provider hierarchy
    Given create "environment" "testenv" via rest
    Given create "provider_type" "testprovider_type" via rest
    Then create provider in env "testenv" of type "testprovider_type" with native_id "testprovider" via rest
    Then create "region" "testregion" under "provider_id" "testenv:testprovider_type:testprovider" via rest
    Then create "zone" "testzone" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
    Then create "zone" "testzone2" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
    Then create "partition" "testpartition" under "region_id" "testenv:testprovider_type:testprovider:testregion" via rest
  Scenario: application hierarchy
    Given create "application" "testapp" via rest
    Given create "language" "json" via rest
    Then create textresource "config_template" "testcfgtmpl" under "language_id" "json" with doc "{}" via rest
    Then create "stack" "teststack" under "application_id" "testapp" via rest
    Then create "service" "testservice" under "stack_id" "testapp:teststack" via rest
    Then create config for resource "service" named "testsvccfg" from template "testcfgtmpl" can be created for "testapp:teststack:testservice" tagged "tag" via rest

  Scenario: deployment
    Given create build for "testapp:teststack:testservice" from job "123" tagged "v1.0" build args "default" via rest
    And create "deployment_target_type" "k8s" via rest
    And create deployment_target "testdt" of type "k8s" in "testenv:testprovider_type:testprovider:testregion:testpartition" via rest

    And create deployment at "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" for "testapp:teststack:testservice" tagged "default" with defaults "{}" via rest
    Then create config for resource "deployment" named "testdepcfg" from template "testcfgtmpl" can be created for "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" tagged "tag" via rest
    
    When add first "zones" "testenv:testprovider_type:testprovider:testregion:testzone" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    And add second "zones" "testenv:testprovider_type:testprovider:testregion:testzone2" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest


    Then remove second "zones" "testenv:testprovider_type:testprovider:testregion:testzone2" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    And remove first "zones" "testenv:testprovider_type:testprovider:testregion:testzone" on "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest


    When delete "deployment_config" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default:testcfgtmpl:testdepcfg:tag" via rest
    When delete "service_config" "testapp:teststack:testservice:testcfgtmpl:testsvccfg:tag" via rest
    When delete "config_template" "testcfgtmpl" via rest

    Then delete "deployment" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt:testapp:teststack:testservice:default" via rest
    Then delete "deployment_target" "testenv:testprovider_type:testprovider:testregion:testpartition:k8s:testdt" via rest
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone" via rest
    Then delete "zone" "testenv:testprovider_type:testprovider:testregion:testzone2" via rest
    Then delete "partition" "testenv:testprovider_type:testprovider:testregion:testpartition" via rest
    Then delete "region" "testenv:testprovider_type:testprovider:testregion" via rest
    Then delete "provider" "testenv:testprovider_type:testprovider" via rest
    And delete "build" "testapp:teststack:testservice:123" via rest
    And delete "service" "testapp:teststack:testservice" via rest
    And delete "stack" "testapp:teststack" via rest
    And delete "application" "testapp" via rest
    Then delete "environment" "testenv" via rest
