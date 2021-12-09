import requests
import json
import pytest
import logging
import time
import sched
import os
import flask
from flask import Flask
from flask import render_template
from flask import request
from newsapi import NewsApiClient, newsapi_client
from covid_data_handler import covid_API_request



news = [
              {
                     "title": "TITLE EXAMPLE",
                     "content": "CONTENT EXAMPLE"
              },
              {
                     "title": "TITLE EXAMPLE 2",
                     "content": "CONTENT EXAMPLE 2"
              }
       ]

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)

dashboard_title, location, locInfectionSum, location_country, natInfectionSum, natHospitalCases, natCumDeaths = covid_API_request()

image = os.path.join('static', 'corona_pic')

with open("config.json", "r") as file:
       temp2 = file.read()
       temp3 = json.loads(temp2)
       personal_api_key = temp3["personal_api_key"]

def covid_API_request():
       #"""import covid data requested in the Covid Data Handler."""
       int(locInfectionSum)
       int(natInfectionSum)
       int(natCumDeaths)

       return dashboard_title, location, locInfectionSum, location_country, natInfectionSum, natHospitalCases, natCumDeaths


app.config['UPLOAD_FOLDER'] = image


def news_API_request(covid_terms="Covid"):
    #"""use NewsApi to request news articles linked with the Covid-19 pandemic."""
    news = [{}]
    newsapi = NewsApiClient(api_key= str(personal_api_key))
    top_headlines = newsapi.get_top_headlines(q = covid_terms)
    for i in range(0,5):
        news.append(top_headlines["articles"][i])
    del news[0]
    print(news)
    
    return news
news_API_request()


def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()


def add_news_article():
    news.append({
           "title": "T",
           "content": "C"
})

def schedule_add_news(up):
       e1 = s.enter(up,1,add_news_article)

def minutes_to_seconds( minutes: str ) -> int:
      #"""Converts minutes to seconds"""
      return int(minutes)*60

def hours_to_minutes( hours: str ) -> int:
      #"""Converts hours to minutes"""
      return int(hours)*60

def hhmm_to_seconds( hhmm: str ) -> int:
      if len(hhmm.split(':')) != 2:
          print('Incorrect format. Argument must be formatted as HH:MM')
          return None
      return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
          minutes_to_seconds(hhmm.split(':')[1])


@app.route('/index')
def run_flask():
       #"""configure flask template, covid data and news articles which will be inputted into the dashboard here."""
       full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'coronaimg.gif')
       news = news_API_request()
       covid_data = covid_API_request()
       s.run(blocking=False)
       data = request.args.get("update")
       data_title = request.args.get("two")
       text_field = request.args.get('two')
       print(text_field)
       print(data)
       if text_field:
              temp_list = {'title':data_title, 'content':data}
              update_time = request.args.get('update')
              print(update_time)
              update_time_sec = hhmm_to_seconds(update_time)
              schedule_add_news(update_time_sec)
       return render_template('index.html', title = dashboard_title,
              image = 'coronaimg.gif', 
              news_articles = news, 
              local_location = location, 
              nation_location = location_country, 
              local_7day_infections = locInfectionSum, 
              national_7day_infections = natInfectionSum, 
              current_hospital_cases = natHospitalCases, 
              total_deaths = natCumDeaths)
if __name__ == '__main__':
    app.run()