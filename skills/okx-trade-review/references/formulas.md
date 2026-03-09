# Statistical Formulas for Trade Review

## Table of Contents
1. [Core Metrics](#1-core-metrics)
2. [Risk Metrics](#2-risk-metrics)
3. [Execution Metrics](#3-execution-metrics)
4. [Pattern Metrics](#4-pattern-metrics)

---

## 1. Core Metrics

### Win Rate
```
win_rate = winning_trades / total_trades
```
- A trade is "winning" if `realizedPnl > 0`
- Express as percentage (e.g. 61.5%)

### Average Winner / Average Loser
```
avg_winner = sum(pnl where pnl > 0) / count(pnl > 0)
avg_loser  = sum(pnl where pnl < 0) / count(pnl < 0)
```

### Win/Loss Ratio (Payoff Ratio)
```
win_loss_ratio = abs(avg_winner) / abs(avg_loser)
```
- >1.0 means winners are larger than losers on average
- Ideal: >2.0

### Profit Factor
```
profit_factor = gross_profit / abs(gross_loss)
```
- Where `gross_profit = sum(pnl where pnl > 0)`
- And `gross_loss = sum(pnl where pnl < 0)`
- >1.0 = profitable, >1.75 = good, >2.5 = excellent
- If gross_loss = 0, return Infinity (all trades won)

### Expectancy (per trade)
```
expectancy = (win_rate * avg_winner) + ((1 - win_rate) * avg_loser)
```
- Positive = system is profitable on average
- This is the expected value per trade

### R-Multiple (per trade)
```
initial_risk = abs(entry_price - stop_loss_price) * position_size
R_multiple = realized_pnl / initial_risk
```
- Requires stop-loss data from order history (`slTriggerPx`)
- If no SL set: R-Multiple = N/A
- +2.0R means profit was 2x the initial risk
- -1.0R means the full initial risk was lost

### Average R-Multiple
```
avg_R = sum(R_multiples) / count(R_multiples)
```
- Only computed for trades with valid R-multiple

### Expectancy in R
```
expectancy_R = (win_rate * avg_win_R) + ((1 - win_rate) * avg_loss_R)
```

### System Quality Number (SQN)
```
SQN = (avg_R / stdev_R) * sqrt(min(N, 100))
```
- N = number of trades (minimum 30 for validity)
- Capped at sqrt(100) to prevent sample size inflation
- Rating: <1.6 poor, 1.6-2.0 below avg, 2.0-2.5 avg, 2.5-3.0 good, >3.0 excellent

---

## 2. Risk Metrics

### Max Drawdown
```
For each trade i (sorted chronologically):
  equity[i] = equity[i-1] + pnl[i]
  peak[i] = max(peak[i-1], equity[i])
  drawdown[i] = equity[i] - peak[i]

max_drawdown_abs = min(drawdown[])           # most negative value
max_drawdown_pct = max_drawdown_abs / peak_at_max_drawdown * 100
```
- Track when it started (peak timestamp) and when it ended (recovery timestamp)
- Duration = recovery timestamp - peak timestamp

### Sharpe Ratio (annualized)
```
daily_returns[] = daily_pnl / starting_equity_that_day
sharpe = mean(daily_returns) / stdev(daily_returns) * sqrt(365)
```
- Crypto markets are 365 days (24/7)
- Risk-free rate assumed 0 for crypto (can adjust)
- >1.0 acceptable, >2.0 excellent

### Sortino Ratio
```
downside_returns = daily_returns where daily_returns < 0
downside_stdev = stdev(downside_returns)
sortino = mean(daily_returns) / downside_stdev * sqrt(365)
```
- Like Sharpe but only penalizes downside volatility

### Calmar Ratio
```
calmar = annualized_return / abs(max_drawdown_pct)
```
- >1.0 good, >3.0 excellent

### Leverage Analysis
```
avg_leverage = mean(lever for each position)
max_leverage = max(lever for each position)
leverage_distribution = histogram of lever values in buckets [1-3x, 3-5x, 5-10x, 10-20x, 20x+]
```

### Liquidation Proximity
```
For each position:
  liq_distance_pct = abs(entry_price - liq_price) / entry_price * 100
```
- If `liqPx` data available from active positions; for historical, estimate from leverage:
  - Isolated: `liq_distance ≈ 1/leverage * 100` (simplified)
  - Cross: depends on total account balance (harder to compute historically)

### Position Sizing
```
position_notional = open_max_pos * entry_price (or use notionalUsd if available)
position_pct_of_equity = position_notional / account_equity * 100
```

### Concentration Risk
```
For each instrument:
  instrument_exposure = sum(abs(position_notional)) for that instrument
  concentration_pct = instrument_exposure / total_exposure * 100
```
- Herfindahl index: `HHI = sum(concentration_pct^2)` — higher = more concentrated

---

## 3. Execution Metrics

### Slippage
```
For entry fills:
  entry_slippage = fill_price - limit_order_price  (for limits)
  entry_slippage = fill_price - index_price_at_fill  (for markets, use fillIdxPx)

For exit fills:
  exit_slippage = similar calculation

avg_slippage = mean(all slippages)
slippage_cost = sum(abs(slippage) * fill_size)
```

### Maker/Taker Ratio
```
maker_volume = sum(fillSz where execType = 'M')
taker_volume = sum(fillSz where execType = 'T')
maker_pct = maker_volume / (maker_volume + taker_volume) * 100
```
- Higher maker % = lower fees (maker often gets rebate)

### Maker/Taker Fee Impact
```
maker_fees = sum(fee where execType = 'M')  # often positive (rebate)
taker_fees = sum(fee where execType = 'T')  # always negative (cost)
net_fee_impact = maker_fees + taker_fees
```

---

## 4. Pattern Metrics

### Performance by Dimension
For any dimension (instrument, direction, leverage bucket, hold duration, time-of-day):

```
For each category in dimension:
  trades = filter positions by category
  category_win_rate = win_rate(trades)
  category_avg_pnl = mean(pnl of trades)
  category_total_pnl = sum(pnl of trades)
  category_profit_factor = profit_factor(trades)
  category_avg_R = avg_R(trades)  # if R data available
```

### Hold Duration Analysis
```
duration_hours = (uTime - cTime) / 3600000
duration_buckets: [<1h, 1-4h, 4-12h, 12-24h, 1-3d, 3-7d, >7d]
```

### Time-of-Day Analysis
```
entry_hour = new Date(cTime).getUTCHours()
session_buckets:
  Asian:    00:00-08:00 UTC
  European: 08:00-16:00 UTC
  US:       16:00-00:00 UTC
```

### Consecutive Wins/Losses
```
max_consec_wins = longest streak of consecutive winning trades
max_consec_losses = longest streak of consecutive losing trades
current_streak = current streak type and length
```

### Kelly Criterion (informational)
```
kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
```
- Theoretical optimal position size as % of bankroll
- Usually apply fractional Kelly (e.g. kelly_pct * 0.25) for safety
- Only show as informational — not a recommendation
