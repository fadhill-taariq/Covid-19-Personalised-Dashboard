import pytest

from app import create_app
from config import DEFAULTS
from covid_data_handler import snapshot_data
from covid_news_handling import NewsStore


class StubNews(NewsStore):
    def update_news(self, update_name=""):
        self.articles = [{"title": "Headline", "content": "Body", "url": "https://x.example"}]
        return self.visible()


@pytest.fixture
def client():
    app = create_app(
        settings=dict(DEFAULTS),
        covid_fetcher=lambda loc, loc_type, nation: snapshot_data(loc, nation),
        news_store=StubNews(),
    )
    return app.test_client(), app


def test_dashboard_renders_figures(client):
    test_client, _ = client
    page = test_client.get("/index").get_data(as_text=True)
    assert "240,299" in page
    assert "7,019" in page
    assert "141,544" in page
    assert "Headline" in page


def test_schedule_and_cancel_update(client):
    test_client, app = client
    response = test_client.get(
        "/index?update=15:15&two=Teatime&repeat=repeat&covid-data=covid-data")
    assert response.status_code == 302
    assert "Teatime" in test_client.get("/index").get_data(as_text=True)

    test_client.get("/index?update_item=Teatime")
    assert app.config["scheduler"].updates == []


def test_dismiss_news(client):
    test_client, _ = client
    test_client.get("/index?notif=Headline")
    assert "Headline" not in test_client.get("/index").get_data(as_text=True)


def test_invalid_update_shows_error(client):
    test_client, _ = client
    response = test_client.get("/index?update=15:15&two=NoBoxes", follow_redirects=True)
    assert "Choose COVID data, news, or both" in response.get_data(as_text=True)
