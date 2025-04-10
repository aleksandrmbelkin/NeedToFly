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
    app.register_blueprint(log.blueprint)
    
    # for i in range(1, 5):
    #     user = User()
    #     user.name = f"Пользователь {i}"
    #     user.email = f"email{i}@email.ru"
    #     user.hashed_password = f"{i}"
    #     db_sess.add(user)

    #     favorit = Favorites(flight_number=i + 5, date="23.07.2025/15.08.2025", user_id=i)
    #     db_sess.add(favorit)
    # db_sess.commit()

    if current_user:
        # TODO Показывание кнопки с пререходом в избранные билеты
        pass

    app.run()


if __name__ == '__main__':
    main()