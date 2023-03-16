import lorrem.quotes as api

from lorrem.config import cfg


def test_load_all_quotes(requests_mock):
    test_quote_1 = "Test Quote 1"
    test_quote_2 = "Test Quote 2"
    quotes = [{"quote": test_quote_1}, {"quote": test_quote_2}]

    query = cfg.get("quote_api_query")

    adapter = requests_mock.get(query, json=quotes)  # nosec B113

    expected = [test_quote_1, test_quote_2]
    actual = list(api.load_quotes())

    assert adapter.called
    assert actual == expected


def test_fake_backend_load(monkeypatch, requests_mock):
    monkeypatch.setattr(api, "MODE", "dev")

    query = cfg.get("quote_api_query")
    adapter = requests_mock.get(query, json={})  # nosec B113

    actual = list(api.load_quotes())

    assert not adapter.called
    assert len(actual) == 2
