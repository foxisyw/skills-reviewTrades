# OKX Trade Review Skill

Structured post-mortem analysis (交易複盤) of OKX trading history for any
MCP-capable LLM agent.

## Skills

| Skill | Purpose |
|-------|---------|
| `okx-trade-review` | Reviews closed positions: period summary, single trade drill-down, risk assessment, execution quality, cost analysis, pattern recognition, trade journal export |

## Architecture

- **Data layer**: `okx-trade-mcp` — MCP server providing OKX API access (installed separately)
- **Intelligence layer**: SKILL.md with reference files for formulas and output formatting
- **Export layer**: Python script for markdown, CSV, and SVG artifacts

## MCP Server

The `.mcp.json` declares `okx-DEMO-simulated-trading` as the default MCP server.
Users can add `okx-LIVE-real-money` profile for live trading data.
