# Market Context Enrichment

This document defines how to enrich OKX trade records with time-aligned market
data. The goal is to make trade review explain not only the result of a trade,
but also the price structure and opportunity set around that trade.

## Principles

- Use deterministic rules. Do not rely on discretionary chart reading.
- Prefer missing data over invented context. If candle coverage is incomplete,
  return `N/A`.
- Keep the same formulas for chat review and exported artifacts.

## Candle Interval Selection

Choose the candle interval from the trade holding duration:

| Holding duration | Candle interval | Pre-entry buffer |
|------------------|-----------------|------------------|
| `<= 4h` | `5m` | `3h` |
| `> 4h` and `<= 24h` | `15m` | `6h` |
| `> 24h` and `<= 7d` | `1H` | `24h` |
| `> 7d` | `4H` | `72h` |

Fetch from:

- `begin = entry_time - pre_entry_buffer`
- `end = close_time`

The pre-entry buffer is required to judge whether the entry followed a move,
faded a move, or entered in a flat context.

## Required Candle Fields

From `market_get_candles`, parse:

- timestamp
- open
- high
- low
- close

Sort candles in ascending timestamp order before computing any field.

## Derived Fields

### 1. `preEntryMovePct`

Measure the market move leading into the trade:

```text
preEntryMovePct = (entry_reference_close - pre_entry_anchor_close) / pre_entry_anchor_close * 100
```

Where:

- `pre_entry_anchor_close` = first close in the fetched candle window
- `entry_reference_close` = last close before or at `entry_time`

Interpretation:

- Positive means price rose into the entry
- Negative means price fell into the entry

### 2. `maePct`

Maximum adverse excursion during the trade, expressed as a positive percentage.

For longs:

```text
maePct = max(0, (entry_price - min_low_during_trade) / entry_price * 100)
```

For shorts:

```text
maePct = max(0, (max_high_during_trade - entry_price) / entry_price * 100)
```

### 3. `mfePct`

Maximum favorable excursion during the trade, expressed as a positive
percentage.

For longs:

```text
mfePct = max(0, (max_high_during_trade - entry_price) / entry_price * 100)
```

For shorts:

```text
mfePct = max(0, (entry_price - min_low_during_trade) / entry_price * 100)
```

### 4. `capturePct`

How much of the favorable move the trade actually captured.

First compute directional realized move:

For longs:

```text
realizedMovePct = (exit_price - entry_price) / entry_price * 100
```

For shorts:

```text
realizedMovePct = (entry_price - exit_price) / entry_price * 100
```

Then compute:

```text
capturePct = max(realizedMovePct, 0) / mfePct * 100
```

Rules:

- If `mfePct <= 0.05`, return `N/A`
- Do not clamp values above `100`; over-capture can happen from coarse candles

## Regime Classification

Classify the local trade window as `trend_up`, `trend_down`, or `range`.

First compute:

```text
netChangePct = (last_close_during_trade - first_close_during_trade) / first_close_during_trade * 100
rangePct = (max_high_during_trade - min_low_during_trade) / first_close_during_trade * 100
```

Trend thresholds by candle interval:

| Candle interval | Trend threshold |
|-----------------|-----------------|
| `5m` | `0.8%` |
| `15m` | `1.2%` |
| `1H` | `2.0%` |
| `4H` | `3.0%` |

Classification:

- `trend_up` when:
  - `netChangePct >= trend_threshold`
  - and `abs(netChangePct) >= rangePct * 0.35`
- `trend_down` when:
  - `netChangePct <= -trend_threshold`
  - and `abs(netChangePct) >= rangePct * 0.35`
- Otherwise `range`

## Trend Alignment

Compare the trade direction with the classified regime:

- Long + `trend_up` -> `aligned`
- Short + `trend_down` -> `aligned`
- Long + `trend_down` -> `countertrend`
- Short + `trend_up` -> `countertrend`
- Any trade in `range` -> `neutral`

## Entry Timing Tag

Judge whether the entry chased a move, entered on a pullback, or entered in a
neutral context.

Entry timing thresholds by candle interval:

| Candle interval | Timing threshold |
|-----------------|------------------|
| `5m` | `0.6%` |
| `15m` | `0.9%` |
| `1H` | `1.5%` |
| `4H` | `2.5%` |

For longs:

- `chase` when `preEntryMovePct >= timing_threshold`
- `pullback` when `preEntryMovePct <= -timing_threshold`
- otherwise `neutral`

For shorts:

- `chase` when `preEntryMovePct <= -timing_threshold`
- `pullback` when `preEntryMovePct >= timing_threshold`
- otherwise `neutral`

## Review Use Rules

- Mention `regimeTag`, `trendAlignment`, and `entryTimingTag` together when
  drawing conclusions from market context.
- Use `maePct`, `mfePct`, and `capturePct` to distinguish:
  - bad idea vs bad execution
  - good idea with poor exit
  - early entry vs late entry
- Do not generalize a market-context pattern unless it passes the review
  sample-size rules in `SKILL.md`.
