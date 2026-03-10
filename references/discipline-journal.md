# Discipline Journal — Storage & Reflection Schema

This document defines the persistence layer for the 交易紀律小簿 (Trading Discipline
Notebook): structured reflections, entry lifecycle, field enums, and indexing rules.

## Directory Layout

```
data/discipline-journal/
  index.json                                         # Master index (lean)
  entries/
    {ISO-timestamp}_{scope}.json                     # One file per reflection
  bias-snapshots/
    {YYYY-MM-DD}.json                                # Periodic bias analysis cache
```

### Filename Convention

- Single-trade: `2026-03-10T14-30-00Z_posId-12345.json`
- Period: `2026-03-10T15-00-00Z_period-20260301-20260307.json`
- Colons replaced with hyphens for filesystem safety.

## index.json Schema

```json
{
  "version": "1.0.0",
  "totalEntries": 47,
  "entries": [
    {
      "id": "2026-03-10T14-30-00Z_posId-12345",
      "type": "single",
      "posId": "12345",
      "instId": "BTC-USDT-SWAP",
      "account": "demo",
      "createdAt": "2026-03-10T14:30:00Z",
      "tags": ["loss_aversion"],
      "pnl": -450.00,
      "direction": "long",
      "selfRating": 3
    }
  ]
}
```

The index is intentionally lean — only fields needed for filtering and display.
Full reflection data lives in the entry file.

## Entry File Schema

```json
{
  "id": "2026-03-10T14-30-00Z_posId-12345",
  "type": "single",
  "createdAt": "2026-03-10T14:30:00Z",
  "updatedAt": "2026-03-10T14:30:00Z",

  "tradeContext": {
    "posId": "12345",
    "instId": "BTC-USDT-SWAP",
    "account": "demo",
    "direction": "long",
    "leverage": 10,
    "entryPrice": 84250.0,
    "exitPrice": 83800.0,
    "pnl": -450.00,
    "realizedPnl": -496.75,
    "durationHours": 2.5,
    "closeType": "manual",
    "regimeTag": "range",
    "trendAlignment": "neutral",
    "entryTimingTag": "chase",
    "maePct": 1.8,
    "mfePct": 0.6,
    "capturePct": 0
  },

  "reflection": {
    "entryReason": "fomo",
    "entryReasonDetail": "",
    "timeframe": "5m",
    "stopLossRationale": "emotional",
    "stopLossRationaleDetail": "",
    "emotion": "fomo",
    "emotionDetail": "",
    "exitReason": "emotional",
    "exitReasonDetail": "",
    "lessonLearned": "Should have waited for pullback confirmation instead of chasing the breakout.",
    "wouldRepeat": false,
    "selfRating": 2
  },

  "biasFlags": ["loss_aversion", "fomo"],
  "biasDetails": {
    "loss_aversion": "Exited near MAE; duration_ratio suggests early panic exit.",
    "fomo": "Entry reason flagged as FOMO; chase entry timing confirmed."
  },

  "newsContext": {
    "available": false,
    "items": []
  },

  "periodContext": null
}
```

### Period Entry Variant

For `type: "period"`, `tradeContext` is replaced by `periodContext`:

```json
{
  "id": "2026-03-10T15-00-00Z_period-20260301-20260307",
  "type": "period",
  "createdAt": "2026-03-10T15:00:00Z",

  "periodContext": {
    "startDate": "2026-03-01",
    "endDate": "2026-03-07",
    "account": "demo",
    "totalTrades": 23,
    "netPnl": -1250.00,
    "winRate": 39.1
  },

  "reflection": {
    "biggestDisciplineIssue": "Revenge trading after consecutive losses on Tuesday.",
    "nextImprovement": "Set a hard 3-trade daily loss limit.",
    "selfRating": 3
  },

  "biasFlags": ["revenge_trading", "overconfidence"],
  "biasDetails": {},
  "newsContext": { "available": false, "items": [] },
  "tradeContext": null
}
```

## Reflection Field Enums

### Single-Trade Reflection

| Field | Enum Values | Allows free text |
|-------|-------------|------------------|
| `entryReason` | `breakout`, `indicator`, `template`, `programmatic`, `intuition`, `fomo`, `grid_dca`, `copy_signal`, `liquidation_bounce`, `other` | Yes, in `entryReasonDetail` |
| `timeframe` | `1m`, `5m`, `15m`, `1H`, `4H`, `1D` | No |
| `stopLossRationale` | `ma_broken`, `preset`, `support`, `trailing`, `liquidation_level`, `atr_volatility`, `sized_for_max_loss`, `emotional`, `none` | Yes, in `stopLossRationaleDetail` |
| `emotion` | `calm`, `fomo`, `fear`, `revenge`, `overconfidence`, `boredom` | Yes, in `emotionDetail` |
| `exitReason` | `stop_loss`, `take_profit`, `trailing_stop`, `manual`, `partial_close`, `forced_liquidation`, `emotional`, `other` | Yes, in `exitReasonDetail` |
| `lessonLearned` | — | Free text |
| `wouldRepeat` | `true`, `false` | No (Phase 2 only, nullable) |
| `selfRating` | `1`, `2`, `3`, `4`, `5` | No |

#### Bilingual Keyword Mapping

Both Chinese and English keywords map to the same enum values:

| Enum | Chinese Keywords | English Keywords |
|------|-----------------|-----------------|
| `breakout` | 突破 | breakout |
| `indicator` | 技術指標, 指標 | indicator |
| `template` | 模板策略, 模板 | template |
| `programmatic` | 程式信號, 程式 | programmatic |
| `intuition` | 直覺 | intuition |
| `fomo` | FOMO | fomo |
| `grid_dca` | 網格DCA, 網格, DCA | grid-dca, grid, dca |
| `copy_signal` | 跟單 | copy-signal, copy |
| `liquidation_bounce` | 清算反彈 | liquidation-bounce |
| `calm` | 冷靜 | calm |
| `fear` | 恐懼 | fear |
| `revenge` | 報復性交易, 報復 | revenge |
| `overconfidence` | 過度自信 | overconfidence |
| `boredom` | 無聊 | boredom |
| `preset` | 預設位, 預設 | preset |
| `support` | 支撐位, 支撐 | support |
| `ma_broken` | 均線跌破 | ma-broken |
| `trailing` | 追蹤止損 | trailing |
| `liquidation_level` | 清算價位 | liquidation-level |
| `atr_volatility` | ATR波動, ATR | atr |
| `sized_for_max_loss` | 最大虧損限制 | sized-for-max-loss |
| `emotional` | 情緒決定, 情緒 | emotional |
| `none` | 未設 | none |
| `stop_loss` | 止損 | stop-loss |
| `take_profit` | 止盈 | take-profit |
| `trailing_stop` | 追蹤止損觸發 | trailing-stop |
| `manual` | 手動 | manual |
| `partial_close` | 部分平倉 | partial-close |
| `forced_liquidation` | 強制清算 | forced-liquidation |

### Period Reflection

| Field | Type |
|-------|------|
| `biggestDisciplineIssue` | Free text |
| `nextImprovement` | Free text |
| `selfRating` | `1`-`5` |

Note: Period reflections were simplified from 5 fields to 3 for faster
completion. The `helpfulHabit` and `harmfulHabit` fields are deprecated but
still accepted if present in legacy entries.

### Self-Rating Scale

| Rating | Meaning |
|--------|---------|
| 1 | Terrible execution — broke multiple rules |
| 2 | Poor — significant discipline failures |
| 3 | Average — some mistakes but some discipline |
| 4 | Good — mostly followed the plan |
| 5 | Perfect — executed exactly as planned |

## Entry Lifecycle

### Create

1. User completes Step 9 reflection prompt.
2. LLM normalizes free-text answers into enum values, preserving originals in `*Detail` fields.
3. Generate entry ID: `{ISO-timestamp}_{scope}` where scope is `posId-{id}` or `period-{start}-{end}`.
4. Write entry JSON to `data/discipline-journal/entries/{id}.json` (new file, no conflict).
5. Atomic index update:
   - Read `index.json` → append entry → write to `index.json.tmp` → rename to `index.json`.
   - This prevents corruption from concurrent writes or interrupted operations.
6. Run preliminary bias flag detection on the new entry.
7. Show confirmation (Template 14 — echoes back normalized answers).

### Update (Upsert)

If a reflection already exists for the same `posId`:

1. Read the existing entry file.
2. Merge new reflection fields (overwrite changed fields, preserve unchanged).
3. Update `updatedAt` timestamp.
4. Update bias flags based on new reflection.
5. Update the corresponding index entry.

### Index Rebuild

If `index.json` is missing, corrupted, or unreadable:

1. Scan `data/discipline-journal/entries/*.json`.
2. Read each entry and extract lean index fields.
3. Sort by `createdAt` descending.
4. Write to `index.json.tmp`, then rename to `index.json`.

This rebuild can also be triggered via
`python trade_review_assets.py --import-journal` which validates and rebuilds
the index from entry files.

## Bias Flag Detection on Entry

When a single entry is created, apply these quick checks:

| Flag | Trigger |
|------|---------|
| `loss_aversion` | `emotion` in (`fear`) AND `exitReason` == `emotional` |
| `revenge_trading` | `emotion` == `revenge` |
| `fomo` | `entryReason` == `fomo` OR `emotion` == `fomo` |
| `overconfidence` | `emotion` == `overconfidence` |
| `emotional_stop` | `stopLossRationale` == `emotional` |
| `disposition` | `exitReason` == `emotional` AND `pnl > 0` AND `capturePct < 30` |
| `overtrading` | Detected at aggregate level only (not per-entry) |

These are preliminary flags. Full bias analysis (with thresholds and confidence)
runs in `BIAS` mode using the algorithms in `references/bias-detection.md`.

## News Context Schema

```json
{
  "available": true,
  "fetchedAt": "2026-03-10T14:30:00Z",
  "items": [
    {
      "source": "opennews",
      "title": "Fed holds rates steady amid inflation concerns",
      "url": "https://...",
      "coins": ["BTC", "ETH"],
      "aiScore": 82,
      "signal": "bearish",
      "summary": "聯準會維持利率不變，但暗示未來可能再升息。",
      "timestamp": "2026-03-09T20:00:00Z"
    }
  ],
  "twitterSentiment": {
    "direction": "bearish",
    "tweetCount": 45,
    "representativeTweet": "\"BTC looking weak after Fed statement\" — @crypto_analyst"
  }
}
```

## Querying Conventions

- **Recent N entries**: Read `index.json`, slice last N from `entries` array.
- **Filter by tag**: Iterate `index.json` entries, match `tags` array.
- **Filter by instrument**: Match `instId` field in index.
- **Filter by date range**: Compare `createdAt` against range bounds.
- **Full entry data**: Read `entries/{id}.json` for matched entries.

## Size Management

- When `totalEntries > 500`, warn the user and suggest archiving old entries.
- Archive = move entries older than a threshold date into `entries/archive/` subdirectory
  and remove them from `index.json`.
