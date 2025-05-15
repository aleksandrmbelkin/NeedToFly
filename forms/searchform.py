from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, DateField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange

        
class SearchForm(FlaskForm):
    originLocationCode = StringField(validators=[DataRequired(), validators.length(max=30)])
    destinationLocationCode = StringField(validators=[DataRequired(), validators.length(max=30)])

    departureDate = DateField('Дата вылета', validators=[DataRequired()])
    returnDate = DateField('Дата прилета', validators=[DataRequired()])

    adults = IntegerField('Взрослые', validators=[DataRequired(), NumberRange(min=1, max=9)])
    children = IntegerField('Дети', validators=[NumberRange(min=0, max=9)])
    infants = IntegerField('Младенцы', validators=[NumberRange(min=0, max=9)])
    
    travelClass = SelectField('Выберите класс', choices=["Эконом", "Бизнес"])
    nonStop = BooleanField('Без пересадок')
    submit = SubmitField('Поиск')
