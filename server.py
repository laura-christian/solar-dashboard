from sqlalchemy import func
from flask import Flask, render_template, request, flash, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from os.path import abspath, dirname, join, pardir
import sys
import os
from model import connect_to_db, db, Geolocation, SolarOutput, Cloudcover
import seed
import helper
from astral import Astral, Location
import sunstats
import requests
from datetime import datetime, date, time, timedelta, tzinfo
from dateutil.relativedelta import relativedelta
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
def get_kWh_data():
    """Aggregate solar output data for different slices of time"""

    timeframe=request.args.get('timeframe')
    comparative=request.args.get('comparative', False)

    interval = helper.get_intervals(timeframe)
    start_date = interval[0]
    end_date = interval[1]
    prior_year_start = interval[2]
    prior_year_end = interval[3]
    display_increment = interval[4]

    # Create subquery object to capture all kWh values b/w start and end dates
    subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
        filter(SolarOutput.dt_local>=start_date, SolarOutput.dt_local<end_date).subquery()
    # In turn perform group-by query on subquery to sum values for display_increment of time in which totals displayed
    q = db.session.query(func.date_trunc(display_increment, subq.c.dt_local),func.sum(subq.c.kWh)).\
        group_by(func.date_trunc(display_increment, subq.c.dt_local)).having(func.sum(subq.c.kWh)>0).\
        order_by(func.date_trunc(display_increment,subq.c.dt_local)).all()

    if comparative:
        # If comparative data called, do same queries for equivalent interval prior year
        prior_y_subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
            filter(SolarOutput.dt_local>=prior_year_start, SolarOutput.dt_local<prior_year_end).subquery()

        prior_y_q = db.session.query(func.date_trunc(display_increment, subq.c.dt_local),func.sum(subq.c.kWh)).\
            group_by(func.date_trunc(display_increment, prior_y_subq.c.dt_local)).having(func.sum(prior_y_subq.c.kWh)>0).\
            order_by(func.date_trunc(display_increment,prior_y_subq.c.dt_local)).all()


    chart_data = helper.generate_kWh_chart_data(display_increment, q, prior_y_q=[])

    return jsonify(chart_data)

@app.route("/daylight_deets.json")
def get_daylight_details():
    """Get details of solar path/daylight hours at site for today (local)"""
    
    sunrise = l.sunrise().strftime('%-I:%M%p')
    sunset = l.sunset().strftime('%-I:%M%p')
    day_length = str(l.sunset()-l.sunrise())
    solar_noon = l.solar_noon().strftime('%-I:%M%p')
    solar_zenith = l.solar_elevation(l.solar_noon().replace(tzinfo=None))
    solar_elevation = l.solar_elevation()

    daylight_data = {'sunrise': sunrise, 'sunset': sunset, 'daylength': day_length, 'solar_noon': solar_noon, 
                        'zenith': solar_zenith, 'elevation': solar_elevation}

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

    else:
        date_range = helper.generate_date_range(timeframe)
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
    comparative=request.args.get('comparative', False)

    interval = helper.get_intervals(timeframe)
    start_date = interval[0]
    end_date = interval[1]
    prior_year_start = interval[2]
    prior_year_end = interval[3]
    display_increment = interval[4]

    if timeframe == 'yesterday':
        # Single-day intervals must be handled via dedicated queries since hourly cloudcover data recorded in Unix time:
        q = Cloudcover.query.filter(Cloudcover.local_date>=start_date, Cloudcover.local_date<end_date)
        if comparative:
            prior_y_q = Cloudcover.query.filter(Cloudcover.local_date>=prior_year_start, Cloudcover.local_date<prior_year_end)

    else:
        # Create subquery object to capture all cloudcover values b/w start and end dates
        subq = db.session.query(Cloudcover.local_date, Cloudcover.cloudcover).\
            filter(Cloudcover.local_date>=start_date, Cloudcover.local_date<end_date).subquery()
        # In turn, perform group-by query on subquery to sum values for display_increment of time in which totals displayed
        q = db.session.query(func.date_trunc(display_increment, subq.c.local_date),func.avg(subq.c.cloudcover)).\
            group_by(func.date_trunc(display_increment, subq.c.local_date)).order_by(func.date_trunc(display_increment,subq.c.local_date)).all()
        if comparative:
            # Do same for equivalent interval prior year
            prior_y_subq = db.session.query(Cloudcover.local_date, Cloudcover.cloudcover).\
                filter(Cloudcover.local_date>=start_date, Cloudcover.local_date<end_date).subquery()
            # In turn, perform group-by query on subquery to sum values for display_increment of time in which totals displayed
            prior_y_q = db.session.query(func.date_trunc(display_increment, prior_y_subq.c.local_date),func.avg(prior_y_subq.c.cloudcover)).\
                group_by(func.date_trunc(display_increment, prior_y_subq.c.local_date)).order_by(func.date_trunc(display_increment,prior_y_subq.c.local_date)).all()

    chart_data = helper.generate_cloudcov_chart_data(display_increment, q, prior_y_q=[])

    return jsonify(chart_data)


if __name__ == "__main__":

    # Necessary to invoke DebugToolbarExtension; note: no debug for demo
    app.debug = True
    DebugToolbarExtension(app)

    connect_to_db(app)

    app.run(host="0.0.0.0")
