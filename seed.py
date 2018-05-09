"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from datetime import datetime, date, timedelta
import pytz
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

    street_addr = '49 Moss Ave'
    city = 'Oakland'
    state = 'CA'
    latitude = 37.8195
    longitude = -122.252303
    elevation = 125
    timezone = 'US/Pacific'

    geolocation = Geolocation(street_addr=street_addr, city=city, state=state, latitude=latitude, longitude=longitude, elevation=elevation, timezone=timezone)

    db.session.add(geolocation)
    db.session.commit()

    print "Geolocation committed"


DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')

DARKSKY_URL="https://api.darksky.net/forecast/"

latitude=37.8195
longitude=-122.2523

start_date = datetime(2016, 1, 1, 3, 0, 0)
today = datetime.today()
diff_in_days = today-start_date

date_list = [start_date + timedelta(days=x) for x in range(diff_in_days.days)]


epoch = datetime.fromtimestamp(0)
localtz = pytz.timezone('US/Pacific')

def load_cloudcover_data(date_range):

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    for date in date_range[:3]:
        naive = date
        local_dt = localtz.localize(naive)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_unaware = utc_dt.replace(tzinfo=None)
        epoch_time = int((utc_unaware - epoch).total_seconds())
        print epoch_time

        response = session.get(DARKSKY_URL + DARKSKY_TOKEN + "/" + str(latitude) + "," + str(longitude) + "," + str(epoch_time))

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

            # db.session.commit()


def load_solardata():
    """Load solar output data from csv file."""

    with open("data/Data_Extract_20160314-20180509.csv", "rb") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            dt_local_raw = row[0]
            dt_local = datetime.strptime(dt_local_raw, '%m/%d/%Y %H:%M:%S')
            kWh = row[1]
        
            solaroutput = SolarOutput(dt_local=dt_local, kWh=kWh)
            db.session.add(solaroutput)

            c_records_added = 0
            for kWh_sum in solaroutput:
                solaroutput = SolarOutput(dt_local=dt_local, kWh=kWh)
                db.session.add(solaroutput)
                c_records_added +=1
                if c_records_added % 1000 == 0:
                    print c_records_added
                    db.session.commit()
    
        db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.drop_all()
    db.create_all()

    load_geolocation()
    # load_cloudcover_data(date_list)
    load_solardata()