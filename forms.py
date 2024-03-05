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
     
def matchesEmailPattern(field):
    if re.match("^[-\w\.]+@([-\w]+\.)+[\w-]{2,4}$", field):
        return True
    else:
        return f" {field} is not a valid email. "

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
        if len(field) < 8 or len(field) > 20:
            flag = False
            break
        elif not re.match("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,20}$", field):
            flag = False
            break
        else:
            return flag
    
    if flag == False:
        return f" Invalid password: password must be 8-20 characters long with no spaces and include at least one lower case letter, one upper case letter, one digit and one special character (#,?,!,@,$,%,^,&,*,-). "

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
    email = EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "myemail@gmail.com", "class":"form-control"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)], render_kw={"class":"form-control"})

    def validate_on_submit(self):
        passwordValidated = passwordIsValid(self.password.data)
        emailValidated = matchesEmailPattern(self.email.data)
        if passwordValidated == True and emailValidated == True:
            return True
        else:
            message = f"Input invalid:"
            if passwordValidated != True: message += passwordValidated
            if emailValidated != True: message += emailValidated
            
            return message
        
class register_form(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "myUsername", "class":"form-control"})
    email = EmailField('Email', validators=[InputRequired()], render_kw={"placeholder": "myemail@gmail.com", "class":"form-control"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)], render_kw={"class":"form-control"})

    def validate_on_submit(self):
        usernameValidated = containsOnlyLetters(self.username.data)
        passwordValidated = passwordIsValid(self.password.data)
        emailValidated = matchesEmailPattern(self.email.data)
        if (
            usernameValidated == True
            and passwordValidated == True
            and emailValidated == True
        ):
            return True
        else:
            message = f"Input invalid:"
            if usernameValidated != True: message += usernameValidated
            if passwordValidated != True: message += passwordValidated
            if emailValidated != True: message += emailValidated
            
            return message
            
    def already_registered(self):
        conn = sqlite3.connect('database.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users where email = (?)",[self.email.data])
        existingEmail = curs.fetchone()
        curs.execute("SELECT username FROM users where username = (?)",[self.username.data])
        existingName = curs.fetchone()
        if existingEmail is not None:
            return "This email is already registered."
        elif existingName is not None:
            return "This username is already registered."
        else:
            return False
        