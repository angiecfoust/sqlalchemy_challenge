# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys
print

# Save references to each table
Meas = Base.classes.measurement
Stat = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Welcome to the'Hawaii' page!<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/station<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>")

# precipitation- returns json with the date as the key and the value as a precipitation
# only returns data for the last year in the database
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    #create session link
    session = Session(engine)

    # query precipitation data- starting 8/23/2016

    sel = [Meas.date, Meas.prcp]

    precip = session.query(*sel).\
        filter(func.strftime(Meas.date) >= "2016-08-23").\
        filter((Meas.prcp) != None).\
        order_by(Meas.date).all()

    session.close()

    #create dictionary from the data & convert to json
    precip_data = []
    for date, precipitation in precip:
        date_dict = {}
        date_dict["date"] = date
        date_dict["precipitation"] = precipitation
        precip_data.append(date_dict)

    return jsonify(precip_data)


# station- returns jsonified data of all the stations in the database
@app.route("/api/v1.0/station")
def station():
    print("Server received request for 'Station' page...")

    #create session link
    session = Session(engine)

    #query station data
    sel = [Stat.id, Stat.station, Stat.name, Stat.latitude, Stat.longitude, Stat.elevation]
    
    stations = session.query(*sel).all()

    session.close()

    #create dictionary from the data & convert to json
    station_data = []
    for id, station, name, latitudue, longitude, elevation in stations:
        stat_dict = {}
        stat_dict["id"] = id
        stat_dict["station"] = station
        stat_dict["name"] = name
        stat_dict["latitude"] = latitudue
        stat_dict["longitude"] = longitude
        stat_dict["elevation"] = elevation
        station_data.append(stat_dict)

    return jsonify(station_data)    


# tobs- returns jsonified data for the most active station USC00519281
# only returns the jsonified data for the last year of data (start: 8/23/2016)
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'TOBS' page...")

    #create session link
    session = Session(engine)

    #query temp data for station & date
    sel = [Meas.date, Meas.prcp, Meas.tobs]

    most_active = session.query(*sel).\
    filter(func.strftime(Meas.date) >= "2016-08-23").\
    filter(Meas.station == "USC00519281").all()

    session.close()

    #create dictionary from the data & convert to json
    tobs_data = []

    for date, prcp, tobs in most_active:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["prcp"] = prcp
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
    
    return jsonify(tobs_data)
    

# start- accepts the start date as a parameter from the URL
# returns min, max, avg temperatures calculated from the given start date to the end of the data set
@app.route("/api/v1.0/<start>")
def start_date(start):
    print("Server received request for 'Start' page...")

    #create session link
    session = Session(engine)

    #query temp statistics from given start to end of data
    sel = [func.min(Meas.tobs), func.max(Meas.tobs), func.avg(Meas.tobs)]

    stat_sum = session.query(*sel).\
        filter(Meas.date >= start).all()
    
    session.close()

    #create dictionary from data & convert to json
    results = []

    for min, max, avg in stat_sum:
        results_dict ={}
        results_dict["min"] = min
        results_dict["max"] = max
        results_dict["avg"] = avg

    return jsonify(results)


# start/end- accepts the start and end dates as parameters from the URL
# returns min, max, avg temperatures calculated from the given start date to the given end date

@app.route("/api/v1.0/<start>/<end>")
def start_end(start):
    print("Server received request for 'End' page...")

    #create session link
    session = Session(engine)

    #query temp statistics from given start to end of data
    sel = [func.min(Meas.tobs), func.max(Meas.tobs), func.avg(Meas.tobs)]

    stat_sum = session.query(*sel).\
        filter(Meas.date >= start).filter(Meas.date <= start).all()
    
    session.close()

    #create dictionary from data & convert to json
    results = []

    for min, max, avg in stat_sum:
        results_dict ={}
        results_dict["min"] = min
        results_dict["max"] = max
        results_dict["avg"] = avg

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug = True)
