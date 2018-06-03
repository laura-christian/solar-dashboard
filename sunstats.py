from astral import Astral, Location
from datetime import datetime, date, timedelta, tzinfo
import pytz
import helper


a = Astral()
a.solar_depression = 'civil'

l = Location()
l.name = 'home'
l.region = 'Northern California'
l.latitude = 37.8195
l.longitude = -122.2523
l.timezone = 'US/Pacific'
l.elevation = 125


def sun_single_day(date):
	"""Returns tuple of datetime objects and numerical values for solar patterns on a single day"""

	sun = l.sun(date=date, local=True)
	sunrise = sun['sunrise']
	sunset = sun['sunset']
	day_length = str(sunset-sunrise)
	solar_noon = l.solar_noon(date=date, local=True)
	solar_zenith = l.solar_elevation(solar_noon.replace(tzinfo=None))

	return {'sunrise':sunrise, 'sunset': sunset, 'daylength': day_length, 'solar_noon': solar_noon, 'zenith': solar_zenith}


def zenith_range_dates(list_dates, timeframe):
	"""Returns dictionary of labels and data to populate graph showing angle of solar zenith for range of dates"""

	zeniths = []

	for date in list_dates:
		solar_noon = l.solar_noon(date=date, local=True)
		solar_zenith = l.solar_elevation(solar_noon.replace(tzinfo=None))
		zeniths.append(solar_zenith)

	list_dates = [date.isoformat() for date in list_dates]

	if timeframe == 'last_seven_days' or timeframe == 'this_month' or timeframe == 'last_month':
		format = 'M/D'
	elif timeframe == 'this_year' or timeframe == 'last_year':
		format = 'MMM D'

	return {'labels': list_dates, 'data': zeniths, 'yAxisLabel': 'Solar Zenith', 'format': format}

def solar_arc_single_day(date):

	sun = l.sun(date=date, local=True)
	sunrise = sun['sunrise']
	sunset = sun['sunset']
	starting_hour = sunrise.replace(minute=0, second=0, tzinfo=None)
	ending_hour = sunset.replace(minute=0, second=0, tzinfo=None) + timedelta(hours=1)

	time_diff = ending_hour - starting_hour
	num_hours = int(time_diff.total_seconds()/3600)

	times = [starting_hour + timedelta(hours=x) for x in range(num_hours + 1)]
	time_strings = [time.isoformat() for time in times]

	solar_positions = [l.solar_elevation(time) for time in times]

	return {'labels': time_strings, 'data': solar_positions, 'yAxisLabel': 'Solar Elevation', 'format': 'h A'}















