from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired


class TabloForm(FlaskForm):
    # Форма для поиска рейсов из конкретного аэропорта в другие страны/аэропорты
    airport = StringField('Название аэропорта (по системе IATA)',
                          validators=[DataRequired(), validators.length(max=10)])
    country = StringField('Название города (по системе IATA)',
                          validators=[DataRequired(), validators.length(max=10)])
    submit = SubmitField('Поиск', validators=[DataRequired()])
