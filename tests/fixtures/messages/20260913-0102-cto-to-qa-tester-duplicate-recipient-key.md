---
id: 20260913-0102-cto-to-qa-tester-duplicate-recipient-key
from: cto
to: qa-tester
to: backend-developer
workspace: engineering
type: work-order
re: Duplicate recipient key
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T01:02
---
Finding S3, golden fixture 3. Two `to:` keys. The old parser silently kept the
last one, so this work order was delivered to `backend-developer` while its id
and its author both said `qa-tester`, and the audit reported PASS because both
roles are engineering members.
