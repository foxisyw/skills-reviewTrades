# OKX Trade Review Skill for Claude Code

> Structured post-mortem analysis (交易複盤) of OKX trading history — powered by MCP

This [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin adds trade review capabilities via the [`okx-trade-mcp`](https://www.npmjs.com/package/okx-trade-mcp) data layer. It analyzes your closed positions, computes performance metrics, identifies trading patterns, and gives you actionable improvement suggestions — all inside your terminal.

## What It Does

| Mode | What you get |
|------|-------------|
| **Period Summary** | Win rate, profit factor, expectancy, equity curve, instrument breakdown |
| **Single Trade** | Full P&L breakdown, execution details, risk metrics, price chart, assessment |
| **Risk Assessment** | Leverage distribution, max drawdown, concentration scoring (1-10), Sharpe/Sortino |
| **Execution Quality** | Maker/taker ratio, slippage analysis, fee impact |
| **Cost Analysis** | Fees, funding rates, liquidation penalties, optimization tips |
| **Pattern Recognition** | Performance by instrument, direction, leverage, hold duration, trading session |
| **Trade Journal** | Export as markdown table, CSV, or JSON |

### Example Output

```
## Period Summary — Mar 01 to Mar 07 [DEMO]

23 trades | Net PnL: +$2,847.25

| Metric          | Value                |
|-----------------|----------------------|
| Win Rate        | 61.5%                |
| Profit Factor   | 2.25                 |
| Expectancy      | +$123.79 / trade     |
| Largest Win     | +$888.25 (BTC, Mar 01) |
| Max Drawdown    | -$620.00 (-4.2%)     |

── By Instrument ──────────────────────────────
BTC-USDT-SWAP  8 trades  +$1,520  ██████████████████  75% win
ETH-USDT-SWAP  9 trades  +$1,180  █████████████████   67% win
SOL-USDT-SWAP  6 trades    +$147  ██                  33% win

── Next Steps ─────────────────────────────────
→ "查看最差那筆交易的詳情" (drill into worst trade)
→ "檢查風險指標" (risk assessment)
→ "分析交易模式" (find patterns)
```

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Node.js 18+
- OKX API key with **read-only** permissions

### 1. Install the MCP server (data layer)

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

Get your API key at [OKX API Management](https://www.okx.com/account/my-api). Select **read-only** permissions — this skill never executes trades.

### 3. Install this skill

```bash
claude plugin add foxisyw/skills-reviewTrades
```

### 4. Use it

Open Claude Code and just ask:

```
複盤我的交易
```

or

```
review my trades this week
```

The skill auto-detects trade review intent and handles MCP connectivity checks.

## Trigger Phrases

The skill activates on natural language — no slash command needed.

| Language | Examples |
|----------|---------|
| English | "how did I do this week", "review my BTC trade", "show win rate", "risk assessment", "export trades" |
| 中文 | "這週績效如何", "複盤那筆交易", "勝率多少", "風險評估", "匯出交易記錄" |

**Full trigger list**: review, 複盤, post-mortem, performance, 績效, win rate, 勝率, P&L, 盈虧, drawdown, 回撤, slippage, 滑點, fees, 手續費, risk, 風險, export, 匯出, patterns, 交易模式, journal, 交易日誌

## Safety

- **Demo by default** — always uses simulated trading account unless you explicitly confirm live
- **Read-only** — never executes trades, only reads historical data
- **Clear labeling** — every output shows `[DEMO]` or `[LIVE]` header
- **3-month limit** — warns when requesting data beyond OKX's retention period

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Claude Code                                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │  okx-trade-review (this plugin)                   │  │
│  │  SKILL.md → intent detection → metric computation │  │
│  │  → formatted output → next-step suggestions       │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │ MCP calls                     │
│  ┌──────────────────────▼────────────────────────────┐  │
│  │  okx-trade-mcp (installed separately)             │  │
│  │  account positions, fills, orders, bills, candles │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │ REST API                      │
└─────────────────────────┼───────────────────────────────┘
                          ▼
                    OKX Exchange API
```

## Plugin Structure

```
skills-reviewTrades/
├── .claude-plugin/
│   └── plugin.json              # Claude Code plugin manifest
├── .mcp.json                    # MCP server dependency declaration
├── skills/
│   └── okx-trade-review/
│       ├── SKILL.md             # Main skill — intent routing + agent instructions
│       └── references/
│           ├── mcp-tools.md     # MCP tool parameter & return field reference
│           ├── formulas.md      # Statistical formulas (Sharpe, drawdown, etc.)
│           └── output-templates.md  # Output formatting templates
├── CLAUDE.md                    # Project-level context
├── package.json
├── LICENSE                      # Apache-2.0
└── README.md
```

## Advanced Configuration

### Live account

Add a second MCP server profile for real trading data:

```json
{
  "mcpServers": {
    "okx-DEMO-simulated-trading": {
      "command": "okx-trade-mcp",
      "args": ["--profile", "demo", "--modules", "account,swap,market"]
    },
    "okx-LIVE-real-money": {
      "command": "okx-trade-mcp",
      "args": ["--profile", "live", "--modules", "account,swap,market"]
    }
  }
}
```

Then tell Claude: "用真實帳戶查看" or "switch to live account".

### Spot trades

The skill supports spot trade review via `spot_get_fills`. Just ask about spot trades specifically — the skill routes to the correct MCP tool.

## Data Limitations

- OKX API retains **3 months** of historical data
- Pagination capped at **1,000 items** (10 pages × 100) per query
- Spot trades use `spot_get_fills` (no position-level aggregation)
- Funding rate data available only for perpetual swaps

## License

[Apache-2.0](LICENSE)

---

# OKX 交易複盤技能

> 在 Claude Code 終端中對 OKX 交易歷史進行結構化複盤分析

## 功能

| 模式 | 輸出內容 |
|------|---------|
| **期間績效** | 勝率、利潤因子、期望值、權益曲線、幣種分佈 |
| **單筆複盤** | 完整盈虧拆解、執行細節、風險指標、價格圖、評估 |
| **風險評估** | 槓桿分佈、最大回撤、集中度評分 (1-10)、Sharpe/Sortino |
| **執行品質** | Maker/Taker 比例、滑點分析、手續費影響 |
| **費用分析** | 手續費、資金費率、強平罰金、優化建議 |
| **交易模式** | 按幣種、方向、槓桿、持倉時長、交易時段分析 |
| **交易日誌** | 匯出為表格、CSV 或 JSON |

## 快速開始

### 1. 安裝 MCP 數據層

```bash
npm install -g okx-trade-mcp
```

### 2. 配置 API 密鑰

```bash
mkdir -p ~/.okx
cat > ~/.okx/config.toml << 'EOF'
[demo]
api_key = "your-api-key"
secret_key = "your-secret-key"
passphrase = "your-passphrase"
EOF
```

在 [OKX API 管理](https://www.okx.com/account/my-api) 申請 **唯讀** 權限的密鑰。

### 3. 安裝技能

```bash
claude plugin add foxisyw/skills-reviewTrades
```

### 4. 使用

```
複盤我的交易
```

技能會自動偵測意圖並驗證 MCP 連接。

## 安全性

- **預設模擬帳戶** — 除非明確確認，否則只查看 demo 數據
- **唯讀** — 永不執行交易
- **清晰標示** — 所有輸出顯示 `[DEMO]` 或 `[LIVE]`
