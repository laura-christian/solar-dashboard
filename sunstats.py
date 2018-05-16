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

l.sun()


today = helper.get_today_local()
yesterday = helper.get_yesterday_local()

def sun_single_day(date):
	"""Returns tuple of datetime objects and numerical values for solar patterns on a single day"""

	sun = l.sun(date=date, local=True)
	sunrise = sun['sunrise']
	sunset = sun['sunset']
	day_length = l.sunset()-l.sunrise()
	solar_noon = l.solar_noon()
	solar_zenith = l.solar_elevation(l.solar_noon().replace(tzinfo=None))

	return (sunrise, sunset, day_length, solar_noon, solar_zenith)


def sun_range_dates(list_dates):
	"""Returns relevant solar information for range of dates as a list of tuples"""

	sunstats = []

	for date in list_dates:
		sun = l.sun(date=date, local=True)
		sunrise = sun['sunrise']
		sunset = sun['sunset']
		day_length = l.sunset()-l.sunrise()
		solar_noon = l.solar_noon()
		solar_zenith = l.solar_elevation(l.solar_noon().replace(tzinfo=None))
		sunstats.append((date, sunrise, sunset, day_length, solar_noon, solar_zenith))

	return sunstats










