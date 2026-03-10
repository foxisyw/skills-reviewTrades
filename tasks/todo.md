# Task Todo

## Change Batch
- Name: Deep Trade Review Skill With Export and Development Logs
- Started: 2026-03-10 10:15 HKT
- Status: in_progress

## Scope
- Redesign `okx-trade-review` into a markdown-first review pipeline.
- Add market-context guidance for per-trade enrichment.
- Replace wide ASCII/box templates with narrow markdown templates.
- Add optional exporter script for markdown, enriched CSV, and SVG.
- Add persistent development logging for future collaborators.
- Sync the redesign into the GitHub repo structure and update repo documentation.

## Plan
- [x] Create `tasks/` and `scripts/` folders.
- [x] Create persistent planning and logging files.
- [x] Rewrite `SKILL.md` to define the new workflow, depth policy, modifiers, exports, and logging policy.
- [x] Add `references/market-context.md` for market-enrichment rules and derived fields.
- [x] Replace `references/output-templates.md` with narrow markdown-first templates.
- [x] Add `scripts/trade_review_assets.py` with markdown, CSV, and SVG export support.
- [x] Run verification on the exporter with representative sample data.
- [x] Update repo README and package metadata to match the new skill behavior.
- [x] Update review notes, lessons, and append the implementation session to `tasks/dev-log.md`.

## Verification Targets
- Markdown output remains readable in a narrow chat window.
- Exporter writes valid markdown and enriched CSV from normalized review JSON.
- Optional SVG renders without third-party Python dependencies.
- Skill spec clearly degrades when Python or file output is unavailable.

## Review
- Implemented a markdown-first review spec, market-context reference, narrow output templates, optional exporter script, and persistent repo logging files.
- Verified the exporter with `python3 -m py_compile` and sample artifact generation to `/tmp/trade-review-out` and `/tmp/trade-review-out-insights`.
- Synced the redesign into `/tmp/skills-reviewTrades`, updated `README.md`, `package.json`, and `.claude-plugin/plugin.json` to reflect the new behavior and repo structure.
- Fixed one implementation bug during verification: currency formatting in generated artifacts initially omitted the `$` symbol and the formatter patch was corrected and re-verified.
