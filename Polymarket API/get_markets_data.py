import json
from typing import Any, Dict, List, Optional
import requests

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
TIMEOUT = 15


def _get(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    r = requests.get(url, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _to_list(x: Any) -> List[str]:
    # Gamma often returns JSON-encoded strings for arrays (e.g., '["Yes","No"]')
    if x is None:
        return []
    if isinstance(x, list):
        return [str(v) for v in x]
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return []
        try:
            v = json.loads(s)
            if isinstance(v, list):
                return [str(i) for i in v]
        except Exception:
            pass
        return [s]
    return [str(x)]


def get_current_price(token_id: str, side: str = "buy") -> Optional[str]:
    """
    Implements:
      https://clob.polymarket.com/price?token_id=YOUR_TOKEN_ID&side=buy
    side: "buy" or "sell" (case-insensitive)
    """
    token_id = str(token_id).strip()
    side = side.strip().lower()
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")

    data = _get(f"{CLOB_API}/price", params={"token_id": token_id, "side": side})
    if isinstance(data, dict) and "price" in data:
        return str(data["price"])
    return None


def get_market_ui_from_clob_token(clob_token_id: str) -> List[Dict[str, Any]]:
    """
    Input:  clob_token_id (string)
    Output: UI-ready list (one per outcome token) containing ONLY:
      - title: gamma_markets[0]["question"]
      - price: summary[i]["clob_mid"]   (midpoint per token)
      - image: gamma_markets[0]["image"]
      - outcome + token_id (needed for UI buttons / routing)
    """
    clob_token_id = str(clob_token_id).strip()

    # 1) Find market(s) containing this token
    markets = _get(
        f"{GAMMA_API}/markets",
        params={"clob_token_ids": [clob_token_id], "limit": 100, "offset": 0},
    )
    if not markets:
        return []

    market = markets[0]
    title = market.get("question")
    image = market.get("image")

    # 2) Pull per-token prices for every token in this market
    tokens = _to_list(market.get("clobTokenIds"))
    outcomes = _to_list(market.get("outcomes"))

    while len(outcomes) < len(tokens):
        outcomes.append("")

    ui_rows: List[Dict[str, Any]] = []
    for i, t in enumerate(tokens):
        # Midpoint is best for a single headline price
        mid_resp = _get(f"{CLOB_API}/midpoint", params={"token_id": t})
        mid = mid_resp.get("mid") or mid_resp.get("midpoint") or mid_resp.get("price")

        # Optional: keep bid/ask in case you want it later (still UI-relevant)
        buy = get_current_price(t, "buy")
        sell = get_current_price(t, "sell")

        ui_rows.append(
            {
                "title": title,                 # gamma_markets[0]["question"]
                "price": str(mid) if mid is not None else None,  # summary[i]["clob_mid"]
                "image": image,                 # gamma_markets[0]["image"]
                "outcome": outcomes[i] if i < len(outcomes) else "",
                "token_id": t,
                "bid": buy,
                "ask": sell,
            }
        )

    return ui_rows


if __name__ == "__main__":
    # Example quick run (edit token below)
    token = "111128191581505463501777127559667396812474366956707382672202929745167742497287"
    rows = get_market_ui_from_clob_token(token)
    print(json.dumps(rows, indent=2))
