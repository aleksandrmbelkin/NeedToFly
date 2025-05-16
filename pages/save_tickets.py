import flask
from db import db_session
from db.models.users import User
from db.models.favorites import Favorites
from flask_login import login_required, current_user


blueprint = flask.Blueprint(
    'save_tickets',
    __name__,
    template_folder='templates'
)


@login_required
@blueprint.route('/save_ticket', methods=['POST'])
def search():
    # Берём данные билета из формы и сохраняем в таблицу Favorites нашей БД
    airport_departure = flask.request.form.get('airport_departure')
    airport_arrival = flask.request.form.get('airport_arrival')
    flight_date = flask.request.form.get('flight_date')
    airline_name = flask.request.form.get('airline_name')
    flight_number = flask.request.form.get('flight_number')
    db_sess = db_session.create_session()
    ticket_info = Favorites(
        airport_departure = airport_departure,
        airport_arrival = airport_arrival,
        flight_date = flight_date,
        airline_name = airline_name,
        flight_number = flight_number,
        user_id = current_user.id
    )
    db_sess.add(ticket_info)
    db_sess.commit()
    return 'Добавлено в избранное'


@login_required
@blueprint.route('/save_ticket_search/<air_dep>/<air_arr>/<fl_date>/<air_name>/<fl_num>', methods=['GET', 'POST'])
def save_ticket_search(air_dep, air_arr, fl_date, air_name, fl_num):
    # Берём данные билета из формы и сохраняем в таблицу Favorites нашей БД
    airport_departure = air_dep
    airport_arrival = air_arr
    flight_date = fl_date
    airline_name = air_name
    flight_number = fl_num
    db_sess = db_session.create_session()
    ticket_info = Favorites(
        airport_departure = airport_departure,
        airport_arrival = airport_arrival,
        flight_date = flight_date,
        airline_name = airline_name,
        flight_number = flight_number,
        user_id = current_user.id
    )
    db_sess.add(ticket_info)
    db_sess.commit()
    return 'Добавлено в избранное'


@login_required
@blueprint.route('/delete/<int:user_id>/<int:ticket_id>')
def deleting_ticket(user_id, ticket_id):
    # Удаляем информацию об избранном билете из БД
    db = db_session.create_session()
    if user_id == current_user.id:
        a = db.query(Favorites).filter(Favorites.user_id == user_id, Favorites.id == ticket_id).first()
        if a:
            db.delete(a)
            db.commit()
            return flask.redirect('/favorites')
        return 'Произошла ошибка при удалении из избранного'
    return 'Ошибка со входом в аккаунт'
