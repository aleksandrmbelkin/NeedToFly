from flask_restful import abort, Resource
from db import db_session
from db.models.favorites import Favorites
from flask import jsonify


def abort_if_news_not_found(fav_id):
    session = db_session.create_session()
    news = session.query(Favorites).get(fav_id)
    if not news:
        abort(404, message=f"Favorite {fav_id} not found")


class FavsResource(Resource):
    def get(self, fav_id):
        abort_if_news_not_found(fav_id)
        session = db_session.create_session()
        fav = session.query(Favorites).get(fav_id)
        return jsonify({'favorites': fav.to_dict(
            only=('airport_departure', 'airport_arrival', 'flight_date', 'airline_name', 'flight_number'))})
