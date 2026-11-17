"""Personalised COVID-19 dashboard - Flask entry point.

Run with:  python app.py   then open http://127.0.0.1:5000/index
"""

import logging

from flask import Flask, redirect, render_template, request, url_for

from config import load_config
from covid_data_handler import get_covid_data
from covid_news_handling import NewsStore
from update_scheduler import UpdateScheduler

logging.basicConfig(
    filename="events.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def create_app(settings: dict = None, covid_fetcher=get_covid_data,
               news_store: NewsStore = None) -> Flask:
    """Build the Flask app. Arguments allow tests to swap in fakes."""
    settings = settings or load_config()
    app = Flask(__name__)

    def fetch_covid():
        return covid_fetcher(settings["local_location"],
                             settings["local_location_type"],
                             settings["location_country"])

    state = {"covid": fetch_covid()}
    news = news_store or NewsStore(settings["news_api_key"],
                                   settings["news_search_terms"])
    news.update_news("startup")

    def update_covid():
        state["covid"] = fetch_covid()

    scheduler = UpdateScheduler(update_covid, news.update_news)
    app.config["scheduler"] = scheduler
    app.config["news"] = news

    @app.route("/")
    def home():
        return redirect(url_for("index"))

    @app.route("/index")
    def index():
        scheduler.run_pending()
        args = request.args

        if args.get("notif"):
            news.remove(args["notif"])
            return redirect(url_for("index"))

        if args.get("update_item"):
            scheduler.cancel(args["update_item"])
            return redirect(url_for("index"))

        if args.get("two"):
            try:
                scheduler.add(
                    title=args["two"],
                    hhmm=args.get("update", ""),
                    repeat="repeat" in args,
                    covid="covid-data" in args,
                    news="news" in args,
                )
            except ValueError as error:
                logging.warning("Rejected scheduled update: %s", error)
                return redirect(url_for("index", error=str(error)))
            return redirect(url_for("index"))

        return render_template(
            "index.html",
            title="Covid-19 Dashboard",
            image="coronaimg.gif",
            covid=state["covid"],
            news_articles=news.visible(),
            updates=scheduler.updates,
            error=args.get("error"),
        )

    return app


if __name__ == "__main__":
    create_app().run()
