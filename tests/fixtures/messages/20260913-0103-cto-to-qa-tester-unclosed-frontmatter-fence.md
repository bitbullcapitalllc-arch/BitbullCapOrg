---
id: 20260913-0103-cto-to-qa-tester-unclosed-frontmatter-fence
from: cto
to: qa-tester
workspace: engineering
type: question
re: Unclosed frontmatter fence
in_reply_to: null
status: open
needs_by: null
created: 2026-09-13T01:03
Finding S3, golden fixture 4. There is no closing fence, so every line below is
frontmatter as far as a line-anchored parser is concerned. The old parser raised
an unpacking ValueError and took the whole audit down with a traceback; the fix
reports it as a finding against this one file.
