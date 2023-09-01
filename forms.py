from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DateField)
from wtforms.validators import InputRequired, Length
import datetime

class new_customer_form(FlaskForm):
        
    name = StringField('Customer Name', validators=[InputRequired(), Length(min=3, max=20)])
    location = StringField('Location e.g. London', validators=[InputRequired(), Length(min=2, max=20)])
    dateJoined = DateField('Date Joined', validators=[InputRequired()])
    useCase = TextAreaField('use Case e.g. To monitor 2sec video fragments', validators=[InputRequired(), Length(max=300)])


    def validate_on_submit(self):
        if (self.dateJoined.data > datetime.date.today()):
            return False
        else:
             return True