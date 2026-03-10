# OKX Trade Review Skill for Claude Code

A comprehensive trade review and discipline tracking skill for [Claude Code](https://claude.com/claude-code). Connects to your OKX account via MCP, fetches closed trades, enriches them with market context, and delivers a structured post-mortem — all in the chat.

Built for crypto traders who want honest, data-driven feedback on their execution without leaving the terminal.

## What It Does

```
You: 複盤我的交易
Skill: [fetches last 7 days from OKX] → analysis → reflection prompt → journal entry
```

### 10 Review Modes

| Mode | Purpose |
|------|---------|
| **PERIOD** | Review a date range — scorecard, drivers, drags, patterns, action items |
| **SINGLE** | Deep dive into one trade — entry timing, MAE/MFE, capture rate, market regime |
| **RISK** | Leverage, drawdown, concentration, liquidation proximity |
| **EXECUTION** | Maker/taker mix, slippage, fill quality |
| **COST** | Fee drag, funding costs, liquidation penalties |
| **PATTERN** | Instrument, direction, session, duration, and leverage patterns |
| **JOURNAL** | Export trades as enriched CSV or markdown report |
| **NOTEBOOK** | View and search your discipline journal |
| **BIAS** | Detect 7 behavioral biases from accumulated reflections |
| **NEWS** | Overlay macro news and Twitter sentiment on a review |

### Key Features

**Market Context Enrichment**
Every trade gets tagged with the local price regime (`trend_up`, `trend_down`, `range`), trend alignment, and entry timing (`chase`, `pullback`, `neutral`). MAE, MFE, and capture rate show whether a loss was a bad idea or bad execution.

**Discipline Journal (紀律小簿)**
After each review, a compact reflection prompt asks 3 quick questions (entry reason, emotion, self-rating). Answers are normalized into enums, stored as JSON, and accumulate over time. Supports bilingual input — answer in Chinese or English.

**7-Bias Detection Engine**
Once you have 5+ journal entries, run `偏差分析` to detect:
- **Loss Aversion** — holding losers too long, cutting winners short (uses median duration ratio, regime-adjusted capture thresholds)
- **Revenge Trading** — re-entry after loss within time window (detects correlated-asset revenge: BTC loss → ETH re-entry)
- **Overconfidence** — leverage escalation after winning streaks (with absolute leverage guard: ≤5x is always safe)
- **FOMO** — chase entries clustered in time (volatility-adaptive window: 4h base, 6h during >3% moves)
- **Emotional Stop-Loss** — exiting at maximum pain without a plan
- **Disposition Effect** — relief-selling small winners while bag-holding losers
- **Overtrading** — frequency-performance degradation, death by a thousand cuts

Each bias reports severity (健康/需注意/嚴重), confidence level, specific evidence, and one actionable suggestion. The composite score uses `max()` for the headline (no misleading averages).

**Artifact Generation**
Request `完整報告`, `匯出 CSV`, or `附圖` to generate:
- Enriched markdown report with deep dives
- CSV with all normalized fields for external analysis
- SVG overview chart (equity curve, drawdown, contribution bars)

## Project Structure

```
.
├── SKILL.md                          # Main skill definition (modes, workflow, prompts)
├── references/
│   ├── bias-detection.md             # 7 bias algorithms with thresholds and worked examples
│   ├── discipline-journal.md         # Journal schema, enums, persistence rules
│   ├── formulas.md                   # Statistical formulas (win rate, Sharpe, Kelly, etc.)
│   ├── market-context.md             # Candle enrichment: regime, MAE/MFE, capture rate
│   ├── mcp-tools.md                  # OKX MCP tool reference and pagination patterns
│   └── output-templates.md           # 14 markdown templates for all output types
├── scripts/
│   └── trade_review_assets.py        # Python artifact generator (markdown, CSV, SVG, journal)
├── data/
│   └── discipline-journal/
│       ├── index.json                # Lean index for fast filtering
│       ├── entries/                   # One JSON file per reflection
│       └── bias-snapshots/           # Periodic bias analysis cache
└── tasks/
    ├── todo.md
    ├── lessons.md
    └── dev-log.md
```

## Prerequisites

1. **Claude Code** — [install guide](https://docs.anthropic.com/en/docs/claude-code)
2. **OKX MCP Server** — `okx-trade-mcp` connected with account module enabled. Configure credentials in `~/.okx/config.toml`.
3. **Python 3.10+** — for artifact generation (markdown, CSV, SVG exports). No external packages required.

### Optional MCP Servers

- **OpenNews MCP** — macro news context ([opennews-mcp](https://github.com/6551Team/opennews-mcp))
- **OpenTwitter MCP** — KOL sentiment ([opentwitter-mcp](https://github.com/6551Team/opentwitter-mcp))
- Get tokens at [6551.io/mcp](https://6551.io/mcp)

## Installation

Copy this skill directory into your Claude Code skills folder, or clone this repo and symlink it:

```bash
git clone https://github.com/foxisyw/skills-reviewTrades.git
# Then add the skill path to your Claude Code configuration
```

## Usage

### Trigger Phrases

The skill activates on a wide range of natural-language triggers:

| Language | Examples |
|----------|----------|
| Chinese | `複盤我的交易`, `看交易`, `我虧了`, `記錄一下`, `我想反思`, `偏差分析`, `交易小簿` |
| English | `review my trades`, `check my BTC`, `why did I lose`, `bias analysis`, `discipline journal` |

### Modifiers

| Modifier | Effect |
|----------|--------|
| `快速複盤` | Skip per-trade candle enrichment |
| `深度逐筆` | Enrich every trade (up to 60) |
| `完整報告` | Generate long markdown artifact |
| `匯出 CSV` | Generate enriched CSV |
| `附圖` | Generate overview SVG chart |
| `只看摘要` | Executive summary only |
| `最近 N 條` | Limit notebook view to N entries |
| `搜尋 {keyword}` | Filter journal by keyword |
| `偏差報告` | Full bias analysis report |

### Reflection Flow

After each SINGLE or PERIOD review, the skill offers a **2-phase reflection**:

**Phase 1** (always shown — answer in one message):
1. Entry reason (breakout / indicator / fomo / grid-dca / ...)
2. Emotion (calm / fomo / fear / revenge / ...)
3. Self-rating (1-5)

**Phase 2** (optional — type `done` to skip):
4. Stop-loss basis (preset / trailing / liquidation-level / atr / ...)
5. Exit reason (stop-loss / trailing-stop / partial-close / forced-liquidation / ...)
6. Lesson learned (free text)

Type `跳過` or `skip` to skip entirely. Partial answers are saved — you don't have to answer everything.

### Python Exporter CLI

```bash
# Generate review artifacts from normalized JSON
python scripts/trade_review_assets.py /tmp/review.json --output-dir /tmp --svg

# Render journal view
python scripts/trade_review_assets.py --journal-index data/discipline-journal/index.json --output-dir /tmp

# Render bias report
python scripts/trade_review_assets.py --bias-report data/discipline-journal/bias-snapshots/2026-03-10.json --output-dir /tmp

# Backup journal to external directory
python scripts/trade_review_assets.py --backup-journal ~/backups --journal-dir data/discipline-journal

# Import journal from previously exported CSV
python scripts/trade_review_assets.py --import-journal ~/backups/journal.csv --journal-dir data/discipline-journal
```

## Data Safety

- Journal data is **device-local** — stored in `data/discipline-journal/`. It does not sync across machines.
- Before updating or reinstalling this skill, **back up the `data/` directory**.
- Index writes use an **atomic tmp+rename pattern** to prevent corruption from interrupted writes.
- If `index.json` becomes corrupted, it is **automatically rebuilt** from individual entry files.
- Journal entries contain personal reflections (emotions, self-criticism). Ensure your machine is password-protected.

## Formulas & Metrics

The skill computes and reports:

| Category | Metrics |
|----------|---------|
| Core | Win rate, profit factor, expectancy, R-multiple, SQN |
| Risk | Max drawdown, Sharpe/Sortino/Calmar ratios, leverage distribution, liquidation proximity |
| Execution | Slippage, maker/taker ratio, fee impact |
| Market Context | Pre-entry move, MAE, MFE, capture rate, regime tag, trend alignment, entry timing |
| Behavior | 7 bias scores with severity, confidence, and evidence |

All formulas are documented in [`references/formulas.md`](references/formulas.md) and [`references/market-context.md`](references/market-context.md).

## Design Decisions

- **Markdown-first** — main chat output works without Python, file writing, or image preview. Artifacts are optional.
- **Evidence-backed** — every `[+]`, `[-]`, `[!]` claim must cite trade count + at least one metric. Patterns require ≥3 trades or ≥20% of sample.
- **Bilingual** — prompts, enums, and trigger phrases work in both Traditional Chinese and English. Language auto-detected from user's last message.
- **Narrow-chat optimized** — tables max 4 columns in chat. Wide ledgers go to exported artifacts only.
- **Crypto-calibrated** — bias thresholds account for 24/7 markets, 5-min to multi-week holding periods, correlated-asset trading, and leverage norms.

## Safety

- Demo account by default — explicit confirmation required for live
- Read-only review — the skill never executes trades
- Clear `[DEMO]` / `[LIVE]` labeling on all outputs
- Warns when requests exceed OKX's ~3-month data retention

## Development Logs

- [tasks/todo.md](./tasks/todo.md) — active implementation checklist
- [tasks/dev-log.md](./tasks/dev-log.md) — append-only session log
- [tasks/lessons.md](./tasks/lessons.md) — mistakes, bugs, and prevention rules

## License

MIT
