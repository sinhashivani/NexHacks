"""
Polymarket Gamma API:
Resolve tag IDs by label, fetch active events for each tag, flatten to one row per active market, export CSV.

Install:
  pip install requests pandas
Run:
  python merged_polymarket_tags_to_events.py

Output:
  polymarket_events_by_tags.csv
"""

import json
import time

import pandas as pd
import requests

GAMMA_BASE = "https://gamma-api.polymarket.com"
TIMEOUT = 30
PAGE_SIZE = 100

TARGET_LABELS = {"finance", "politics", "elections", "tech", "economy"}


def list_tags(limit: int = PAGE_SIZE, offset: int = 0) -> list[dict]:
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


def get_tag_ids_by_label(target_labels: set[str]) -> dict[str, int]:
    remaining = {s.lower() for s in target_labels}
    resolved: dict[str, int] = {}

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


def maybe_json(v):
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
    limit: int = PAGE_SIZE,
    sleep_s: float = 0.15,
) -> list[dict]:
    events: list[dict] = []
    offset = 0

    while True:
        r = requests.get(
            f"{GAMMA_BASE}/events",
            params={
                "tag_id": tag_id,
                "active": str(active).lower(),
                "closed": str(closed).lower(),
                "limit": limit,
                "offset": offset,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        batch = r.json()
        if not isinstance(batch, list):
            raise ValueError(f"Unexpected /events response shape: {type(batch)}")
        if not batch:
            break

        events.extend(batch)
        offset += limit
        time.sleep(sleep_s)

    return events


def events_to_rows(events: list[dict], tag_id: int, tag_label: str) -> list[dict]:
    rows: list[dict] = []

    for ev in events:
        markets = ev.get("markets") or []
        if not isinstance(markets, list):
            continue

        for m in markets:
            # Only keep active, not closed markets
            if m.get("active") is not True or m.get("closed") is True:
                continue

            clob_token_ids = maybe_json(m.get("clobTokenIds"))

            rows.append(
                {
                    "tag_label": tag_label,
                    "tag_id": tag_id,
                    "market_id": m.get("id"),
                    "market_slug": m.get("slug"),
                    "question": m.get("question") or m.get("title") or m.get("name"),
                    "clob_token_ids": (
                        json.dumps(clob_token_ids, ensure_ascii=False)
                        if clob_token_ids is not None
                        else None
                    ),
                }
            )

    return rows


def build_csv(
    target_labels: set[str],
    out_csv_path: str = "polymarket_events_by_tags.csv",
) -> pd.DataFrame:
    label_to_id = get_tag_ids_by_label(target_labels)

    missing = sorted({s.lower() for s in target_labels} - set(label_to_id))
    if missing:
        print(f"warning: could not resolve tag labels: {missing}")

    all_rows: list[dict] = []
    for label, tag_id in sorted(label_to_id.items()):
        print(f"fetching: label={label} tag_id={tag_id}")
        events = fetch_events_by_tag(tag_id=tag_id, active=True, closed=False)
        all_rows.extend(events_to_rows(events, tag_id=tag_id, tag_label=label))

    df = pd.DataFrame(all_rows)
    df.to_csv(out_csv_path, index=False)
    print(f"saved: {out_csv_path} rows={len(df):,}")
    return df


if __name__ == "__main__":
    df = build_csv(TARGET_LABELS, out_csv_path="polymarket_events_by_tags.csv")
    print(df.head(3).to_string(index=False) if not df.empty else "no rows returned")
