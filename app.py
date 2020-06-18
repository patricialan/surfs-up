import datetime as dt
import numpy as np
import pandas as pd

# import dependencies for SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
 
 # import dependencies for Flask
from flask import Flask, jsonify

# setup database engine for Flask application
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect the database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# create reference variable for each class
Measurement = Base.classes.measurement
Station = Base.classes.station

# create session link from Python to the database
session = Session(engine)

# create a new flask app instance
app = Flask(__name__)

# create flask routes
@app.route('/')
def welcome():
   return(
   f'Welcome to the Climate Analysis API!<br/>'
   f'<br/>'
   f'Available Routes:<br/>'
   f'/api/v1.0/precipitation<br/>'
   f'/api/v1.0/stations<br/>'
   f'/api/v1.0/tobs<br/>'
   f'/api/v1.0/temp/start/end<br/>'
   )

@app.route("/api/v1.0/precipitation")
def precipitation():
   session = Session(engine)
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
	   filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
   session = Session(engine)
   results = session.query(Station.station).all()
   stations = list(np.ravel(results))
   return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
   session = Session(engine)
   prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
   
   results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
   
   temps = list(np.ravel(results))

   return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
# to specify start & end dates: /api/v1.0/temp/2017-06-01/2017-06-30

def stats(start=None, end=None):
   session = Session(engine)
   sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

   if not end:
      results = session.query(*sel).\
         filter(Measurement.date <= start).all()
      temps = list(np.ravel(results))
      jsonify(temps=temps)
         
   results = session.query(*sel).\
      filter(Measurement.date >= start).\
      filter(Measurement.date <= end).all()
   temps = list(np.ravel(results))
   return jsonify(temps=temps)