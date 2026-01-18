# polymarket/get_whales_data.py
import time
import requests
from typing import Literal, List, Dict, Any, Optional

LEADERBOARD_URL = "https://data-api.polymarket.com/v1/leaderboard"
TRADES_URL = "https://data-api.polymarket.com/trades"
EVENT_BY_SLUG_URL = "https://gamma-api.polymarket.com/events/slug"

# Canonical categories expected by Polymarket
Category = Literal[
    "OVERALL",
    "POLITICS",
    "SPORTS",
    "CRYPTO",
    "CULTURE",
    "MENTIONS",
    "WEATHER",
    "ECONOMICS",
    "TECH",
    "FINANCE",
]

_ALLOWED_CATEGORIES = {
    "overall": "OVERALL",
    "politics": "POLITICS",
    "sports": "SPORTS",
    "crypto": "CRYPTO",
    "culture": "CULTURE",
    "mentions": "MENTIONS",
    "weather": "WEATHER",
    "economics": "ECONOMICS",
    "tech": "TECH",
    "technology": "TECH",   # alias
    "finance": "FINANCE",
}


RETRY_STATUSES = {429, 502, 503, 504}


def _normalize_category(category: str) -> Category:
    """
    Accepts category in any case (lower, upper, title case).
    Also supports light aliases (e.g. 'technology' -> TECH).
    """
    if not category or not isinstance(category, str):
        raise ValueError("category must be a non-empty string")

    key = category.strip().lower()
    if key not in _ALLOWED_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'")

    return _ALLOWED_CATEGORIES[key]  # type: ignore


def _get_json_with_retries(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
    max_retries: int = 4,
    backoff_seconds: float = 0.6,
) -> Any:
    last_err: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, params=params or {}, timeout=timeout)
            if r.status_code in RETRY_STATUSES:
                raise requests.HTTPError(f"{r.status_code} retryable", response=r)
            r.raise_for_status()
            return r.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            last_err = e
            status = getattr(getattr(e, "response", None), "status_code", None)

            if status is not None and status not in RETRY_STATUSES:
                raise

            if attempt >= max_retries:
                break

            time.sleep(backoff_seconds * (2 ** attempt))

    raise last_err if last_err else RuntimeError("Request failed")


def _leaderboard_proxy_wallets(category: str) -> List[str]:
    normalized = _normalize_category(category)

    data = _get_json_with_retries(
        LEADERBOARD_URL,
        params={
            "category": normalized,
            "timePeriod": "DAY",
            "orderBy": "PNL",
            "limit": 5,
        },
    )

    if not isinstance(data, list):
        return []

    return [
        row["proxyWallet"]
        for row in data
        if isinstance(row, dict) and row.get("proxyWallet")
    ]


def _get_user_latest_trade(user_wallet: str) -> Optional[Dict[str, Any]]:
    try:
        data = _get_json_with_retries(TRADES_URL, params={"user": user_wallet})
    except Exception:
        return None

    if isinstance(data, dict):
        data = data.get("data") or data.get("trades") or []

    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return None


def _extract_slug_from_trade(trade: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(trade, dict):
        return None

    event = trade.get("event")
    if isinstance(event, dict) and event.get("slug"):
        return event["slug"]

    if trade.get("eventSlug"):
        return trade["eventSlug"]

    market = trade.get("market")
    if isinstance(market, dict):
        ev = market.get("event")
        if isinstance(ev, dict) and ev.get("slug"):
            return ev["slug"]

    return trade.get("slug")


def _get_event_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    if not slug:
        return None
    try:
        return _get_json_with_retries(f"{EVENT_BY_SLUG_URL}/{slug}")
    except Exception:
        return None


def _extract_title(event: Optional[Dict[str, Any]], trade: Optional[Dict[str, Any]]) -> Optional[str]:
    if isinstance(event, dict):
        t = event.get("title") or event.get("name")
        if isinstance(t, str) and t.strip():
            return t.strip()

    if isinstance(trade, dict):
        for k in ("question", "title", "marketQuestion", "marketTitle"):
            v = trade.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

        m = trade.get("market")
        if isinstance(m, dict):
            for k in ("question", "title"):
                v = m.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

    return None


def _extract_image(event: Optional[Dict[str, Any]], trade: Optional[Dict[str, Any]]) -> Optional[str]:
    if isinstance(event, dict):
        for k in ("image", "imageUrl", "image_url", "bannerImage", "bannerImageUrl", "thumbnail", "icon"):
            v = event.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

        media = event.get("media")
        if isinstance(media, dict):
            for k in ("image", "imageUrl", "thumbnail", "banner"):
                v = media.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

    if isinstance(trade, dict):
        m = trade.get("market")
        if isinstance(m, dict):
            for k in ("image", "imageUrl", "image_url", "icon", "thumbnail"):
                v = m.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()

    return None


def _extract_price(trade: Optional[Dict[str, Any]]) -> Optional[float]:
    if not isinstance(trade, dict):
        return None
    try:
        return float(trade.get("price"))
    except Exception:
        return None


def _extract_side(trade: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(trade, dict):
        return None
    s = trade.get("side")
    if isinstance(s, str) and s.strip():
        return s.strip()
    is_buy = trade.get("isBuy")
    if isinstance(is_buy, bool):
        return "BUY" if is_buy else "SELL"
    return None


def top5_latest_trade_cards(category: str) -> List[Dict[str, Any]]:
    """
    category can be lowercase, uppercase, or title case.
    """
    wallets = _leaderboard_proxy_wallets(category)
    out: List[Dict[str, Any]] = []

    for w in wallets:
        trade = _get_user_latest_trade(w)
        slug = _extract_slug_from_trade(trade)
        event = _get_event_by_slug(slug) if slug else None

        out.append(
            {
                "proxyWallet": w,
                "title": _extract_title(event, trade),
                "price": _extract_price(trade),
                "side": _extract_side(trade),
                "image": _extract_image(event, trade),
            }
        )

    return out


if __name__ == "__main__":
    print(top5_latest_trade_cards("overall"))
    print(top5_latest_trade_cards("Politics"))
    print(top5_latest_trade_cards("TECH"))
