import lorrem.quotes as api

from lorrem.config import cfg


def test_load_all_quotes(requests_mock):
    test_quote_1 = "Test Quote 1"
    test_quote_2 = "Test Quote 2"
    quotes = [{"quote": test_quote_1}, {"quote": test_quote_2}]

    query = cfg.get("quote_api_query")

    adapter = requests_mock.get(query, json=quotes)

    expected = [test_quote_1, test_quote_2]
    actual = api.load_quotes()

    assert adapter.called
    assert actual == expected
