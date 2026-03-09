# Output Templates for Trade Review

These templates guide the AI agent's output formatting. Use **markdown** as the
primary structure — it renders reliably in Claude Code's terminal UI.

Key principles:
- Use markdown headers (`##`, `###`) for sections
- Use backtick-wrapped separators for visual dividers: `` `── Section ────────` ``
- Use markdown tables (`| col |`) instead of box-drawing tables
- Sparklines (▁▂▃▄▅▆▇█) and bar blocks (█▓░) are safe inline
- Bold key numbers: **+$1,234.56**, **61.5%**
- Always show `[DEMO]` or `[LIVE]` in the top header

---

## 1. SINGLE — Single Trade Review

```markdown
## Trade Review — {instId} [{LIVE|DEMO}]
**{openTime}** → **{closeTime}** ({duration})

| | |
|---|---|
| Direction | **{LONG/SHORT}** |
| Leverage | **{lever}x** |
| Entry | **${openAvgPx}** |
| Exit | **${closeAvgPx}** |
| Size | {closeTotalPos} (peak: {openMaxPos}) |
| Margin Mode | {mgnMode} |

`── P&L Breakdown ──────────────────────────────────`

| Component | Amount |
|-----------|--------|
| Price PnL | **{+/-}${pnl}** ({+/-}{pnlRatio}%) |
| Trading Fees | -${fee} |
| Funding Costs | {+/-}${fundingFee} |
| Liq. Penalty | -${liqPenalty} |
| **Net Realized** | **{+/-}${realizedPnl}** |

`── Risk Metrics ───────────────────────────────────`

- R-Multiple: **{R}R** {or N/A if no SL}
- Initial Risk: ${risk} (SL @ ${slTriggerPx})
- Reward:Risk: **{ratio} : 1**
- Leverage Risk: {distance}% from liquidation

`── Price Action ───────────────────────────────────`

(Simple ASCII chart of price during position hold)

    ${high} |          /\
    ${mid}  |     /---/  \--- EXIT
    ${low}  |/---/
    ${sl}   |. . . . . SL . . . . .
            +---------------------------
             {date1}   {date2}   {date3}

`── Execution ──────────────────────────────────────`

- Entry fills: {n} ({maker%}% maker, {taker%}% taker)
- Exit fills: {n} ({maker%}% maker, {taker%}% taker)
- Entry slippage: {+/-}{bps} bps
- Exit slippage: {+/-}{bps} bps
- Close type: {Manual close | Partial liq | Full liq | ADL}

`── Assessment ─────────────────────────────────────`

[+] {strength_1}
[+] {strength_2}
[-] {weakness_1}
[!] {warning_1}

`── Next Steps ─────────────────────────────────────`

→ "{suggestion_1}" ({target_mode})
→ "{suggestion_2}" ({target_mode})
→ "{suggestion_3}" ({target_mode})
```

---

## 2. PERIOD — Period Summary

```markdown
## Period Summary — {startDate} to {endDate} [{LIVE|DEMO}]

**{n}** trades | Net PnL: **{+/-}${pnl}**

| | Count | Amount |
|---|---|---|
| Winners | {w} ({w%}%) | +${win} |
| Losers | {l} ({l%}%) | -${loss} |
| Break-even | {b} ({b%}%) | — |

`── Key Metrics ────────────────────────────────────`

| Metric | Value |
|--------|-------|
| Profit Factor | **{pf}** |
| Expectancy | **{+/-}${exp}** / trade |
| Avg Winner | +${avgW} ({avgWR}R) |
| Avg Loser | -${avgL} ({avgLR}R) |
| Win/Loss Ratio | {ratio} : 1 |
| Largest Win | +${lgW} ({instId}, {date}) |
| Largest Loss | -${lgL} ({instId}, {date}) |
| Max Consec Win/Loss | {w} / {l} |

`── Daily P&L ──────────────────────────────────────`

▅▃▁▆▇█▃ (+680 +340 -280 +520 +890 +950 +47)

`── Equity Curve ───────────────────────────────────`

    +${max} |                         /\
    +${mid} |               /--------/  \--
    +${low} |     /--------/
        $0  |/---/
            +--------------------------------------
             {date labels across period}

`── By Instrument ──────────────────────────────────`

| Instrument | Trades | Net PnL | Win Rate |
|------------|--------|---------|----------|
| BTC-USDT-SWAP | 8 | **+$1,520** | 75.0% |
| ETH-USDT-SWAP | 9 | **+$1,180** | 66.7% |
| SOL-USDT-SWAP | 6 | **+$147** | 33.3% |

`── By Direction ───────────────────────────────────`

- **Long**: {n} trades, {w%}% win, {+/-}${pnl} █████████████
- **Short**: {n} trades, {w%}% win, {+/-}${pnl} ████████

`── Costs ──────────────────────────────────────────`

- Trading Fees: **${fees}**
- Funding Costs: **${funding}**
- Total Costs: **${total}** ({pct}% of gross win)

`── Next Steps ─────────────────────────────────────`

→ "查看最差那筆交易的詳情" (SINGLE)
→ "檢查風險指標" (RISK)
→ "分析交易模式" (PATTERN)
```

---

## 3. RISK — Risk Assessment

```markdown
## Risk Assessment — {startDate} to {endDate} [{LIVE|DEMO}]

`── Risk Scores ────────────────────────────────────`

Overall Risk:     **{LEVEL}**  ▓▓▓░░░░░░░  **{n}/10**
Leverage Risk:    **{LEVEL}**  ▓▓▓░░░░░░░  **{n}/10**
Concentration:    **{LEVEL}**  ▓▓▓░░░░░░░  **{n}/10**
Sizing Risk:      **{LEVEL}**  ▓▓▓░░░░░░░  **{n}/10**
Drawdown Risk:    **{LEVEL}**  ▓▓▓░░░░░░░  **{n}/10**

`── Leverage Profile ───────────────────────────────`

- Avg Leverage: **{avg}x** | Max: **{max}x** ({instId}, {date})

| Bucket | Trades | Distribution |
|--------|--------|--------------|
| 1-3x | {n} ({pct}%) | ████████████████ |
| 3-5x | {n} ({pct}%) | ██████████ |
| 5-10x | {n} ({pct}%) | ██████ |
| 10-20x | {n} ({pct}%) | ███ |
| 20x+ | {n} ({pct}%) | █ |

`── Drawdown Analysis ──────────────────────────────`

- Max Drawdown: **-${dd}** (-{pct}% of equity)
- Drawdown Duration: {duration}
- Recovery Time: {duration}
- Sharpe Ratio: **{sharpe}**
- Sortino Ratio: **{sortino}**

`── Position Sizing ────────────────────────────────`

- Avg position / equity: **{pct}%**
- Max position / equity: **{pct}%** ({instId})
- Recommended max: 10% per position

`── Concentration ──────────────────────────────────`

| Instrument | Exposure | |
|------------|----------|-|
| {inst1} | {pct}% | ████████████████████ |
| {inst2} | {pct}% | ██████████ |
| {inst3} | {pct}% | █████ |

`── Liquidation Events ─────────────────────────────`

- Full liquidations: **{n}**
- Partial liquidations: **{n}**
- ADL events: **{n}**

`── Recommendations ────────────────────────────────`

[!] {warning_1}
[!] {warning_2}
[+] {positive_1}

`── Next Steps ─────────────────────────────────────`

→ "{view cost breakdown}" (COST)
→ "{check execution quality}" (EXECUTION)
```

---

## 4. EXECUTION — Execution Quality

```markdown
## Execution Quality — {startDate} to {endDate} [{LIVE|DEMO}]

`── Maker/Taker Breakdown ─────────────────────────`

Total fills: **{n}**

| Type | Fills | Volume % | |
|------|-------|----------|-|
| Maker | {n} | {pct}% | ████████████████████ |
| Taker | {n} | {pct}% | █████████ |

`── Fee Impact ─────────────────────────────────────`

- Maker fees (rebate): **+${rebate}**
- Taker fees (cost): **-${cost}**
- Net fee impact: **-${net}**
- Potential savings with 100% maker: **${savings}**

`── Slippage Analysis ──────────────────────────────`

| Metric | Value |
|--------|-------|
| Avg entry slippage | {+/-}{bps} bps |
| Avg exit slippage | {+/-}{bps} bps |
| Total slippage cost | ${cost} |
| Worst slippage | {bps} bps ({instId}, {date}) |

`── Order Type Usage ───────────────────────────────`

- Market: {n} ({pct}%) ██████████████
- Limit: {n} ({pct}%) ████████████████████
- Post-only: {n} ({pct}%) ██████

`── Recommendations ────────────────────────────────`

[!] {suggestion about limit vs market orders}
[+] {positive execution finding}
```

---

## 5. COST — Cost Analysis

```markdown
## Cost Analysis — {startDate} to {endDate} [{LIVE|DEMO}]

`── Summary ────────────────────────────────────────`

| Metric | Value |
|--------|-------|
| Total Costs | **${total}** |
| Costs / Volume | {bps} bps |
| Costs / Net PnL | {pct}% |

`── Breakdown ──────────────────────────────────────`

| Category | Amount | Share | |
|----------|--------|-------|-|
| Trading Fees | ${fees} | {pct}% | ████████████ |
| Funding Costs | ${fund} | {pct}% | ██████ |
| Liq. Penalties | ${liq} | {pct}% | ██ |

`── Trading Fee Detail ─────────────────────────────`

- Maker rebates: **+${rebate}**
- Taker fees: **-${taker}**
- Net trading fee: **-${net}**

`── Funding Rate Impact ────────────────────────────`

- Funding paid: -${paid}
- Funding received: +${received}
- Net funding: **{+/-}${net}**
- Avg daily cost: **${daily}**

`── By Instrument ──────────────────────────────────`

| Instrument | Cost | |
|------------|------|-|
| {inst1} | ${cost} | ██████████████████████ |
| {inst2} | ${cost} | ████████████ |
| {inst3} | ${cost} | █████ |

`── Optimization Tips ──────────────────────────────`

[!] {fee tier suggestion}
[!] {funding rate strategy tip}
```

---

## 6. PATTERN — Pattern Recognition

```markdown
## Pattern Analysis — {startDate} to {endDate} [{LIVE|DEMO}]

`── By Instrument ──────────────────────────────────`

| Instrument | Trades | Net PnL | Win Rate | PF |
|------------|--------|---------|----------|-----|
| BTC-USDT-SWAP | 8 | **+$1,520** | 75.0% | 3.21 |
| ETH-USDT-SWAP | 9 | **+$1,180** | 66.7% | 2.45 |
| SOL-USDT-SWAP | 6 | **+$147** | 33.3% | 1.12 |

`── By Direction ───────────────────────────────────`

- **Long**: {n} trades, {w%}% win, **{+/-}${pnl}** ████████████████
- **Short**: {n} trades, {w%}% win, **{+/-}${pnl}** ████████

`── By Leverage ────────────────────────────────────`

| Bucket | Trades | Win Rate | PF | |
|--------|--------|----------|----|-|
| 1-5x | {n} | {w%}% | {pf} | ████████████████ |
| 5-10x | {n} | {w%}% | {pf} | ██████████ |
| 10-20x | {n} | {w%}% | {pf} | ████ |

`── By Hold Duration ───────────────────────────────`

| Duration | Trades | Win Rate | Avg PnL |
|----------|--------|----------|---------|
| <1h | {n} | {w%}% | {+/-}${avg} |
| 1-4h | {n} | {w%}% | {+/-}${avg} |
| 4-12h | {n} | {w%}% | {+/-}${avg} |
| 12-24h | {n} | {w%}% | {+/-}${avg} |
| 1-3d | {n} | {w%}% | {+/-}${avg} |
| >3d | {n} | {w%}% | {+/-}${avg} |

`── By Session (UTC) ───────────────────────────────`

- Asian (00-08): {n} trades, {w%}% win ████████
- European (08-16): {n} trades, {w%}% win ████████████████
- US (16-00): {n} trades, {w%}% win ██████████████

`── Key Findings ───────────────────────────────────`

1. {finding with strongest signal}
2. {second finding}
3. {third finding}

`── Actionable Insights ────────────────────────────`

[+] {what to do more of}
[-] {what to do less of}
[!] {what to change}
```

---

## 7. JOURNAL — Export Format

### Table format (default)

Use a markdown table:

| Date | Instrument | Dir | Lever | Entry | Exit | Net PnL | PnL% | Dur |
|------|-----------|-----|-------|-------|------|---------|------|-----|
| Mar 01 | BTC-USDT-SWAP | LONG | 10x | $84,250 | $86,120 | **+$888.25** | +20.63% | 43h |
| Mar 02 | ETH-USDT-SWAP | SHORT | 5x | $3,850 | $3,920 | **-$480.00** | -6.24% | 8h |
| Mar 03 | SOL-USDT-SWAP | LONG | 3x | $142.30 | $148.90 | **+$660.00** | +13.89% | 26h |
| **TOTAL** | **{n} trades** | | **avg {x}x** | | | **+$2,847** | | |

### CSV format

```csv
date,instrument,direction,leverage,entry_price,exit_price,net_pnl,pnl_pct,duration_hours,fees,funding_fee,close_type
2026-03-01,BTC-USDT-SWAP,long,10,84250.00,86120.00,888.25,20.63,42.75,-34.45,-12.30,manual
```

### JSON format

```json
{
  "period": { "start": "2026-03-01", "end": "2026-03-07" },
  "account": "demo",
  "trades": [
    {
      "posId": "12345",
      "instId": "BTC-USDT-SWAP",
      "direction": "long",
      "leverage": 10,
      "openAvgPx": 84250.00,
      "closeAvgPx": 86120.00,
      "realizedPnl": 888.25,
      "pnlRatio": 0.2063,
      "fee": -34.45,
      "fundingFee": -12.30,
      "durationHours": 42.75,
      "closeType": "manual",
      "openTime": "2026-03-01T14:30:00Z",
      "closeTime": "2026-03-03T09:15:00Z"
    }
  ],
  "summary": { ... }
}
```

---

## 8. Shared Components

### Sparkline
Use Unicode block elements for inline mini-charts:
```
▁▂▃▄▅▆▇█
```
Map values to 8 levels proportionally. Example:
```
Daily P&L: ▅▃▁▆▇█▃  (+680 +340 -280 +520 +890 +950 +47)
```

### Horizontal Bar Chart
Scale bars proportionally to the maximum value:
```
BTC  +$1,520  ██████████████████████  75% win
ETH  +$1,180  █████████████████       67% win
SOL    +$147  ██                      33% win
```
Use `█` for positive, `▓` for negative.

### Risk Score Bar
```
{LABEL}  {LEVEL}  {▓▓▓▓▓░░░░░}  {n}/10
```
Level thresholds: 1-3 = LOW, 4-6 = MODERATE, 7-8 = HIGH, 9-10 = CRITICAL

### Formatting Notes

Claude Code renders markdown in the terminal. These render well:
- **Bold** for key numbers and headers
- Markdown tables (pipe `|` format)
- Backtick-wrapped section dividers
- Inline Unicode blocks (█▓░▁▂▃▄▅▆▇)
- Lists with `-` or numbered

These have known issues and should be avoided:
- ANSI color escape codes (get mangled by line-wrapping)
- Complex box-drawing borders (┌─┐│└─┘) around entire output blocks
- Nested box-drawing tables inside box-drawing borders

### Number Formatting
- USD amounts: `$1,234.56` with commas, 2 decimal places
- Percentages: `12.3%` with 1 decimal place
- R-multiples: `+2.37R` with 2 decimal places
- Leverage: `10x`
- Duration: `42.75h` or `1d 18h 45m` for longer durations
- Large numbers: `$1.23M`, `$456K` for readability
