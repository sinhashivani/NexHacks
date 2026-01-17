import json
from typing import Any, Dict, List, Optional
import requests

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TIMEOUT = 15

def _get(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    r = requests.get(url, params=params or {}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _to_list(x: Any) -> List[str]:
    if x is None: return []
    if isinstance(x, list): return [str(v) for v in x]
    if isinstance(x, str):
        s = x.strip()
        if not s: return []
        try:
            v = json.loads(s)
            if isinstance(v, list): return [str(i) for i in v]
        except Exception:
            pass
        return [s]
    return [str(x)]

def mid(token_id: str) -> Optional[str]:
    d = _get(f"{CLOB}/midpoint", {"token_id": str(token_id).strip()})
    v = d.get("mid") or d.get("midpoint") or d.get("price")
    return str(v) if v is not None else None

def ui(token_id: str) -> Dict[str, Any]:
    ms = _get(f"{GAMMA}/markets", {"clob_token_ids": [str(token_id).strip()], "limit": 1})
    if not ms:
        return {}
    m = ms[0]
    tokens = _to_list(m.get("clobTokenIds"))
    outs = _to_list(m.get("outcomes"))
    n = min(len(tokens), len(outs))
    return {
        "q": m.get("question"),
        "img": m.get("image"),
        "p": {outs[i]: mid(tokens[i]) for i in range(n)},
    }
