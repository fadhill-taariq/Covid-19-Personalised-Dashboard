"""Schedule COVID data and news updates for a chosen time of day."""

import logging
import sched
import time
from datetime import datetime, timedelta

SECONDS_PER_DAY = 24 * 60 * 60


def hhmm_to_seconds(hhmm: str) -> int:
    """Convert 'HH:MM' to seconds after midnight. Raises ValueError if malformed."""
    parts = hhmm.split(":")
    if len(parts) != 2:
        raise ValueError("Time must be formatted as HH:MM")
    hours, minutes = int(parts[0]), int(parts[1])
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError("Time must be between 00:00 and 23:59")
    return hours * 3600 + minutes * 60


def seconds_until(hhmm: str, now: datetime = None) -> int:
    """Seconds from now until the next occurrence of HH:MM (today or tomorrow)."""
    now = now or datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    target = midnight + timedelta(seconds=hhmm_to_seconds(hhmm))
    if target <= now:
        target += timedelta(days=1)
    return int((target - now).total_seconds())


class UpdateScheduler:
    """Keeps a list of scheduled updates and runs them when they fall due.

    Call run_pending() regularly (the dashboard does this on every page load,
    and the page refreshes itself every minute).
    """

    def __init__(self, update_covid, update_news,
                 timefunc=time.time, now_func=datetime.now):
        self._update_covid = update_covid
        self._update_news = update_news
        self._now = now_func
        self._scheduler = sched.scheduler(timefunc, time.sleep)
        self.updates = []

    def add(self, title: str, hhmm: str, repeat: bool = False,
            covid: bool = False, news: bool = False) -> dict:
        """Schedule an update. Raises ValueError for bad input or duplicate titles."""
        title = title.strip()
        if not title:
            raise ValueError("An update needs a label")
        if any(update["title"] == title for update in self.updates):
            raise ValueError(f"An update called {title!r} already exists")
        if not (covid or news):
            raise ValueError("Choose COVID data, news, or both")

        delay = seconds_until(hhmm, self._now())
        update = {"title": title, "time": hhmm, "repeat": repeat,
                  "covid": covid, "news": news}
        update["content"] = self._describe(update)
        update["event"] = self._scheduler.enter(delay, 1, self._run_update, (update,))
        self.updates.append(update)
        logging.info("Scheduled update %r at %s (repeat=%s)", title, hhmm, repeat)
        return update

    def cancel(self, title: str) -> bool:
        """Remove a scheduled update by title. Returns True if one was removed."""
        for update in self.updates:
            if update["title"] == title:
                try:
                    self._scheduler.cancel(update["event"])
                except ValueError:
                    pass  # it had already run
                self.updates.remove(update)
                logging.info("Cancelled update %r", title)
                return True
        return False

    def run_pending(self) -> None:
        """Run any updates whose time has come, without waiting for future ones."""
        self._scheduler.run(blocking=False)

    def _run_update(self, update: dict) -> None:
        logging.info("Running update %r", update["title"])
        if update["covid"]:
            self._update_covid()
        if update["news"]:
            self._update_news(update["title"])
        if update["repeat"]:
            update["event"] = self._scheduler.enter(
                SECONDS_PER_DAY, 1, self._run_update, (update,))
        elif update in self.updates:
            self.updates.remove(update)

    @staticmethod
    def _describe(update: dict) -> str:
        parts = [name for name, wanted in
                 (("COVID data", update["covid"]), ("news", update["news"])) if wanted]
        when = f"every day at {update['time']}" if update["repeat"] else f"at {update['time']}"
        return f"Update {' and '.join(parts)} {when}"
