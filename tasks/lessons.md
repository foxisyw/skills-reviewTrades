# Lessons Learned

## 2026-03-10
- Mistake/bug: Planned a large skill redesign without first creating a persistent development log inside the skill repo.
- Symptom: Future collaborators would not have a durable record of what changed in each implementation pass.
- Root cause: I treated the redesign as a spec/document update and did not immediately establish project-local logging discipline.
- Prevention rule: For every non-trivial skill change, create or update `tasks/todo.md`, `tasks/dev-log.md`, and `tasks/lessons.md` before editing functional files.
- Affected files or workflow: Repo-wide implementation workflow for `Trade Review Skills`.

## 2026-03-10
- Mistake/bug: Patched the artifact money formatter too quickly and briefly introduced an invalid Python format-string idea while trying to add the `$` symbol.
- Symptom: The exporter risked emitting broken money formatting or failing verification after a display-layer change.
- Root cause: I tried to compress sign and currency formatting into the format spec instead of composing the string explicitly and re-checking Python's formatting rules first.
- Prevention rule: After any change to shared rendering helpers, immediately run `py_compile` plus a sample artifact generation pass, and prefer explicit sign/currency composition for money output.
- Affected files or workflow: `scripts/trade_review_assets.py` output formatting and verification workflow.
