from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import timedelta
from matplotlib import style
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(autoload_with=engine)

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
    """List all available routes."""
    
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return a JSON representation of precipitation data for the last 12 months."""
    
    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    session.close()

    return jsonify(precipitation_data)


@app.route('/api/v1.0/stations')
def stations():
    """Return a JSON list of stations."""
    results = session.query(Station.station, Station.name).all()
    station_list = [{"Station": station, "Name": name} for station, name in results]
    session.close()

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    """Return a JSON list of temperature observations for the most active station."""

    most_active_station = 'USC00519281'

    # Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temperature observations
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= prev_year).all()

    # Convert the query results to a list of dictionaries
    tobs_data = [{'date': date, 'tobs': tobs} for date, tobs in results]
    session.close()

    return jsonify(tobs_data)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """Return a JSON list of the minimum, average, and maximum temperatures for a date range."""
    
    # Print received dates for debugging
    print("Received start date:", start)
    print("Received end date:", end)

    try:
        # Parse input dates
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d") if end else None

    except ValueError:
        return jsonify({"error": "Invalid date format. Please use the format YYYY-MM-DD"}), 400

    # Perform a query to calculate TMIN, TAVG, and TMAX for the specified date range
    if end_date:
        query = session.query(  
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date.between(start_date, end_date))
    else:
        query = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_date)

    # Print the generated SQL query for debugging
    print("SQL Query:", query)

    # Execute the query
    results = query.all()
    session.close()

    # Check if there are no results
    if not results:
        return jsonify({"error": "No data available for the specified date range"}), 404

    # Convert the query results to a list of dictionaries
    temperature_data = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in results]

    return jsonify(temperature_data)



# Run the app
if __name__ == "__main__":
    app.run(debug=True)
