# OKX Trade Review Skill for Claude Code

Markdown-first OKX trade review for Claude Code, backed by `okx-trade-mcp`.

This plugin is designed for exchange trade post-mortems in terminal-first or
browserless environments. It fetches closed trade history, enriches selected
trades with time-aligned market candles, explains what actually drove PnL, and
can export artifacts for later analysis.

## What Changed in v2

- Markdown-first reporting for narrow chat windows
- Deeper `複盤我的交易` workflow with market-context enrichment
- Optional artifact export:
  - long-form markdown report
  - enriched CSV
  - optional SVG overview
- Persistent contributor logs in `tasks/`

## Core Capabilities

| Mode | Output |
|------|--------|
| `PERIOD` | Executive summary, scorecard, PnL drivers, drags, market context, behavior patterns, action adjustments |
| `SINGLE` | One-trade deep dive with MAE/MFE, capture, regime, alignment, entry timing |
| `RISK` | Drawdown, leverage, concentration, liquidation, position-sizing review |
| `EXECUTION` | Maker/taker mix, slippage, fill quality, execution drag |
| `COST` | Fees, funding, liquidation penalties, cost drag |
| `PATTERN` | Instrument, direction, leverage, duration, and session patterns |
| `JOURNAL` | Enriched CSV export and optional markdown/SVG artifacts |

## Default Behavior

When the user says:

```text
複盤我的交易
```

the skill defaults to:

- `demo` account
- last 7 days
- chat markdown only
- `standard` depth

Depth policy:

- `<= 20 trades`: enrich every trade with market context
- `21-100 trades`: enrich top 10 impact trades and summarize the rest
- `> 100 trades`: warn and fall back to aggregate review plus top 12 trades

Supported modifiers:

- `快速複盤`
- `深度逐筆`
- `完整報告`
- `輸出 markdown 檔`
- `匯出 CSV`
- `附圖`
- `只看摘要`

## What the Review Looks Like

The main chat response is structured as:

1. `Executive Summary`
2. `Scorecard`
3. `What Drove PnL`
4. `What Hurt`
5. `Market Context`
6. `Behavior Patterns`
7. `Action Adjustments`
8. `Next Steps`

This replaces the older wide ASCII box layout. The goal is readability inside
Claude Code, OpenClaw, and other narrow chat surfaces.

## Market-Context Enrichment

For selected trades, the skill uses `market_get_candles` to compute:

- `preEntryMovePct`
- `maePct`
- `mfePct`
- `capturePct`
- `regimeTag`
- `trendAlignment`
- `entryTimingTag`

These fields are used to distinguish:

- good idea vs bad execution
- aligned vs countertrend trades
- chased entries vs pullback entries
- exits that captured too little of the available move

## Export Artifacts

When scripting is available and the user asks for exports, the skill can
generate:

- `review-YYYYMMDD-YYYYMMDD.md`
- `review-YYYYMMDD-YYYYMMDD.enriched.csv`
- `review-YYYYMMDD-YYYYMMDD.svg`

The exporter lives at:

- [skills/okx-trade-review/scripts/trade_review_assets.py](./skills/okx-trade-review/scripts/trade_review_assets.py)

It accepts normalized review JSON and writes artifacts without third-party
Python dependencies.

### Example exporter usage

```bash
python skills/okx-trade-review/scripts/trade_review_assets.py /tmp/okx-review.json --output-dir /tmp/review-out --svg
```

If Python or file writing is unavailable, the skill should still return the full
markdown review in chat and can fall back to inline fenced CSV/markdown content.

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Node.js 18+
- OKX API key with read-only permissions

### 1. Install the MCP server

```bash
npm install -g okx-trade-mcp
```

### 2. Configure API credentials

```bash
mkdir -p ~/.okx
cat > ~/.okx/config.toml << 'EOF'
[demo]
api_key = "your-api-key"
secret_key = "your-secret-key"
passphrase = "your-passphrase"
EOF
```

### 3. Install the plugin

```bash
claude plugin add foxisyw/skills-reviewTrades
```

### 4. Use it

Examples:

```text
複盤我的交易
```

```text
review my trades this week
```

```text
複盤我的交易，匯出 CSV
```

```text
深度逐筆複盤這個月的 BTC 和 ETH 交易
```

## Trigger Phrases

English:

- `review my trades`
- `how did I do this week`
- `review my BTC trade`
- `risk assessment`
- `export trades`

中文:

- `複盤我的交易`
- `這週績效如何`
- `複盤那筆交易`
- `風險評估`
- `匯出交易記錄`

## Safety

- Demo by default
- Read-only review only
- Clear `[DEMO]` / `[LIVE]` labeling
- Warns when requests exceed OKX's approximate 3-month retention window

## Repository Structure

```text
skills-reviewTrades/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   └── okx-trade-review/
│       ├── SKILL.md
│       ├── references/
│       │   ├── formulas.md
│       │   ├── market-context.md
│       │   ├── mcp-tools.md
│       │   └── output-templates.md
│       └── scripts/
│           └── trade_review_assets.py
├── tasks/
│   ├── dev-log.md
│   ├── lessons.md
│   └── todo.md
├── CLAUDE.md
├── LICENSE
├── README.md
└── package.json
```

## Development Logs

This repo now keeps project-local implementation records:

- [tasks/todo.md](./tasks/todo.md): active implementation checklist and review notes
- [tasks/dev-log.md](./tasks/dev-log.md): append-only session log of repo changes
- [tasks/lessons.md](./tasks/lessons.md): mistakes, bugs, and prevention rules

These files are meant for contributors, not end users.

## Limitations

- OKX historical retention is limited
- Pagination is capped in the skill flow
- Spot review has different data availability from derivatives
- The exporter expects normalized review JSON from the calling agent
- Current verification is sample-based; there is no formal test suite yet

## License

[Apache-2.0](./LICENSE)
