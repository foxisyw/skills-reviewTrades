# Bias Detection Algorithms

This document defines the 7 behavioral bias detection algorithms for the 交易紀律小簿.
Each bias has quantitative thresholds, worked examples, and severity levels.

## Global Evidence Rules

| Rule | Value |
|------|-------|
| MIN_SAMPLE_ABSOLUTE | 3 trades matching the pattern |
| MIN_SAMPLE_RELATIVE | 20% of the total sample |
| MIN_TRADES_ANY_ANALYSIS | 5 trades total |

Below MIN_TRADES_ANY_ANALYSIS: refuse analysis with `需要至少 5 筆交易才能分析`.
Below MIN_SAMPLE_ABSOLUTE for a specific bias: label `低樣本` and note the gap.

## Confidence Levels

| Level | Criteria |
|-------|----------|
| LOW | 5-14 total trades, OR pattern count equals threshold exactly |
| MEDIUM | 15-49 total trades, AND pattern count >= 1.5x threshold |
| HIGH | 50+ total trades, AND pattern count >= 2x threshold |

Report confidence alongside every bias finding.

## Severity Levels

| Level | Label | Action |
|-------|-------|--------|
| HEALTHY | 健康 | No concern |
| CONCERNING | 需注意 | Monitor and adjust |
| CRITICAL | 嚴重 | Immediate behavioral change needed |

---

## 1. Loss Aversion (損失厭惡)

### Definition
Holding losers too long while cutting winners too short. The trader fears realizing
losses, leading to asymmetric hold times and poor capture rates.

### Required Data
- Trades with `pnl > 0` (winners) and `pnl < 0` (losers)
- `durationHours` for each trade
- `capturePct` for enriched trades
- `maePct` for enriched losers

### Minimum Sample
At least 3 winners AND 3 losers.

### Metrics

#### Duration Ratio
```
median_winner_duration = median(durationHours where pnl > 0)
median_loser_duration  = median(durationHours where pnl < 0)
duration_ratio         = median_loser_duration / median_winner_duration
```

Note: Use median instead of mean to prevent one outlier swing trade (e.g., 100h)
from skewing the ratio. If the sample includes both scalp (<1h) and swing (>24h)
trades, segment by `holdBucket` before computing and report separately.

| duration_ratio | Severity |
|----------------|----------|
| < 1.3 | HEALTHY |
| 1.3 - 2.0 | CONCERNING |
| > 2.0 | CRITICAL |

#### Capture Rate (Winners Only)
```
avg_capture_winners = mean(capturePct where pnl > 0 AND capturePct is not null)
```

Use regime-adjusted thresholds:

**If majority of trades in `trend_up` or `trend_down` regime:**

| avg_capture_winners | Severity |
|---------------------|----------|
| > 40% | HEALTHY |
| 20% - 40% | CONCERNING |
| < 20% | CRITICAL |

**If majority of trades in `range` regime:**

| avg_capture_winners | Severity |
|---------------------|----------|
| > 30% | HEALTHY |
| 15% - 30% | CONCERNING |
| < 15% | CRITICAL |

**Default (mixed or unknown regime):**

| avg_capture_winners | Severity |
|---------------------|----------|
| > 50% | HEALTHY |
| 30% - 50% | CONCERNING |
| < 30% | CRITICAL |

#### MAE Proximity (Losers Only)
```
For each loser with maePct data:
  loser_mae_proximity = abs(realized_loss_pct) / maePct
  (closer to 1.0 means exited at or near maximum pain)

avg_loser_mae_proximity = mean(loser_mae_proximity for all qualifying losers)
```

#### Composite Loss Aversion Score (LAS)
```
LAS = (duration_ratio * 0.5)
    + ((100 - avg_capture_winners) / 50 * 0.3)
    + (avg_loser_mae_proximity * 0.2)

LAS_normalized = clamp(LAS * 2.5, 0, 10)
```

### Worked Example

Given 10 trades (5 winners, 5 losers):
- avg_winner_duration = 4.2h, avg_loser_duration = 8.6h → duration_ratio = 2.05 (CRITICAL)
- avg_capture_winners = 28% (CRITICAL)
- avg_loser_mae_proximity = 0.88

LAS = (2.05 * 0.5) + ((100 - 28)/50 * 0.3) + (0.88 * 0.2)
    = 1.025 + 0.432 + 0.176 = 1.633
LAS_normalized = clamp(1.633 * 2.5, 0, 10) = 4.08

Report: LAS 4.08/10, 需注意 severity.

---

## 2. Revenge Trading (報復性交易)

### Definition
Opening a new trade shortly after a loss, often with higher leverage or opposite
direction, driven by the desire to "get back" the lost money.

### Required Data
- Sorted trades by `openTime`
- `pnl` for each trade
- `leverage` for each trade
- `instId` base asset extraction

### Time Window (T_REVENGE)
| Hold Bucket of Losing Trade | T_REVENGE |
|------------------------------|-----------|
| < 1h (scalp) | 1 hour |
| 1h - 12h (default) | 2 hours |
| > 12h (swing) | 4 hours |

### Metrics

#### Revenge Candidate Detection

Asset groups for correlated-asset revenge detection:
```
BTC_GROUP = {BTC}
ETH_GROUP = {ETH}
ALT_GROUP = {SOL, AVAX, DOGE, PEPE, WIF, ...}  # all non-BTC/ETH alts
```

```
For each losing trade L:
  T = T_REVENGE based on L's holdBucket
  base_asset_L = extract base asset from L.instId (e.g., "BTC" from "BTC-USDT-SWAP")
  group_L = asset group of base_asset_L

  For each trade N opened within T hours after L.closeTime:
    base_asset_N = extract base asset from N.instId

    if base_asset_N == base_asset_L:
      mark N as revenge_candidate (HIGH confidence)
    elif group(base_asset_N) == group_L:
      mark N as revenge_candidate (LOW confidence)
      # e.g., loss on SOL → re-entry on AVAX within T
    elif (base_asset_L in BTC_GROUP and base_asset_N in ETH_GROUP) or vice versa:
      mark N as possible_revenge (LOW confidence)
      # e.g., loss on BTC → re-entry on ETH within T

revenge_rate = count(revenge_candidates) / count(losing_trades)
# Report HIGH and LOW confidence candidates separately
```

| revenge_rate | Severity |
|--------------|----------|
| < 15% | HEALTHY |
| 15% - 35% | CONCERNING |
| > 35% | CRITICAL |

#### Leverage Escalation After Loss
```
For each revenge_candidate N following loser L:
  escalation = (N.leverage - L.leverage) / L.leverage * 100
  if escalation > 20%: flag as leverage_escalation
```

#### Contrarian Re-entry
```
For each revenge_candidate N following loser L:
  if N.direction != L.direction AND N.instId == L.instId:
    flag as contrarian_reentry
```

#### Revenge Win Rate vs Normal Win Rate
```
revenge_winrate = count(revenge_candidates where pnl > 0) / count(revenge_candidates)
normal_winrate  = count(non-revenge trades where pnl > 0) / count(non-revenge trades)

Report both and the delta.
```

### Worked Example

15 losing trades, 4 followed by same-asset trades within T_REVENGE:
- revenge_rate = 4/15 = 26.7% (CONCERNING)
- 2 of 4 had leverage escalation > 20%
- 1 was a contrarian re-entry
- Revenge win rate: 1/4 = 25% vs normal: 55% → significant underperformance

---

## 3. Overconfidence (過度自信)

### Definition
After a winning streak, the trader increases leverage or abandons disciplined
entry/exit rules, believing their edge is larger than it actually is.

### Required Data
- Sequential trades sorted by `closeTime`
- `leverage` for each trade
- Reflection data: `entryReason`, `stopLossRationale`, `emotion`

### Minimum Sample
At least one winning streak of >= 3 trades.

### Metrics

#### Leverage Escalation After Winning Streak
```
For each winning streak of >= 3 consecutive winners:
  avg_leverage_streak = mean(leverage during streak)
  next_3 = next 3 trades after streak
  avg_leverage_next_3 = mean(leverage of next_3)

  escalation_pct = (avg_leverage_next_3 - avg_leverage_streak) / avg_leverage_streak * 100
```

Absolute leverage guard: escalation is only CONCERNING or CRITICAL if
`avg_leverage_next_3 > 5x`. Below 5x, the trader is within conservative
bounds regardless of percentage escalation.

| escalation_pct | avg_leverage_next_3 | Severity |
|----------------|---------------------|----------|
| any | <= 5x | HEALTHY |
| < 25% | > 5x | HEALTHY |
| 25% - 50% | > 5x | CONCERNING |
| > 50% | > 5x | CRITICAL |

#### Discipline Degradation
```
For trades in a winning streak:
  structured_score = 1 if (stopLossRationale in [preset, support, ma_broken, trailing]
                          AND entryReason not in [fomo, intuition])
                    else 0
  pre_discipline = mean(structured_score during streak)

For next 3 trades after streak:
  post_discipline = mean(structured_score for next_3)

  degradation = pre_discipline - post_discipline
```

| degradation | Severity |
|-------------|----------|
| < 0.33 | HEALTHY |
| 0.33 - 0.66 | CONCERNING |
| > 0.66 | CRITICAL |

### Worked Example

Winning streak of 4 trades: avg leverage 5x, all with preset SL and indicator entries.
Next 3 trades: avg leverage 9x, 2 with FOMO entries, 1 with no SL.
- escalation_pct = (9 - 5) / 5 * 100 = 80% (CRITICAL)
- pre_discipline = 1.0, post_discipline = 0.0, degradation = 1.0 (CRITICAL)

---

## 4. FOMO Trading (追漲殺跌)

### Definition
Entering trades driven by fear of missing out, typically chasing moves that have
already happened, resulting in poor entry prices.

### Required Data
- `entryReason` from reflection (or inferred from `entryTimingTag`)
- `emotion` from reflection
- `openTime` for cluster detection
- `pnl` for performance comparison

### Metrics

#### FOMO Rate
```
fomo_trade = (entryReason == "fomo" OR emotion == "fomo" OR entryTimingTag == "chase")
fomo_rate = count(fomo_trades) / total_trades * 100
```

| fomo_rate | Severity |
|-----------|----------|
| < 10% | HEALTHY |
| 10% - 25% | CONCERNING |
| > 25% | CRITICAL |

#### FOMO vs Non-FOMO Performance
```
fomo_avg_pnl     = mean(pnl where fomo_trade == true)
non_fomo_avg_pnl = mean(pnl where fomo_trade == false)

Report both and the delta.
```

#### FOMO Cluster Detection

Use a volatility-adaptive window instead of a fixed 4h to account for
crypto's 24/7 market structure:

```
base_window = 4 hours

If candle data is available for the cluster period:
  recent_move = max price move in the past 4h (from candle highs/lows)
  if recent_move > 3%: window = 6 hours  # volatile market, widen window
  else: window = base_window

For each {window}-hour sliding window:
  trades_in_window = trades with openTime within the window
  if count(trades_in_window) >= 3:
    fomo_pct_in_window = count(fomo_trades in window) / count(trades_in_window)
    if fomo_pct_in_window >= 50%:
      flag as fomo_cluster
      report: timestamp range, trade count, aggregate PnL, market_move_pct
```

### Worked Example

30 trades total, 9 flagged as FOMO:
- fomo_rate = 9/30 = 30% (CRITICAL)
- FOMO avg PnL: -$85/trade vs non-FOMO avg PnL: +$42/trade
- 1 cluster: 2026-03-05 14:00-18:00, 4 trades, 3 FOMO, aggregate PnL -$520

---

## 5. Emotional Stop-Loss (情緒化止損)

### Definition
Exiting losing trades based on fear/panic rather than a predetermined stop level,
often at or near the point of maximum adverse excursion (worst price).

### Required Data
- `stopLossRationale` from reflection
- `exitReason` from reflection
- `maePct` from market context
- `pnl` for each trade

### Metrics

#### Emotional Exit Rate
```
emotional_exits = count(stopLossRationale == "emotional" OR exitReason == "emotional")
emotional_exit_rate = emotional_exits / count(losers) * 100
```

#### Emotional vs Structured Exit Win Rate
```
emotional_exit_winrate   = winrate of trades with emotional exit
structured_exit_winrate  = winrate of trades with non-emotional exit

winrate_gap = structured_exit_winrate - emotional_exit_winrate
```

| winrate_gap | Severity |
|-------------|----------|
| < 15pp | CONCERNING |
| >= 15pp | CRITICAL |

#### MAE Proximity (Exit at Pain)
```
For each losing trade with maePct data:
  realized_loss_pct = abs(pnl / (entryPrice * size)) * 100   # or use provided metric
  mae_proximity = realized_loss_pct / maePct
  (closer to 1.0 = exited at or near maximum pain point)

exit_at_pain_rate = count(mae_proximity > 0.85) / count(losers_with_mae)
```

| exit_at_pain_rate | Severity |
|-------------------|----------|
| < 20% | HEALTHY |
| 20% - 40% | CONCERNING |
| > 40% | CRITICAL |

### Worked Example

20 losing trades, 8 with emotional exit:
- emotional_exit_rate = 40%
- Emotional exit winrate: 15% vs structured: 42% → gap = 27pp (CRITICAL)
- 6 of 8 emotional exits had mae_proximity > 0.85 → exit_at_pain_rate = 75% (CRITICAL)

---

## 6. Disposition Effect (處置效應)

### Definition
Selling winners too early to "lock in gains" while holding losers too long hoping
they recover. The classic bias documented by Shefrin & Statman (1985).

### Required Data
- `capturePct` for winners
- `maePct` for losers
- `exitReason` and `emotion` from reflection
- `pnl` for classification

### Metrics

#### Disposition Effect Index (DEI)
```
avg_loss_to_mae = mean(abs(realized_loss_pct) / maePct) for losers with mae data
  (high = held losers close to max pain)

avg_capture_winners = mean(capturePct where pnl > 0) / 100
  (low = cut winners short)

DEI = avg_loss_to_mae - avg_capture_winners
```

| DEI | Severity |
|-----|----------|
| < 0 | HEALTHY (capturing more of winners than absorbing of losers) |
| 0 - 0.3 | CONCERNING |
| > 0.3 | CRITICAL |

#### Relief Exit Rate
```
relief_exit = trade where:
  - emotion or exitReason contains "relief" or exitReason == "take_profit"
  - capturePct < 30
  - pnl > 0

relief_on_small_win = count(relief_exits) / count(winners)
```

| relief_on_small_win | Severity |
|---------------------|----------|
| < 0.15 | HEALTHY |
| 0.15 - 0.30 | CONCERNING |
| > 0.30 | CRITICAL |

### Worked Example

Winners: avg capturePct = 22%, many exits at small profit with "take_profit" reason.
Losers: avg loss_to_mae = 0.78 (held close to max pain).
- DEI = 0.78 - 0.22 = 0.56 (CRITICAL)
- 5 of 12 winners exited with capturePct < 30 and take_profit → relief rate = 42% (CRITICAL)

---

## 7. Overtrading (過度交易)

### Definition
Trading too frequently, often from boredom or compulsive behavior, leading to
degraded decision quality, accumulated costs, and "death by a thousand cuts."

### Required Data
- Trades grouped by calendar date (UTC)
- `pnl` for each trade
- `totalCosts` for each trade
- `emotion` from reflection (optional)

### Metrics

#### High Frequency Day Detection
```
trading_days = count(distinct dates with at least 1 trade)
baseline_freq = total_trades / trading_days
daily_counts = {date: count of trades on that date}

high_freq_days = count(days where daily_count > 2 * baseline AND daily_count >= 3)
high_freq_rate = high_freq_days / trading_days
```

| high_freq_rate | Severity |
|----------------|----------|
| < 10% | HEALTHY |
| 10% - 25% | CONCERNING |
| > 25% | CRITICAL |

#### Frequency-Performance Correlation
```
Classify each trading day:
  low_freq:  daily_count <= baseline * 0.5
  mid_freq:  baseline * 0.5 < daily_count <= baseline * 2
  high_freq: daily_count > baseline * 2

winrate_low  = winrate of trades on low_freq days
winrate_mid  = winrate of trades on mid_freq days
winrate_high = winrate of trades on high_freq days

winrate_drop = winrate_mid - winrate_high
```

| winrate_drop | Severity |
|--------------|----------|
| < 10pp | HEALTHY |
| 10pp - 20pp | CONCERNING |
| > 20pp | CRITICAL |

#### Death by 1000 Cuts
```
small_loss_threshold = min(abs(avg_loser) * 0.3, $50)  # whichever is lower
small_losses = count(trades where pnl < 0 AND abs(pnl) <= small_loss_threshold)
small_loss_rate = small_losses / total_trades
```

| small_loss_rate | Severity |
|-----------------|----------|
| < 15% | HEALTHY |
| 15% - 30% | CONCERNING |
| > 30% | CRITICAL |

### Worked Example

40 trades over 12 trading days (baseline = 3.3/day):
- 4 days had 7+ trades → high_freq_rate = 4/12 = 33% (CRITICAL)
- Winrate on high-freq days: 28% vs mid-freq: 52% → drop = 24pp (CRITICAL)
- 14 trades with loss < $15 → small_loss_rate = 35% (CRITICAL)

---

## Composite Bias Score

### Calculation
```
For each of the 7 biases:
  Map severity to score: HEALTHY = 0, CONCERNING = 5, CRITICAL = 10
  Use the highest severity metric within each bias

max_score = max(scores of all analyzed biases)
mean_score = mean(scores of all analyzed biases)

# Use max_score for the headline severity label
# Report mean_score as secondary context
# This prevents averaging 2 CRITICAL + 3 HEALTHY = "minor" which is misleading
```

### Interpretation (based on max_score)

| max_score | Label | Meaning |
|-----------|-------|---------|
| 0 | 紀律優秀 | No behavioral biases detected |
| 5 | 需要注意 | At least one bias at concerning level |
| 10 | 嚴重偏差 | At least one critical bias requiring immediate change |

Secondary context (based on mean_score):

| mean_score | Context |
|------------|---------|
| 0 - 3 | 整體紀律良好 — overall discipline is good |
| 3 - 5 | 多項輕微偏差 — multiple minor biases |
| 5 - 7 | 多項偏差需注意 — multiple biases at concerning level |
| 7 - 10 | 多項嚴重偏差 — widespread critical biases |

### Report Structure

For each bias:
1. **Severity label** with confidence level
2. **Key metric** (the primary number)
3. **Evidence** (specific trades or patterns cited)
4. **Suggestion** (one concrete action to mitigate)

Report healthy patterns too — positive reinforcement matters.

---

## Bias Snapshot Schema

Saved to `data/discipline-journal/bias-snapshots/{date}.json`:

```json
{
  "date": "2026-03-10",
  "account": "demo",
  "tradeSample": {
    "total": 47,
    "dateRange": ["2026-02-01", "2026-03-10"],
    "winnersCount": 22,
    "losersCount": 25
  },
  "compositeScore": 5.2,
  "compositeLabel": "需要注意",
  "biases": {
    "loss_aversion": {
      "severity": "CONCERNING",
      "confidence": "MEDIUM",
      "metrics": {
        "duration_ratio": 1.65,
        "avg_capture_winners": 38.2,
        "LAS_normalized": 4.1
      },
      "suggestion": "Set take-profit targets before entry to avoid cutting winners short."
    },
    "revenge_trading": {
      "severity": "HEALTHY",
      "confidence": "MEDIUM",
      "metrics": {
        "revenge_rate": 8.0
      },
      "suggestion": null
    }
  }
}
```
