from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz

######################################Time-based Helper Functions##############################################

localtz = pytz.timezone('US/Pacific')

def get_today_local():

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
    """Converts timezone-aware utc date object to seconds since epoch as integer"""

    epoch = datetime.fromtimestamp(0)
    utc_unaware = utc_dtobj.replace(tzinfo=None)

    return int((utc_unaware - epoch).total_seconds())

def get_yesterday_local():

    today = datetime.today()
    today_local = get_today_local()

    return today_local - timedelta(days=1)

def get_seven_days_ago():

    today = get_today_local()

    return today - timedelta(days=6)

def get_first_day_this_month():

    today = get_today_local()

    return today.replace(day=1)

def get_first_day_last_month():

    today = get_today_local()
    first_this_month = get_first_day_this_month()
    last_last_month = first_this_month - timedelta(days=1) 

    return last_last_month.replace(day=1)

def get_first_this_year():

    today = get_today_local() 

    return today.replace(month=1, day=1)

def get_first_last_year():

    today = get_today_local()
    year_today = today.year
    last_year = today.year - 1

    return today.replace(year=last_year, month=1, day=1)

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
        prior_year_end = end_date - relativedelta(years=1)
        display_increment = 'month'

    elif timeframe == 'last_year':
             
        start_date = get_first_last_year()
        end_date = get_first_this_year()
        prior_year_start = start_date.replace(year=(start_date.year-1))
        prior_year_end = end_date
        display_increment = 'month'

    return (start_date, end_date, prior_year_start, prior_year_end, display_increment)

def generate_date_ranges(timeframe):

    if timeframe == 'last_seven_days':

        start_date = helper.get_seven_days_ago()
        end_date = helper.get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

    elif timeframe == 'this_month':
             
        start_date = helper.get_first_day_this_month()
        end_date = helper.get_today_local() + timedelta(days=1)
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

    elif timeframe == 'last_month':

        start_date = helper.get_first_day_last_month()
        end_date = helper.get_first_day_this_month()
        num_days = (end_date - start_date).days
        date_range = [start_date + timedelta(days=x) for x in range(num_days)]

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

    elif timeframe == 'last_year':
             
        start_date = helper.get_first_last_year()
        end_date = helper.get_first_this_year()
        date_range = []
        for m in range(1, 13):
            date_range.append(start_date.replace(month=m))
            date_range.append(date_range[-1]+timedelta(days=14))
        date_range.append(end_date - timedelta(days=1))

def generate_kWh_chart_data(display_increment, q, prior_y_q):
    """Iterate over SQLAlchemy query results to get labels and data for bar chart and totals for tile stats"""

    formats = {'hour': '%-I %p', 'day': '%-m/%-d', 'month': '%b'}

    primary_labels = []
    prior_y_labels = []
    primary_data = []
    prior_y_data = []
    for dt, kWh in q:
        if display_increment == 'hour':
            dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
        dt = dt.strftime(formats[display_increment]) # Convert to string reflecting local date/time
        primary_labels.append(dt)
        primary_data.append(dt, kWh)
    for dt, kWh in prior_y_q:
        if display_increment == 'hour':
            dt += timedelta(hours=1) #Adding an hour so that kWh sums reflect totals at top of *next* hour
        dt = dt.strftime(formats[display_increment]) # Convert to string reflecting local date/time
        primary_labels.append(dt)
        primary_data.append((dt, kWh))

    # If prior_y_labels remains an empty list, comparative data has not been requested and need not be returned 
    if prior_y_labels == []:
        labels = primary_labels
        primary_data = [x[1] for x in primary_data]
    # If x-axis values are congruent for the two data sets, one set of labels can be used to plot both
    elif primary_labels == prior_y_labels:
        labels = primary_labels
        primary_data = [x[1] for x in primary_data]
        prior_y_data = [x[1] for x in prior_y_data]
    # This third condition is meant to account for the fact that query results for current timeframe and prior year may not always yield the 
    # same number of data points, in which case label sets must be merged
    else:
        labels = sorted(list(set(primary_labels) | set(prior_y_labels)))
        primary_data = [x[1] if x[0] in labels else 0 for x in primary_data]
        prior_y_data = [x[1] if x[0] in labels else 0 for x in prior_y_data]

    # For updating tile stats, which will only ever reflect emission reduction equivalents for current (not prior-year) time period
    total_kWh = sum(primary_data)

    return {'labels': labels, 'primary_data': primary_data, 'prior_y_data': prior_y_data, 'total_kWh': total_kWh}

def generate_cloudcov_chart_data(display_increment, q, prior_y_q):
    """Iterate over SQLAlchemy query results to get labels and data for cloudcover line graph"""
    
    formats = {'hour' '%-I %p': 'day': '%-m/%-d', 'month': '%b'}

    primary_labels = []
    prior_y_labels = []
    primary_data = []
    prior_y_data = []

    if display_increment == 'hour':
    # Labels for single-day intervals must be generated separately since hourly cloudcover observations are fetched from API and recorded
    # in database in Unix time
        for cc_obj in q:
            utc_time = datetime.fromtimestamp(cc_obj.epoch_time)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            local_time = local_time.strftime(formats[display_increment]) # Convert epoch time values to local time in hourly intervals
            primary_labels.append(local_time)
            primary_data.append((local_time, int(cc_obj.cloudcover*100)))
        for cc_obj in prior_y_q:
            utc_time = datetime.fromtimestamp(cc_obj.epoch_time)
            utc_time = utc_time.replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(localtz)
            local_time = local_time.strftime(formats[display_increment]) # Convert epoch time values to local time in hourly intervals
            prior_y_labels.append(local_time)
            prior_y_data.append((local_time, int(cc_obj.cloudcover*100)))

    else:
    # Labels for intervals of more than a day correspond to cloudcover percentages that have already been averaged and grouped by day or month;
    # hence can be generated in fewer steps.
        for local_date, cloudcover_percentage in q:
            local_date = local_date.strftime(formats[display_increment])  # Convert datetime object to string reflecting local date/month
            primary_labels.append(local_date)
            primary_data.append((local_date, int(cloudcover_percentage*100)))
        for local_date, cloudcover_percentage in prior_y_q:
            local_date = local_date.strftime(formats[display_increment])  # Convert datetime object to string reflecting local date/month
            prior_y_labels.append(local_date)
            prior_y_data.append((local_date, int(cloudcover_percentage*100)))

    # If prior_y_labels remains an empty list, comparative data has not been requested and need not be returned 
    if prior_y_labels == []:
        labels = primary_labels
        primary_data = [x[1] for x in primary_data]
    # If x-axis values are congruent for the two data sets, one set of labels can be used to plot both
    elif primary_labels == prior_y_labels:
        labels = primary_labels
        primary_data = [x[1] for x in primary_data]
        prior_y_data = [x[1] for x in prior_y_data]
    # This third condition is meant to account for the fact that query results for current timeframe and prior year may not always yield the 
    # same number of data points, in which case label sets must be merged
    else:
        labels = sorted(list(set(primary_labels) | set(prior_y_labels)))
        primary_data = [x[1] if x[0] in labels else 0 for x in primary_data]
        prior_y_data = [x[1] if x[0] in labels else 0 for x in prior_y_data]


    return {'labels': labels, 'primary_data': primary_data,
                'prior_y_data': prior_y_data}
