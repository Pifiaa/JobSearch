import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 30
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def get(url: str, headers: dict = {}) -> requests.Response | None:
    try:
        response = requests.get(url, headers={**DEFAULT_HEADERS, **headers}, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response
    except Exception:
        return None


def post(url: str, data: dict, headers: dict = {}) -> requests.Response | None:
    try:
        response = requests.post(url, data=data, headers={**DEFAULT_HEADERS, **headers}, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        return response
    except Exception:
        return None


def parse_html(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, "lxml")