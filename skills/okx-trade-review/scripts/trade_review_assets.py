#!/usr/bin/env python3
"""Generate markdown, CSV, and optional SVG artifacts for trade review."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


CSV_FIELDS = [
    "posId",
    "account",
    "openTime",
    "closeTime",
    "instId",
    "direction",
    "leverage",
    "entryPrice",
    "exitPrice",
    "size",
    "pnl",
    "realizedPnl",
    "fee",
    "fundingFee",
    "liqPenalty",
    "totalCosts",
    "durationHours",
    "closeType",
    "session",
    "holdBucket",
    "leverageBucket",
    "costRatioPct",
    "preEntryMovePct",
    "maePct",
    "mfePct",
    "capturePct",
    "regimeTag",
    "trendAlignment",
    "entryTimingTag",
]

BLOCKS = "▁▂▃▄▅▆▇█"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate markdown, CSV, and optional SVG trade review artifacts.",
    )
    parser.add_argument("input_json", help="Path to normalized review JSON")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write generated files into",
    )
    parser.add_argument(
        "--svg",
        action="store_true",
        help="Generate an overview SVG in addition to markdown and CSV",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Override the default review file prefix",
    )
    return parser.parse_args()


def to_float(value: Any, default: float = 0.0) -> float:
    if value in (None, "", "N/A"):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_optional_float(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_time(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 1e11:
            timestamp /= 1000.0
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            numeric = float(raw)
        except ValueError:
            numeric = None
        if numeric is not None:
            if numeric > 1e11:
                numeric /= 1000.0
            return datetime.fromtimestamp(numeric, tz=timezone.utc)
        iso = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        try:
            dt = datetime.fromisoformat(iso)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return None


def isoformat_z(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compact_date(value: str | datetime | None) -> str:
    dt = parse_time(value) if not isinstance(value, datetime) else value
    if dt is None:
        return "unknown"
    return dt.strftime("%Y%m%d")


def human_date(value: str | datetime | None) -> str:
    dt = parse_time(value) if not isinstance(value, datetime) else value
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def format_money(value: float | None, signed: bool = True) -> str:
    if value is None:
        return "N/A"
    if signed:
        prefix = "+" if value > 0 else "-" if value < 0 else ""
        return f"{prefix}${abs(value):,.2f}"
    return f"${value:,.2f}"


def format_pct(value: float | None, digits: int = 1, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.{digits}f}%"


def format_ratio(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    if math.isinf(value):
        return "Infinity"
    return f"{value:.{digits}f}"


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    minimum = min(values)
    maximum = max(values)
    if math.isclose(minimum, maximum):
        return BLOCKS[len(BLOCKS) // 2] * len(values)
    chars = []
    for value in values:
        idx = round((value - minimum) / (maximum - minimum) * (len(BLOCKS) - 1))
        chars.append(BLOCKS[idx])
    return "".join(chars)


def session_bucket(dt: datetime | None) -> str:
    if dt is None:
        return "N/A"
    hour = dt.hour
    if 0 <= hour < 8:
        return "Asian"
    if 8 <= hour < 16:
        return "European"
    return "US"


def hold_bucket(duration_hours: float) -> str:
    if duration_hours < 1:
        return "<1h"
    if duration_hours < 4:
        return "1-4h"
    if duration_hours < 12:
        return "4-12h"
    if duration_hours < 24:
        return "12-24h"
    if duration_hours < 24 * 3:
        return "1-3d"
    if duration_hours < 24 * 7:
        return "3-7d"
    return ">7d"


def leverage_bucket(leverage: float) -> str:
    if leverage < 3:
        return "1-3x"
    if leverage < 5:
        return "3-5x"
    if leverage < 10:
        return "5-10x"
    if leverage < 20:
        return "10-20x"
    return "20x+"


def sample_confident(count: int, total: int) -> bool:
    if total <= 0:
        return False
    return count >= 3 or (count / total) >= 0.2


def safe_div(numerator: float, denominator: float) -> float | None:
    if math.isclose(denominator, 0.0):
        return None
    return numerator / denominator


def map_close_type(value: Any) -> str:
    if value in (None, ""):
        return "manual"
    raw = str(value).strip().lower()
    mapping = {
        "1": "manual",
        "2": "manual",
        "3": "liquidation",
        "4": "liquidation",
        "5": "adl",
        "6": "adl",
        "manual": "manual",
        "liquidation": "liquidation",
        "adl": "adl",
        "delivery": "delivery",
    }
    return mapping.get(raw, raw)


def normalize_trade(raw: dict[str, Any], default_account: str) -> dict[str, Any]:
    open_dt = parse_time(raw.get("openTime") or raw.get("cTime") or raw.get("openTs"))
    close_dt = parse_time(raw.get("closeTime") or raw.get("uTime") or raw.get("closeTs"))

    duration_hours = to_optional_float(raw.get("durationHours"))
    if duration_hours is None and open_dt and close_dt:
        duration_hours = (close_dt - open_dt).total_seconds() / 3600.0

    leverage = to_float(raw.get("leverage") or raw.get("lever"), 1.0)
    pnl = to_float(raw.get("pnl"), 0.0)
    realized_pnl = to_float(raw.get("realizedPnl"), pnl)
    fee = to_float(raw.get("fee"), 0.0)
    funding_fee = to_float(raw.get("fundingFee"), 0.0)
    liq_penalty = to_float(raw.get("liqPenalty"), 0.0)
    total_costs = abs(fee) + abs(funding_fee) + abs(liq_penalty)
    base_for_cost_ratio = abs(pnl) if not math.isclose(pnl, 0.0) else abs(realized_pnl)
    cost_ratio = raw.get("costRatioPct")
    if cost_ratio in (None, "", "N/A"):
        cost_ratio = safe_div(total_costs * 100.0, base_for_cost_ratio or 0.0)
    else:
        cost_ratio = to_optional_float(cost_ratio)

    trade = {
        "posId": str(raw.get("posId", "")),
        "account": str(raw.get("account") or default_account or "demo"),
        "openTime": isoformat_z(open_dt),
        "closeTime": isoformat_z(close_dt),
        "instId": str(raw.get("instId") or raw.get("instrument") or "UNKNOWN"),
        "direction": str(raw.get("direction") or raw.get("posSide") or "unknown").lower(),
        "leverage": leverage,
        "entryPrice": to_float(raw.get("entryPrice") or raw.get("openAvgPx"), 0.0),
        "exitPrice": to_float(raw.get("exitPrice") or raw.get("closeAvgPx"), 0.0),
        "size": to_float(raw.get("size") or raw.get("closeTotalPos") or raw.get("openMaxPos"), 0.0),
        "pnl": pnl,
        "realizedPnl": realized_pnl,
        "fee": fee,
        "fundingFee": funding_fee,
        "liqPenalty": liq_penalty,
        "totalCosts": total_costs,
        "durationHours": duration_hours or 0.0,
        "closeType": map_close_type(raw.get("closeType") or raw.get("type")),
        "session": str(raw.get("session") or session_bucket(open_dt)),
        "holdBucket": str(raw.get("holdBucket") or hold_bucket(duration_hours or 0.0)),
        "leverageBucket": str(raw.get("leverageBucket") or leverage_bucket(leverage)),
        "costRatioPct": cost_ratio,
        "preEntryMovePct": to_optional_float(raw.get("preEntryMovePct")),
        "maePct": to_optional_float(raw.get("maePct")),
        "mfePct": to_optional_float(raw.get("mfePct")),
        "capturePct": to_optional_float(raw.get("capturePct")),
        "regimeTag": raw.get("regimeTag") or "N/A",
        "trendAlignment": raw.get("trendAlignment") or "N/A",
        "entryTimingTag": raw.get("entryTimingTag") or "N/A",
        "_open_dt": open_dt,
        "_close_dt": close_dt,
    }
    if math.isclose(trade["pnl"], 0.0) and not math.isclose(trade["realizedPnl"], 0.0):
        trade["pnl"] = trade["realizedPnl"]
    return trade


def aggregate_by(trades: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"label": "", "count": 0, "pnl": 0.0, "wins": 0, "losses": 0, "costs": 0.0}
    )
    for trade in trades:
        label = str(trade.get(key) or "N/A")
        bucket = buckets[label]
        bucket["label"] = label
        bucket["count"] += 1
        bucket["pnl"] += trade["realizedPnl"]
        bucket["costs"] += trade["totalCosts"]
        if trade["realizedPnl"] > 0:
            bucket["wins"] += 1
        elif trade["realizedPnl"] < 0:
            bucket["losses"] += 1
    ordered = list(buckets.values())
    ordered.sort(key=lambda item: item["pnl"], reverse=True)
    return ordered


def compute_summary(trades: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        trades,
        key=lambda trade: trade.get("_close_dt") or trade.get("_open_dt") or datetime.min.replace(tzinfo=timezone.utc),
    )
    total = len(ordered)
    winners = [trade for trade in ordered if trade["realizedPnl"] > 0]
    losers = [trade for trade in ordered if trade["realizedPnl"] < 0]
    breakeven = total - len(winners) - len(losers)
    gross_win = sum(trade["realizedPnl"] for trade in winners)
    gross_loss = sum(trade["realizedPnl"] for trade in losers)
    net_pnl = sum(trade["realizedPnl"] for trade in ordered)
    total_costs = sum(trade["totalCosts"] for trade in ordered)
    win_rate = (len(winners) / total * 100.0) if total else 0.0
    avg_winner = gross_win / len(winners) if winners else None
    avg_loser = gross_loss / len(losers) if losers else None
    profit_factor = math.inf if losers and math.isclose(gross_loss, 0.0) else None
    if losers:
        profit_factor = gross_win / abs(gross_loss) if not math.isclose(gross_loss, 0.0) else math.inf
    elif winners:
        profit_factor = math.inf
    expectancy = net_pnl / total if total else 0.0

    equity_curve: list[float] = []
    running = 0.0
    peak = 0.0
    max_drawdown = 0.0
    current_wins = 0
    current_losses = 0
    max_consec_wins = 0
    max_consec_losses = 0

    for trade in ordered:
        running += trade["realizedPnl"]
        equity_curve.append(running)
        peak = max(peak, running)
        max_drawdown = min(max_drawdown, running - peak)

        if trade["realizedPnl"] > 0:
            current_wins += 1
            current_losses = 0
        elif trade["realizedPnl"] < 0:
            current_losses += 1
            current_wins = 0
        else:
            current_wins = 0
            current_losses = 0
        max_consec_wins = max(max_consec_wins, current_wins)
        max_consec_losses = max(max_consec_losses, current_losses)

    enriched_trades = [
        trade for trade in ordered if trade["regimeTag"] != "N/A" or trade["maePct"] is not None or trade["mfePct"] is not None
    ]
    largest_win = max(ordered, key=lambda trade: trade["realizedPnl"], default=None)
    largest_loss = min(ordered, key=lambda trade: trade["realizedPnl"], default=None)

    return {
        "totalTrades": total,
        "winners": len(winners),
        "losers": len(losers),
        "breakeven": breakeven,
        "grossWin": gross_win,
        "grossLoss": gross_loss,
        "netPnl": net_pnl,
        "winRate": win_rate,
        "avgWinner": avg_winner,
        "avgLoser": avg_loser,
        "profitFactor": profit_factor,
        "expectancy": expectancy,
        "totalCosts": total_costs,
        "maxDrawdown": abs(max_drawdown),
        "maxConsecWins": max_consec_wins,
        "maxConsecLosses": max_consec_losses,
        "equityCurve": equity_curve,
        "equitySparkline": sparkline(equity_curve),
        "largestWin": largest_win,
        "largestLoss": largest_loss,
        "avgLeverage": sum(trade["leverage"] for trade in ordered) / total if total else 0.0,
        "maxLeverage": max((trade["leverage"] for trade in ordered), default=0.0),
        "enrichedTrades": len(enriched_trades),
    }


def normalize_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    account = str(payload.get("account") or payload.get("profile") or "demo")
    raw_trades = payload.get("trades") or payload.get("positions") or payload.get("data") or []
    trades = [normalize_trade(trade, account) for trade in raw_trades]
    summary = compute_summary(trades)
    period = payload.get("period") or {}
    start = period.get("start") or isoformat_z(min((trade["_open_dt"] for trade in trades if trade["_open_dt"]), default=None))
    end = period.get("end") or isoformat_z(max((trade["_close_dt"] for trade in trades if trade["_close_dt"]), default=None))
    metadata = {
        "account": account,
        "period": {
            "start": start,
            "end": end,
        },
        "summary": summary,
        "insights": payload.get("insights") or {},
        "breakdowns": {
            "instrument": aggregate_by(trades, "instId"),
            "direction": aggregate_by(trades, "direction"),
            "leverage": aggregate_by(trades, "leverageBucket"),
            "duration": aggregate_by(trades, "holdBucket"),
            "session": aggregate_by(trades, "session"),
            "regime": aggregate_by(trades, "regimeTag"),
            "alignment": aggregate_by(trades, "trendAlignment"),
            "entryTiming": aggregate_by(trades, "entryTimingTag"),
        },
        "selectedTradeIds": payload.get("selectedTradeIds") or [],
    }
    return metadata, trades, summary, metadata["breakdowns"]


def top_group(groups: list[dict[str, Any]], total: int, positive: bool = True) -> dict[str, Any] | None:
    filtered = [group for group in groups if sample_confident(group["count"], total)]
    if not filtered:
        filtered = groups
    if not filtered:
        return None
    return max(filtered, key=lambda group: group["pnl"]) if positive else min(filtered, key=lambda group: group["pnl"])


def selected_trades(
    trades: list[dict[str, Any]],
    selected_ids: list[str],
    limit: int = 5,
) -> list[dict[str, Any]]:
    if selected_ids:
        wanted = {str(item) for item in selected_ids}
        selected = [trade for trade in trades if trade["posId"] in wanted]
        if selected:
            return sorted(selected, key=lambda trade: abs(trade["realizedPnl"]), reverse=True)[:limit]
    return sorted(trades, key=lambda trade: abs(trade["realizedPnl"]), reverse=True)[:limit]


def trade_label(trade: dict[str, Any]) -> str:
    time_label = human_date(trade["closeTime"] or trade["openTime"])
    return f"{trade['instId']} @ {time_label}"


def summarize_market_context(trades: list[dict[str, Any]]) -> list[str]:
    enriched = [trade for trade in trades if trade["regimeTag"] != "N/A"]
    if not enriched:
        return ["- Market context: no enriched trades in the dataset."]
    aligned = [trade for trade in enriched if trade["trendAlignment"] == "aligned"]
    counter = [trade for trade in enriched if trade["trendAlignment"] == "countertrend"]
    lines = [f"- Enriched trades: **{len(enriched)}/{len(trades)}**"]
    if aligned and counter:
        aligned_avg = sum(trade["realizedPnl"] for trade in aligned) / len(aligned)
        counter_avg = sum(trade["realizedPnl"] for trade in counter) / len(counter)
        lines.append(
            "- Trend alignment: aligned trades averaged "
            f"**{format_money(aligned_avg)}**, countertrend trades averaged **{format_money(counter_avg)}**."
        )
    captures = [trade["capturePct"] for trade in enriched if trade["capturePct"] is not None]
    if captures:
        lines.append(f"- Average capture across enriched trades: **{sum(captures) / len(captures):.1f}%**.")
    return lines


def derive_drivers(summary: dict[str, Any], breakdowns: dict[str, Any], total: int) -> list[str]:
    drivers: list[str] = []
    best_inst = top_group(breakdowns["instrument"], total, positive=True)
    if best_inst and best_inst["pnl"] > 0:
        drivers.append(
            f"- `[+]` Instrument leader: **{best_inst['label']}** drove **{format_money(best_inst['pnl'])}** "
            f"across **{best_inst['count']}** trades."
        )
    best_direction = top_group(breakdowns["direction"], total, positive=True)
    if best_direction and best_direction["pnl"] > 0:
        drivers.append(
            f"- `[+]` Direction edge: **{best_direction['label']}** produced **{format_money(best_direction['pnl'])}** "
            f"across **{best_direction['count']}** trades."
        )
    if summary["largestWin"] and summary["largestWin"]["realizedPnl"] > 0:
        trade = summary["largestWin"]
        drivers.append(
            f"- `[+]` Largest win: **{trade_label(trade)}** closed **{format_money(trade['realizedPnl'])}**."
        )
    return drivers or ["- No strong positive driver met the confidence threshold."]


def derive_hurts(summary: dict[str, Any], breakdowns: dict[str, Any], total: int) -> list[str]:
    hurts: list[str] = []
    worst_inst = top_group(breakdowns["instrument"], total, positive=False)
    if worst_inst and worst_inst["pnl"] < 0:
        hurts.append(
            f"- `[-]` Instrument drag: **{worst_inst['label']}** lost **{format_money(worst_inst['pnl'])}** "
            f"across **{worst_inst['count']}** trades."
        )
    worst_direction = top_group(breakdowns["direction"], total, positive=False)
    if worst_direction and worst_direction["pnl"] < 0:
        hurts.append(
            f"- `[-]` Direction drag: **{worst_direction['label']}** contributed **{format_money(worst_direction['pnl'])}**."
        )
    if summary["largestLoss"]:
        trade = summary["largestLoss"]
        hurts.append(
            f"- `[!]` Largest loss: **{trade_label(trade)}** closed **{format_money(trade['realizedPnl'])}**."
        )
    hurts.append(
        f"- `[!]` Total costs were **{format_money(summary['totalCosts'], signed=False)}**, "
        f"with max drawdown **-{format_money(summary['maxDrawdown'], signed=False)}**."
    )
    return hurts


def summarize_bucket(groups: list[dict[str, Any]], total: int) -> str:
    if not groups:
        return "N/A"
    leader = top_group(groups, total, positive=True)
    if leader is None:
        return "N/A"
    confidence = "" if sample_confident(leader["count"], total) else " (low confidence)"
    return (
        f"{leader['label']} led with {format_money(leader['pnl'])} across "
        f"{leader['count']} trades{confidence}"
    )


def derive_actions(trades: list[dict[str, Any]], summary: dict[str, Any], breakdowns: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    total = len(trades)
    aligned = next((group for group in breakdowns["alignment"] if group["label"] == "aligned"), None)
    counter = next((group for group in breakdowns["alignment"] if group["label"] == "countertrend"), None)
    if aligned and counter and aligned["pnl"] > counter["pnl"]:
        actions.append(
            "- `[+]` Keep favoring trades aligned with the local regime; they outperformed countertrend trades."
        )
    if summary["totalCosts"] > max(abs(summary["netPnl"]) * 0.2, 1.0):
        actions.append("- `[!]` Reduce fee/funding drag by cutting unnecessary churn and high-cost holds.")
    low_capture = [
        trade for trade in trades if trade["capturePct"] is not None and trade["capturePct"] < 40 and trade["mfePct"] not in (None, 0)
    ]
    if len(low_capture) >= max(2, math.ceil(total * 0.2)):
        actions.append("- `[-]` Work on exits: too many trades captured less than 40% of available favorable move.")
    highest_leverage = top_group(breakdowns["leverage"], total, positive=False)
    if highest_leverage and highest_leverage["label"] in {"10-20x", "20x+"} and highest_leverage["pnl"] < 0:
        actions.append("- `[!]` Cap leverage: the highest-leverage bucket was a net drag.")
    return actions[:3] or ["- Keep logging the same enriched fields so future reviews can compare execution quality consistently."]


def normalize_insight_lines(raw: Any) -> list[str]:
    if raw in (None, ""):
        return []
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped:
            return []
        return [f"- {stripped}" if not stripped.startswith("- ") else stripped]
    if isinstance(raw, list):
        lines = []
        for item in raw:
            if item in (None, ""):
                continue
            text = str(item).strip()
            if not text:
                continue
            lines.append(f"- {text}" if not text.startswith("- ") else text)
        return lines
    return []


def section_lines(metadata: dict[str, Any], key: str, fallback: list[str]) -> list[str]:
    provided = normalize_insight_lines(metadata["insights"].get(key))
    return provided or fallback


def executive_summary_lines(
    metadata: dict[str, Any],
    summary: dict[str, Any],
    breakdowns: dict[str, Any],
) -> list[str]:
    total = summary["totalTrades"]
    account_label = metadata["account"].upper()
    lines = [
        f"- Net PnL: **{format_money(summary['netPnl'])}** across **{summary['totalTrades']}** trades on **[{account_label}]**.",
        f"- Win rate: **{summary['winRate']:.1f}%**, Profit Factor: **{format_ratio(summary['profitFactor'])}**, "
        f"Expectancy: **{format_money(summary['expectancy'])}** / trade.",
    ]
    best_inst = top_group(breakdowns["instrument"], total, positive=True)
    if best_inst and best_inst["pnl"] > 0:
        lines.append(
            f"- `[+]` Best driver: **{best_inst['label']}** added **{format_money(best_inst['pnl'])}** across **{best_inst['count']}** trades."
        )
    worst_inst = top_group(breakdowns["instrument"], total, positive=False)
    if worst_inst and worst_inst["pnl"] < 0:
        lines.append(
            f"- `[-]` Main drag: **{worst_inst['label']}** lost **{format_money(worst_inst['pnl'])}** across **{worst_inst['count']}** trades."
        )
    lines.append(
        f"- `[!]` Max drawdown reached **-{format_money(summary['maxDrawdown'], signed=False)}** "
        f"while total costs reached **{format_money(summary['totalCosts'], signed=False)}**."
    )
    return lines


def trade_commentary(trade: dict[str, Any]) -> str:
    commentary: list[str] = []
    if trade["trendAlignment"] == "countertrend":
        commentary.append("The trade fought the local trend.")
    elif trade["trendAlignment"] == "aligned":
        commentary.append("The trade aligned with the local trend.")
    if trade["entryTimingTag"] == "chase":
        commentary.append("Entry likely chased the move.")
    elif trade["entryTimingTag"] == "pullback":
        commentary.append("Entry was taken on a pullback.")
    if trade["capturePct"] is not None and trade["capturePct"] < 40:
        commentary.append("Exit captured only a small share of the available favorable move.")
    if trade["maePct"] is not None and trade["mfePct"] is not None and trade["maePct"] > trade["mfePct"]:
        commentary.append("Adverse excursion outweighed favorable excursion.")
    return " ".join(commentary) or "No strong contextual edge or execution issue was detected from the enriched fields."


def render_markdown(
    metadata: dict[str, Any],
    trades: list[dict[str, Any]],
    summary: dict[str, Any],
    breakdowns: dict[str, Any],
) -> str:
    period = metadata["period"]
    start = human_date(period["start"])
    end = human_date(period["end"])
    selected = selected_trades(trades, metadata["selectedTradeIds"])
    lines: list[str] = [
        f"# OKX Trade Review — {start} to {end} [{metadata['account'].upper()}]",
        "",
        "## Executive Summary",
        *section_lines(
            metadata,
            "executiveSummary",
            executive_summary_lines(metadata, summary, breakdowns),
        ),
        "",
        "## Scorecard",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Net PnL | {format_money(summary['netPnl'])} |",
        f"| Trades | {summary['totalTrades']} |",
        f"| Win Rate | {summary['winRate']:.1f}% |",
        f"| Profit Factor | {format_ratio(summary['profitFactor'])} |",
        f"| Expectancy | {format_money(summary['expectancy'])} / trade |",
        f"| Max Drawdown | -{format_money(summary['maxDrawdown'], signed=False)} |",
        f"| Total Costs | {format_money(summary['totalCosts'], signed=False)} |",
        "",
        f"Equity sparkline: `{summary['equitySparkline']}`",
        "",
        "## What Drove PnL",
        *section_lines(
            metadata,
            "drivers",
            derive_drivers(summary, breakdowns, summary["totalTrades"]),
        ),
        "",
        "## What Hurt",
        *section_lines(
            metadata,
            "hurts",
            derive_hurts(summary, breakdowns, summary["totalTrades"]),
        ),
        "",
        "## Market Context",
        *section_lines(metadata, "marketContext", summarize_market_context(trades)),
        "",
        "## Behavior Patterns",
        f"- Direction: {summarize_bucket(breakdowns['direction'], summary['totalTrades'])}",
        f"- Leverage: {summarize_bucket(breakdowns['leverage'], summary['totalTrades'])}",
        f"- Hold duration: {summarize_bucket(breakdowns['duration'], summary['totalTrades'])}",
        f"- Session: {summarize_bucket(breakdowns['session'], summary['totalTrades'])}",
        "",
        "## Action Adjustments",
        *section_lines(metadata, "actions", derive_actions(trades, summary, breakdowns)),
        "",
        "## Selected Trade Deep Dives",
    ]
    for trade in selected:
        lines.extend(
            [
                f"### {trade['instId']} — {human_date(trade['openTime'])}",
                f"- Direction / leverage: `{trade['direction']}` / `{trade['leverage']}x`",
                f"- Net PnL / costs: {format_money(trade['realizedPnl'])} / {format_money(trade['totalCosts'], signed=False)}",
                f"- Regime / alignment / timing: `{trade['regimeTag']}` / `{trade['trendAlignment']}` / `{trade['entryTimingTag']}`",
                f"- MAE / MFE / Capture: {format_pct(trade['maePct'])} / {format_pct(trade['mfePct'])} / {format_pct(trade['capturePct'])}",
                f"- Review: {trade_commentary(trade)}",
                "",
            ]
        )
    lines.extend(
        [
            "## Appendix — Enriched Ledger",
            "| Close Time | Instrument | Dir | Net PnL | Costs | Tags |",
            "|------------|------------|-----|---------|-------|------|",
        ]
    )
    for trade in sorted(
        trades,
        key=lambda item: item.get("_close_dt") or item.get("_open_dt") or datetime.min.replace(tzinfo=timezone.utc),
    ):
        tags = ",".join(
            tag
            for tag in [trade["regimeTag"], trade["trendAlignment"], trade["entryTimingTag"]]
            if tag not in ("", "N/A")
        )
        lines.append(
            f"| {human_date(trade['closeTime'])} | {trade['instId']} | {trade['direction']} | "
            f"{format_money(trade['realizedPnl'])} | {format_money(trade['totalCosts'], signed=False)} | {tags or 'N/A'} |"
        )
    lines.extend(
        [
            "",
            "## Next Steps",
            "- Inspect the largest losing trade in `SINGLE` mode.",
            "- Run a focused `RISK` review on the same period.",
            "- Export the enriched CSV for further filtering.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_csv(path: Path, trades: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for trade in trades:
            row = {field: trade.get(field, "") for field in CSV_FIELDS}
            writer.writerow(row)


def svg_bar(width: float, value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0
    return width * abs(value) / maximum


def line_points(values: list[float], x: float, y: float, width: float, height: float) -> str:
    if not values:
        return ""
    minimum = min(values)
    maximum = max(values)
    spread = maximum - minimum or 1.0
    step = width / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        px = x + index * step
        py = y + height - ((value - minimum) / spread) * height
        points.append(f"{px:.2f},{py:.2f}")
    return " ".join(points)


def render_svg(
    metadata: dict[str, Any],
    trades: list[dict[str, Any]],
    summary: dict[str, Any],
    breakdowns: dict[str, Any],
) -> str:
    width = 1200
    height = 820
    chart_x = 70
    chart_y = 170
    chart_w = 1060
    chart_h = 220

    equity_values = summary["equityCurve"] or [0.0]
    drawdowns = []
    peak = 0.0
    for value in equity_values:
        peak = max(peak, value)
        drawdowns.append(value - peak)

    max_inst = max((abs(group["pnl"]) for group in breakdowns["instrument"]), default=1.0)
    top_instruments = breakdowns["instrument"][:5]
    directions = {group["label"]: group for group in breakdowns["direction"]}
    long_group = directions.get("long", {"pnl": 0.0, "count": 0})
    short_group = directions.get("short", {"pnl": 0.0, "count": 0})
    max_direction = max(abs(long_group["pnl"]), abs(short_group["pnl"]), 1.0)

    title = (
        f"OKX Trade Review — {compact_date(metadata['period']['start'])} to "
        f"{compact_date(metadata['period']['end'])} [{metadata['account'].upper()}]"
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; fill: #e5e7eb; }",
        ".muted { fill: #94a3b8; }",
        ".good { fill: #34d399; }",
        ".bad { fill: #f87171; }",
        ".panel { fill: #111827; stroke: #1f2937; stroke-width: 1; rx: 14; }",
        ".grid { stroke: #1f2937; stroke-width: 1; }",
        "</style>",
        '<rect width="100%" height="100%" fill="#0b1220"/>',
        f'<text x="70" y="60" font-size="30" font-weight="700">{escape(title)}</text>',
        f'<text x="70" y="95" font-size="16" class="muted">Trades: {summary["totalTrades"]}  |  Win Rate: {summary["winRate"]:.1f}%  |  '
        f'Profit Factor: {format_ratio(summary["profitFactor"])}  |  Max DD: -{format_money(summary["maxDrawdown"], signed=False)}</text>',
        '<rect class="panel" x="50" y="120" width="1100" height="300"/>',
        '<text x="70" y="155" font-size="20" font-weight="600">Equity Curve</text>',
    ]
    for offset in range(5):
        y = chart_y + offset * (chart_h / 4)
        parts.append(f'<line class="grid" x1="{chart_x}" y1="{y:.2f}" x2="{chart_x + chart_w}" y2="{y:.2f}"/>')
    parts.append(
        f'<polyline fill="none" stroke="#38bdf8" stroke-width="4" points="{line_points(equity_values, chart_x, chart_y, chart_w, chart_h)}"/>'
    )
    parts.append(
        f'<text x="{chart_x}" y="{chart_y + chart_h + 30}" font-size="14" class="muted">{escape(compact_date(metadata["period"]["start"]))}</text>'
    )
    parts.append(
        f'<text x="{chart_x + chart_w - 120}" y="{chart_y + chart_h + 30}" font-size="14" class="muted">{escape(compact_date(metadata["period"]["end"]))}</text>'
    )

    dd_x = 70
    dd_y = 470
    dd_w = 500
    dd_h = 250
    parts.extend(
        [
            '<rect class="panel" x="50" y="440" width="540" height="320"/>',
            '<text x="70" y="475" font-size="20" font-weight="600">Drawdown</text>',
        ]
    )
    for offset in range(5):
        y = dd_y + offset * (dd_h / 4)
        parts.append(f'<line class="grid" x1="{dd_x}" y1="{y:.2f}" x2="{dd_x + dd_w}" y2="{y:.2f}"/>')
    parts.append(
        f'<polyline fill="none" stroke="#f87171" stroke-width="4" points="{line_points(drawdowns, dd_x, dd_y, dd_w, dd_h)}"/>'
    )

    right_x = 640
    parts.extend(
        [
            '<rect class="panel" x="610" y="440" width="540" height="320"/>',
            '<text x="630" y="475" font-size="20" font-weight="600">Contribution</text>',
        ]
    )
    base_y = 520
    for index, group in enumerate(top_instruments):
        y = base_y + index * 38
        bar_w = svg_bar(240, group["pnl"], max_inst)
        color = "#34d399" if group["pnl"] >= 0 else "#f87171"
        parts.append(f'<text x="630" y="{y}" font-size="14">{escape(group["label"])}</text>')
        parts.append(f'<rect x="820" y="{y - 14}" width="{bar_w:.2f}" height="12" fill="{color}" rx="6"/>')
        parts.append(
            f'<text x="1075" y="{y}" font-size="14" text-anchor="end">{escape(format_money(group["pnl"]))}</text>'
        )

    parts.append('<text x="630" y="690" font-size="18" font-weight="600">Long vs Short</text>')
    for label, group, y in [
        ("Long", long_group, 725),
        ("Short", short_group, 755),
    ]:
        bar_w = svg_bar(240, group["pnl"], max_direction)
        color = "#34d399" if group["pnl"] >= 0 else "#f87171"
        parts.append(f'<text x="630" y="{y}" font-size="14">{label}</text>')
        parts.append(f'<rect x="700" y="{y - 14}" width="{bar_w:.2f}" height="12" fill="{color}" rx="6"/>')
        parts.append(f'<text x="960" y="{y}" font-size="14">{escape(format_money(group["pnl"]))}</text>')
        parts.append(f'<text x="1075" y="{y}" font-size="14" class="muted">{group["count"]} trades</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    metadata, trades, summary, breakdowns = normalize_payload(payload)
    if not trades:
        raise SystemExit("No trades found in input JSON.")

    prefix = args.prefix.strip() or (
        f"review-{compact_date(metadata['period']['start'])}-{compact_date(metadata['period']['end'])}"
    )
    md_path = output_dir / f"{prefix}.md"
    csv_path = output_dir / f"{prefix}.enriched.csv"
    svg_path = output_dir / f"{prefix}.svg"

    md_path.write_text(render_markdown(metadata, trades, summary, breakdowns), encoding="utf-8")
    write_csv(csv_path, trades)
    generated = [md_path, csv_path]

    if args.svg:
        svg_path.write_text(render_svg(metadata, trades, summary, breakdowns), encoding="utf-8")
        generated.append(svg_path)

    print("Generated files:")
    for path in generated:
        print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
