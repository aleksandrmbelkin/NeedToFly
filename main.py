import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_restful import Api

import fav_resource
from pages import login_manager as log
from pages import search
from pages import save_tickets, favorites, download
from db import db_session
from db.models.users import User
from db.models.favorites import Favorites

from fav_resource import FavsResource


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("index.html", title='NeedToFly', header=True)


@app.errorhandler(404)
def handle_bad_request(_):
    return render_template("error.html")


def main():
    db_session.global_init("db/users_favorites.db")
    db_session.create_session()

    port = int(os.environ.get("PORT", 5000))
    app.register_blueprint(search.blueprint)
    app.register_blueprint(tablo.blueprint)
    app.register_blueprint(log.blueprint)
    app.register_blueprint(save_tickets.blueprint)
    app.register_blueprint(favorites.blueprint)
    app.register_blueprint(download.blueprint)

    api.add_resource(fav_resource.FavsResource, '/api/v2/favs/<int:fav_id>')

    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
