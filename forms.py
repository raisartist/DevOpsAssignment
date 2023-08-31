from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DateField)
from wtforms.validators import InputRequired, Length

class new_customer_form(FlaskForm):
    name = StringField('Customer Name', validators=[InputRequired(), Length(min=3, max=20)])
    location = StringField('Location e.g. London', validators=[InputRequired(), Length(min=2, max=20)])
    dateJoined = DateField('Date Joined (yyyy-mm-dd)', validators=[InputRequired()])
    useCase = TextAreaField('use Case e.g. To monitor 2sec video fragments', validators=[InputRequired(), Length(max=300)])