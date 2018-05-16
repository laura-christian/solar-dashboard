from datetime import datetime, date, timedelta
import pytz

######################################Time-based Helper Functions##############################################

localtz = pytz.timezone('US/Pacific')

def get_today_local():

	today = datetime.today()
	utc_dt = pytz.utc.localize(today)
	today_local = utc_dt.astimezone(localtz)

	return today_local.date()

def generate_date_range(start_date, num_days):
	"""For generating range of dates between start and end dates"""

	return [start_date + timedelta(days=x) for x in range(num_days)]


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

