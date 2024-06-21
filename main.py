from datetime import datetime

from flask import Flask, request, render_template, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets
import os

from sqlalchemy import func

if "VERCEL" in os.environ:
    app = Flask(__name__, instance_path="/tmp")
else:
    app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db = SQLAlchemy(app)


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)


class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))


class Forecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placeid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    condition = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    rain = db.Column(db.Float)
    humidity = db.Column(db.Integer)
    wind = db.Column(db.Integer)
    wind_direction = db.Column(db.String(5))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_pw = db.Column(db.String(64))
    apikey = db.Column(db.String(40))


from db_utils import reset_db


import hashlib
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_error_json(errorcode, message=""):
    return {"errorcode": errorcode, "message": message}, errorcode


def validate_key(key):
    if User.query.filter_by(apikey=key).first() is None:
        return False
    else:
        return True


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def get_placeid(placename=None):
    if placename is not None:
        place = Place.query.filter(func.lower(Place.name) == func.lower(placename)).first()
        if place is None:
            return None
        else:
            return place.id
    else:
        return None


@app.route("/")
def home():
    return render_template("index.html", error="")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        if "username" in session and session["username"] is not None:
            return redirect('/dashboard')
        else:
            return render_template("login.html", error="")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        user = User.query.filter_by(username=username, hashed_pw=hashed_pw).first()
        if user is None:
            return render_template("login.html", error="Wrong username or password!")
        else:
            session['username'] = username
            return redirect('/dashboard')


@app.route("/logout")
def logout():
    if request.method == "GET":
        if "username" in session:
            del session["username"]
    return redirect('/')


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "GET":
        return render_template("login.html", error="")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        # TODO cannot register new user if username is alread taken
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return render_template("login.html", error="An user with this username already exists!")

        user = User(username=username, hashed_pw=hashed_pw)
        db.session.add(user)
        session['username'] = username
        db.session.commit()

        return redirect('/dashboard')


@app.route("/apicalls")
def apicalls():
    return render_template("apicalls.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        apikey = "Click \"Generate\" to get an API key"
        user = User.query.filter_by(username=session["username"]).first()
        if user.apikey is not None:
            apikey = user.apikey
        return render_template("dashboard.html", username=session["username"], apikey=apikey)
    else:
        return redirect('/')


@app.route("/generateapikey", methods=["GET"])
def generateapikey():
    if request.method == "GET":
        if "username" in session:
            user = User.query.filter_by(username=session["username"]).first()
            user.apikey = secrets.token_hex(20)
            db.session.commit()

            return user.apikey
        else:
            return "User is not authenticated yet. Go to homepage to login."


@app.route("/api/forecast", methods=["GET", "PUT", "DELETE"])
def forecastAPI():
    if request.method == "GET":
        if "key" in request.args:
            if not validate_key(request.args["key"]):
                return create_error_json(401, "Unauthorized or invalid API key.")
        else:
            return create_error_json(400, "Missing required parameter: key. Request an API key from the homepage.")

        if "placename" in request.args:
            placename = request.args["placename"]
            place = Place.query.filter(func.lower(Place.name) == func.lower(placename)).first()
            if place is None:
                return create_error_json(400, "Place not found. Check the value or use another parameter to specify a place.")
            else:
                placeid = place.id
        elif "placeid" in request.args:
            placeid = request.args["placeid"]
        else:
            return create_error_json(400, "Missing required parameter, one of the following must be used: 'placename' or 'placeid'.")

        if "date" in request.args:
            try:
                date = datetime.fromisoformat(request.args["date"])
            except ValueError:
                return create_error_json(400, "Unable to parse 'date', provide it with the format 'yyyy-mm-dd' or 'yyyymmdd'.")
        else:
            date = datetime.today()

        details = False
        if "details" in request.args:
            if request.args["details"].lower() == "true":
                details = True
            elif request.args["details"].lower() == "false":
                pass
            else:
                return create_error_json(400, "Unable to parse 'details', value must be 'true' or 'false'.")

        forecast = Forecast.query.filter_by(placeid=placeid, date=date).first()

        if forecast is None:
            return create_error_json(404, "Nothing was found in the database with the parameters specified.")
        else:
            result = {"id": forecast.id,
                      "placeid": forecast.placeid,
                      "date": forecast.date,
                      "condition": forecast.condition,
                      "temperature": forecast.temperature,
                      "rain": forecast.rain,
                      "humidity": forecast.humidity,
                      "wind": forecast.wind,
                      "wind_direction": forecast.wind_direction}
            if details:
                condition = Condition.query.filter_by(id=forecast.condition).first()
                result["condition_description"] = condition.description
                place = Place.query.filter_by(id=forecast.placeid).first()
                result["placename"] = place.name
            return result

    elif request.method == "PUT":
        if "key" in request.form:
            if not validate_key(request.form["key"]):
                return create_error_json(401, "Unauthorized, invalid or missing API key.")
        else:
            return create_error_json(400, "Missing required parameter: key. Request an API key from the homepage.")

        if "placeid" in request.form:
            placeid = request.form["placeid"]
        else:
            return create_error_json(400, "Missing required parameter 'placeid'.")

        if "date" in request.form:
            date = datetime.fromisoformat(request.form["date"])
        else:
            return create_error_json(400, "Missing required parameter 'date'.")

        condition = request.form.get("condition", None)
        temperature = request.form.get("temperature", None)
        rain = request.form.get("rain", None)
        humidity = request.form.get("humidity", None)
        wind = request.form.get("wind", None)
        wind_direction = request.form.get("wind_direction", None)

        forecast = Forecast(placeid=placeid,
                            date=date,
                            condition=condition,
                            temperature=temperature,
                            rain=rain,
                            humidity=humidity,
                            wind=wind,
                            wind_direction=wind_direction)

        db.session.add(forecast)
        db.session.commit()

        return "Uploaded", 200

    elif request.method == "DELETE":
        if "key" in request.form:
            if not validate_key(request.form["key"]):
                return create_error_json(401, "Unauthorized or invalid API key.")
        else:
            return create_error_json(400, "Missing required parameter 'key'. Request an API key from the homepage.")

        if "forecastid" in request.form:
            forecastid = request.form["forecastid"]
        else:
            return create_error_json(400, "Missing required parameter 'forecastid'")

        forecast = Forecast.query.filter_by(id=forecastid).first()
        if forecast is None:
            return create_error_json(404, "Nothing was found in the database with the parameters specified.")
        else:
            db.session.delete(forecast)
            db.session.commit()
        return "Deleted", 200


@app.route("/api/places", methods=["GET", "PUT"])
def placesAPI():
    if request.method == "GET":
        if "placename" in request.args:
            place = Place.query.filter(func.lower(Place.name) == func.lower(request.args["placename"])).first()
        elif "placeid" in request.args:
            place = Place.query.filter(func.lower(Place.name) == func.lower(request.args["placename"])).first()
        else:
            return create_error_json(400, "Missing required parameter, one of the following must be used: 'placename', 'placeid'")

        if place is None:
            return create_error_json(404, "Nothing was found in the database with the parameters specified.")
        else:
            return to_dict(place)

    elif request.method == "PUT":
        if "key" in request.form:
            if not validate_key(request.form["key"]):
                return create_error_json(401, "Unauthorized or invalid API key.")
        else:
            return create_error_json(400, "Missing required parameter: key. Request an API key from the homepage.")

        if "name" in request.form:
            placename = request.form["placename"]
        else:
            return create_error_json(400, "Missing required parameter 'name'")

        coords = request.form.get("coords", None)
        lat = request.form.get("lat", None)
        lon = request.form.get("lon", None)
        if lat and lon:
            pass
        elif coords:
            try:
                lat, lon = coords.split(",")
                lat = float(lat)
                lon = float(lon)
            except:
                return create_error_json(400, "Unable to parse 'coords', value must be of format 'float,float'.")
        else:
            return create_error_json(400, "Missing required parameter, one of the following must be used: 'coords' or 'lat' and 'lon'.")

        place = Place(name=placename,
                      lat=lat,
                      lon=lon)

        db.session.add(place)
        db.session.commit()


@app.route("/api/conditions", methods=["GET"])
def conditionsAPI():
    if request.method == "GET":
        if "id" in request.args:
            condition = Condition.query.filter_by(id=request.args["id"]).first()
            if condition is None:
                return create_error_json(404, "Nothing was found in the database with the parameters specified.")
            else:
                return to_dict(condition)
        else:
            data = {}
            for condition in Condition.query.all():
                data[condition.id] = condition.description
            return data


@app.route("/api/alltables", methods=["GET"])
def alltables():
    if request.method == "GET":
        metadata = db.MetaData()
        metadata.reflect(bind=db.engine)

        from sqlalchemy import Table
        result = []
        for table_name in metadata.tables.keys():
            table = Table(table_name, metadata, autoload_with=db.engine)
            tb = {table_name: []}
            query = db.session.query(table).all()
            for row in query:
                row_data = {}
                for column in table.columns:
                    row_data[column.name] = getattr(row, column.name)
                tb[table_name].append(row_data)
            result.append(tb)

        return jsonify(result)


if __name__ == "__main__":
    reset_db(app, db)
    app.run(debug=False)
