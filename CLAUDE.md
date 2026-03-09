# OKX Trade Review Skill

This is a Claude Code plugin that provides structured post-mortem analysis (交易複盤) of OKX trading history.

## Skills

| Skill | Purpose |
|-------|---------|
| `okx-trade-review` | Reviews closed positions: period summary, single trade drill-down, risk assessment, execution quality, cost analysis, pattern recognition, trade journal export |

## Architecture

- **Data layer**: `okx-trade-mcp` — MCP server providing OKX API access (installed separately)
- **Intelligence layer**: This plugin — SKILL.md with reference files for formulas and output formatting

## MCP Server

The `.mcp.json` declares `okx-DEMO-simulated-trading` as the default MCP server.
Users can add `okx-LIVE-real-money` profile for live trading data.
