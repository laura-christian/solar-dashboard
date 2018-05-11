"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from datetime import datetime, date, timedelta
import pytz
from flask_sqlalchemy import SQLAlchemy
from model import Geolocation, SolarOutput, Cloudcover, connect_to_db, db
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import csv
from pprint import pprint
from server import app
import os


def load_geolocation():
    """Load geolocation into database."""

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

start_date = datetime(2016, 3, 1, 3, 0, 0)
today = datetime(2018, 5, 9, 3, 0, 0)
diff_in_days = today-start_date

date_list = [start_date + timedelta(days=x) for x in range(diff_in_days.days)]

DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')

DARKSKY_URL="https://api.darksky.net/forecast/"

def load_cloudcover_data(date_range):

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    for date in date_range:
        naive = date
        local_dt = geoloc.timezone.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_unaware = utc_dt.replace(tzinfo=None)
        epoch_time = int((utc_unaware - epoch).total_seconds())
        print epoch_time

        response = session.get(DARKSKY_URL + DARKSKY_TOKEN + "/" + str(geoloc.latitude) + "," + str(geoloc.longitude) + "," + str(epoch_time))
        data = response.json()

        if response.ok:
            sunrise = data['daily']['data'][0]['sunriseTime']
            # print sunrise
            sunset = data['daily']['data'][0]['sunsetTime']
            # print sunset

            cloudcover_percentages = []
            for hourly_dict in data['hourly']['data']:
                cloudiness = hourly_dict.get('cloudCover', 0)
                cloudcover_percentages.append((hourly_dict['time'], cloudiness))
            cloudcover_percentages.sort()
            
            for i in range(len(cloudcover_percentages)-1):
                if sunrise >= cloudcover_percentages[i][0] and sunrise < cloudcover_percentages[i+1][0]:
                    start_idx = i
                if sunset > cloudcover_percentages[i][0] and sunset <= cloudcover_percentages[i+1][0]:
                    end_idx = i + 1

            print cloudcover_percentages[start_idx:end_idx]

            c_records_added = 0
            for epoch_t, cc_perc in cloudcover_percentages[start_idx:end_idx]:
                cloudiness = Cloudcover(local_date=naive.date(), epoch_time=epoch_t, cloudcover=cc_perc)
                db.session.add(cloudiness)
                c_records_added +=1
                if c_records_added % 100 == 0:
                    print c_records_added
                    db.session.commit()

            db.session.commit()


def load_solardata():
    """Load solar output data from csv file."""

    with open("data/Data_Extract_20160314-20180509.csv", "rb") as f:
        
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

    # load_geolocation()
    # load_cloudcover_data(date_list)
    # load_solardata()

geoloc = Geolocation.query.filter_by(geoloc_id=1).one()