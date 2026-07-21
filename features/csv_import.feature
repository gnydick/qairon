Feature: CSV Import

  Scenario: Import applications from CSV
    Given a CSV file with applications
    When I import applications from the CSV file
    Then applications should be created successfully

  Scenario: Import with dry run
    Given a CSV file with stacks
    When I import stacks with dry run flag
    Then no stacks should be created
    And validation should succeed

  Scenario: Import with invalid CSV
    Given a CSV file with invalid data
    When I import resources from the invalid CSV
    Then import should fail with errors

  Scenario: Import hierarchical resources
    Given a CSV file with environments
    And a CSV file with providers
    When I import environments first
    And I import providers second
    Then both resources should be created in correct order
