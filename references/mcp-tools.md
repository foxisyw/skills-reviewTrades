# OKX MCP Tool Reference for Trade Review

The `okx-trade-mcp` server provides the data layer. This reference documents the
tools used by the Trade Review Skill.

## Table of Contents
1. [account_get_positions_history](#1-account_get_positions_history)
2. [swap_get_fills / spot_get_fills](#2-swap_get_fills--spot_get_fills)
3. [swap_get_orders / spot_get_orders](#3-swap_get_orders--spot_get_orders)
4. [account_get_bills](#4-account_get_bills)
5. [market_get_candles](#5-market_get_candles)
6. [market_get_funding_rate](#6-market_get_funding_rate)
7. [system_get_capabilities](#7-system_get_capabilities)
8. [Pagination Pattern](#8-pagination-pattern)
9. [Rate Limits](#9-rate-limits)

---

## 1. account_get_positions_history

**Primary tool for trade review.** Returns closed position lifecycle data.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instType` | No | all | `MARGIN`, `SWAP`, `FUTURES`, `OPTION` |
| `instId` | No | - | e.g. `BTC-USDT-SWAP` |
| `mgnMode` | No | - | `cross` or `isolated` |
| `type` | No | - | Close type: `1`=close long, `2`=close short, `3`=liq long, `4`=liq short, `5`=ADL long, `6`=ADL short |
| `posId` | No | - | Specific position ID |
| `after` | No | - | Pagination: IDs earlier than this |
| `before` | No | - | Pagination: IDs newer than this |
| `limit` | No | 20 | Max 100 |

### Key Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `posId` | String | Position ID |
| `instType` | String | Instrument type |
| `instId` | String | Instrument ID |
| `mgnMode` | String | `cross` or `isolated` |
| `type` | String | Close type (1-6) |
| `openAvgPx` | String | Average entry price |
| `closeAvgPx` | String | Average exit price |
| `openMaxPos` | String | Peak position size |
| `closeTotalPos` | String | Total closed size |
| `lever` | String | Leverage |
| `direction` | String | `long` or `short` |
| `pnl` | String | Price PnL |
| `realizedPnl` | String | Realized PnL (comprehensive) |
| `pnlRatio` | String | PnL ratio (return %) |
| `fee` | String | Accumulated trading fees |
| `fundingFee` | String | Accumulated funding fees |
| `liqPenalty` | String | Liquidation penalty |
| `cTime` | String | Position open timestamp (ms) |
| `uTime` | String | Position close timestamp (ms) |
| `ccy` | String | Currency |
| `uly` | String | Underlying |
| `posSide` | String | `long`, `short`, `net` |

**Note**: Does NOT include SPOT. For spot trade review, use `spot_get_fills`.

---

## 2. swap_get_fills / spot_get_fills

Per-execution fill details. Use `swap_get_fills` for SWAP/FUTURES, `spot_get_fills` for SPOT.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instId` | No | - | Instrument ID |
| `ordId` | No | - | Filter by order ID |
| `archive` | No | false | Set `true` for fills older than 3 days (up to 3 months) |
| `begin` | No | - | Start timestamp (ms) |
| `end` | No | - | End timestamp (ms) |
| `after` | No | - | Pagination cursor (older) |
| `before` | No | - | Pagination cursor (newer) |
| `limit` | No | 20 | Max 100 |

### Key Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `tradeId` | String | Trade ID |
| `ordId` | String | Order ID |
| `instId` | String | Instrument ID |
| `fillPx` | String | Fill price |
| `fillSz` | String | Fill quantity |
| `fillIdxPx` | String | Index price at fill time (for slippage) |
| `fillPnl` | String | PnL of this fill |
| `fillMarkPx` | String | Mark price at fill |
| `side` | String | `buy` or `sell` |
| `posSide` | String | `long`, `short`, `net` |
| `execType` | String | `T` (taker) or `M` (maker) |
| `fee` | String | Fee for this fill |
| `feeCcy` | String | Fee currency |
| `ts` | String | Fill timestamp (ms) |

**Important**: Use `archive: true` to get fills older than 3 days.

---

## 3. swap_get_orders / spot_get_orders

Order history with TP/SL settings.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instId` | No | - | Instrument ID |
| `status` | No | `pending` | Set `history` for filled/canceled orders |
| `ordType` | No | - | `market`, `limit`, `post_only`, etc. |
| `after` | No | - | Pagination cursor |
| `before` | No | - | Pagination cursor |
| `limit` | No | 20 | Max 100 |

### Key Return Fields (for trade review)

| Field | Type | Description |
|-------|------|-------------|
| `ordId` | String | Order ID |
| `instId` | String | Instrument ID |
| `ordType` | String | Order type |
| `side` | String | `buy` or `sell` |
| `px` | String | Order price |
| `avgPx` | String | Average fill price |
| `accFillSz` | String | Filled quantity |
| `state` | String | `filled` or `canceled` |
| `tpTriggerPx` | String | Take-profit trigger price |
| `slTriggerPx` | String | Stop-loss trigger price |
| `tpOrdPx` | String | TP order price |
| `slOrdPx` | String | SL order price |
| `lever` | String | Leverage |
| `category` | String | `normal`, `twap`, `adl`, `full_liquidation`, etc. |
| `cTime` | String | Creation timestamp |

---

## 4. account_get_bills

Financial ledger — every balance change.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instType` | No | - | Filter by instrument type |
| `ccy` | No | - | Filter by currency |
| `mgnMode` | No | - | `cross` or `isolated` |
| `type` | No | - | Bill type: `2`=trade, `5`=liquidation, `8`=funding fee |
| `after` | No | - | Pagination cursor |
| `before` | No | - | Pagination cursor |
| `begin` | No | - | Start timestamp (ms) |
| `end` | No | - | End timestamp (ms) |
| `limit` | No | 20 | Max 100 |

### Key Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `billId` | String | Bill ID |
| `instType` | String | Instrument type |
| `instId` | String | Instrument ID |
| `type` | String | Bill type |
| `subType` | String | Sub type (173=funding expense, 174=funding income) |
| `balChg` | String | Balance change |
| `bal` | String | Balance after |
| `sz` | String | Size |
| `px` | String | Price |
| `pnl` | String | PnL |
| `fee` | String | Fee |
| `ts` | String | Timestamp |

**Note**: Default returns last 7 days only. For older data (up to 3 months), call multiple times with time range params.

---

## 5. market_get_candles

Price context during a trade. Public endpoint, no auth needed.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instId` | Yes | - | Instrument ID |
| `bar` | No | `1m` | `1m`,`5m`,`15m`,`30m`,`1H`,`4H`,`1D`,`1W` |
| `after` | No | - | Timestamp (older) |
| `before` | No | - | Timestamp (newer) |
| `limit` | No | 100 | Max 100 |

### Return
Array of arrays: `[ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]`

---

## 6. market_get_funding_rate

Funding rate data for perpetual swaps.

### Parameters

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `instId` | Yes | - | Swap instrument ID (e.g. `BTC-USDT-SWAP`) |

### Return Fields

| Field | Type | Description |
|-------|------|-------------|
| `fundingRate` | String | Current funding rate |
| `realizedRate` | String | Last realized rate |
| `fundingTime` | String | Next funding timestamp |

---

## 7. system_get_capabilities

Health check. Returns server status, available modules, auth status.

### No Parameters

### Return Fields
- `modules`: list of enabled modules
- `authenticated`: boolean
- `demo`: boolean (simulated trading mode)
- `profile`: active profile name

**Use this as the first call to verify MCP connectivity.**

---

## 8. Pagination Pattern

All list tools use cursor-based pagination:

```
Call 1: tool(limit: 100)
  → get results, note last item's ID
Call 2: tool(limit: 100, after: <last_id>)
  → get more results
Call 3: ...continue until results.length < limit
```

**Cursor fields by tool:**
- `account_get_positions_history` → use `posId` of last item
- `swap_get_fills` / `spot_get_fills` → use `tradeId` of last item
- `swap_get_orders` / `spot_get_orders` → use `ordId` of last item
- `account_get_bills` → use `billId` of last item

**Cap at 10 pages (1000 items)** to prevent excessive calls.

---

## 9. Rate Limits

| Tool | Rate Limit | Strategy |
|------|------------|----------|
| `account_get_positions_history` | 1 req/s | Slowest — paginate carefully |
| `swap_get_fills` / `spot_get_fills` | 20 req/s | Fast pagination OK |
| `swap_get_orders` / `spot_get_orders` | 10 req/s | Standard pagination |
| `account_get_bills` | 5 req/s | Standard pagination |
| `market_get_candles` | 20 req/s | Usually single call sufficient |
| `market_get_funding_rate` | 10 req/s | Single call |

**All OKX values are returned as strings.** Parse to numbers for computation.
**Data retention: 3 months max** for most endpoints.
