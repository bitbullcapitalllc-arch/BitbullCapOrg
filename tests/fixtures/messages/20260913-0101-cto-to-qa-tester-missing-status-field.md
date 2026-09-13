---
id: 20260913-0101-cto-to-qa-tester-missing-status-field
from: cto
to: qa-tester
workspace: engineering
type: work-order
re: Test harness scope
in_reply_to: null
needs_by: null
created: 2026-09-13T01:01
---
Finding S3, golden fixture 2. `status:` is absent. `inbox` filters on
`status == open`, so this work order is invisible to its recipient, and the old
audit never checked for required keys — it reported PASS. An audit that cannot
see a lost message is worse than no audit.
