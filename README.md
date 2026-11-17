# Personalised COVID-19 Dashboard

A Flask web dashboard that shows COVID-19 statistics for a chosen local area and nation, alongside the latest COVID news headlines. You can schedule automatic data and news updates for a time of day, either once or daily.

Originally built in late 2021 as coursework for ECM1400 (Programming) at the University of Exeter, and tidied up since.

## Features

- **Local and national figures:** cases over the last 7 days for your area and nation, current hospital cases and total deaths.
- **News headlines:** the latest COVID-related articles from [NewsAPI](https://newsapi.org). Dismissed articles stay hidden after later refreshes.
- **Scheduled updates:** pick a time, give the update a label, and choose whether to refresh COVID data, news, or both, once or every day. Updates can be cancelled from the dashboard.
- **Offline fallback:** the UK government coronavirus API the project was built on has since been retired. If a live request fails, the dashboard shows national figures from a bundled snapshot (28 October 2021) and labels them as such.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Flask app and routes (entry point) |
| `covid_data_handler.py` | Fetches live figures, parses the CSV snapshot, falls back when the API is unavailable |
| `covid_news_handling.py` | NewsAPI requests and the store of current and dismissed headlines |
| `update_scheduler.py` | Schedules, repeats and cancels updates using Python's `sched` module |
| `config.py` | Loads settings from `config.json` and environment variables |
| `templates/index.html` | Dashboard page (Bootstrap) |
| `data/nation_2021-10-28.csv` | National snapshot used for the fallback and tests |
| `tests/` | pytest suite |

## Getting started

Requires Python 3.9 or later.

```bash
git clone https://github.com/fadhill-taariq/Covid-19-Personalised-Dashboard.git
cd Covid-19-Personalised-Dashboard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Copy the example config and edit it:

```bash
cp config.example.json config.json
```

| Setting | Meaning |
| --- | --- |
| `news_api_key` | Your free key from [newsapi.org/register](https://newsapi.org/register). Leave blank to run without news. |
| `location_country` | Nation to show, e.g. `England` |
| `local_location` | Local area, e.g. `Exeter` |
| `local_location_type` | Area type used by the API, e.g. `ltla` (lower-tier local authority) |
| `news_search_terms` | Space-separated terms; an article matching any of them is included |

`config.json` is git-ignored so your key is never committed. You can also set the key as an environment variable instead:

```bash
export NEWS_API_KEY=your-key-here
```

### Running

```bash
python app.py
```

Then open <http://127.0.0.1:5000/index>. The page refreshes every minute, which is also when due scheduled updates run. Scheduled updates are held in memory, so they are lost when the app stops.

### Tests

```bash
pytest
```

The tests do not need network access or an API key: API calls are replaced with fakes and the scheduler runs on a simulated clock.

## Credits

The page template is based on the starter template provided for ECM1400. COVID data © UK Health Security Agency, published under the Open Government Licence.
