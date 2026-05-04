from typing import Iterator

from django.conf import settings
import httpx


def iter_polish_points(per_page: int = 500) -> Iterator[dict]:
    with httpx.Client(timeout=60.0) as client:
        page = 1
        while True:
            resp = client.get(settings.INPOST_API_URL, params={
                "page": page,
                "per_page": per_page,
                "country": "PL",
            })
            resp.raise_for_status()
            body = resp.json()

            items = body.get("items") or []
            if not items:
                break

            yield from items

            total_pages = body.get("total_pages")
            if total_pages and page >= total_pages:
                break

            page += 1