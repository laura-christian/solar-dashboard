"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from datetime import datetime, date, timedelta
import pytz
from flask_sqlalchemy import SQLAlchemy
from model import Geolocation, SolarOutput, Cloudcover, connect_to_db, db
import helper
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import csv
from pprint import pprint
from server import app
import os


def load_geolocations():
    """Load geolocation(s) into database."""

    with open("data/geolocation.csv", "rb") as f:
        
        reader = csv.reader(f, delimiter=",")

        for row in reader:    

            street_addr = row[0]
            city = row[1]
            state = row[2]
            latitude = row[3]
            longitude = row[4]
            elevation = row[5]
            timezone=row[6]

            geolocation = Geolocation(street_addr=street_addr, city=city, state=state, latitude=latitude, 
                                        longitude=longitude, elevation=elevation, timezone=timezone)

            db.session.add(geolocation)
            db.session.commit()

            print "Geolocation committed"

start_date = datetime(2016, 3, 1, 0, 0, 0)
today = datetime(2018, 5, 21, 0, 0, 0)
diff_in_days = today-start_date

date_list = [start_date + timedelta(days=x) for x in range(diff_in_days.days + 1)]

localtz = pytz.timezone('US/Pacific')

DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')

def load_cloudcover_data(date_range):

    # session = requests.Session()
    # retry = Retry(connect=3, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://', adapter)
    # session.mount('https://', adapter)

    for date in date_range:
        # Convert naive datetime object to utc, then to epoch time
        utc = helper.convert_naive_local_time_to_utc(date, localtz)
        epoch_time = helper.convert_utc_to_epoch(utc)

        # Ping darksky API for historical weather data

        url = "https://api.darksky.net/forecast/{token}/{lat},{long},{epoch_time}".format(token=DARKSKY_TOKEN, lat=37.8195, long=-122.2523, epoch_time=epoch_time)
        response = requests.get(url)
        data = response.json()

        if response.ok:
            sunrise = data['daily']['data'][0]['sunriseTime']
            sunset = data['daily']['data'][0]['sunsetTime']

            # Record cloudcover percentages observed at each hour within corresponding 24-hour period
            cloudcover_percentages = []
            for hourly_dict in data['hourly']['data']:
                cloudiness = hourly_dict.get('cloudCover', 0)
                cloudcover_percentages.append((hourly_dict['time'], cloudiness))
            cloudcover_percentages.sort()
            
            # Filter out nighttime cloudcover percentages (irrelevant in relation to solar energy data)
            for i in range(len(cloudcover_percentages)-2):
                if sunrise >= cloudcover_percentages[i][0] and sunrise < cloudcover_percentages[i+1][0]:
                    start_idx = i
                if sunset > cloudcover_percentages[i][0] and sunset <= cloudcover_percentages[i+1][0]:
                    end_idx = i + 2

            print cloudcover_percentages[start_idx:end_idx]

            c_records_added = 0
            for epoch_t, cc_perc in cloudcover_percentages[start_idx:end_idx]:
                cloudiness = Cloudcover(local_date=date.date(), epoch_time=epoch_t, cloudcover=cc_perc)
                db.session.add(cloudiness)
                c_records_added +=1
                if c_records_added % 100 == 0:
                    print c_records_added
                    db.session.commit()

            db.session.commit()


def load_solardata():
    """Load solar output data from csv file."""

    with open("data/Data_Extract_20180501-20180521.csv", "rb") as f:
        
        reader = csv.reader(f, delimiter=",")

        c_records_added = 0
        for row in reader:

            dt_local_raw = row[0]
            dt_local = datetime.strptime(dt_local_raw, '%m/%d/%Y %H:%M:%S')
            
            if row[1]:
                kWh = row[1]
            else:
                kWh = 0
                
            solaroutput = SolarOutput(dt_local=dt_local, kWh=kWh)

            db.session.add(solaroutput)
            c_records_added += 1
            if c_records_added % 1000 == 0:
                db.session.commit()
                print c_records_added
    
        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    # db.drop_all()
    # db.create_all()

    # load_geolocations()
    # load_cloudcover_data(date_list)
    # load_solardata()

