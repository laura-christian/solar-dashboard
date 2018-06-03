import unittest
from selenium import webdriver
import server
from os.path import abspath, dirname, join, pardir


path_test = dirname(abspath(__file__))
path_parent = abspath(join(path_test, pardir))
path_app = join(path_parent, 'source')
if path_app not in sys.path:
    sys.path.append(path_app)

class TestHomepageInitState(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome(join(path_test, 'chromedriver', 'chromedriver.exe'))
        self.browser.get('http://localhost:5000/')

        def _mock_get_kWh_data():
            return {'labels': ["7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM",
                        "5 PM", "6 PM", "7 PM", "8 PM"], 'primary_data': [0.05, 0.17, 0.3, 0.5, 1.45, 1.6, 2.29, 
                        2.08, 2.28, 1.82, 1.34, 0.48, 0.11, 0.07], 'prior_y_data': {}, 'total_kWh': 14.540000000000001}

        server.get_kWh_data = _mock_get_kWh_data

        def _mock_daylight_details():
            return {'daylength': "14:35:57", 'elevation': -21.42454835219715, 'solar_noon': "1:06PM", 'sunrise': "5:48AM",
                    'sunset': "8:24PM", 'zenith': 74.42085908673457}

        server.get_daylight_details = _mock_daylight_details

        def _mock_cloudcover_today():
            return {'labels': ["5 AM", "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM", "1 PM", "2 PM", 
                        "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM"], 'primary_data': [51, 49, 38, 49, 46,
                        54, 56, 56, 46, 35, 24, 22, 27, 19, 16, 11, 10], 'prior_y_data': {}}

        server.get_cloudcover_today = _mock_cloudcover_today

        def _mock_weather_data():
            return {'current': {u'cloudCover': 0, u'icon': u'clear-day', u'temperature': 73.12,}, 'forecast': [{u'cloudCover': 0.12,
                        u'icon': u'partly-cloudy-day', u'temperatureHigh': 76.83}, {u'cloudCover': 0.27, u'icon': u'partly-cloudy-day',
                        u'temperatureHigh': 70.4}, {u'cloudCover': 0.39, u'icon': u'partly-cloudy-day', u'temperatureHigh': 69.1}, {u'cloudCover': 0.26,
                        u'icon': u'partly-cloudy-day', u'temperatureHigh': 71.77}, {'cloudCover': 0.7, u'icon': u'partly-cloudy-day', u'temperatureHigh': 63.33},
                        {u'cloudCover': 0.51, u'icon': u'partly-cloudy-day', u'temperatureHigh': 67.41}, {u'cloudCover': 0, u'icon': u'clear-day',
                        u'temperatureHigh': 72.13}]}

        server.get_weather_forecast = _mock_weather_data

    def tearDown(self):
        self.browser.quit()

    def test_title(self):
        self.assertEqual(self.browser.title, 'My Sunstats')

    def test_today_button(self):
        today_btn = self.browser.find_element_by_id('today-button')
        self.assertIn("active", today_btn.get_attribute("class"))

    def test_daylight_deets(self):
        hours_daylight = self.browser.find_element_by_id('daylight')
        self.assertEqual(hours_daylight.text, "14:35:57")

    def test_tile_stats(self):
        miles_driven = self.browser.find_element_by_id('miles-driven')
        self.assertEqual(miles_driven.text, '26')

    def test_weather_widget(self):
        weather_today = self.browser.find_element_by_id('main-day-weather')
        self.assertEqual(weather_today.text, 'Clear Day')



if __name__ == "__main__":
    unittest.main()


