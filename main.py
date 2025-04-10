import os
from flask import Flask, render_template
from flask_login import LoginManager, current_user

from data.pages import login_manager as log
from db import db_session
from db.models.users import User
from db.models.favorites import Favorites

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("main.html", title='NeedToFly', header=True)


@app.errorhandler(404)
def handle_bad_request(e):
    return render_template("error.html")


def main():
    db_session.global_init("db/users_favorites.db")
    db_sess = db_session.create_session()
    
    port = int(os.environ.get("PORT", 5000))
    app.register_blueprint(log.blueprint)
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
