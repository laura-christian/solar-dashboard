from sqlalchemy import func
from flask import Flask, render_template, request, flash, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from os.path import abspath, dirname, join, pardir
import sys
import os
from model import connect_to_db, db, Geolocation, SolarOutput, Cloudcover
import seed
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

JS_TESTING_MODE = False

path_source = dirname(abspath(__file__))
path_parent = abspath(join(path_source, pardir))
if path_source not in sys.path:
    sys.path.append(path_source)

DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')
localtz = pytz.timezone('US/Pacific')

a = Astral()
a.solar_depression = 'civil'

l = Location()
l.latitude = 37.8195
l.longitude = -122.2523
l.timezone = 'US/Pacific'
l.elevation = 125

@app.before_request
def add_tests():

    g.jasmine_tests = JS_TESTING_MODE


@app.route('/')
def index():
    """Render homepage."""

    # seed.update_cloudcover_data()

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

@app.route("/daylight_deets.json")
def get_daylight_details():
    """Get details of solar path/daylight hours at site for today (local)"""
    
    sunrise = l.sunrise().strftime('%-I:%M%p')
    sunset = l.sunset().strftime('%-I:%M%p')
    day_length = str(l.sunset()-l.sunrise())
    solar_noon = l.solar_noon().strftime('%-I:%M%p')
    solar_zenith = l.solar_elevation(l.solar_noon().replace(tzinfo=None))
    solar_elevation = l.solar_elevation()

    daylight_data = {'sunrise': sunrise, 'sunset': sunset, 'daylength': day_length, 'solar_noon': solar_noon, 'zenith': solar_zenith, 'elevation': solar_elevation}

    return jsonify(daylight_data)

@app.route("/solar_arc.json")
def get_solar_arc_data():
    """Get data relevant to solar arc above site for different slices of time"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'today':
        today = helper.get_today_local()
        solar_arc_data = sunstats.solar_arc_single_day(today)

    elif timeframe == 'yesterday':
        yesterday = helper.get_yesterday_local()
        solar_arc_data = sunstats.solar_arc_single_day(yesterday)

    elif timeframe == 'last_seven_days':

        start_date = helper.get_seven_days_ago()
        end_date = helper.get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]
        solar_arc_data = sunstats.zenith_range_dates(date_range, timeframe)

    elif timeframe == 'this_month':
             
        start_date = helper.get_first_day_this_month()
        end_date = helper.get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]
        solar_arc_data = sunstats.zenith_range_dates(date_range, timeframe)

    elif timeframe == 'last_month':

        start_date = helper.get_first_day_last_month()
        end_date = helper.get_first_day_this_month()
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]
        solar_arc_data = sunstats.zenith_range_dates(date_range, timeframe)

    elif timeframe == 'this_year':

        start_date = helper.get_first_this_year()
        today = helper.get_today_local()
        current_month = today.month
        current_day = today.day
        date_range = []
        for m in range(1, current_month):
            date_range.append(start_date.replace(month=m))
            date_range.append(date_range[-1]+timedelta(days=14))
        date_range.append(today.replace(day=1))
        if current_day >= 15:
            date_range.extend([today.replace(day=15), today])
        else:
            date_range.append(today)
        solar_arc_data = sunstats.zenith_range_dates(date_range, timeframe)

    elif timeframe == 'last_year':
             
        start_date = helper.get_first_last_year()
        end_date = helper.get_first_this_year()
        date_range = []
        for m in range(1, 13):
            date_range.append(start_date.replace(month=m))
            date_range.append(date_range[-1]+timedelta(days=14))
        date_range.append(end_date - timedelta(days=1))
        solar_arc_data = sunstats.zenith_range_dates(date_range, timeframe)

    return jsonify(solar_arc_data)


@app.route("/weather.json")
def get_weather_forecast():
    """Get current local weather conditions plus forecast from DarkSky API"""

    url = "https://api.darksky.net/forecast/{token}/{lat},{long}".format(token=DARKSKY_TOKEN, lat=37.8195, long=-122.2523)
    response = requests.get(url)
    data = response.json()

    if response.ok:
        current_conditions = data['currently']
        forecast_conditions = data['daily']['data'][1:] # Skipping over forecast for today

    return jsonify({'current': current_conditions, 'forecast': forecast_conditions})


@app.route("/cloudcover_today.json")
def get_cloudcover_today():
    """Retrieve observed and anticipated cloudcover patterns for today from DarkSky API"""

    today = helper.get_today_local()
    today = datetime(today.year, today.month, today.day, 0, 0, 0) #Get today midnight (local) as naive date-time object
    today_utc = helper.convert_naive_local_time_to_utc(today, localtz)
    today_epoch = helper.convert_utc_to_epoch(today_utc)


    cloudcover_percentages = seed.poll_darksky(today_epoch)

    labels = []
    data = []
    for epoch, cloudcover_percentage in cloudcover_percentages:
        utc_time = datetime.fromtimestamp(epoch)
        utc_time = utc_time.replace(tzinfo=pytz.utc)
        local_time = utc_time.astimezone(localtz) #Convert to local time, hourly intervals
        labels.append(local_time.strftime('%-I %p')) 
        data.append(int(cloudcover_percentage*100))

    return jsonify({'labels': labels, 'data': data})


@app.route("/cloudcover_averages.json")
def get_cloudcover_data():
    """Get average cloudcover for different slices of time in the past"""

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

    # Single-day graph values require dedicated query since data is displayed in hourly increments, while values returned by API are in Unix time
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
