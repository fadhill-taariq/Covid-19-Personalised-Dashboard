"""Load dashboard settings from config.json, with environment-variable overrides.

Copy config.example.json to config.json and fill in your own values.
The NewsAPI key can also be supplied with the NEWS_API_KEY environment variable,
so it never has to be written to a file.
"""

import json
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(BASE_DIR, "config.example.json")

DEFAULTS = {
    "news_api_key": "",
    "location_country": "England",
    "local_location": "Exeter",
    "local_location_type": "ltla",
    "news_search_terms": "Covid COVID-19 coronavirus",
}


def load_config(path: str = CONFIG_PATH) -> dict:
    """Return the dashboard settings, falling back to defaults for anything missing."""
    settings = dict(DEFAULTS)
    source = path if os.path.exists(path) else EXAMPLE_CONFIG_PATH
    try:
        with open(source, "r", encoding="utf-8") as file:
            settings.update(json.load(file))
    except (OSError, json.JSONDecodeError) as error:
        logging.warning("Could not read config file %s: %s", source, error)

    env_key = os.environ.get("NEWS_API_KEY")
    if env_key:
        settings["news_api_key"] = env_key
    return settings
