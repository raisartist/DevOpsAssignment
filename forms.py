from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DateField)
from wtforms.validators import InputRequired, Length
import datetime

def containsOnlyLetters(field):
     if (field.isalpha()):
         return True
     else:
         return f"{field} must only contain letters."

def dateIsInThePast(field):
    if(field <= datetime.date.today()):
        return True
    else:
        return "Date must be in the past."

class customer_form(FlaskForm):
        
    name = StringField('Customer Name', validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "TNF", "class":"form-control"})
    location = StringField('Location', validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "London", "class":"form-control"})
    dateJoined = DateField('Date Joined', validators=[InputRequired()], render_kw={"class":"form-control"})
    useCase = TextAreaField('Use Case', validators=[InputRequired(), Length(max=300)], render_kw={"placeholder": "To monitor video fragments", "class":"form-control"})


    def validate_on_submit(self):
        dateValidated = dateIsInThePast(self.dateJoined.data)
        nameValidated = containsOnlyLetters(self.name.data)
        locationValidated = containsOnlyLetters(self.location.data)
        if (
            dateValidated == True
            and  nameValidated == True
            and  locationValidated == True
        ):
            return True
        else:
            message = f"Input invalid:"
            if dateValidated != True: message += dateValidated
            if nameValidated != True: message += nameValidated
            if locationValidated != True: message += locationValidated
            return message
        