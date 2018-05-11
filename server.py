"""Movie Ratings."""

from jinja2 import StrictUndefined
from sqlalchemy import func
from flask import Flask, render_template, request, flash, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Geolocation, SolarOutput, Cloudcover
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


@app.before_request
def add_tests():

    g.jasmine_tests = JS_TESTING_MODE


@app.route('/')
def index():
    """Render homepage."""

    return render_template("index.html")


@app.route("/solaroutput_single_day.json")
def get_bar_graph_data_single_day():
    """Aggregate solar output data for a single day"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'today':

        start_date = helper.get_today_local()
        end_date = today + timedelta(days=1)


    elif timeframe == 'yesterday':
             
        start_date = helper.get_yesterday_local()
        end_date = helper.get_today_local()

    # Create subquery object to capture all kWh values b/w day selected and following day (midnight)
    subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
        filter(SolarOutput.dt_local>=start_date, SolarOutput.dt_local<end_date).subquery()
    # In turn perform group-by query on subquery to sum values for each hour, and filter out any hours
        #in which no solar energy was produced
    q = db.session.query(func.date_trunc('hour', subq.c.dt_local),func.sum(subq.c.kWh)).\
        group_by(func.date_trunc('hour', subq.c.dt_local)).having(func.sum(subq.c.kWh)>0).\
        order_by(func.date_trunc('hour',subq.c.dt_local)).all()

    # Iterate over query results to get labels and data for bar chart and totals for emissions equivalent tiles
    labels = []
    data = []
    for dt, kWh in q:
        dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
        labels.append(dt.strftime('%-I %p')) # Convert to string reflecting local time
        data.append(kWh)
    total_kWh = sum(data)


    return jsonify({'labels': labels, 'data': data, 'total_kWh': total_kWh})

@app.route("/solaroutput_range_days.json")
def get_bar_graph_data_range_days():
    """Aggregate solar output data for a single day"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'last_seven_days':

        start_date = helper.get_seven_days_ago()
        end_date = helper.get_today_local() + timedelta(days=1)

    elif timeframe == 'this_month':
             
        start_date = helper.get_first_day_this_month()
        end_date = helper.get_today_local() + timedelta(days=1)

    elif timeframe == 'last_month':

        start_date = helper.get_first_day_last_month()
        end_date = helper.get_first_day_this_month()

    # Create subquery object to capture all kWh values for range of days selected
    subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
        filter(SolarOutput.dt_local>=start_date, SolarOutput.dt_local<end_date).subquery()
    # In turn perform group-by query on subquery to sum values for each day
    q = db.session.query(func.date_trunc('day', subq.c.dt_local),func.sum(subq.c.kWh)).\
        group_by(func.date_trunc('day', subq.c.dt_local)).order_by(func.date_trunc('day',subq.c.dt_local)).all()

    # Iterate over query results to get labels and data for bar chart and totals for emissions equivalent tiles
    labels = []
    data = []
    for dt, kWh in q:
        labels.append(dt.strftime('%-m/%-d')) # Convert to string reflecting local date
        data.append(kWh)
    total_kWh = sum(data)


    return jsonify({'labels': labels, 'data': data, 'total_kWh': total_kWh})

@app.route("/solaroutput_by_month.json")
def get_bar_graph_data_by_month():
    """Aggregate solar output data for a single day"""

    timeframe=request.args.get('timeframe')

    if timeframe == 'this_year':

        start_date = helper.get_first_this_year()
        end_date = helper.get_today_local() + timedelta(days=1)

    elif timeframe == 'last_year':
             
        start_date = helper.get_first_last_year()
        end_date = helper.get_first_this_year()

    # Create subquery object to capture all kWh values for range of days selected
    subq = db.session.query(SolarOutput.dt_local, SolarOutput.kWh).\
        filter(SolarOutput.dt_local>=start_date, SolarOutput.dt_local<end_date).subquery()
    # In turn perform group-by query on subquery to sum values for each month
    q = db.session.query(func.date_trunc('month', subq.c.dt_local),func.sum(subq.c.kWh)).\
        group_by(func.date_trunc('month', subq.c.dt_local)).order_by(func.date_trunc('month',subq.c.dt_local)).all()

    # Iterate over query results to get labels and data for bar chart and totals for emissions equivalent tiles
    labels = []
    data = []
    for dt, kWh in q:
        labels.append(dt.strftime('%b')) #Convert to abbreviation for month
        data.append(kWh)
    total_kWh = sum(data)


    return jsonify({'labels': labels, 'data': data, 'total_kWh': total_kWh})



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
