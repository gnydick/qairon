Feature: full test

  Scenario: provider hierarchy
    Given create "provider_type" "testprovider_type" via rest
    Then create provider of type "testprovider_type" with native_id "testprovider" named "testprovider" via rest
    Then create "region" "testregion" under "provider_id" "testprovider_type:testprovider" via rest
    Then create "zone" "testzone" under "region_id" "testprovider_type:testprovider:testregion" via rest
    Then create "zone" "testzone2" under "region_id" "testprovider_type:testprovider:testregion" via rest
    Then create "partition" "testpartition" under "region_id" "testprovider_type:testprovider:testregion" via rest
  Scenario: application hierarchy
    Given create "application" "testapp" via rest
    Given create "config_template" "testcfgtmpl" via rest
    Then create "stack" "teststack" under "application_id" "testapp" via rest
    Then create "service" "testservice" under "stack_id" "testapp:teststack" via rest
    Then create config for resource "service" named "testsvccfg" from template version "testcfgtype:1" can be created for "testapp:teststack:testservice" tagged "tag" via rest

  Scenario: deployment
    Given create "environment" "testenv" via rest
    And create build for "testapp:teststack:testservice" from job "123" tagged "v1.0" via rest
    And create "deployment_target_type" "k8s" via rest
    And create deployment_target "testdt" of type "k8s" for "testenv" in "testprovider_type:testprovider:testregion:testpartition" via rest
    And create deployment at "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt" for "testapp:teststack:testservice" tagged "default" with defaults "{}" at version "1" via rest
    And create config for resource "deployment" named "testdepcfg" from template version "testcfgtype:1" can be created for "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" tagged "tag" via rest

    And update "version" for "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" to "2" via rest
    When add first "zones" "testprovider_type:testprovider:testregion:testzone" on "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" via rest
    And add second "zones" "testprovider_type:testprovider:testregion:testzone2" on "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" via rest


    Then remove second "zones" "testprovider_type:testprovider:testregion:testzone2" on "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" via rest
    And remove first "zones" "testprovider_type:testprovider:testregion:testzone" on "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" via rest


    When delete "deployment_config" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default:testcfgtype:1:testdepcfg:tag" via rest
    When delete "service_config" "testapp:teststack:testservice:testcfgtype:1:testsvccfg:tag" via rest
    When delete "config_template" "testcfgtype:1" via rest

    Then delete "deployment" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt:testapp:teststack:testservice:default" via rest
    Then delete "deployment_target" "testprovider_type:testprovider:testregion:testpartition:testenv:k8s:testdt" via rest
    Then delete "environment" "testenv" via rest
    Then delete "zone" "testprovider_type:testprovider:testregion:testzone" via rest
    Then delete "zone" "testprovider_type:testprovider:testregion:testzone2" via rest
    Then delete "partition" "testprovider_type:testprovider:testregion:testpartition" via rest
    Then delete "region" "testprovider_type:testprovider:testregion" via rest
    Then delete "provider" "testprovider_type:testprovider" via rest
    And delete "build" "testapp:teststack:testservice:123" via rest
    And delete "service" "testapp:teststack:testservice" via rest
    And delete "stack" "testapp:teststack" via rest
    And delete "application" "testapp" via rest
