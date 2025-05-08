import flask
from db import db_session
from flask import render_template, redirect
from flask_login import login_user, logout_user, login_required, current_user
from forms.registerform import RegisterForm
from forms.loginform import LoginForm
from db.models.users import User
from db.models.favorites import Favorites


blueprint = flask.Blueprint(
    'favorites',
    __name__,
    template_folder='templates'
)


@login_required
@blueprint.route('/favorites')
def favorite():
    db = db_session.create_session()
    a = db.query(Favorites).filter(Favorites.user_id == current_user.id).all()
    return render_template('favorites.html', lt=a)
