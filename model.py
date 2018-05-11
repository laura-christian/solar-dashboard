"""Models and database functions for Ratings project."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, date, time, timedelta, tzinfo
import pytz
import helper

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class Geolocation(db.Model):
    """Holds key geolocational info for solar array site (one record in this case)."""

    __tablename__ = "geolocations"

    geoloc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    street_addr = db.Column(db.String(128), nullable=False)
    city = db.Column(db.String(128), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    elevation = db.Column(db.Integer, nullable=True)
    timezone = db.Column(db.String(64), nullable=False) #Should correspond to pytz tz designation

    def __repr__(self):
        """Provides helpful representation of object when printed."""

        return "<Location street address={} city= {} state={} latitude={} longitude={}>".format(self.street_addr, 
                    self.city, self.state, self.latitude, self.longitude)


class SolarOutput(db.Model):
    """Movie on ratings website."""

    __tablename__ = "solaroutput"

    output_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    dt_local = db.Column(db.DateTime, nullable=False)
    kWh = db.Column(db.Float, nullable=False, default=0)

    def __repr__(self):
        """Provides helpful representation of object when printed."""

        return "<SolarOutput local date/time={} kWh={}>".format(self.dt_local, self.kWh)

class Cloudcover(db.Model):
    """Historical weather data regarding cloudcover, recorded hourly (for daylight hours only), expressed as percentage."""

    __tablename__ = "cloudcover"

    cloudiness_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    local_date = db.Column(db.DateTime, nullable=False) #This will be a naive date
    epoch_time = db.Column(db.Integer, nullable=False)
    cloudcover = db.Column(db.Float, nullable=False) # Expressed as percentage

    def __repr__(self):
        """Provides helpful representation of object when printed."""

        return "<Cloudcover epoch time={} percent cloudcover={}>".format(self.epoch_time, self.cloudcover)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///solar'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
