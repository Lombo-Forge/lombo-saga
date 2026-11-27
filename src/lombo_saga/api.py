"""The Kavita calls, standard library only. Checked against Kavita 0.9.1.

Every failure becomes an ApiError with a short message, so callers print it instead of crashing.
"""

import json
import urllib.error
import urllib.request
from typing import Any, cast

PAGE, MAX_PAGES = 200, 200
COLLECTION_FIELD = 7  # Kavita's series filter: "in collection"


class ApiError(Exception):
    """A request failed. The message names the path and the reason."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """urllib would turn a redirected POST into a GET and resend the key."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


_opener = urllib.request.build_opener(_NoRedirect)


class Kavita:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30):
        self.base = base_url.rstrip("/")
        self.key = api_key
        self.timeout = timeout

    def _call(self, path: str, body: object = None) -> Any:
        data = None if body is None else json.dumps(body).encode()
        headers = {"x-api-key": self.key, "Content-Type": "application/json"}
        # S310 is silenced: config.py only accepts http(s) URLs.
        req = urllib.request.Request(self.base + path, data=data, headers=headers)  # noqa: S310
        try:
            with _opener.open(req, timeout=self.timeout) as resp:
                text = resp.read()
            return json.loads(text) if text.strip() else None
        except urllib.error.HTTPError as e:
            raise ApiError(f"Kavita {path}: HTTP {e.code}") from e
        except (urllib.error.URLError, OSError) as e:
            raise ApiError(f"Kavita {path}: {e}") from e
        except ValueError as e:
            raise ApiError(f"Kavita {path}: not JSON (is the URL right?)") from e

    def account(self) -> dict[str, Any]:
        return cast(dict[str, Any], self._call("/api/Account"))

    def series(self, collection_id: int | None = None) -> list[dict[str, Any]]:
        """Every series, or only those in one collection."""
        body: dict[str, Any] = {}
        if collection_id is not None:
            statement = {"comparison": 0, "field": COLLECTION_FIELD, "value": str(collection_id)}
            body = {"statements": [statement], "combination": 1, "limitTo": 0}
        out: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            rows = self._call(f"/api/Series/all-v2?pageNumber={page}&pageSize={PAGE}", body) or []
            out.extend(rows)
            if len(rows) < PAGE:
                break
        return out

    def collections(self) -> list[dict[str, Any]]:
        return cast(list[dict[str, Any]], self._call("/api/Collection") or [])

    def add(self, title: str, series_ids: list[int], collection_id: int = 0) -> None:
        """Add series to a collection; id 0 always makes a NEW one, even if the name exists. Never removes."""
        body = {"collectionTagId": collection_id, "collectionTagTitle": title, "seriesIds": series_ids}
        self._call("/api/Collection/update-for-series", body)

    def promote(self, collection: dict[str, Any]) -> None:
        """Make a collection visible to everyone. Only used on one this app just made."""
        body = {"id": collection["id"], "title": collection["title"], "summary": collection.get("summary") or ""}
        body |= {"promoted": True, "coverImageLocked": bool(collection.get("coverImageLocked"))}
        self._call("/api/Collection/update", body)
