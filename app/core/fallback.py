"""Firecrawl web-search fallback for RAG queries.

This module provides a small, tolerant wrapper around the installed
`firecrawl-py` client. The package API has changed over time, so the
implementation attempts a few common import/constructor/method names and
normalizes results to a simple list of dicts with `title`, `url`, and
`snippet` keys.

If no compatible client is found, a `RuntimeError` is raised with
instructions for the developer.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.config import get_settings


def _normalize_result_item(item: Any) -> Dict[str, str]:
    """Normalize a single result item to a dict with title,url,snippet."""

    if not isinstance(item, dict):
        # If it's a simple string, put it in the snippet
        return {"title": "", "url": "", "snippet": str(item)}

    title = item.get("title") or item.get("name") or item.get("headline") or ""
    url = item.get("url") or item.get("link") or item.get("href") or ""
    snippet = (
        item.get("snippet")
        or item.get("summary")
        or item.get("text")
        or item.get("description")
        or ""
    )

    return {"title": title, "url": url, "snippet": snippet}


def _extract_from_response(resp: Any, limit: int) -> List[Dict[str, str]]:
    """Attempt to extract a list of result-like dicts from various response shapes."""

    results: List[Any] = []

    if resp is None:
        return []

    # Common shapes: list of items
    if isinstance(resp, list):
        results = resp

    # Dicts with common keys
    elif isinstance(resp, dict):
        for key in ("results", "web", "items", "hits", "data"):
            if key in resp and isinstance(resp[key], (list, tuple)):
                results = resp[key]
                break

        # Some clients return {'results': {'web': [...]}}
        if not results:
            for k in ("results", "data"):  # nested dicts
                val = resp.get(k)
                if isinstance(val, dict):
                    for subkey in ("web", "items", "hits"):
                        if subkey in val and isinstance(val[subkey], (list, tuple)):
                            results = val[subkey]
                            break
                    if results:
                        break

    # Fallback: try to coerce single-item dict into list
    if isinstance(results, dict):
        results = [results]

    # Normalize and limit
    normalized: List[Dict[str, str]] = []
    for item in results:
        normalized.append(_normalize_result_item(item))
        if len(normalized) >= limit:
            break

    return normalized


def firecrawl_search(query: str, limit: int = 3) -> List[Dict[str, str]]:
    """Search the web using the installed Firecrawl client.

    This function attempts to import common client entrypoints from
    `firecrawl` / `firecrawl_py` and call a reasonable search method.

    Returns a list of normalized result dicts with keys: `title`, `url`, `snippet`.
    """

    settings = get_settings()
    api_key = getattr(settings, "firecrawl_api_key", None)

    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is not set in settings/.env")

    # Try a few import names and client constructors/methods.
    import_errors = []

    # Try module name variants
    module_names = ("firecrawl", "firecrawl_py", "firecrawl_py.client")

    for mod_name in module_names:
        try:
            module = __import__(mod_name, fromlist=["*"])
        except Exception as exc:  # pragma: no cover - import failures
            import_errors.append((mod_name, exc))
            continue

        # If module exposes a convenient top-level search function, try it
        for top_func in ("search", "web_search", "query"):
            fn = getattr(module, top_func, None)
            if callable(fn):
                try:
                    resp = fn(query, limit=limit, api_key=api_key)
                    return _extract_from_response(resp, limit)
                except TypeError:
                    try:
                        resp = fn(query, limit=limit)
                        return _extract_from_response(resp, limit)
                    except Exception:
                        pass

        # Try to construct a client from common class names
        for cls_name in ("Firecrawl", "Client", "FirecrawlClient"):
            cls = getattr(module, cls_name, None)
            if cls:
                try:
                    client = cls(api_key=api_key)
                except TypeError:
                    # some constructors accept 'key' or 'token'
                    try:
                        client = cls(key=api_key)
                    except Exception:
                        client = None

                if client:
                    for method in ("search", "web_search", "query"):
                        m = getattr(client, method, None)
                        if callable(m):
                            try:
                                resp = m(query, limit=limit)
                                return _extract_from_response(resp, limit)
                            except TypeError:
                                try:
                                    resp = m(query)
                                    return _extract_from_response(resp, limit)
                                except Exception:
                                    pass

    # If we reach here, no compatible client was found or all attempts failed
    msg = (
        "No compatible firecrawl client found. Install 'firecrawl-py' and\n"
        "ensure the package exposes a search client. If you have a custom\n"
        "client, adapt app/core/fallback.py to call its search API."
    )
    raise RuntimeError(msg)
