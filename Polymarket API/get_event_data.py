"""
Polymarket Gamma API: Resolve tag IDs by label, then fetch all active events for each tag
and flatten into one-row-per-event CSV (with parent event metadata).

Outputs:
- polymarket_events_by_tags.csv (all requested tags combined)
- polymarket_events_tag_<label>.csv (optional per-tag splits)

Install:
  pip install requests pandas
Run:
  python merged_polymarket_tags_to_events.py
"""

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

GAMMA_BASE = "https://gamma-api.polymarket.com"
TIMEOUT = 30
PAGE_SIZE = 100

# Labels you want to resolve -> tag IDs
TARGET_LABELS = {
    "finance",
    "politics",
    "elections",
    "tech",
    "economy"
}


# -----------------------------
# Tag resolution
# -----------------------------
def list_tags(limit: int = PAGE_SIZE, offset: int = 0) -> List[Dict[str, Any]]:
    r = requests.get(
        f"{GAMMA_BASE}/tags",
        params={"limit": limit, "offset": offset},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        raise ValueError(f"Unexpected /tags response shape: {type(data)}")
    return data


def get_category_ids_by_label(target_labels: set[str]) -> Dict[str, int]:
    remaining = {s.lower() for s in target_labels}
    resolved: Dict[str, int] = {}

    offset = 0
    while remaining:
        tags = list_tags(limit=PAGE_SIZE, offset=offset)
        if not tags:
            break

        for t in tags:
            label = str(t.get("label", "")).strip().lower()
            if label in remaining:
                resolved[label] = int(t["id"])
                remaining.remove(label)

        offset += PAGE_SIZE

    return resolved


# -----------------------------
# Event + market fetching
# -----------------------------
def _maybe_json(v: Any) -> Any:
    """
    Gamma sometimes returns fields like outcomes/outcomePrices/clobTokenIds as JSON-encoded strings.
    Try to decode if it looks like JSON; otherwise return as-is.
    """
    if isinstance(v, str):
        s = v.strip()
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return v
    return v


def fetch_events_by_tag(
    tag_id: int,
    active: bool = True,
    closed: bool = False,
    limit: int = 100,
    sleep_s: float = 0.15,
    max_pages: Optional[int] = None,
) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    offset = 0
    page = 0

    while True:
        params = {
            "tag_id": tag_id,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "limit": limit,
            "offset": offset,
        }
        r = requests.get(f"{GAMMA_BASE}/events", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()

        if not isinstance(batch, list):
            raise ValueError(f"Unexpected /events response shape: {type(batch)}")

        if len(batch) == 0:
            break

        events.extend(batch)
        offset += limit
        page += 1

        if max_pages is not None and page >= max_pages:
            break

        time.sleep(sleep_s)

    return events


def events_to_event_rows(
    events: List[Dict[str, Any]],
    tag_id: int,
    tag_label: str,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for ev in events:
        parent_event_id = ev.get("id")
        parent_event_slug = ev.get("slug")
        parent_event_title = ev.get("title") or ev.get("name")
        parent_event_start = ev.get("startTime") or ev.get("start_time")
        parent_event_end = ev.get("endTime") or ev.get("end_time")

        # IMPORTANT: keep the API field name "markets" (do not rename)
        markets = ev.get("markets") or []
        if not isinstance(markets, list):
            markets = []

        for m in markets:
            outcomes = _maybe_json(m.get("outcomes"))
            outcome_prices = _maybe_json(m.get("outcomePrices"))
            clob_token_ids = _maybe_json(m.get("clobTokenIds"))

            rows.append(
                {
                    "category_label": tag_label,
                    "category_tag_id": tag_id,
                    "parent_event_id": parent_event_id,
                    "parent_event_slug": parent_event_slug,
                    "parent_event_title": parent_event_title,
                    "parent_event_start_time": parent_event_start,
                    "parent_event_end_time": parent_event_end,
                    # renamed "market_*" columns to "event_*" columns
                    "event_id": m.get("id"),
                    "event_slug": m.get("slug"),
                    "event_question": m.get("question") or m.get("title") or m.get("name"),
                    "outcomes": json.dumps(outcomes, ensure_ascii=False) if outcomes is not None else None,
                    "outcome_prices": json.dumps(outcome_prices, ensure_ascii=False) if outcome_prices is not None else None,
                    "clob_token_ids": json.dumps(clob_token_ids, ensure_ascii=False) if clob_token_ids is not None else None,
                    "event_active": m.get("active"),
                    "event_closed": m.get("closed"),
                }
            )

    return rows


def build_events_csv_for_tags(
    target_labels: set[str],
    out_csv_path: str = "polymarket_events_by_tags.csv",
    write_per_tag: bool = False,
) -> pd.DataFrame:
    label_to_id = get_category_ids_by_label(target_labels)

    missing = sorted({s.lower() for s in target_labels} - set(label_to_id.keys()))
    if missing:
        print(f"warning: could not resolve tag labels: {missing}")

    all_rows: List[Dict[str, Any]] = []

    for label, tag_id in sorted(label_to_id.items()):
        print(f"fetching: label={label} tag_id={tag_id}")
        events = fetch_events_by_tag(tag_id=tag_id, active=True, closed=False, limit=PAGE_SIZE)
        rows = events_to_event_rows(events, tag_id=tag_id, tag_label=label)
        all_rows.extend(rows)

        if write_per_tag:
            df_tag = pd.DataFrame(rows)
            df_tag.to_csv(f"polymarket_events_tag_{label}.csv", index=False)
            print(f"saved per-tag: polymarket_events_tag_{label}.csv rows={len(df_tag):,}")

    df = pd.DataFrame(all_rows)

    col_order = [
        "category_label",
        "category_tag_id",
        "parent_event_id",
        "parent_event_slug",
        "parent_event_title",
        "parent_event_start_time",
        "parent_event_end_time",
        "event_id",
        "event_slug",
        "event_question",
        "outcomes",
        "outcome_prices",
        "clob_token_ids",
        "event_active",
        "event_closed",
    ]
    if not df.empty:
        df = df[[c for c in col_order if c in df.columns]]

    df.to_csv(out_csv_path, index=False)
    print(f"saved combined: {out_csv_path} rows={len(df):,}")
    return df


if __name__ == "__main__":
    # Single entrypoint: resolve labels -> tag IDs -> events -> events -> CSV
    df = build_events_csv_for_tags(
        target_labels=TARGET_LABELS,
        out_csv_path="polymarket_events_by_tags.csv",
        write_per_tag=False,
    )
    print(df.head(3).to_string(index=False) if not df.empty else "no rows returned")
