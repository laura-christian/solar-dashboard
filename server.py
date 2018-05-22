"""Movie Ratings."""

from jinja2 import StrictUndefined
from sqlalchemy import func
from flask import Flask, render_template, request, flash, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from os.path import abspath, dirname, join, pardir
import sys
import os
from model import connect_to_db, db, Geolocation, SolarOutput, Cloudcover
import requests
import sunstats
from astral import Astral, Location
import helper
from datetime import datetime, date, time, timedelta, tzinfo
import pytz

# Create Flask application
app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "adlkfj123fdn394a"

# Cause Jinja to fail loudly, so errors are caught
app.jinja_env.undefined = StrictUndefined

JS_TESTING_MODE = False

path_source = dirname(abspath(__file__))
path_parent = abspath(join(path_source, pardir))
if path_source not in sys.path:
    sys.path.append(path_source)

DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')
localtz = pytz.timezone('US/Pacific')

@app.before_request
def add_tests():

    g.jasmine_tests = JS_TESTING_MODE


@app.route('/')
def index():
    """Render homepage."""

    return render_template("homepage.html")


@app.route("/solaroutput.json")
def get_bar_graph_data():
    """Aggregate solar output data for different slices of time"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'today':

        start_date = helper.get_today_local()
        end_date = start_date + timedelta(days=1)
        increment = 'hour'


    elif timeframe == 'yesterday':
             
        start_date = helper.get_yesterday_local()
        end_date = helper.get_today_local()
        increment = 'hour'

    elif timeframe == 'last_seven_days':

        start_date = helper.get_seven_days_ago()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'day'

    elif timeframe == 'this_month':
             
        start_date = helper.get_first_day_this_month()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'day'

    elif timeframe == 'last_month':

        start_date = helper.get_first_day_last_month()
        end_date = helper.get_first_day_this_month()
        increment = 'day'

    elif timeframe == 'this_year':

        start_date = helper.get_first_this_year()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'month'

    elif timeframe == 'last_year':
             
        start_date = helper.get_first_last_year()
        end_date = helper.get_first_this_year()
        increment = 'month'

    # Create subquery object to capture all kWh values b/w start and end dates
    subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
        filter(SolarOutput.dt_local>=start_date, SolarOutput.dt_local<end_date).subquery()
    # In turn perform group-by query on subquery to sum values for increment of time in which totals displayed
    q = db.session.query(func.date_trunc(increment, subq.c.dt_local),func.sum(subq.c.kWh)).\
        group_by(func.date_trunc(increment, subq.c.dt_local)).having(func.sum(subq.c.kWh)>0).\
        order_by(func.date_trunc(increment,subq.c.dt_local)).all()

    # Iterate over query results to get labels and data for bar chart and totals for tile stats

    if increment == 'hour':
        labels = []
        data = []
        for dt, kWh in q:
            dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
            labels.append(dt.strftime('%-I %p')) # Convert to string reflecting local time
            data.append(kWh)
        total_kWh = sum(data)

    elif increment == 'day':
        labels = []
        data = []
        for dt, kWh in q:
            labels.append(dt.strftime('%-m/%-d')) # Convert to string reflecting local date
            data.append(kWh)
        total_kWh = sum(data)

    elif increment == 'month':
        labels = []
        data = []
        for dt, kWh in q:
            labels.append(dt.strftime('%b')) #Convert to abbreviation for month
            data.append(kWh)
        total_kWh = sum(data)


    return jsonify({'labels': labels, 'data': data, 'total_kWh': total_kWh})

@app.route("/solarpath.json")
def get_solar_path_data():
    """Get data relevant to solar path above site for different slices of time"""

    a = Astral()
    a.solar_depression = 'civil'

    l = Location()
    l.latitude = 37.8195
    l.longitude = -122.2523
    l.timezone = 'US/Pacific'
    l.elevation = 125

    timeframe=request.args.get('timeframe')

    if timeframe == 'today':
        sunrise = l.sunrise().strftime('%-I:%M%p')
        sunset = l.sunset().strftime('%-I:%M%p')
        day_length = str(l.sunset()-l.sunrise())
        solar_noon = l.solar_noon().strftime('%-I:%M%p')
        solar_zenith = l.solar_elevation(l.solar_noon().replace(tzinfo=None))
        solar_elevation = l.solar_elevation()
        solar_path_data = {'sunrise': sunrise, 'sunset': sunset, 'daylength': day_length, 'solar_noon': solar_noon, 'zenith': solar_zenith, 'elevation': solar_elevation}

    elif timeframe == 'yesterday':
        yesterday = helper.get_yesterday_local()
        solar_path_data = sunstats.sun_single_day(yesterday)

    return jsonify(solar_path_data)

@app.route("/weather.json")
def get_weather_forecast():
    """Get current local weather conditions plus forecast from DarkSky API"""

    url = "https://api.darksky.net/forecast/{token}/{lat},{long}".format(token=DARKSKY_TOKEN, lat=37.8195, long=-122.2523)
    response = requests.get(url)
    data = response.json()

    if response.ok:
        current_conditions = data['currently']
        forecast_conditions = data['daily']['data'][1:] # Skpping over forecast for today

    return jsonify({'current': current_conditions, 'forecast': forecast_conditions})

@app.route("/cloudcover_today.json")
def get_cloudcover_today():
    """Retrieve observed and anticipated cloudcover patterns for today from DarkSky API"""

    today = helper.get_today_local()
    today = datetime(today.year, today.month, today.day, 0, 0, 0) #Get today midnight (local) as naive date-time object
    today_utc = helper.convert_naive_local_time_to_utc(today, localtz)
    today_epoch = helper.convert_utc_to_epoch(today_utc)

    url = "https://api.darksky.net/forecast/{token}/{lat},{long},{epoch_time}".format(token=DARKSKY_TOKEN, lat=37.8195, long=-122.2523, epoch_time=today_epoch)
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
        print cloudcover_percentages

        labels = []
        data = []
        for epoch, cloudcover_percentage in cloudcover_percentages:
            utc_time = datetime.fromtimestamp(epoch)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            labels.append(local_time.strftime('%-I %p')) #Convert to local time, hourly intervals
            data.append(int(cloudcover_percentage*100))

    return jsonify({'labels': labels, 'data': data})


@app.route("/cloudcover_averages.json")
def get_cloudcover_data():
    """Get average cloudcover for different slices of time"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'yesterday':
             
        start_date = helper.get_yesterday_local()
        end_date = helper.get_today_local()
        increment = 'hour'

    elif timeframe == 'last_seven_days':

        start_date = helper.get_seven_days_ago()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'day'

    elif timeframe == 'this_month':
             
        start_date = helper.get_first_day_this_month()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'day'

    elif timeframe == 'last_month':

        start_date = helper.get_first_day_last_month()
        end_date = helper.get_first_day_this_month()
        increment = 'day'

    elif timeframe == 'this_year':

        start_date = helper.get_first_this_year()
        end_date = helper.get_today_local() + timedelta(days=1)
        increment = 'month'

    elif timeframe == 'last_year':
             
        start_date = helper.get_first_last_year()
        end_date = helper.get_first_this_year()
        increment = 'month'

    # Single-day graph values require dedicated query since data is displayed in hourly increments
    if timeframe == 'yesterday':

        cloudcover_percentages = Cloudcover.query.filter(Cloudcover.local_date>=start_date, Cloudcover.local_date<end_date)

        labels = []
        data = []
        for cc_obj in cloudcover_percentages:
            utc_time = datetime.fromtimestamp(cc_obj.epoch_time)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            labels.append(local_time.strftime('%-I %p')) #Convert to local time, hourly intervals
            data.append(int(cc_obj.cloudcover*100))

    else:

        # Create subquery object to capture all cloudcover values b/w start and end dates
        subq = db.session.query(Cloudcover.local_date, Cloudcover.cloudcover).\
            filter(Cloudcover.local_date>=start_date, Cloudcover.local_date<end_date).subquery()
        # In turn perform group-by query on subquery to sum values for increment of time in which totals displayed
        q = db.session.query(func.date_trunc(increment, subq.c.local_date),func.avg(subq.c.cloudcover)).\
            group_by(func.date_trunc(increment, subq.c.local_date)).order_by(func.date_trunc(increment,subq.c.local_date)).all()

    # Iterate over query results to get labels and data for cloudcover line graph
    if increment == 'day':
        labels = []
        data = []
        for local_date, cloudcover_percentage in q:
            labels.append(local_date.strftime('%-m/%-d')) # Convert datetime object to string reflecting local date
            data.append(int(cloudcover_percentage*100))

    elif increment == 'month':
        labels = []
        data = []
        for month, cloudcover_percentage in q:
            labels.append(month.strftime('%b')) #Convert datetime object to abbreviation for month
            data.append(int(cloudcover_percentage*100))
        total_kWh = sum(data)


    return jsonify({'labels': labels, 'data': data})


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
