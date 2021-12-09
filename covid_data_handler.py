import json
import csv
import sched
import time
import logging
from uk_covid19 import Cov19API
  
#"""initialise an events logging file."""
logging.basicConfig(filename='events.log', encoding='utf-8')
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


with open("config.json", "r") as file:
       temp2 = file.read()
       temp3 = json.loads(temp2)
       location_country = temp3["location_country"]
       location = temp3["local_location"]


def parse_csv_data(csv_filename):
    #"""read data from covid_csv_data and return the data."""
    covid_csv_data =open(csv_filename , 'r').readlines()
    return(covid_csv_data)


def test_parse_csv_data():
    #"""check that csv file is processed correctly."""
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639
    print(data)


def process_covid_csv_data(covid_csv_data):
    #"""process covid data, return 3 variables: the number of cases in the last 7 days, current hospital cases, and the total number of deaths."""
    last7days_cases = 0
    for i in range(3,10):
        content_list_7days = covid_csv_data[i].split(",")
        last7days_cases += int(content_list_7days[6])
    content_hospital_list = covid_csv_data[1].split(",")
    current_hospital_cases = int(content_hospital_list[5])
    cumu_deaths = covid_csv_data[14].split(",")
    total_deaths = int(cumu_deaths[4])
    return(last7days_cases, current_hospital_cases, total_deaths)
last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(parse_csv_data('nation_2021_10_28.csv'))
print("The number of cases in the last 7 days is " + str(last7days_cases) + "." + "\n",
"The current number of hospital cases is " + str(current_hospital_cases) + "." + "\n",
"The cumulative number of deaths are " + str(total_deaths) + ".") 


def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def covid_API_request( location="Exeter", location_type="ltla"):
    #"""use the Covid-19 Api to request values which will be displayed on the Covid Dashboard."""
    local = ['areaType=' + location_type,'areaName=' + location]
    national = ['areaType=nation','areaName=' + location_country]

    national_filt = {
        "newCasesBySpecimenDate": "newCasesBySpecimenDate", 
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate", 
        "hospitalCases": "hospitalCases"
    }
    local_filt = {
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }
    
    local_api = Cov19API(filters=local, structure=local_filt)
    local_data_API = local_api.get_json()['data']

    national_api = Cov19API(filters=national, structure=national_filt)
    national_data_api = national_api.get_json()['data']

    natInfectionSum=0
    locInfectionSum=0
    count=1

    while(count!=7):
        singleDayNat = national_data_api[count]
        singleDayLoc = local_data_API[count]
        natInfectionSum = natInfectionSum + singleDayNat.get('newCasesBySpecimenDate')
        locInfectionSum = locInfectionSum + singleDayLoc.get('newCasesBySpecimenDate')
        count=count+1
    natHospCases = national_data_api[0].get('hospitalCases')
    natCumDeaths = national_data_api[17].get('cumDailyNsoDeathsByDeathDate')
    dashboard_title = "Covid-19 Infection Rates:"
    
    return dashboard_title, location , locInfectionSum, location_country, natInfectionSum, natHospCases, natCumDeaths
def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)


{
    'data': [
        {
            'date': '2020-07-28',
            'location': 'Exeter',
            'areaCode': 'E92000001',
            'newCasesByPublishDate': 547,
            'cumCasesByPublishDate': 259022,
            'newDeaths28DaysByDeathDate': None,
            'cumDeaths28DaysByDeathDate': None
        },
        {
            'date': '2020-07-27',
            'location': 'Exeter',
            'areaCode': 'E92000001',
            'newCasesByPublishDate': 616,
            'cumCasesByPublishDate': 258475,
            'newDeaths28DaysByDeathDate': 20,
            'cumDeaths28DaysByDeathDate': 41282
        },
        ...
    ],
    'lastUpdate': '2020-07-28T15:34:31.000000Z',
    'length': 162,
    'totalPages': 1
}


cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeaths28DaysByDeathDate": "newDeaths28DaysByDeathDate",
    "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate"
}


england_only = [
    'areaType=nation',
    'areaName=England'
]


api = Cov19API(filters=england_only, structure=cases_and_deaths)


api_timestamp = api.last_update


schedule_covid_updates = sched.scheduler(time.time, time.sleep)
def print_event(covid_API_request):
    print(covid_API_request)

e1 = schedule_covid_updates.enter(10, 1, print_event, ('first',))
e1 = schedule_covid_updates.enter(10, 1, print_event, ('second',))
schedule_covid_updates.run(blocking=True)