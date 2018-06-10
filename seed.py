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


def load_cloudcover_data(date_range):

    for date in date_range:
        # Convert naive datetime object to utc, then to epoch time
        utc_dt = helper.convert_naive_local_time_to_utc(date, localtz)
        epoch_time = helper.convert_utc_to_epoch(utc_dt)

        cloudcover_percentages = helper.poll_darksky(epoch_time)

        c_records_added = 0
        for epoch_t, cc_perc in cloudcover_percentages:
            cloudiness = Cloudcover(local_date=date.date(), epoch_time=epoch_t, cloudcover=cc_perc)
            db.session.add(cloudiness)
            c_records_added +=1
            if c_records_added % 100 == 0:
                print c_records_added
                db.session.commit()

            db.session.commit()

def load_solardata(file):
    """Load solar output data from csv file."""

    with open("data/{}.csv".format(file), "rb") as f:
        
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
#     # db.drop_all()
#     # db.create_all()

#     # load_geolocations()
#     # start_date = datetime(2016, 3, 1, 0, 0, 0)
#     # today = datetime.today()
#     # today = today.replace(hour=0, minute=0)
#     # diff_in_days = today-start_date
#     # date_list = [start_date + timedelta(days=x) for x in range(diff_in_days.days +1)]
    # load_cloudcover_data(date_list)
    files = ['Data_Extract_20160314-20180509', 'Data_Extract_20180501-20180521', 'Data_Extract_20180521-20180528', 'Data_Extract_20180528-20180607']
    for file in files:
        load_solardata(file)
    # update_cloudcover_data()

