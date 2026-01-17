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

def robust_read_3col_csv(path: str) -> pd.DataFrame:
    """
    Reads a 3-column CSV:
      event_title, market_question, clob_token_ids
    Handles broken quoting by:
      - if row has >3 fields: keep col0 as event_title, col_last as clob_token_ids,
        and join the middle back into market_question
      - if row has <3 fields: skip
    """
    rows = []
    bad_rows = []

    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"', skipinitialspace=True)

        # Header
        header = next(reader, None)
        if not header:
            raise ValueError("Empty CSV")

        # Normalize header
        header_norm = [h.strip().lower().replace("\ufeff", "") for h in header]
        # We don't fully trust it; we enforce position-based mapping.

        for line_no, row in enumerate(reader, start=2):
            if not row:
                continue

            # Trim whitespace on each cell
            row = [c.strip() for c in row]

            if len(row) == 3:
                event_title, market_question, clob_token_ids = row
                rows.append((event_title, market_question, clob_token_ids))
                continue

            if len(row) > 3:
                # Heuristic repair: first col is title, last col is token_ids,
                # everything in the middle is the question (commas inside broken quotes)
                event_title = row[0]
                clob_token_ids = row[-1]
                market_question = ",".join(row[1:-1]).strip()
                rows.append((event_title, market_question, clob_token_ids))
                continue

            # len(row) < 3 => unrecoverable
            bad_rows.append({"line_no": line_no, "raw": "|".join(row)})

    if bad_rows:
        pd.DataFrame(bad_rows).to_csv(BAD_ROWS_CSV, index=False)

    df = pd.DataFrame(rows, columns=["event_title", "market_question", "clob_token_ids"])
    return df


def normalize_token_ids(s: str) -> str:
    """
    Your clob_token_ids are often a JSON-encoded list string.
    Keep original if parse fails; otherwise re-dump compact for consistency.
    """
    if s is None:
        return ""
    s = str(s).strip()
    if not s or s.lower() == "none":
        return ""
    try:
        v = json.loads(s)
        if isinstance(v, list):
            return json.dumps(v, separators=(",", ":"))
    except Exception:
        pass
    return s


def main():
    df = robust_read_3col_csv(INPUT_CSV)

    # Clean fields
    df["market_question"] = (
        df["market_question"]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df["clob_token_ids"] = df["clob_token_ids"].apply(normalize_token_ids)

    # Hard filters: no empty question, no empty token ids
    df = df[(df["market_question"] != "") & (df["clob_token_ids"] != "")].reset_index(drop=True)

    # Vectorize
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=200_000,
    )
    X = vectorizer.fit_transform(df["market_question"].tolist())

    # Nearest neighbor besides itself => one similarity score per row
    nn = NearestNeighbors(n_neighbors=2, metric="cosine", algorithm="brute", n_jobs=-1)
    nn.fit(X)
    distances, _ = nn.kneighbors(X)
    cosine_similarity = 1.0 - distances[:, 1]

    out = pd.DataFrame({
        "clob_token_ids": df["clob_token_ids"].values,
        "cosine_similarity": cosine_similarity.astype(float),
    })
    out.to_csv(OUTPUT_CSV, index=False)

    # KPI printout (so you see what got dropped/kept)
    print(f"Input rows after robust parse: {len(df):,}")
    print(f"Output rows: {len(out):,}")
    print(f"Similarity == 1.0 count: {(out['cosine_similarity'] == 1.0).sum():,}")
    print(f"Similarity == 0.0 count: {(out['cosine_similarity'] == 0.0).sum():,}")
    if Path(BAD_ROWS_CSV).exists():
        print(f"Bad rows audit written to: {BAD_ROWS_CSV}")
    print(f"Output written to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
