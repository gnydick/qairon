# Test index — Deployment schedule (T21–T31)
#
# T21 — Release lookup returns None when no releases exist
#   Data: empty DeploymentSchedule (no timelines, no windows); lookup for content/posts/prod/us-east-1
#   Relationship: get_active_release_id with no timeline entries for the key must return None
#   Passes when: method returns None for an unknown (stack, service, env, region) key
#   Fails when: method returns a default or placeholder release; KeyError propagates instead of None
#   False success risk: method returns None due to an unhandled exception being swallowed
#   False failure risk: hard — None is exact; only breaks if method changes return contract
#
# T22 — Release lookup returns None before any releases are created
#   Data: one release at 2025-06-01, lookup timestamp 2025-01-01 (5 months before)
#   Relationship: binary search must find no release with created_at ≤ timestamp; all releases
#                 are in the future relative to the query time
#   Passes when: method returns None (no release active yet at that timestamp)
#   Fails when: binary search off-by-one returns the post-timestamp release; inclusive vs
#               exclusive boundary wrong (≤ vs <); list not sorted before search
#   False success risk: returns None because datetime comparison fails silently (naive vs aware
#                       mismatch) — test passes but for the wrong reason
#   False failure risk: timezone offset causes 2025-06-01T00:00:00+00:00 to compare differently
#                       than expected naive datetime
#
# T23 — Release lookup returns the active release after creation
#   Data: one release at 2025-06-01 with id "release-1"; lookup at 2025-07-01 (after)
#   Relationship: single entry in timeline; binary search must return that entry
#   Passes when: method returns "release-1"
#   Fails when: binary search skips single-element list; tuple index wrong (returns created_at
#               instead of release_id); key mismatch between insert and lookup
#   False success risk: method always returns the last inserted release regardless of timestamp
#   False failure risk: timeline key tuple order differs between set and get
#
# T24 — Release lookup returns the most recent release before the timestamp
#   Data: release-1 at 2025-03-01, release-2 at 2025-06-01; lookup at 2025-07-01
#   Relationship: binary search must find the greatest created_at ≤ timestamp; release-2 wins
#   Passes when: method returns "release-2"
#   Fails when: binary search returns first match rather than last; list is unsorted;
#               result index wrong (returns build_num instead of release_id)
#   False success risk: method always returns last element — passes T24 but fails T25
#   False failure risk: timeline entries in wrong order (not sorted by created_at)
#
# T25 — Release lookup selects the correct release between two releases
#   Data: same two releases as T24; lookup at 2025-04-15 (between release-1 and release-2)
#   Relationship: only release-1 has created_at ≤ 2025-04-15; release-2 is in the future
#   Passes when: method returns "release-1" (not release-2)
#   Fails when: binary search returns release-2 (boundary condition off by direction);
#               "most recent before" logic selects wrong half of the list
#   False success risk: method returns "release-1" because it happens to be first and binary
#                       search implementation is broken but gets lucky on this input
#   False failure risk: same timezone sensitivity as T22/T23
#
# T26 — Deployment window lookup returns None when no windows exist
#   Data: empty DeploymentSchedule; window lookup for content/posts/prod/us-east-1
#   Relationship: get_active_deployment_window with no window entries for the key returns None
#   Passes when: method returns None
#   Fails when: method returns a default window; exception swallowed and returns None for wrong reason
#   False success risk: returns None due to silent KeyError rather than correct "no windows" path
#   False failure risk: hard
#
# T27 — Deployment window lookup returns None when timestamp is outside all windows
#   Data: one window 10:00–10:15; lookup at 09:00 (one hour before start)
#   Relationship: timestamp < window.start_time → no window active; binary search must not
#                 return the future window
#   Passes when: method returns None
#   Fails when: binary search returns window regardless of timestamp; start_time comparison
#               uses wrong operator (< vs ≤); timezone naive/aware mismatch causes wrong comparison
#   False success risk: returns None because window key lookup fails silently (wrong key format)
#                       — test passes but window lookup is broken for all timestamps
#   False failure risk: timezone offset causes 09:00+00:00 to appear inside the window
#
# T28 — Deployment window lookup returns window when timestamp is within it
#   Data: one window 10:00–10:15; lookup at 10:07 (7 minutes in)
#   Relationship: start_time ≤ timestamp ≤ end_time → window is active
#   Passes when: method returns the DeploymentWindow object
#   Fails when: binary search misses the window; boundary comparison off; key mismatch
#   False success risk: method returns first window unconditionally regardless of timestamp
#   False failure risk: timezone handling causes 10:07 to miss the window
#
# T29 — Active deployment window has throughput degradation below 1.0
#   Data: window with throughput_factor=0.75, latency_multiplier=1.35, error_rate_boost=0.03
#   Relationship: DeploymentWindow fields must satisfy throughput_factor<1.0,
#                 latency_multiplier>1.0, error_rate_boost>0.0
#   Passes when: all three inequalities hold on the returned window
#   Fails when: window fields swapped during construction; values at boundary (exactly 1.0, 0.0);
#               window returned is not the one constructed in the test helper
#   False success risk: weak — any values satisfying the inequalities pass; test helper
#                       hardcodes valid values so the test always reflects the fixture not the
#                       generator's actual range; a generator producing throughput_factor=0.99
#                       would pass even if semantically wrong
#   False failure risk: _make_window helper values changed to be at or outside boundary
#
# T30 — Deployment schedule serialization round-trip preserves release lookups
#   Data: schedule with one release; serialize via to_serializable(); deserialize via
#         from_serializable(); re-run same lookup
#   Relationship: release timeline must survive JSON-compatible dict encoding and decoding;
#                 datetime isoformat must round-trip; tuple key must survive string join/split
#   Passes when: lookup after round-trip returns the same release_id as before
#   Fails when: datetime loses timezone on isoformat; tuple key separator "|" appears in a
#               component (e.g., region name contains "|"); release_id lost in serialization;
#               from_serializable uses wrong index in the deserialized tuple
#   False success risk: release found for wrong reason (fallback or different matching key)
#   False failure risk: Python version differences in isoformat output (Z vs +00:00 suffix)
#
# T31 — Deployment schedule serialization round-trip preserves deployment windows
#   Data: schedule with one window; serialize/deserialize; re-run same window lookup
#   Relationship: all DeploymentWindow fields must survive dict encoding/decoding; start_time
#                 and end_time must parse back to datetime correctly for binary search to work
#   Passes when: window lookup returns a window object after round-trip
#   Fails when: start_time/end_time lost or misformatted; window key reconstruction wrong;
#               any required window field missing from the serialized dict
#   False success risk: window found but with wrong properties (e.g., zeroed latency_multiplier)
#                       — T29 would catch property correctness if run after round-trip, but T31
#                       only checks presence
#   False failure risk: same datetime isoformat sensitivity as T30

Feature: Deployment schedule

  # T21
  Scenario: release lookup returns None when no releases exist
    Given an empty deployment schedule
    When looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-07-01T12:00:00"
    Then no active release is found

  # T22
  Scenario: release lookup returns None before any releases are created
    Given a deployment schedule with a release for "content" "posts" in "prod" "us-east-1" created at "2025-06-01T00:00:00" with id "release-1"
    When looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-01-01T00:00:00"
    Then no active release is found

  # T23
  Scenario: release lookup returns the active release after creation
    Given a deployment schedule with a release for "content" "posts" in "prod" "us-east-1" created at "2025-06-01T00:00:00" with id "release-1"
    When looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-07-01T12:00:00"
    Then the active release id is "release-1"

  # T24
  Scenario: release lookup returns the most recent release before the timestamp
    Given a deployment schedule with a release for "content" "posts" in "prod" "us-east-1" created at "2025-03-01T00:00:00" with id "release-1"
    And a release for "content" "posts" in "prod" "us-east-1" created at "2025-06-01T00:00:00" with id "release-2"
    When looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-07-01T12:00:00"
    Then the active release id is "release-2"

  # T25
  Scenario: release lookup selects the correct release between two releases
    Given a deployment schedule with a release for "content" "posts" in "prod" "us-east-1" created at "2025-03-01T00:00:00" with id "release-1"
    And a release for "content" "posts" in "prod" "us-east-1" created at "2025-06-01T00:00:00" with id "release-2"
    When looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-04-15T00:00:00"
    Then the active release id is "release-1"

  # T26
  Scenario: deployment window lookup returns None when no windows exist
    Given an empty deployment schedule
    When checking for a deployment window for "content" "posts" in "prod" "us-east-1" at "2025-06-01T10:07:00"
    Then no deployment window is active

  # T27
  Scenario: deployment window lookup returns None when timestamp is outside all windows
    Given a deployment schedule with a deployment window for "content" "posts" in "prod" "us-east-1" from "2025-06-01T10:00:00" to "2025-06-01T10:15:00"
    When checking for a deployment window for "content" "posts" in "prod" "us-east-1" at "2025-06-01T09:00:00"
    Then no deployment window is active

  # T28
  Scenario: deployment window lookup returns window when timestamp is within it
    Given a deployment schedule with a deployment window for "content" "posts" in "prod" "us-east-1" from "2025-06-01T10:00:00" to "2025-06-01T10:15:00"
    When checking for a deployment window for "content" "posts" in "prod" "us-east-1" at "2025-06-01T10:07:00"
    Then a deployment window is active

  # T29
  Scenario: active deployment window has throughput degradation below 1.0
    Given a deployment schedule with a deployment window for "content" "posts" in "prod" "us-east-1" from "2025-06-01T10:00:00" to "2025-06-01T10:15:00"
    When checking for a deployment window for "content" "posts" in "prod" "us-east-1" at "2025-06-01T10:07:00"
    Then the deployment window throughput_factor is less than 1.0
    And the deployment window latency_multiplier is greater than 1.0
    And the deployment window error_rate_boost is greater than 0.0

  # T30
  Scenario: deployment schedule serialization round-trip preserves release lookups
    Given a deployment schedule with a release for "content" "posts" in "prod" "us-east-1" created at "2025-06-01T00:00:00" with id "release-1"
    When the schedule is serialized and deserialized
    Then looking up the active release for "content" "posts" in "prod" "us-east-1" at "2025-07-01T12:00:00" returns "release-1"

  # T31
  Scenario: deployment schedule serialization round-trip preserves deployment windows
    Given a deployment schedule with a deployment window for "content" "posts" in "prod" "us-east-1" from "2025-06-01T10:00:00" to "2025-06-01T10:15:00"
    When the schedule is serialized and deserialized
    Then a deployment window is active for "content" "posts" in "prod" "us-east-1" at "2025-06-01T10:07:00"
