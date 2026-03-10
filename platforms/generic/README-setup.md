# Setup: Generic MCP-Capable Agent

This guide covers any LLM agent that supports MCP tool calling and can
read/write files and execute shell commands.

## Requirements

Your agent must support:

1. **File read/write** — reading reference files, writing journal entries
2. **Shell execution** — running Python scripts
3. **Python 3.10+** — for artifact generation (no external packages needed)
4. **MCP tool calling** — connecting to `okx-trade-mcp` and invoking its tools

## Environment variable

Set `SKILL_DIR` to the directory containing `SKILL.md`:

```bash
export SKILL_DIR="/path/to/skills-reviewTrades"
```

The skill uses `${SKILL_DIR}` to locate reference files, scripts, and the
journal data directory.

## Loading the skill

Feed `SKILL.md` to your agent as a system prompt or skill definition.
The reference files in `references/` are linked from SKILL.md and should
be accessible at relative paths from `${SKILL_DIR}`.

## MCP server connection

Connect the OKX MCP server to your agent. The `.mcp.json` file at the repo
root contains the server configuration:

```json
{
  "okx-DEMO-simulated-trading": {
    "command": "npx",
    "args": ["-y", "okx-trade-mcp@latest", "--profile", "demo"]
  }
}
```

Adapt this to your agent's MCP connection method.

## Verifying connectivity

After connecting, verify the MCP server is working:

```
Call: account_get_positions_history with limit: 1
Expected: A response with position data (or empty array if no trades)
```

## Optional MCP servers

- **OpenNews MCP**: [opennews-mcp](https://github.com/6551Team/opennews-mcp) — macro news
- **OpenTwitter MCP**: [opentwitter-mcp](https://github.com/6551Team/opentwitter-mcp) — KOL sentiment
- Get tokens at [6551.io/mcp](https://6551.io/mcp)

## Quick start

```bash
git clone https://github.com/foxisyw/skills-reviewTrades.git
export SKILL_DIR="$(pwd)/skills-reviewTrades"
# Load SKILL.md into your agent, connect MCP, then say: 複盤我的交易
```
