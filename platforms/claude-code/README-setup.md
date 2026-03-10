# Setup: Claude Code

## Auto-discovery

Claude Code discovers this skill automatically via `.claude-plugin/plugin.json`.
Place the repo (or symlink it) anywhere on your machine — Claude Code scans for
`.claude-plugin/` directories.

## Environment variable

Claude Code injects `${CLAUDE_SKILL_DIR}` automatically. The skill's
`${SKILL_DIR}` resolves to the same path — no manual configuration needed.

## Allowed tools

On first use, Claude Code will prompt you to approve tool access:

- **Read / Write** — reading reference files, writing journal entries
- **Bash (python)** — running the artifact exporter
- **MCP tools** — `okx-DEMO-simulated-trading`, `okx-LIVE-real-money`,
  `opennews`, `opentwitter`

Approve each when prompted, or pre-authorize in your Claude Code settings.

## MCP server

The `.mcp.json` at the repo root declares `okx-DEMO-simulated-trading`.
Claude Code reads this file and connects the MCP server automatically.

To add a live account, edit `.mcp.json` and add an `okx-LIVE-real-money` entry
with the appropriate credentials path.

## Quick start

```bash
git clone https://github.com/foxisyw/skills-reviewTrades.git
# Claude Code will auto-discover the skill
# Say: 複盤我的交易
```
