from covid_data_handler import (
    SNAPSHOT_CSV,
    get_covid_data,
    parse_csv_data,
    process_covid_csv_data,
)
import covid_data_handler


def test_parse_csv_data():
    data = parse_csv_data(SNAPSHOT_CSV)
    assert len(data) == 639


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = \
        process_covid_csv_data(parse_csv_data(SNAPSHOT_CSV))
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_falls_back_to_snapshot_when_api_fails(monkeypatch):
    def broken_api(*args, **kwargs):
        raise ConnectionError("API retired")

    monkeypatch.setattr(covid_data_handler, "covid_API_request", broken_api)
    data = get_covid_data("Exeter", "ltla", "England")

    assert isinstance(data, dict)
    assert data["source"].startswith("snapshot")
    assert data["national_7day_cases"] == 240_299
    assert data["local_7day_cases"] is None
