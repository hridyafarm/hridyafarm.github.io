from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SITE_URL = os.environ.get("GSC_SITE_URL", "sc-domain:hridyafarm.com")
SITEMAP_URL = os.environ.get("GSC_SITEMAP_URL", "https://hridyafarm.com/sitemap.xml")
ACCESS_TOKEN = os.environ.get("GSC_ACCESS_TOKEN")


def main() -> int:
    if not ACCESS_TOKEN:
        print("Missing GSC_ACCESS_TOKEN environment variable.", file=sys.stderr)
        return 1

    endpoint = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        f"{quote(SITE_URL, safe='')}/sitemaps/{quote(SITEMAP_URL, safe='')}"
    )
    request = Request(
        endpoint,
        method="PUT",
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request) as response:
            body = response.read().decode("utf-8", "ignore").strip()
            print(body or "Sitemap submitted successfully.")
            return 0
    except HTTPError as exc:
        payload = exc.read().decode("utf-8", "ignore").strip()
        print(payload or str(exc), file=sys.stderr)
        return exc.code or 1
    except URLError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
