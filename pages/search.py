import flask
from db import db_session
from flask import render_template, redirect
from forms.searchform import SearchForm

blueprint = flask.Blueprint(
    'search',
    __name__,
    template_folder='templates'
)

@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    # form = SearchForm()
    # if form.validate_on_submit():
        # TODO запрос к Amadeus на получение данных или сделать это с помощью JS
    return render_template('search.html', title='Поиск авиабилетов', header=True)