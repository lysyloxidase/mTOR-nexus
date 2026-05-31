"""Small HTTP helpers shared by identifier validators."""

import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TRANSIENT_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}


def resolves(url: str, timeout: float = 15.0, attempts: int = 3) -> bool:
    """Return whether an identifier endpoint responds successfully."""

    request = Request(url, headers={"User-Agent": "mTOR-NEXUS/0.2 identifier-check"})
    for attempt in range(max(attempts, 1)):
        try:
            with urlopen(request, timeout=timeout) as response:
                if 200 <= response.status < 300:
                    return True
                if response.status not in TRANSIENT_HTTP_STATUSES:
                    return False
        except HTTPError as error:
            if error.code not in TRANSIENT_HTTP_STATUSES:
                return False
        except (URLError, TimeoutError):
            pass
        if attempt < attempts - 1:
            time.sleep(0.25 * 2**attempt)
    return False
