from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, DateField, IntegerField, PasswordField, EmailField)
from wtforms.validators import InputRequired, Length
import datetime
import sqlite3
import re

def containsOnlyLetters(field):
     if field.isalpha():
         return True
     else:
         return f" {field} must only contain letters. "

def dateIsInThePast(field):
    if field <= datetime.date.today() and field >= datetime.date(2019,1,1):
        return True
    else:
        return " Date must be between 01/01/2019 and today. "
    
def integerIsValid(field:int, min:int, max: int):
    if field >= min and field <=max:
        return True
    else:
        return f" Duration must be between {min} and {max} mins. "
    
def passwordIsValid(field:str):
    flag = True
    while True:
        if not re.search("[a-z]", field):
            flag = False
            break
        elif not re.search("[A-Z]", field):
            flag = False
            break
        elif not re.search("[0-9]", field):
            flag = False
            break
        elif not re.search("[_@$!]" , field):
            flag = False
            break
        elif re.search("\s" , field):
            flag = False
            break
        else:
            return flag
    
    if flag == False:
        return f" Invalid password: password must be 8-20 characters long with no spaces and include at least one lower case letter, one upper case letter, one digit and one special character ('_', '@', '$', '!'). "

def create_customer_form(
    nameValue: str = '',
    dateJoinedValue: str = '',
    locationValue: str = '',
    useCaseValue: str = ''
):
    class customer_form(FlaskForm):

        name = StringField('Customer Name', default = nameValue, validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Team A", "class":"form-control"})
        location = StringField('Location', default = locationValue, validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "London", "class":"form-control"})
        dateJoined = DateField('Date Joined', default = dateJoinedValue, validators=[InputRequired()], render_kw={"class":"form-control"})
        useCase = TextAreaField('Use Case', default = useCaseValue, validators=[InputRequired(), Length(max=300)], render_kw={"placeholder": "To monitor video fragments", "class":"form-control"})


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
    
    return customer_form()

def create_event_form(
    nameValue: str = '',
    locationValue: str = '',
    dateStartedValue: str = '',
    durationMinsValue: str = ''
):

    class event_form(FlaskForm):
            
        name = StringField('Event Name', default = nameValue, validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "TNF", "class":"form-control"})
        location = StringField('Location', default = locationValue, validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "London", "class":"form-control"})
        dateStarted = DateField('Date Started', default = dateStartedValue, validators=[InputRequired()], render_kw={"class":"form-control"})
        durationMins = IntegerField('Event duration in mins (15-300)', default = durationMinsValue, validators=[InputRequired()], render_kw={"placeholder": "120", "class":"form-control"})


        def validate_on_submit(self):
            dateValidated = dateIsInThePast(self.dateStarted.data)
            locationValidated = containsOnlyLetters(self.location.data)
            durationValidated = integerIsValid(self.durationMins.data, 15, 300)
            if (
                dateValidated == True
                and locationValidated == True
                and durationValidated == True
            ):
                return True
            else:
                message = f"Input invalid:"
                if dateValidated != True: message += dateValidated
                if locationValidated != True: message += locationValidated
                if durationValidated != True: message += durationValidated
                return message
    
    return event_form()
        

class login_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "myUsername", "class":"form-control"})
    email = EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "myemail@gmail.com", "class":"form-control"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)], render_kw={"class":"form-control"})

    def validate_on_submit(self):
        usernameValidated = containsOnlyLetters(self.username.data)
        passwordValidated = passwordIsValid(self.password.data)
        if (
            usernameValidated == True
            and passwordValidated == True
        ):
            return True
        else:
            message = f"Input invalid:"
            if usernameValidated != True: message += usernameValidated
            if passwordValidated != True: message += passwordValidated
            
            return message
            
    def email_registered(self):
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)",[self.email.data])
        valemail = curs.fetchone()
        print("ValEmail from validation func: ", valemail)
        if valemail is None:
            return False
        else:
            return True
        