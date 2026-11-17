from covid_news_handling import NewsStore, news_API_request


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.payload)


PAYLOAD = {"articles": [
    {"title": "Story A", "description": "About A", "url": "https://a.example"},
    {"title": "[Removed]", "description": None, "url": None},
    {"title": "Story B", "description": None, "url": "https://b.example"},
]}


def test_news_API_request_without_key_returns_empty():
    assert news_API_request("Covid", api_key="") == []


def test_news_API_request_parses_articles():
    session = FakeSession(PAYLOAD)
    articles = news_API_request("Covid coronavirus", api_key="test-key", session=session)

    assert [a["title"] for a in articles] == ["Story A", "Story B"]
    assert articles[1]["content"] == ""
    params = session.calls[0][1]["params"]
    assert params["q"] == "Covid OR coronavirus"


def test_removed_articles_stay_hidden(monkeypatch):
    import covid_news_handling
    monkeypatch.setattr(
        covid_news_handling, "news_API_request",
        lambda terms, key: [{"title": "Story A", "content": "", "url": ""},
                            {"title": "Story B", "content": "", "url": ""}],
    )
    store = NewsStore(api_key="test-key")
    store.update_news("first")
    store.remove("Story A")
    store.update_news("second")

    assert [a["title"] for a in store.visible()] == ["Story B"]
