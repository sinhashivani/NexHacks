# get_similarity_scores.py
# Build a "Table 2" neighbors CSV for Supabase:
# source_clob_token_ids, neighbor_clob_token_ids, cosine_similarity
#
# Input CSV must have 3 columns:
# event_title, market_question, clob_token_ids
#
# Install:
#   pip install pandas numpy scikit-learn
#
# Run:
#   python get_similarity_scores.py

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

INPUT_CSV = "polymarket_events_by_tags.csv"
OUTPUT_CSV = "similarity_scores.csv"
BAD_ROWS_CSV = "bad_rows_skipped.csv"

TOP_K = 5


def robust_read_3col_csv(path: str) -> pd.DataFrame:
    """
    Reads a 3-column CSV:
      event_title, market_question, clob_token_ids

    Repairs broken quoting by:
      - if row has >3 fields: col0 as event_title, col_last as clob_token_ids,
        join middle back into market_question
      - if row has <3 fields: skip (audited)
    """
    rows = []
    bad_rows = []

    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"', skipinitialspace=True)

        header = next(reader, None)
        if not header:
            raise ValueError("Empty CSV")

        for line_no, row in enumerate(reader, start=2):
            if not row:
                continue

            row = [c.strip() for c in row]

            if len(row) == 3:
                rows.append((row[0], row[1], row[2]))
                continue

            if len(row) > 3:
                event_title = row[0]
                clob_token_ids = row[-1]
                market_question = ",".join(row[1:-1]).strip()
                rows.append((event_title, market_question, clob_token_ids))
                continue

            bad_rows.append({"line_no": line_no, "raw": "|".join(row)})

    if bad_rows:
        pd.DataFrame(bad_rows).to_csv(BAD_ROWS_CSV, index=False)

    return pd.DataFrame(rows, columns=["event_title", "market_question", "clob_token_ids"])


def normalize_token_ids(s: str) -> str:
    """
    clob_token_ids are often a JSON-encoded list string.
    Normalize to compact JSON list string for consistent joins/keys.
    """
    if s is None:
        return ""
    s = str(s).strip()
    if not s or s.lower() == "none":
        return ""

    # If it's a JSON list, normalize items and dump compact
    try:
        v = json.loads(s)
        if isinstance(v, list):
            v = [str(x).strip() for x in v if str(x).strip()]
            if not v:
                return ""
            return json.dumps(v, separators=(",", ":"))
    except Exception:
        pass

    # Otherwise keep as-is (but stripped)
    return s


def main():
    df_raw = robust_read_3col_csv(INPUT_CSV)
    parsed_rows = len(df_raw)

    # Clean fields
    df = df_raw.copy()

    df["market_question"] = (
        df["market_question"]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df["clob_token_ids"] = df["clob_token_ids"].apply(normalize_token_ids)

    # Hard filters
    df = df[(df["market_question"] != "") & (df["clob_token_ids"] != "")].reset_index(drop=True)
    post_filter_rows = len(df)

    if post_filter_rows < 2:
        raise ValueError("Not enough valid rows after filtering to compute neighbors.")

    # Dedup by clob_token_ids (critical for stable keys)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["clob_token_ids"], keep="first").reset_index(drop=True)
    after_dedup = len(df)
    deduped = before_dedup - after_dedup

    # Sanity: keys must be unique now
    nunique = int(df["clob_token_ids"].nunique())
    if nunique != len(df):
        raise RuntimeError("Dedup failed: clob_token_ids are still not unique.")

    # Vectorize
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=200_000,
    )
    X = vectorizer.fit_transform(df["market_question"].tolist())

    # We need TOP_K neighbors excluding itself => ask for TOP_K+1 including self
    n_neighbors = min(TOP_K + 1, len(df))
    nn = NearestNeighbors(metric="cosine", algorithm="brute", n_jobs=-1, n_neighbors=n_neighbors)
    nn.fit(X)

    distances, indices = nn.kneighbors(X)

    # Build output rows
    out_rows = []
    for i in range(len(df)):
        src_ids = df.at[i, "clob_token_ids"]

        added = 0
        for j in range(n_neighbors):
            nbr_idx = int(indices[i, j])

            # Exclude self
            if nbr_idx == i:
                continue

            nbr_ids = df.at[nbr_idx, "clob_token_ids"]
            sim = float(1.0 - float(distances[i, j]))

            out_rows.append(
                {
                    "source_clob_token_ids": src_ids,
                    "neighbor_clob_token_ids": nbr_ids,
                    "cosine_similarity": sim,
                }
            )
            added += 1
            if added >= TOP_K:
                break

    out = pd.DataFrame(out_rows)

    # Deterministic ordering
    out = out.sort_values(
        by=["source_clob_token_ids", "cosine_similarity"],
        ascending=[True, False],
        kind="mergesort",
    ).reset_index(drop=True)

    # Sanity: every source should have exactly TOP_K rows if dataset big enough
    if len(df) > TOP_K:
        counts = out.groupby("source_clob_token_ids").size()
        bad = counts[counts != TOP_K]
        if not bad.empty:
            # Not fatal, but indicates duplicates/self-filtering reduced neighbors for some sources
            print(f"WARNING: {len(bad)} sources do not have exactly {TOP_K} neighbors.")

    out.to_csv(OUTPUT_CSV, index=False)

    # KPI printout
    print(f"Parsed rows (raw): {parsed_rows:,}")
    print(f"Parsed rows (post-filter): {post_filter_rows:,}")
    print(f"Deduped by clob_token_ids: -{deduped:,}")
    print(f"Rows used for neighbors: {len(df):,}")
    print(f"Neighbors per source (target): {TOP_K}")
    print(f"Expected output rows: {len(df) * TOP_K:,}" if len(df) > TOP_K else "Expected output rows: < TOP_K dataset")
    print(f"Output rows: {len(out):,}")
    if Path(BAD_ROWS_CSV).exists():
        print(f"Bad rows audit written to: {BAD_ROWS_CSV}")
    print(f"Output written to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
