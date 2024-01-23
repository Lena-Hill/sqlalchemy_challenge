# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import numpy as np 


#################################################
# Database Setup
#################################################

# Create Flask app
app = Flask(__name__)

# Set up SQLite connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)



# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    #print("Server received request for 'Home' page...")
    return ("Welcome to my Climate App! <br/>"
            'available routes are: <br/>'
            '/api/v1.0/precipitation <br/>'
            '/api/v1.0/stations <br/>'
            '/api/v1.0/tobs <br/>'
            '/api/v1.0/yyyy-mm-dd <br/>'
            '/api/v1.0/start/end')

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate one year from the last date in the dataset
    most_recent = session.query(func.max(Measurement.date)).first()
    most_recent_str = most_recent[0]
    most_recent = dt.datetime.strptime(most_recent_str, '%Y-%m-%d')
    one_year_ago = most_recent - dt.timedelta(days=365)
    # Query the precipitation data for last date and covert to a dictionary
    precipitation_score = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation = []
    for date, prcp in precipitation_score:
        prcp_dict = {}
        prcp_dict ['Date'] = date
        prcp_dict ['Precipitation'] = prcp
        precipitation.append(prcp_dict)
    return jsonify(precipitation)

## Two more routes go here ##

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations and return a JSON list
    stations_list = session.query(Station.station).all()
    stations_list = [station[0] for station in stations_list]
    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent = session.query(func.max(Measurement.date)).first()
    most_recent_str = most_recent[0]
    most_recent_date = dt.datetime.strptime(most_recent_str, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    # Query temperature observations for the most-active station for the last year
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281', Measurement.date >= one_year_ago).all()
    tobs_data = [{'date': date, 'temperature': tobs} for date, tobs in temperature_data]
    return jsonify(tobs_data)
    #return ('tobs route: **FIX THIS**')


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def statistics(start = None, end= None):
    '''returns min, max, and avg temperatures for any range of dates in the database'''
    data = [func.min (Measurement.tobs), func.max (Measurement.tobs), func.avg (Measurement.tobs)]
    if not end:
        results = session.query(*data).filter(Measurement.date >= start).all()
        session.close()
        stats = list(np.ravel(results))
        return jsonify(stats)
    results = session.query(*data).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    stats = list(np.ravel(results))
    return jsonify(stats)







if __name__ == "__main__":
    app.run(debug=True)