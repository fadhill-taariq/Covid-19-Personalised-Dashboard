from datetime import datetime

import pytest

from update_scheduler import UpdateScheduler, hhmm_to_seconds, seconds_until


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def make_scheduler():
    calls = {"covid": 0, "news": []}
    clock = FakeClock()

    def update_covid():
        calls["covid"] += 1

    def update_news(name):
        calls["news"].append(name)

    scheduler = UpdateScheduler(
        update_covid, update_news, timefunc=clock,
        now_func=lambda: datetime(2021, 12, 8, 15, 0),
    )
    return scheduler, clock, calls


def test_hhmm_to_seconds():
    assert hhmm_to_seconds("01:30") == 5400
    with pytest.raises(ValueError):
        hhmm_to_seconds("1530")
    with pytest.raises(ValueError):
        hhmm_to_seconds("25:00")


def test_seconds_until_rolls_over_to_tomorrow():
    now = datetime(2021, 12, 8, 15, 0)
    assert seconds_until("15:15", now) == 15 * 60
    assert seconds_until("14:00", now) == 23 * 3600


def test_one_off_update_runs_once_and_is_removed():
    scheduler, clock, calls = make_scheduler()
    scheduler.add("Afternoon", "15:15", covid=True, news=True)

    clock.now = 14 * 60
    scheduler.run_pending()
    assert calls["covid"] == 0

    clock.now = 15 * 60
    scheduler.run_pending()
    assert calls == {"covid": 1, "news": ["Afternoon"]}
    assert scheduler.updates == []


def test_repeating_update_reschedules_for_next_day():
    scheduler, clock, calls = make_scheduler()
    scheduler.add("Daily", "15:15", repeat=True, covid=True)

    clock.now = 15 * 60
    scheduler.run_pending()
    clock.now = 15 * 60 + 24 * 3600
    scheduler.run_pending()

    assert calls["covid"] == 2
    assert len(scheduler.updates) == 1


def test_cancelled_update_never_runs():
    scheduler, clock, calls = make_scheduler()
    scheduler.add("Cancel me", "15:15", news=True)
    assert scheduler.cancel("Cancel me")

    clock.now = 24 * 3600
    scheduler.run_pending()
    assert calls["news"] == []


def test_rejects_invalid_updates():
    scheduler, _, _ = make_scheduler()
    with pytest.raises(ValueError):
        scheduler.add("Nothing ticked", "15:15")
    scheduler.add("Dup", "15:15", covid=True)
    with pytest.raises(ValueError):
        scheduler.add("Dup", "16:00", covid=True)
