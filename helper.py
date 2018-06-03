from model import Geolocation, SolarOutput, Cloudcover, connect_to_db, db
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import os
import requests
import seed

###################################### Helper Functions for Handling Time Operations and Populating Graphs ###################################

localtz = pytz.timezone('US/Pacific')
DARKSKY_TOKEN=os.environ.get('DARKSKY_TOKEN')

def get_today_local():
    """Returns today's date in Pacific Daylight Time; for doc-testing purposes, change date below.
    >>> get_today_local()
    datetime.date(2018, 5, 31)"""

    today = datetime.today()
    utc_dt = pytz.utc.localize(today)
    today_local = utc_dt.astimezone(localtz)

    return today_local.date()

def convert_naive_local_time_to_utc(dtobj, localtz):
    """Converts 'naive' or non-timezone-aware date object, localizes and then returns as timezone-aware utc datetime object"""

    local_dt = localtz.localize(dtobj)
    utc_dt = local_dt.astimezone(pytz.utc)
    
    return local_dt.astimezone(pytz.utc) 

def convert_utc_to_epoch(utc_dtobj):
    """Converts timezone-aware utc date object to seconds since epoch as integer
    >>> convert_utc_to_epoch(datetime(2018, 6, 1, 2, 35, 35, 785354, tzinfo=pytz.utc))
    1527820535
    """

    epoch = datetime.fromtimestamp(0)
    utc_unaware = utc_dtobj.replace(tzinfo=None)

    return int((utc_unaware - epoch).total_seconds())

def get_yesterday_local():
    """Returns yesterday's date in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_yesterday_local()
    datetime.date(2018, 5, 30)"""

    today = datetime.today()
    today_local = get_today_local()

    return today_local - timedelta(days=1)

def get_seven_days_ago():
    """Returns yesterday's date in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_seven_days_ago()
    datetime.date(2018, 5, 25)"""

    today = get_today_local()

    return today - timedelta(days=6)

def get_first_day_this_month():
    """Returns first day of current month in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_first_day_this_month()
    datetime.date(2018, 5, 1)"""

    today = get_today_local()

    return today.replace(day=1)

def get_first_day_last_month():
    """Returns first day of last month in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_first_day_last_month()
    datetime.date(2018, 5, 1)"""

    today = get_today_local()
    first_this_month = get_first_day_this_month()
    last_last_month = first_this_month - timedelta(days=1) 

    return last_last_month.replace(day=1)

def get_first_this_year():
    """Returns first day of the current year in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_first_this_year()
    datetime.date(2018, 1, 1)"""

    today = get_today_local() 

    return today.replace(month=1, day=1)

def get_first_last_year():
    """Returns first day of last year in Pacific Daylight Time; for doc-testing purposes, change date below
    >>> get_first_last_year()
    datetime.date(2017, 1, 1)"""

    today = get_today_local()
    year_today = today.year
    last_year = today.year - 1

    return today.replace(year=last_year, month=1, day=1)

def generate_date_range(start_date, num_days):
    """For generating range of dates to be passed into other functions
    >>> generate_date_range(datetime(2018, 1, 1), 5)
    [datetime.datetime(2018, 1, 1, 0, 0), datetime.datetime(2018, 1, 2, 0, 0), datetime.datetime(2018, 1, 3, 0, 0), 
    datetime.datetime(2018, 1, 4, 0, 0), datetime.datetime(2018, 1, 5, 0, 0)]
    """
    return [start_date + timedelta(days=x) for x in range(num_days)]

def get_intervals(timeframe):

    if timeframe == 'today':

        start_date = get_today_local()
        end_date = start_date + timedelta(days=1)
        prior_year_start = start_date - relativedelta(years=1)
        prior_year_end = prior_year_start + timedelta(days=1)
        display_increment = 'hour'

    elif timeframe == 'yesterday':
             
        start_date = get_yesterday_local()
        end_date = get_today_local()
        prior_year_start = start_date - relativedelta(years=1)
        prior_year_end = prior_year_start + timedelta(days=1)
        display_increment = 'hour'

    elif timeframe == 'last_seven_days':

        start_date = get_seven_days_ago()
        end_date = get_today_local() + timedelta(days=1)
        prior_year_start = start_date - relativedelta(years=1)
        prior_year_end = prior_year_start + timedelta(days=7)
        display_increment = 'day'

    elif timeframe == 'this_month':
             
        start_date = get_first_day_this_month()
        end_date = get_today_local() + timedelta(days=1)
        prior_year_start = start_date.replace(year=(start_date.year-1))
        prior_year_end = prior_year_start.replace(month=(prior_year_start.month+1))
        display_increment = 'day'

    elif timeframe == 'last_month':

        start_date = get_first_day_last_month()
        end_date = get_first_day_this_month()
        prior_year_start = start_date.replace(year=(start_date.year-1))
        prior_year_end = prior_year_start.replace(month=(prior_year_start.month+1))
        display_increment = 'day'

    elif timeframe == 'this_year':

        start_date = get_first_this_year()
        end_date = get_today_local() + timedelta(days=1)
        prior_year_start = start_date.replace(year=(start_date.year-1))
        prior_year_end = start_date
        display_increment = 'month'

    elif timeframe == 'last_year':
             
        start_date = get_first_last_year()
        end_date = get_first_this_year()
        prior_year_start = start_date.replace(year=(start_date.year-1))
        prior_year_end = start_date
        display_increment = 'month'

    return (start_date, end_date, prior_year_start, prior_year_end, display_increment)

def generate_x_axis_points(timeframe):

    if timeframe == 'last_seven_days':

        start_date = get_seven_days_ago()
        end_date = get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

    elif timeframe == 'this_month':
             
        start_date = get_first_day_this_month()
        end_date = get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

    elif timeframe == 'last_month':

        start_date = get_first_day_last_month()
        end_date = get_first_day_this_month()
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

    elif timeframe == 'this_year':

        start_date = get_first_this_year()
        today = get_today_local()
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

    elif timeframe == 'last_year':
             
        start_date = get_first_last_year()
        end_date = get_first_this_year()
        date_range = []
        for m in range(1, 13):
            date_range.append(start_date.replace(month=m))
            date_range.append(date_range[-1]+timedelta(days=14))
        date_range.append(end_date - timedelta(days=1))

    return date_range

def generate_kWh_chart_data(display_increment, q, prior_y_q):
    """Iterate over SQLAlchemy query results to get labels and data for bar chart and totals for tile stats"""

    formats = {'hour': '%H-%-I %p', 'day': '%m/%d', 'month': '%m-%b'}

    primary_labels = []
    prior_y_labels = []
    primary_data = {}
    prior_y_data = {}
    for dt, kWh in q:
        if display_increment == 'hour':
            dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
        dt = dt.strftime(formats[display_increment]) # Convert to string reflecting local date/time
        primary_labels.append(dt)
        primary_data[dt] = kWh
    for dt, kWh in prior_y_q:
        if display_increment == 'hour':
            dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
        dt = dt.strftime(formats[display_increment]) # Convert to string reflecting local date/time
        prior_y_labels.append(dt)
        prior_y_data[dt] = kWh

    # If prior_y_labels remains an empty list, comparative data has not been requested and need not be returned 
    if prior_y_labels == []:
        labels = primary_labels
        primary_data = [primary_data[label] for label in primary_labels]
    # If x-axis values are congruent for the two data sets, one set of labels can be used to plot both
    elif primary_labels == prior_y_labels:
        labels = primary_labels
        primary_data = [primary_data[label] for label in labels]
        prior_y_data = [prior_y_data[label] for label in labels]
    # This third condition is meant to account for the fact that query results for current timeframe and prior year may not always yield the 
    # same number of data points, in which case label sets must be merged
    else:
        labels = sorted(list(set(primary_labels) | set(prior_y_labels)))
        primary_data = [primary_data[label] if label in primary_data else 0 for label in labels]
        prior_y_data = [prior_y_data[label] if label in prior_y_data else 0 for label in labels]

    # Datetime labels had to start with zero-padded numeric figures to be properly sortable; here they get left-stripped for display purposes
    if display_increment == 'month':
        labels = [label.split('-')[1] for label in labels]
    elif display_increment == 'day':
        labels = [label[1:] if label[0] == '0' else label for label in labels]
    elif display_increment == 'hour':
        labels = [label[3:] for label in labels]

    # For updating tile stats, which will only ever reflect emission reduction equivalents for current (not prior-year) timeframe
    total_kWh = sum(primary_data)

    return {'labels': labels, 'primary_data': primary_data, 'prior_y_data': prior_y_data, 'total_kWh': total_kWh}


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

def generate_cloudcov_chart_data(display_increment, q, prior_y_q):
    """Iterate over SQLAlchemy query results to get labels and data for cloudcover line graph"""
    
    formats = {'hour': '%H-%-I %p', 'day': '%m/%d', 'month': '%m-%b'}

    primary_labels = []
    prior_y_labels = []
    primary_data = {}
    prior_y_data = {}

    if display_increment == 'hour':
    # Labels for single-day intervals must be generated separately since hourly cloudcover observations are fetched from API and recorded
    # in database in Unix time
        for cc_obj in q:
            utc_time = datetime.fromtimestamp(cc_obj.epoch_time)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            local_time = local_time.strftime(formats[display_increment]) # Convert epoch time values to local time (hourly intervals)
            primary_labels.append(local_time)
            primary_data[local_time] = int(cc_obj.cloudcover*100)
        for cc_obj in prior_y_q:
            utc_time = datetime.fromtimestamp(cc_obj.epoch_time)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            local_time = local_time.strftime(formats[display_increment]) # Convert epoch time values to local time (hourly intervals)
            prior_y_labels.append(local_time)
            prior_y_data[local_time] = int(cc_obj.cloudcover*100)

    else:
    # Labels for intervals of more than a day correspond to cloudcover percentages that have already been averaged and grouped by day or month;
    # hence can be generated in fewer steps.
        for local_date, cloudcover_percentage in q:
            local_date = local_date.strftime(formats[display_increment])  # Convert datetime object to string reflecting local date/month
            primary_labels.append(local_date)
            primary_data[local_date] = int(cloudcover_percentage*100)
        for local_date, cloudcover_percentage in prior_y_q:
            local_date = local_date.strftime(formats[display_increment])  # Convert datetime object to string reflecting local date/month
            prior_y_labels.append(local_date)
            prior_y_data[local_date] = int(cloudcover_percentage*100)

    # If prior_y_labels remains an empty list, comparative data has not been requested and need not be returned 
    if prior_y_labels == []:
        labels = primary_labels
        primary_data = [primary_data[label] for label in labels]
    # If x-axis values are congruent for the two data sets, one set of labels can be used to plot both
    elif primary_labels == prior_y_labels:
        labels = primary_labels
        primary_data = [primary_data[label] for label in labels]
        prior_y_data = [prior_y_data[label] for label in labels]
    # This third condition is meant to account for the fact that query results for current timeframe and prior year may not always yield the 
    # same number of data points, in which case label sets must be merged
    else:
        labels = sorted(list(set(primary_labels) | set(prior_y_labels)))
        primary_data = [primary_data[label] if label in primary_data else 'null' for label in labels]
        prior_y_data = [prior_y_data[label] if label in prior_y_data else 'null' for label in labels]

    # Datetime labels had to start with zero-padded numeric figures to be properly sortable; here they get left-stripped for display purposes
    if display_increment == 'month':
        labels = [label.split('-')[1] for label in labels]
    elif display_increment == 'day':
        labels = [label[1:] if label[0] == '0' else label for label in labels]
    elif display_increment == 'hour':
        labels = [label[3:] for label in labels]

    return {'labels': labels, 'primary_data': primary_data, 'prior_y_data': prior_y_data}


def update_cloudcover_data():

    # Get date of last record
    last_record = db.session.query(Cloudcover).order_by(Cloudcover.cloudiness_id.desc()).first()
    date_of_last_record = last_record.local_date

    # Delete records from last day of recorded cloudcover percentages for greater accuracy (some will
    # have been forecast rather than observed values)
    Cloudcover.query.filter(Cloudcover.local_date == date_of_last_record).delete()

    # Convert date of last record to epoch time in order to poll Darksky API for interim cloudcover
    # percentages
    date_utc = convert_naive_local_time_to_utc(date_of_last_record, localtz)
    date_epoch = convert_utc_to_epoch(date_utc)

    today = get_today_local()
    today = datetime(today.year, today.month, today.day, 0, 0, 0) #Get today midnight (local) as naive date-time object

    # Get number of days between last update and today
    date_diff = today - date_of_last_record
    num_days = date_diff.days

    # Generate date range
    date_range = generate_date_range(date_of_last_record, num_days+1) 

    # Call seeding function to load new data
    seed.load_cloudcover_data(date_range)


# if __name__ == "__main__":
    # import doctest

    # print()
    # result = doctest.testmod()
    # if not result.failed:
    #     print("ALL TESTS PASSED.")
    # print()