---
id: 20260913-0100-cto-to-backend-developer-fill-model-v2-questions
from: cto
to: backend-developer
workspace: engineering
type: work-order
re: Fill model --- v2 questions before we implement
in_reply_to: null
status: open
needs_by: 2026-09-20
created: 2026-09-13T01:00
---
Finding S3, golden fixture 1. This file is well formed. The subject contains
`---`, which the old `text.split("---", 2)` parser treated as the end of the
frontmatter block, so `status:` was never parsed, `inbox` filtered the message
out, and `--audit` still reported PASS. Nothing about the file is wrong; the
parser was.
