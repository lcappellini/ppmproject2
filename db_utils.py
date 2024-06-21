from datetime import datetime

conditions = [
    "Clear",
    "Partly Cloudy",
    "Mostly Cloudy",
    "Cloudy",
    "Foggy",
    "Light Rain",
    "Rain",
    "Heavy Rain",
    "Showers",
    "Thunderstorm",
    "Snow",
    "Windy"
]

# erases all the db and repopulates the tables with some example data
def reset_db(app, db):
    from main import Place, Condition, Forecast, User

    with app.app_context():
        db.create_all()

        # erases db
        metadata = db.MetaData()
        metadata.reflect(bind=db.engine)
        for table in reversed(metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        # add all the available conditions
        for condition in conditions:
            db.session.add(Condition(description=condition))

        #
        db.session.add(Place(id=1, name="Firenze", center_lat=43.77, center_lon=11.2577, radius=4.5))
        db.session.add(Place(id=2, name="Prato", center_lat=43.8777, center_lon=11.1022, radius=0))
        db.session.add(Place(id=3, name="Roma", center_lat=43.8777, center_lon=11.1022, radius=0))

        # add sample entities to db for testing purpose
        db.session.add(Forecast(placeid=1, date=datetime(2024, 6, 19), condition=1, temperature=31.3, rain=0, humidity=30, wind=3, wind_direction="N"))
        db.session.add(Forecast(placeid=2, date=datetime(2024, 6, 19), condition=1, temperature=30.1, rain=0, humidity=32, wind=5, wind_direction="NE"))
        db.session.add(Forecast(placeid=3, date=datetime(2024, 6, 19), condition=2, temperature=32.1, rain=0, humidity=32, wind=5, wind_direction="NO"))

        db.session.add(Forecast(placeid=1, date=datetime(2024, 6, 20), condition=2, temperature=29.4, rain=0, humidity=35, wind=8, wind_direction="S"))
        db.session.add(Forecast(placeid=2, date=datetime(2024, 6, 20), condition=2, temperature=27.5, rain=0, humidity=40, wind=7, wind_direction="SO"))
        db.session.add(Forecast(placeid=3, date=datetime(2024, 6, 20), condition=3, temperature=24.1, rain=0, humidity=42, wind=7, wind_direction="SE"))

        db.session.add(Forecast(placeid=1, date=datetime(2024, 6, 21), condition=3, temperature=28.7, rain=0, humidity=30, wind=4, wind_direction="E"))
        db.session.add(Forecast(placeid=2, date=datetime(2024, 6, 21), condition=3, temperature=27.3, rain=0, humidity=30, wind=9, wind_direction="E"))
        db.session.add(Forecast(placeid=3, date=datetime(2024, 6, 21), condition=5, temperature=19.8, rain=1, humidity=52, wind=8, wind_direction="O"))

        db.session.commit()
