# Output Templates for Trade Review

These templates define the canonical markdown layouts for `okx-trade-review`.
They are optimized for narrow chat windows and browserless environments.

## Global Rules

- Use markdown headings, bullets, short tables, sparklines, and 10-character bars.
- Avoid box-drawing frames in main chat output.
- Avoid wide ledgers or tables with more than 4 columns in main chat output.
- Lead with findings, not raw dumps.
- Every `[+]`, `[-]`, `[!]` claim must cite evidence.
- Mark small samples as `低樣本` / `low confidence` instead of overstating them.

## 1. PERIOD — Standard Chat Review

```markdown
## 交易複盤 — {startDate} to {endDate} [{DEMO|LIVE}]

### Executive Summary
- 淨盈虧：**{+/-}$ {netPnl}**，共 **{n}** 筆，勝率 **{winRate}%**，Profit Factor **{pf}**
- `[+]` {top_positive_finding_with_evidence}
- `[-]` {top_negative_finding_with_evidence}
- `[!]` {main_risk_or_cost_warning_with_evidence}
- 下一個最值得追查的是：**{specific_follow_up_target}**

### Scorecard
| Metric | Value |
|--------|-------|
| Net PnL | {+/-}${netPnl} |
| Trades | {n} |
| Win Rate | {winRate}% |
| Profit Factor | {pf} |
| Expectancy | {+/-}${expectancy} / trade |
| Max Drawdown | -${maxDd} |
| Total Costs | ${totalCosts} |

### What Drove PnL
- `[+]` {best_instrument_or_direction}: {evidence}
- `[+]` {best_behavior_pattern}: {evidence}
- `[+]` {best_market_context_pattern}: {evidence}

### What Hurt
- `[-]` {largest_drag_1}: {evidence}
- `[-]` {largest_drag_2}: {evidence}
- `[!]` 成本拖累：${totalCosts}，約占 {costPct}% {cost_denominator}

### Market Context
- 已做 market-context enrich：**{enrichedTrades}/{totalTrades}** 筆
- {tradeA}: `{regimeTag}` / `{trendAlignment}` / `{entryTimingTag}`，MAE {maePct}% ，MFE {mfePct}% ，Capture {capturePct}%
- {tradeB}: `{regimeTag}` / `{trendAlignment}` / `{entryTimingTag}`，MAE {maePct}% ，MFE {mfePct}% ，Capture {capturePct}%
- {market_context_conclusion_with_evidence}

### Behavior Patterns
- 方向：Long **{longCount}** 筆 {+/-}${longPnl} vs Short **{shortCount}** 筆 {+/-}${shortPnl}
- 槓桿：{best_leverage_bucket_or_low_sample_note}
- 持倉時長：{best_hold_bucket_or_low_sample_note}
- 交易時段：{best_session_or_low_sample_note}

### Action Adjustments
- `[+]` 保留：{do_more_of_this}
- `[-]` 減少：{do_less_of_this}
- `[!]` 調整：{specific_process_change}

### Next Steps
- `查看最大虧損那筆交易`
- `檢查風險指標`
- `匯出 CSV`
```

## 2. PERIOD — Executive Summary Only

```markdown
## 交易複盤摘要 — {startDate} to {endDate} [{DEMO|LIVE}]

- 淨盈虧：**{+/-}${netPnl}**，共 **{n}** 筆，勝率 **{winRate}%**
- `[+]` {best_finding_with_evidence}
- `[-]` {worst_finding_with_evidence}
- `[!]` {primary_warning_with_evidence}
- 建議下一步：**{best_follow_up_mode_or_export}**
```

## 3. SINGLE — Detailed Trade Review

```markdown
## 單筆交易複盤 — {instId} [{DEMO|LIVE}]

### Snapshot
| Metric | Value |
|--------|-------|
| Direction | {direction} |
| Leverage | {leverage}x |
| Entry | ${entryPrice} |
| Exit | ${exitPrice} |
| Net PnL | {+/-}${realizedPnl} |
| Duration | {duration} |

### Trade Outcome
- Price PnL：{+/-}${pnl}
- Costs：${costs}
- Close Type：{closeType}

### Market Context
- Local regime：`{regimeTag}`
- Alignment：`{trendAlignment}`
- Entry timing：`{entryTimingTag}`
- MAE：{maePct}% ，MFE：{mfePct}% ，Capture：{capturePct}%

### Assessment
- `[+]` {strength_with_evidence}
- `[-]` {weakness_with_evidence}
- `[!]` {main_warning_with_evidence}

### Next Steps
- `檢查執行品質`
- `比較同類型交易`
```

## 4. RISK — Risk Review

```markdown
## 風險複盤 — {startDate} to {endDate} [{DEMO|LIVE}]

### Risk Snapshot
| Metric | Value |
|--------|-------|
| Max Drawdown | -${maxDd} |
| Avg Leverage | {avgLev}x |
| Max Leverage | {maxLev}x |
| Concentration | {topInstPct}% in {topInst} |
| Liquidations | {liqCount} |

### Main Findings
- `[!]` {largest_risk_problem_with_evidence}
- `[-]` {second_risk_problem_with_evidence}
- `[+]` {best_risk_discipline_finding_with_evidence}

### Risk Buckets
- 槓桿：{bucket_summary}
- 倉位集中：{concentration_summary}
- 回撤：{drawdown_summary}

### Next Steps
- `查看成本拖累`
- `詳細看最大回撤區間`
```

## 5. EXECUTION — Execution Review

```markdown
## 執行品質複盤 — {startDate} to {endDate}

### Snapshot
| Metric | Value |
|--------|-------|
| Total fills | {fillCount} |
| Maker share | {makerPct}% |
| Taker share | {takerPct}% |
| Avg slippage | {avgSlipBps} bps |
| Fee drag | ${feeDrag} |

### Findings
- `[+]` {best_execution_finding_with_evidence}
- `[-]` {worst_execution_finding_with_evidence}
- `[!]` {main_slippage_or_order_quality_warning}

### Next Steps
- `比對單筆交易的進出場`
- `查看費用分析`
```

## 6. COST — Cost Review

```markdown
## 成本複盤 — {startDate} to {endDate}

### Cost Snapshot
| Metric | Value |
|--------|-------|
| Trading Fees | ${fees} |
| Funding | ${funding} |
| Liq. Penalties | ${liqPenalty} |
| Total Costs | ${totalCosts} |
| Cost / Gross Win | {costPct}% |

### Findings
- `[-]` {largest_cost_drag_with_evidence}
- `[-]` {second_cost_drag_with_evidence}
- `[+]` {best_cost_discipline_finding}

### Next Steps
- `查看交易模式`
- `匯出 CSV`
```

## 7. PATTERN — Pattern Review

```markdown
## 交易模式複盤 — {startDate} to {endDate}

### High-Signal Patterns
- `[+]` {best_pattern_with_evidence}
- `[-]` {worst_pattern_with_evidence}
- `[!]` {low_confidence_or_concentration_warning}

### Buckets
- Instrument：{instrument_summary}
- Direction：{direction_summary}
- Hold Duration：{duration_summary}
- Session：{session_summary}

### Next Steps
- `查看對應的代表性交易`
- `匯出完整報告`
```

## 8. JOURNAL — Artifact Response

```markdown
## 已生成交易複盤工件

- Markdown：`{markdownPath}`
- CSV：`{csvPath}`
- SVG：`{svgPath_or_not_requested}`

### Included
- 摘要與詳報
- 選中交易深挖
- Enriched trade ledger

### If file generation is unavailable
- 直接在聊天內返回 markdown 內容
- 將 CSV 內容放入 ```csv fenced block
```

## 9. Markdown Artifact Template

Use this for exported `.md` reports. It can be longer than the chat version.

```markdown
# OKX Trade Review — {startDate} to {endDate} [{DEMO|LIVE}]

## Executive Summary
- {summary_bullets}

## Scorecard
| Metric | Value |
|--------|-------|
| Net PnL | {netPnl} |
| Win Rate | {winRate}% |
| Profit Factor | {pf} |
| Expectancy | {expectancy} |
| Max Drawdown | {maxDd} |
| Total Costs | {totalCosts} |

## What Drove PnL
- {drivers}

## What Hurt
- {hurts}

## Market Context
- {context_summary}

## Behavior Patterns
- {pattern_summary}

## Action Adjustments
- {actions}

## Selected Trade Deep Dives
### {instId} — {openTime}
- Regime: `{regimeTag}`
- Alignment: `{trendAlignment}`
- Entry timing: `{entryTimingTag}`
- MAE/MFE/Capture: {maePct}% / {mfePct}% / {capturePct}%
- Review: {trade_commentary}

## Appendix — Enriched Ledger
| Close Time | Instrument | Dir | Net PnL | Costs | Tags |
|------------|------------|-----|---------|-------|------|
| {closeTime} | {instId} | {direction} | {realizedPnl} | {costs} | {tags} |
```

## 10. Shared Components

### Sparkline

Use `▁▂▃▄▅▆▇█` for daily PnL, equity, or capture trends.

Example:

```text
Daily PnL: ▁▃▂▅█▄▆
```

### 10-Character Bar

Use a fixed-width 10-character bar for comparisons.

Example:

```text
BTC   +$1,520  ████████░░
ETH   +$620    ████░░░░░░
SOL   -$240    ██░░░░░░░░
```

### Small Tables Only

Use 2-column or 3-column tables in chat. Move wide ledgers to the exported
markdown or CSV.
