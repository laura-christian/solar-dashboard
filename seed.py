"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from datetime import datetime, date, timedelta
import pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from model import Geolocation, SolarOutput, Cloudcover, connect_to_db, db
import helper
import requests
import csv
from server import app
import os

localtz = pytz.timezone('US/Pacific')
DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')

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

def poll_darksky(epoch_time):
    """For retrieving historical cloudcover data from DarkSky weather API"""

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

        cloudcover_percentages = cloudcover_percentages[start_idx:end_idx]
        
        return cloudcover_percentages


def load_cloudcover_data(date_range):

    for date in date_range:
        # Convert naive datetime object to utc, then to epoch time
        utc_dt = helper.convert_naive_local_time_to_utc(date, localtz)
        epoch_time = helper.convert_utc_to_epoch(utc_dt)

        cloudcover_percentages = poll_darksky(epoch_time)

        c_records_added = 0
        for epoch_t, cc_perc in cloudcover_percentages:
            cloudiness = Cloudcover(local_date=date.date(), epoch_time=epoch_t, cloudcover=cc_perc)
            db.session.add(cloudiness)
            c_records_added +=1
            if c_records_added % 100 == 0:
                print c_records_added
                db.session.commit()

            db.session.commit()

def update_cloudcover_data():

    # Get date of last record
    last_record = db.session.query(Cloudcover).order_by(Cloudcover.cloudiness_id.desc()).first()
    date_of_last_record = last_record.local_date

    # Delete records from last day of recorded cloudcover percentages for greater accuracy (some will
    # have been forecast rather than observed values)
    Cloudcover.query.filter(Cloudcover.local_date == date_of_last_record).delete()

    # Convert date of last record to epoch time in order to poll Darksky API for interim cloudcover
    # percentages
    date_utc = helper.convert_naive_local_time_to_utc(date_of_last_record, localtz)
    date_epoch = helper.convert_utc_to_epoch(date_utc)

    today = helper.get_today_local()
    today = datetime(today.year, today.month, today.day, 0, 0, 0) #Get today midnight (local) as naive date-time object

    # Get number of days between last update and today
    date_diff = today - date_of_last_record
    num_days = date_diff.days

    # Generate date range
    date_range = helper.generate_date_range(date_of_last_record, num_days+1) 

    # Call seeding function to load new data
    load_cloudcover_data(date_range)


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
    # update_cloudcover_data()

