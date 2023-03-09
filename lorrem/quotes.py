import requests

from .config import cfg


QUOTE_API_TOKEN = cfg.get("quote_api_token")
HEADERS = {"Authorization": QUOTE_API_TOKEN}
QUERY = cfg.get("quote_api_query")
MODE = cfg.get("mode")

# In Finnish because the default corpus is in Finnish
# TODO: Generate test data from a file?
DEV_QUOTES = [
    {"quote": "Tämä on lainaus numero kaksi."},
    {"quote": "Tuo on lainaus osa kolme."},
]


def request_all_quotes():
    # Return fake response in dev environment
    if MODE == "dev":
        return DEV_QUOTES
    else:
        return requests.get(QUERY, headers=HEADERS).json()


def load_quotes():
    return [quote["quote"] for quote in request_all_quotes()]
