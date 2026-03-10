# Setup: OpenClaw

## Loading the skill

Point OpenClaw at the `SKILL.md` file in this repository:

```
skill load /path/to/skills-reviewTrades/SKILL.md
```

Or add it to your OpenClaw configuration file.

## Environment variable

Set `SKILL_DIR` to the directory containing `SKILL.md`:

```bash
export SKILL_DIR="/path/to/skills-reviewTrades"
```

OpenClaw resolves this as the skill's root directory automatically if
the skill is loaded from a local path.

## MCP server

Connect the OKX MCP server before using the skill:

```bash
mcp connect okx-DEMO-simulated-trading --config /path/to/skills-reviewTrades/.mcp.json
```

Or configure it in your OpenClaw MCP settings to match the entries in
`.mcp.json`.

## Optional MCP servers

- **OpenNews**: `opennews` — macro news context
- **OpenTwitter**: `opentwitter` — KOL sentiment

Get tokens at [6551.io/mcp](https://6551.io/mcp).

## Quick start

```bash
git clone https://github.com/foxisyw/skills-reviewTrades.git
export SKILL_DIR="$(pwd)/skills-reviewTrades"
# Load skill and connect MCP, then say: 複盤我的交易
```
