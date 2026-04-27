# Test index — Log entry format (T8–T20)
#
# T8  — server error type → ERROR level
# T9  — database error type → ERROR level
# T10 — cache error type → ERROR level
# T11 — queue error type → ERROR level
# T12 — internal error type → ERROR level
#   Data: failed log entry with each infrastructure-class error_type
#   Relationship: error_type ∈ {"server","database","cache","queue","internal"} → level="ERROR"
#   Passes when: generate_log sets level="ERROR" for each of these types
#   Fails when: any type is omitted from the ERROR branch; type string is misspelled in either
#               the generator or the test; error_info not threaded through to level assignment
#   False success risk: generator defaults to ERROR for all failures regardless of type —
#                       T13 (client→WARN) would expose this, but only if run together
#   False failure risk: error_type string casing changes (e.g., "Server" vs "server")
#
# T13 — client error type → WARN level
#   Data: failed log entry with error_type="client"
#   Relationship: error_type="client" is the only non-ERROR failure type; everything else is ERROR
#   Passes when: generate_log sets level="WARN" for error_type="client"
#   Fails when: client errors fall through to ERROR branch; "client" not recognized;
#               level assignment logic inverted
#   False success risk: if test only runs T13 in isolation and generator happens to WARN for
#                       all failures, T8–T12 would be needed to expose that
#   False failure risk: "client" type renamed to "4xx" or similar
#
# T14 — Successful read produces INFO level with "returned data" message
#   Data: ServiceAction with is_write=False, success=True
#   Relationship: success=True + is_write=False → level="INFO", message ends with "returned data"
#   Passes when: level is INFO and the literal string "returned data" is in the message
#   Fails when: success path sets wrong level; is_write=False not detected; message template changed;
#               action name prepended to message differently than expected
#   False success risk: message accidentally contains "returned data" as part of a longer phrase
#                       in a failure message; string check is substring not full match
#   False failure risk: message template wording changes slightly (e.g., "returns data")
#
# T15 — Successful write produces INFO level with "completed successfully" message
#   Data: ServiceAction with is_write=True, success=True
#   Relationship: success=True + is_write=True → level="INFO", message ends with "completed successfully"
#   Passes when: level is INFO and "completed successfully" is in the message
#   Fails when: is_write flag not inspected; both reads and writes produce same message;
#               message template changed
#   False success risk: "completed successfully" appears in error messages for some other reason
#   False failure risk: message template wording changes slightly
#
# T16 — All required fields are present in a log entry
#   Data: successful log entry; checked fields: timestamp, level, service, stack, action,
#         user_id, request_id, success, message, release_id, trace_id, span_id
#   Relationship: LogEntry dataclass must populate all 12 fields with non-None values
#   Passes when: every field in the required list is present and not None
#   Fails when: any required field is removed from LogEntry or not populated;
#               field set to None instead of a default value; field renamed in the dataclass
#   False success risk: mitigated — string fields checked for both not-None and not-empty-string;
#                       success field checked specifically as a bool instance
#   False failure risk: field renamed (e.g., "action" → "action_name"); __dict__ lookup fails
#
# T17 — Error fields are null on success
#   Data: successful log entry; checked fields: error_code, error_message, error_source, error_type
#   Relationship: success=True must leave all error fields as None (not empty string, not "none")
#   Passes when: all four error fields are exactly None
#   Fails when: any error field is set to a non-None default on success (e.g., empty string,
#               "N/A", 0); error path accidentally runs for success case
#   False success risk: hard — None is exact; empty string or 0 would correctly fail this test
#   False failure risk: field name changes in LogEntry dataclass
#
# T18 — Error fields are populated on failure
#   Data: failed log entry with error_type="server", error_code="503", error_message="test error"
#   Relationship: error_info dict is passed to generate_log and must surface on the LogEntry
#   Passes when: log_entry.error_code=="503", log_entry.error_type=="server",
#                log_entry.error_message is not None
#   Fails when: error_info not extracted in generate_log; wrong dict key used; error_info
#               silently ignored in success/failure branching
#   False success risk: generate_log uses a hardcoded default code "503" for all server errors —
#                       test passes but the actual passed-in value is ignored
#   False failure risk: error_info key names change ("error_code" → "code")
#
# T19 — Root span has null parent_span_id
#   Data: log entry generated without parent_span_id argument (default None)
#   Relationship: omitting parent_span_id must leave the field None, not auto-assign a value
#   Passes when: log_entry.parent_span_id is exactly None
#   Fails when: generate_log auto-assigns a parent_span_id; default value changed from None;
#               field accidentally populated from some other context variable
#   False success risk: parent_span_id is set to empty string "" — test fails correctly
#   False failure risk: None default changed to a sentinel value
#
# T20 — Child span links to parent via parent_span_id
#   Data: log entry generated with parent_span_id="abcd1234abcd1234" (explicit 16-char hex)
#   Relationship: explicitly passed parent_span_id must be stored verbatim on the LogEntry
#   Passes when: log_entry.parent_span_id == "abcd1234abcd1234"
#   Fails when: generate_log ignores the passed value; field overwritten by internal logic;
#               value transformed (e.g., uppercased, truncated)
#   False success risk: hard — exact string match
#   False failure risk: field renamed; value type coerced

Feature: Log entry format

  Background:
    Given a monitoring data generator with seed 42

  # T8–T13: one scenario per Examples row
  Scenario Outline: log level is assigned by error type
    Given an action "get_post" on "social:content:posts" that is a read
    When a failed log entry is generated with error_type "<error_type>"
    Then the log level is "<expected_level>"

    Examples:
      | error_type | expected_level |
      # T8
      | server     | ERROR          |
      # T9
      | database   | ERROR          |
      # T10
      | cache      | ERROR          |
      # T11
      | queue      | ERROR          |
      # T12
      | internal   | ERROR          |
      # T13
      | client     | WARN           |

  # T14
  Scenario: successful read produces INFO level with "returned data" message
    Given an action "get_post" on "social:content:posts" that is a read
    When a successful log entry is generated
    Then the log level is "INFO"
    And the log message contains "returned data"

  # T15
  Scenario: successful write produces INFO level with "completed successfully" message
    Given an action "create_post" on "social:content:posts" that is a write
    When a successful log entry is generated
    Then the log level is "INFO"
    And the log message contains "completed successfully"

  # T16
  Scenario: all required fields are present in a log entry
    Given an action "get_post" on "social:content:posts" that is a read
    When a successful log entry is generated
    Then the log entry has all required fields

  # T17
  Scenario: error fields are null on success
    Given an action "get_post" on "social:content:posts" that is a read
    When a successful log entry is generated
    Then the log entry error fields are all None

  # T18
  Scenario: error fields are populated on failure
    Given an action "get_post" on "social:content:posts" that is a read
    When a failed log entry is generated with code "503" and type "server"
    Then the log entry error_code is "503"
    And the log entry error_type is "server"
    And the log entry error_message is not None

  # T19
  Scenario: root span has null parent_span_id
    Given an action "get_post" on "social:content:posts" that is a read
    When a successful log entry is generated as a root span
    Then the log entry parent_span_id is None

  # T20
  Scenario: child span links to parent via parent_span_id
    Given an action "get_post" on "social:content:posts" that is a read
    When a successful log entry is generated as a child of span "abcd1234abcd1234"
    Then the log entry parent_span_id is "abcd1234abcd1234"