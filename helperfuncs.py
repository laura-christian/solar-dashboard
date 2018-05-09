from datetime import datetime, date, timedelta
import pytz

today = date.today()
localtz = 'US/Pacifi'c

def generate_date_range(start_date, num_days):
	"""For generating range of dates between start and end dates"""

	return [start_date + timedelta(days=x) for x in range(num_days)]


def convert_local_time_to_utc(dtobj, localtz):
	"""Converts 'naive' or non-timezone-aware date object, localizes and then returns as timezone-aware utc datetime object"""

	naive = dtobj
	local_dt = localtz.localize(naive)
	utc_dt = local_dt.astimezone(pytz.utc)
	
	return local_dt.astimezone(pytz.utc) 

def convert_local_time_to_epoch(utc_dtobj):
	"""Converts timezone-aware utc date object to seconds since epoch as integer"""

	naive_utc = utc_dt.replace(tzinfo=None)

	return int((utc_unaware - epoch).total_seconds())

def get_yesterday():

	return today - timedelta(days=1)

def get_last_seven_days():

	seven_days_ago = today - timedelta(days=6)

	return [seven_days_ago + timedelta(days=x) for x in range(7)]

def get_days_this_month():

	first_of_month = today.replace(day=1)

	return [first_of_month + timedelta(days=x) for x in range((today-first_of_month).days+1)]

def get_days_last_month():

	first_this_month = today.replace(day=1)
	last_last_month = first_this_month - timedelta(days=1)
	first_last_month = last_last_month.replace(day=1)

	return [first_last_month + timedelta(days=x) for x in range((last_last_month-first_last_month).days+1)]

def get_days_this_year():

	first_of_year = today.replace(month=1, day=1)

	return [first_of_year + timedelta(days=x) for x in range((today-first_of_year).days+1)]

def get_days_last_year():

	year_today = today.year
	last_year = today.year - 1
	first_of_last_year = today.replace(year=last_year, month=1, day=1)
	last_of_last_year = today.replace(year=last_year, month=12, day=31)

	return [first_of_last_year + timedelta(days=x) for x in range((last_of_last_year-first_of_last_year).days+1)]


