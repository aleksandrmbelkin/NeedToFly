from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired


class TabloForm(FlaskForm):
    airport = StringField('Название аэропорта (по системе IATA)',
                          validators=[DataRequired(), validators.length(max=20)])
    country = StringField('Название города (по системе IATA)',
                          validators=[DataRequired(), validators.length(max=20)])
    submit = SubmitField('Поиск', validators=[DataRequired()])
