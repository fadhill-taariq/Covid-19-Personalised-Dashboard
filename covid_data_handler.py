"""Fetch and process COVID-19 statistics for the dashboard.

Live figures come from the UK government's coronavirus API via the uk_covid19
package. That API has since been retired, so if a live request fails the
dashboard falls back to the bundled national snapshot in data/ and says so.
"""

import csv
import logging
import os

from config import BASE_DIR

SNAPSHOT_CSV = os.path.join(BASE_DIR, "data", "nation_2021-10-28.csv")
SNAPSHOT_DATE = "28 October 2021"


def parse_csv_data(csv_filename: str) -> list:
    """Return the lines of a CSV file as a list of strings (header included)."""
    with open(csv_filename, "r", encoding="utf-8") as file:
        return file.read().splitlines()


def _to_int(value):
    """Convert a CSV/API value to int, treating blanks and None as missing."""
    if value in (None, ""):
        return None
    return int(value)


def _summarise(rows: list) -> tuple:
    """Work out the three headline figures from rows ordered newest first.

    Each row is a dict with newCasesBySpecimenDate, hospitalCases and
    cumDailyNsoDeathsByDeathDate. The most recent day with a case count is
    usually incomplete, so it is skipped and the next seven days are summed.
    """
    case_counts = [_to_int(row.get("newCasesBySpecimenDate")) for row in rows]
    case_counts = [count for count in case_counts if count is not None]
    last7days_cases = sum(case_counts[1:8]) if len(case_counts) >= 8 else None

    current_hospital_cases = next(
        (_to_int(row.get("hospitalCases")) for row in rows
         if _to_int(row.get("hospitalCases")) is not None),
        None,
    )
    total_deaths = next(
        (_to_int(row.get("cumDailyNsoDeathsByDeathDate")) for row in rows
         if _to_int(row.get("cumDailyNsoDeathsByDeathDate")) is not None),
        None,
    )
    return last7days_cases, current_hospital_cases, total_deaths


def process_covid_csv_data(covid_csv_data: list) -> tuple:
    """Return (cases in the last 7 days, current hospital cases, total deaths).

    Columns are looked up by header name, not position, and blank values are
    skipped, so the result does not depend on fixed row numbers.
    """
    rows = list(csv.DictReader(covid_csv_data))
    return _summarise(rows)


def _local_7day_cases(rows: list):
    """Sum the seven complete days of local cases (skipping the latest day)."""
    counts = [_to_int(row.get("newCasesBySpecimenDate")) for row in rows]
    counts = [count for count in counts if count is not None]
    return sum(counts[1:8]) if len(counts) >= 8 else None


def covid_API_request(location: str = "Exeter", location_type: str = "ltla",
                      nation: str = "England") -> dict:
    """Request live figures from the UK coronavirus API.

    Returns a dict with local and national figures. Raises an exception if
    the API cannot be reached, so the caller can fall back to the snapshot.
    """
    from uk_covid19 import Cov19API  # imported here so offline use doesn't need it

    local_api = Cov19API(
        filters=[f"areaType={location_type}", f"areaName={location}"],
        structure={"newCasesBySpecimenDate": "newCasesBySpecimenDate"},
    )
    national_api = Cov19API(
        filters=["areaType=nation", f"areaName={nation}"],
        structure={
            "newCasesBySpecimenDate": "newCasesBySpecimenDate",
            "hospitalCases": "hospitalCases",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        },
    )
    local_rows = local_api.get_json()["data"]
    national_rows = national_api.get_json()["data"]
    national_cases, hospital_cases, total_deaths = _summarise(national_rows)

    return {
        "location": location,
        "nation": nation,
        "local_7day_cases": _local_7day_cases(local_rows),
        "national_7day_cases": national_cases,
        "hospital_cases": hospital_cases,
        "total_deaths": total_deaths,
        "source": "live",
    }


def snapshot_data(location: str = "Exeter", nation: str = "England") -> dict:
    """Return national figures from the bundled CSV snapshot."""
    national_cases, hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data(SNAPSHOT_CSV)
    )
    return {
        "location": location,
        "nation": nation,
        "local_7day_cases": None,  # the snapshot only holds national data
        "national_7day_cases": national_cases,
        "hospital_cases": hospital_cases,
        "total_deaths": total_deaths,
        "source": f"snapshot ({SNAPSHOT_DATE})",
    }


def get_covid_data(location: str = "Exeter", location_type: str = "ltla",
                   nation: str = "England") -> dict:
    """Try the live API; if it fails, use the bundled snapshot instead."""
    try:
        data = covid_API_request(location, location_type, nation)
        logging.info("Fetched live COVID data for %s / %s", location, nation)
        return data
    except Exception as error:  # the retired API can fail in many ways
        logging.warning("Live COVID API unavailable (%s); using snapshot", error)
        return snapshot_data(location, nation)
