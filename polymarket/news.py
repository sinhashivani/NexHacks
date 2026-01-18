import os
import re
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

GNEWS_URL = "https://gnews.io/api/v4/search"
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY") or os.getenv("GNEWS")
TIMEOUT = 20
MAX_ARTICLES = 5


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _squash_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _strip_wrapping_quotes(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].strip()
    return s


def _normalize_for_keywords(q: str) -> str:
    q = (q or "").replace("bps", "basis points")
    q = re.sub(r"[^A-Za-z0-9\s]", " ", q)
    return _squash_spaces(q)


def _extract_core_terms(question: str) -> list[str]:
    q = _normalize_for_keywords(question).lower()

    stop = {
        "will", "the", "a", "an", "by", "on", "in", "at", "of", "to", "for",
        "and", "or", "after", "before", "during", "from", "than", "then",
        "meeting", "decision", "announce", "announces", "announced",
        "hit", "reach", "before", "after", "under", "over",
        "question", "market", "polymarket",
    }

    tokens = [t for t in q.split() if t not in stop and (len(t) >= 3 or t.isdigit())]
    out, seen = [], set()
    for t in tokens:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out[:10]


def _build_query_variants(question: str) -> list[str]:
    raw = _squash_spaces(_strip_wrapping_quotes(question))
    if not raw:
        return []

    core = _extract_core_terms(raw)

    variants = [
        f"\"{raw}\"",
        " ".join(core),
        " OR ".join(core[:6]),
    ]

    uniq, seen = [], set()
    for v in variants:
        v = _squash_spaces(v)
        if v and v not in seen:
            uniq.append(v)
            seen.add(v)
    return uniq


def fetch_news(question: str) -> list[dict]:
    if not GNEWS_API_KEY:
        raise RuntimeError("Missing GNEWS_API_KEY")

    queries = _build_query_variants(question)
    if not queries:
        raise ValueError("question is required")

    now = datetime.now(timezone.utc)
    from_dt = now - timedelta(days=30)

    western_countries = ["us", "gb", "ca", "au", "ie", "fr", "de", "nl", "ch"]

    base_params = {
        "apikey": GNEWS_API_KEY,
        "lang": "en",
        "max": MAX_ARTICLES,  # <= 5
        "sortby": "relevance",
        "in": "title,description,content",
        "nullable": "image,description,content",
        "from": _iso_z(from_dt),
        "to": _iso_z(now),
    }

    for country in western_countries:
        for q in queries:
            params = dict(base_params, country=country, q=q)

            r = requests.get(GNEWS_URL, params=params, timeout=TIMEOUT)
            if not r.ok:
                continue

            articles = (r.json() or {}).get("articles") or []
            if not articles:
                continue

            out = []
            for a in articles[:MAX_ARTICLES]:  # defensive cap
                out.append(
                    {
                        "title": a.get("title"),
                        "image": a.get("image"),
                        "name": (a.get("source") or {}).get("name"),
                        "url": a.get("url"),
                    }
                )
            return out

    return []


if __name__ == "__main__":
    q = "Will Trump cut corporate taxes before 2027?"
    results = fetch_news(q)

    print(results)