"""Small HTTP helpers shared by identifier validators."""

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def resolves(url: str, timeout: float = 15.0) -> bool:
    """Return whether an identifier endpoint responds successfully."""

    request = Request(url, headers={"User-Agent": "mTOR-NEXUS/0.1 identifier-check"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (HTTPError, URLError, TimeoutError):
        return False
