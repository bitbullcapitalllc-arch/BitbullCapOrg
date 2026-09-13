---
id: 20260913-0104-cto-to-qa-tester-body-quotes-a-status-line
from: cto
to: qa-tester
workspace: engineering
type: question
re: Body quotes a status line
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T01:04
---
Hardening fixture, not a defect found in the wild. Reports in this repo quote
message frontmatter, so a body legitimately contains lines like

    status: open

and `close`/`reply` must rewrite the frontmatter field, not the first textual
match anywhere in the file.
