# Test index — Tab completion (T32–T37)
#
# T32 — unassign_zone completer returns only assigned zones
#   Data: deployment with zone1 and zone2 assigned; zone3 exists but is not assigned
#   Relationship: deployment_zones_completer scopes results to zones currently on the deployment
#   Passes when: zone1 and zone2 appear; zone3 does not
#   Fails when: completer returns all zones regardless of assignment; owner_id not parsed from args;
#               /deployment/{id}/zones endpoint returns wrong data
#   False success risk: zone3 happens to be filtered by prefix match rather than assignment filter
#   False failure risk: zone IDs change format; owner_id not set in parsed_args at completion time
#
# T33 — unassign_zone completer filters by prefix
#   Data: same three zones; prefix is the start of zone1's id
#   Relationship: prefix narrows the set further within the already-scoped assignment filter
#   Passes when: only zone1 appears (matches prefix and is assigned); zone2 absent (assigned but
#               wrong prefix); zone3 absent (unassigned)
#   Fails when: prefix filtering not applied; all assigned zones returned regardless of prefix
#   False success risk: zone2 also starts with the same prefix characters
#   False failure risk: prefix comparison is case-sensitive but IDs are stored differently
#
# T34 — assign_zone completer returns all zones including already-assigned
#   Data: same three zones; zone1 and zone2 assigned
#   Relationship: zone_completer is not scoped to a deployment — it returns all zone IDs;
#                 this is by design (the API allows re-assigning an already-assigned zone)
#   Passes when: zone1, zone2, and zone3 all appear in completions
#   Fails when: completer incorrectly filters out already-assigned zones
#   False success risk: hard — requires all three to appear
#   False failure risk: zone IDs returned in unexpected format
#
# T35 — unassign_repo completer returns only assigned repos
#   Data: service with repo1 and repo2 assigned; repo3 exists but is not assigned
#   Relationship: service_repos_completer scopes results to repos on /service/{id}/repos
#   Passes when: repo1 and repo2 appear; repo3 does not
#   Fails when: completer returns all repos; owner_id not parsed; endpoint returns wrong data
#   False success risk: same as T32
#   False failure risk: same as T32
#
# T36 — unassign_repo completer filters by prefix
#   Data: same repos; prefix is the start of repo1's id
#   Relationship: same as T33 but for repo/service
#   Passes when: only repo1 appears
#   Fails when: prefix not applied; all assigned repos returned
#   False success risk: repo2 starts with the same prefix
#   False failure risk: same as T33
#
# T37 — assign_repo completer returns all repos including already-assigned
#   Data: same repos; repo1 and repo2 assigned
#   Relationship: repo_completer is not scoped — returns all repos
#   Passes when: repo1, repo2, and repo3 all appear
#   Fails when: already-assigned repos filtered out
#   False success risk: hard
#   False failure risk: same as T34

@db
Feature: Tab completion

  Scenario: setup fixtures
    Given a live environment for tab completion tests
    And a deployment with zones "tczone1" and "tczone2" assigned and "tczone3" unassigned
    And a service with repos "tcrepo1" and "tcrepo2" assigned and "tcrepo3" unassigned

  # T32
  Scenario: unassign_zone completer returns only assigned zones
    When tab-completing "qcli deployment unassign_zone tcenv:tcptype:tcprov:tcregion:tcpart:tck8s:tcdt:tcapp:tcstack:tcsvc:default "
    Then "tcenv:tcptype:tcprov:tcregion:tczone1" is in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone2" is in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone3" is not in completions

  # T33
  Scenario: unassign_zone completer filters by prefix
    When tab-completing "qcli deployment unassign_zone tcenv:tcptype:tcprov:tcregion:tcpart:tck8s:tcdt:tcapp:tcstack:tcsvc:default tcenv:tcptype:tcprov:tcregion:tczone1"
    Then "tcenv:tcptype:tcprov:tcregion:tczone1" is in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone2" is not in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone3" is not in completions

  # T34
  Scenario: assign_zone completer returns all zones including already-assigned
    When tab-completing "qcli deployment assign_zone tcenv:tcptype:tcprov:tcregion:tcpart:tck8s:tcdt:tcapp:tcstack:tcsvc:default "
    Then "tcenv:tcptype:tcprov:tcregion:tczone1" is in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone2" is in completions
    And "tcenv:tcptype:tcprov:tcregion:tczone3" is in completions

  # T35
  Scenario: unassign_repo completer returns only assigned repos
    When tab-completing "qcli service unassign_repo tcapp:tcstack:tcsvc "
    Then "tcrepotype:tcrepo1" is in completions
    And "tcrepotype:tcrepo2" is in completions
    And "tcrepotype:tcrepo3" is not in completions

  # T36
  Scenario: unassign_repo completer filters by prefix
    When tab-completing "qcli service unassign_repo tcapp:tcstack:tcsvc tcrepotype:tcrepo1"
    Then "tcrepotype:tcrepo1" is in completions
    And "tcrepotype:tcrepo2" is not in completions
    And "tcrepotype:tcrepo3" is not in completions

  # T37
  Scenario: assign_repo completer returns all repos including already-assigned
    When tab-completing "qcli service assign_repo tcapp:tcstack:tcsvc "
    Then "tcrepotype:tcrepo1" is in completions
    And "tcrepotype:tcrepo2" is in completions
    And "tcrepotype:tcrepo3" is in completions
