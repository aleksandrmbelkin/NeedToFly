import flask
from db import db_session
from flask import render_template, redirect
from flask_login import login_user, logout_user, login_required, current_user
from forms.registerform import RegisterForm
from forms.loginform import LoginForm
from db.models.users import User
from db.models.favorites import Favorites
import os


blueprint = flask.Blueprint(
    'download',
    __name__,
    template_folder='templates'
)


@login_required
@blueprint.route('/download/<int:user_id>/<int:fav_id>')
def favorite(user_id, fav_id):
    if user_id == current_user.id:
        db = db_session.create_session()
        a = db.query(Favorites).filter(Favorites.user_id == current_user.id, Favorites.id == fav_id).first()
        filename = f'{user_id}{fav_id}.txt'
        # Создаём файл для скачивания
        with open(f'static/tickets_info/{filename}', 'w', encoding='utf-8') as f:
            f.write(f'Начальный аэропорт: {a.airport_departure}\n')
            f.write(f'Конечный аэропорт: {a.airport_arrival}\n')
            f.write(f'Дата: {a.flight_date}\n')
            f.write(f'Авиакомпания: {a.airline_name}\n')
            f.write(f'Номер полёта: {a.flight_number}\n')
            return render_template('download.html', filename=filename)

    return 'Ошибка с аккаунтом'


@login_required
@blueprint.route('/delete_ticket_info/<int:user_id>/<filename>')
def delete_ticket_info(user_id, filename):
    if user_id == current_user.id:
        # Удаляем файл для скачивания
        os.remove(f'static/tickets_info/{filename}')
    return redirect('/favorites')
