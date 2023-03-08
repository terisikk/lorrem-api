import requests

from .config import cfg


QUOTE_API_TOKEN = cfg.get('quote_api_token')
HEADERS = {'Authorization': QUOTE_API_TOKEN}
QUERY = cfg.get('quote_api_query')


def request_all_quotes():
    print(cfg)
    return requests.get(QUERY, headers=HEADERS).json()


def load_quotes():
    return [quote["quote"] for quote in request_all_quotes()]
