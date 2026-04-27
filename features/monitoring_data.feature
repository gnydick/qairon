# Test index — Child span generation (T1–T7)
#
# T1 — Leaf service with no dependencies produces no child spans
#   Data: root event for social:notifications:preferences (absent from SERVICE_DEPENDENCIES)
#   Relationship: service_key built from application:stack:service fields → SERVICE_DEPENDENCIES lookup
#   Passes when: SERVICE_DEPENDENCIES.get(service_key) returns [] or is missing; result list is empty
#   Fails when: service is later added to SERVICE_DEPENDENCIES; service_key is accidentally
#               constructed to match a different service that does have dependencies
#   False success risk: function raises internally (KeyError on wrong field names) and returns []
#                       as a side effect — test passes but no spans ever get generated for anyone
#   False failure risk: none — asserting absence is robust; only breaks on legitimate behavior change
#
# T2 — Service with dependencies produces child spans
#   Data: root event for social:feed:ranking; SERVICE_DEPENDENCIES["social:feed:ranking"] = ["social:discovery:interests"]
#   Relationship: one-level dependency expansion; child span service/stack/application match dep entry
#   Passes when: at least one child span exists with application=social, stack=discovery, service=interests
#   Fails when: SERVICE_DEPENDENCIES entry removed or renamed; service_key field names wrong (the
#               pre-fix bug); select_release_func returns malformed release_id
#   False success risk: a span exists in the output for social:discovery:interests but was generated
#                       for wrong reasons (e.g., defaults or copy-paste error in caller)
#   False failure risk: dep service_id format in SERVICE_DEPENDENCIES changes casing or separator
#
# T3 — Deep dependency tree is fully expanded
#   Data: root event for social:feed:timeline; full SERVICE_DEPENDENCIES graph with multi-level paths
#         (e.g., timeline→content:posts→content:media, timeline→feed:fanout→social:connections)
#   Relationship: recursive expansion — each child must also expand its own SERVICE_DEPENDENCIES entry
#   Passes when: services at depth ≥2 (content:media, content:hashtags, social:connections,
#                social:search:indexer, social:discovery:interests) all appear in the flat output list
#   Fails when: recursion is not implemented (one-level only); visited set blocks legitimate paths;
#               service_key field names wrong; select_release_func raises for any dep service
#   False success risk: mitigated — lineage assertions ("X is a child of Y") verify actual
#                       parent_span_id linkage for content:media→posts, interests→ranking,
#                       connections→fanout; a flat 1-level expansion cannot satisfy these
#   False failure risk: SERVICE_DEPENDENCIES graph is modified; any dep service removed or renamed
#
# T4 — All spans in a trace share the root trace_id
#   Data: root event with trace_id='a'*32; all generated child spans
#   Relationship: trace_id must be propagated unchanged from root → every descendant span
#   Passes when: every span in child_spans has trace_id equal to the root's trace_id
#   Fails when: any level of recursion creates a new trace_id instead of inheriting; child_event
#               dict omits trace_id key; trace_id is overwritten somewhere in the recursion
#   False success risk: all spans have the same trace_id but it is not the root's (e.g., all
#                       hardcoded to a constant) — unlikely with current code but possible after refactor
#   False failure risk: trace_id field renamed in the event dict schema
#
# T5 — Every span links to a valid parent via parent_span_id
#   Data: root event plus all generated child spans; lookup dict keyed by span_id
#   Relationship: every child's parent_span_id must equal the span_id of some known span
#                 (root or another child)
#   Passes when: no span has a dangling parent_span_id (one that matches no span in the tree)
#   Fails when: recursive call passes wrong parent_event (passes root instead of immediate parent);
#               span_id not stored on child_event before recursing; parent_span_id field omitted
#   False success risk: if only root and first-level spans are generated and they all link correctly,
#                       the test passes even if deeper recursion is broken (but T3 would catch that)
#   False failure risk: span_id or parent_span_id field renamed
#
# T6 — The same service can appear under multiple parents (diamond pattern)
#   Data: root event for social:content:reactions; SERVICE_DEPENDENCIES has reactions→[posts, comments]
#         and comments→[posts], so posts is reachable via two paths
#   Relationship: per-branch visited set (immutable union) allows same service under different parents;
#                 a global visited set would incorrectly block second occurrence
#   Passes when: social:content:posts appears at least twice in child_spans
#   Fails when: visited is mutated globally (set.add instead of set | {key}); recursion not
#               implemented; reactions has no deps in SERVICE_DEPENDENCIES
#   False success risk: hard — two occurrences requires genuinely being generated twice
#   False failure risk: SERVICE_DEPENDENCIES changes so posts is only reachable once from reactions
#
# T7 — A blamed child is marked as the error originator
#   Data: root event with error_info.error_source set to deployment_id of social:content:posts;
#         fake_release returns deterministic release_id so deployment_id is predictable
#   Relationship: parent_error_source == child_deployment_id triggers parent_blames_child=True;
#                 blamed child gets error_source=None (it is the originator, not propagating further)
#   Passes when: the first social:content:posts span has success=False and error_info.error_source=None
#   Fails when: deployment_id_from_release_id strips wrong component (release_id mismatch);
#               fake_release returns different release_id than expected; blamed child not found;
#               error_info not set on child; error_source not set to None (set to something else)
#   False success risk: mitigated — step searches ALL posts spans for one with both success=False
#                       AND error_source=None; positional ordering is not relied upon
#   False failure risk: deployment_id format changes (e.g., separator or component order)

Feature: Monitoring data child span generation

  Background:
    Given a predictable release selector

  # T1
  Scenario: leaf service with no dependencies produces no child spans
    Given a root event for service "social:notifications:preferences"
    When child spans are generated
    Then no child spans are produced

  # T2
  Scenario: service with dependencies produces child spans
    Given a root event for service "social:feed:ranking"
    When child spans are generated
    Then child spans are produced
    And a span exists for service "social:discovery:interests"

  # T3
  Scenario: deep dependency tree is fully expanded
    Given a root event for service "social:feed:timeline"
    When child spans are generated
    Then a span exists for service "social:feed:ranking"
    And a span exists for service "social:discovery:interests"
    And a span exists for service "social:content:posts"
    And a span exists for service "social:content:media"
    And a span exists for service "social:content:hashtags"
    And a span exists for service "social:feed:fanout"
    And a span exists for service "social:social:connections"
    And a span exists for service "social:search:indexer"
    And the span for "social:content:media" is a child of "social:content:posts"
    And the span for "social:discovery:interests" is a child of "social:feed:ranking"
    And the span for "social:social:connections" is a child of "social:feed:fanout"

  # T4
  Scenario: all spans in a trace share the root trace_id
    Given a root event for service "social:feed:timeline"
    When child spans are generated
    Then every span has the root trace_id

  # T5
  Scenario: every span links to a valid parent via parent_span_id
    Given a root event for service "social:feed:timeline"
    When child spans are generated
    Then every span has a parent_span_id that matches a known span_id

  # T6
  Scenario: the same service can appear under multiple parents (diamond pattern)
    Given a root event for service "social:content:reactions"
    When child spans are generated
    Then "social:content:posts" appears more than once

  # T7
  Scenario: a blamed child is marked as the error originator
    Given a root event for service "social:feed:timeline"
    And the root event blames "social:content:posts" for its error
    When child spans are generated
    Then a blamed span exists for "social:content:posts"