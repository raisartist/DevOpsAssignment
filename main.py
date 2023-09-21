from flask import Flask, render_template, request, flash, url_for, redirect
import sqlite3
from forms import create_customer_form, create_event_form, login_form
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime

login_manager = LoginManager()
bcrypt = Bcrypt()

def addAdmin():
    try:
        with sqlite3.connect("database.db") as connection:
            current = connection.cursor()
            current.execute("INSERT INTO users (username, email, password, isAdmin) VALUES (?,?,?,?)",("admin","admin@agile.com",bcrypt.generate_password_hash("Qwerty123@").decode("utf-8"),"True"))
            connection.commit()
        print("Added an admin to users")
    except Exception as error:
        print(f"Failed to add Admin: {error}")
    finally:
        connection.close()

conn = sqlite3.connect('database.db')
print ("Opened database successfully")

# Uncomment the block below to refresh the tables:

# conn.execute('DROP TABLE IF EXISTS events')
# print("Dropped events")
# conn.execute('DROP TABLE IF EXISTS customers')
# print("Dropped customers")
# conn.execute('DROP TABLE IF EXISTS users')
# print("Dropped users")

conn.execute('CREATE TABLE IF NOT EXISTS customers (name VARCHAR PRIMARY KEY UNIQUE NOT NULL, author VARCHAR NOT NULL, dateJoined TEXT NOT NULL, useCase TEXT NOT NULL, location TEXT NOT NULL)')
print ("Customers table created successfully");
conn.execute('CREATE TABLE IF NOT EXISTS events (name VARCHAR PRUMARY KEY UNIQUE NOT NULL, author VARCHAR NOT NULL, location TEXT NOT NULL, dateStarted TEXT NOT NULL, durationMins INTEGER NOT NULL)')
print ("Events table created successfully");
conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, isAdmin VARCHAR NOT NULL)')
print ("Users table created successfully");
conn.close()

addAdmin()

def create_app():
    app = Flask(__name__)
    app.secret_key = "my super secret key for the app"

    login_manager.init_app(app)
    bcrypt.init_app(app)

    return app

app = create_app()

class User(UserMixin):
    def __init__(self, id, username, email, password, isAdmin = False):
        self.id = id  
        self.username = username
        self.email = email
        self.password = password
        self.isAdmin = isAdmin
        self.authenticated = False
        def is_active(self):
            return self.is_active()   
        def is_anonymous(self):
            return False    
        def is_authenticated(self):
            return self.authenticated    
        def is_active(self):
            return True    
        def get_id(self):
            return self.id
        
@login_manager.user_loader
def load_user(id):
    try: 
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = (?)",[id])
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return User(result[0], result[1], result[2], result[3], result[4])
    except Exception as e:
        return e

@app.route("/")
def home():
    username = ""
    if current_user.is_authenticated:
        username = current_user.username
    return render_template("home.html", isAuthenticated = current_user.is_authenticated, username = username)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Logged out successfully.")
        return redirect(url_for("home"))
    else:
        flash("You are not logged in.")
        return redirect(url_for("home"))

@app.route("/login")
def login():
    if current_user.is_authenticated:
        flash(f"Already logged in as {current_user.username}", category = "info")
        return redirect(url_for("home"))
    form = login_form()
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row

    current = connection.cursor()
    current.execute("select * from users")

    rows = current.fetchall(); 
    return render_template("login.html", form=form, rows=rows)

@app.route("/login_or_register", methods = ['POST', 'GET'])
def login_or_register():
    form = login_form(request.form)
    isValid = form.validate_on_submit()
    isRegistered = form.email_registered()
    if isValid == True:
        if request.method == 'POST':
            try:
                username = form.username.data
                email = form.email.data
                password = form.password.data
                passwordHash = bcrypt.generate_password_hash(password).decode("utf-8")
                if isRegistered == True:
                    with sqlite3.connect("database.db") as connection:
                        current = connection.cursor()
                        current.execute("SELECT * from users where username = (?)",[username])
                        userList = list(current.fetchone())
                        try:
                            user = load_user(userList[0])
                            isValidPassword = bcrypt.check_password_hash(user.password, password)
                            if email == user.email and isValidPassword:
                                login_user(user, remember=True)
                                message = f"Logged in successfully - Welcome back, {user.username}!"
                            else:
                                print(f"email: {email}, userEmail: {user.email}, pas: {isValidPassword}")
                                message = "Login unsuccessful: invalid username or password."
                        except Exception as error:
                            connection.rollback()
                            message = f"Unexpected error line 143: {error}"

                else:
                    with sqlite3.connect("database.db") as connection:
                        current = connection.cursor()
                        current.execute("INSERT INTO users (username, email, password, isAdmin) VALUES (?,?,?,?)",(str(username),str(email),str(passwordHash),str(False)) )
                        connection.commit()
                        message = (f"New user {username} is successfully registered.")
            except Exception as error:
                connection.rollback()
                message = (f"email or username already exist. Please try other credentials or check your entries")
            
            finally:
                connection.close()
                flash(message)
                return redirect(url_for("home"))
        else:
            return redirect(url_for("home"))
    else:
        flash(f"{isValid}")
        return redirect(url_for("home"))
                    

# Customers

@app.route("/customers_database")
@login_required
def customers_database():
    form = create_customer_form()
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    current = connection.cursor()
    currentUser = current_user.username
    isAdmin = current_user.isAdmin

    current.execute("select * from customers")
    rows = current.fetchall(); 

    return render_template("customers_database.html", rows = rows, form=form, currentUser = currentUser, isAdmin = isAdmin, isAuthenticated = current_user.is_authenticated)

@app.route("/delete_customer/<customer_name>", methods = ['POST', 'GET'])
@login_required
def delete_customer(customer_name):
    if request.method == 'POST':
        try: 
            with sqlite3.connect("database.db") as connection:
                current = connection.cursor()
                current.execute("DELETE FROM customers WHERE name = (?)",(customer_name,) )
                
                connection.commit()
                message = "Customer record successfully deleted"
        except Exception as error:
            connection.rollback()
            message = "Failed to delete a record. Please try again later."
        
        finally:
            connection.close()
            flash(message)
            return redirect(url_for("customers_database"))

@app.route("/update_customer/<name>/<dateJoined>/<location>/<useCase>")
@login_required
def update_customer(name, dateJoined, location, useCase):
    form = create_customer_form(name, datetime.strptime(dateJoined,'%Y-%m-%d'), location, useCase)
    return render_template("update_customer.html", name = name, dateJoined = dateJoined, location = location, useCase = useCase, form = form)

@app.route("/update_set_customer/<customer_name>", methods = ['POST', 'GET'])
@login_required
def update_set_customer(customer_name):
    form = create_customer_form(request.form)
    isValid = form.validate_on_submit()
    if isValid == True:
        if request.method == 'POST':
            try:
                name = form.name.data
                dateJoined = form.dateJoined.data
                useCase = form.useCase.data
                location = form.location.data
                with sqlite3.connect("database.db") as connection:
                        current = connection.cursor()
                        current.execute("UPDATE customers SET name = (?), dateJoined = (?), useCase = (?), location = (?) WHERE name = (?)",(name, dateJoined, useCase, location, customer_name) )
                        
                        connection.commit()
                        message = "Customer record successfully updated."
            except Exception as error:
                connection.rollback()
                message = f"Failed to update a record: {str(error)}"
            
            finally:
                connection.close()
                flash(message)
                return redirect(url_for("customers_database"))
    else:
        flash(isValid)
        return redirect(url_for("customers_database"))

@app.route("/add_customer", methods = ['POST', 'GET'])
@login_required
def add_customer():
    form = create_customer_form(request.form)
    isValid = form.validate_on_submit()
    if isValid == True:
        if request.method == 'POST':
            try:
                name = form.name.data
                dateJoined = form.dateJoined.data
                useCase = form.useCase.data
                location = form.location.data
                currentUser = current_user.username
                with sqlite3.connect("database.db") as connection:
                    current = connection.cursor()
                    current.execute("INSERT OR IGNORE INTO customers (name,author,dateJoined,useCase,location) VALUES (?,?,?,?,?)",(str(name),str(currentUser),str(dateJoined),str(useCase),str(location)))
                    connection.commit()
                    message = "Customer record successfully added"
            except Exception as error:
                connection.rollback()
                message = f"Failed to add a customer record: {str(error)}"
            
            finally:
                connection.close()
                flash(message)
                return redirect(url_for("customers_database"))
    else:
        flash(f"{isValid}")
        return redirect(url_for("customers_database"))

# Events

@app.route("/events_database")
@login_required
def events_database():
    form = create_event_form()
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    current = connection.cursor()
    currentUser = current_user.username
    isAdmin = current_user.isAdmin

    current.execute("select * from events")
    rows = current.fetchall();

    return render_template("events_database.html", rows = rows, form=form, currentUser = currentUser, isAdmin = isAdmin, isAuthenticated = current_user.is_authenticated)

@app.route("/add_event", methods = ['POST', 'GET'])
@login_required
def add_event():
    form = create_event_form(request.form)
    isValid = form.validate_on_submit()
    currentUser = current_user.username
    if isValid == True:
        if request.method == 'POST':
            try:
                name = form.name.data
                dateStarted= form.dateStarted.data
                durationMins = form.durationMins.data
                location = form.location.data
                with sqlite3.connect("database.db") as connection:
                    current = connection.cursor()
                    current.execute("INSERT OR IGNORE INTO events (name,author,dateStarted,durationMins,location) VALUES (?,?,?,?,?)",(str(name),str(currentUser),str(dateStarted),str(durationMins),str(location)) )
                    connection.commit()
                    message = "Event record successfully added"
            except Exception as error:
                connection.rollback()
                message = f"Failed to add an event record: {str(error)}"
            
            finally:
                connection.close()
                flash(message)
                return redirect(url_for("events_database"))
    else:
        flash(isValid)
        return redirect(url_for("events_database"))

@app.route("/update_event/<name>/<dateStarted>/<location>/<durationMins>")
@login_required
def update_event(name, dateStarted, location, durationMins):
    form = create_event_form(name, location, datetime.strptime(dateStarted,'%Y-%m-%d'), durationMins)
    return render_template("update_event.html", name = name, dateStarted = dateStarted, location = location, durationMins = durationMins, form = form)

@app.route("/update_set_event/<event_name>", methods = ['POST', 'GET'])
@login_required
def update_set_event(event_name):
    form = create_event_form(request.form)
    isValid = form.validate_on_submit()
    if isValid == True:
        if request.method == 'POST':
            try:
                name = form.name.data
                dateStarted = form.dateStarted.data
                durationMins = form.durationMins.data
                location = form.location.data
                with sqlite3.connect("database.db") as connection:
                        current = connection.cursor()
                        current.execute("UPDATE events SET name = (?), dateStarted = (?), durationMins = (?), location = (?) WHERE name = (?)",(name, dateStarted, durationMins, location, event_name) )
                        
                        connection.commit()
                        message = "Event record successfully updated"
            except Exception as error:
                connection.rollback()
                message = f"Failed to update an event record: {str(error)}"
            
            finally:
                connection.close()
                flash(message)
                return redirect(url_for("events_database"))
    else:
        flash(isValid)
        return redirect(url_for("events_database"))

@app.route("/delete_event/<event_name>", methods = ['POST', 'GET'])
@login_required
def delete_event(event_name):
    if request.method == 'POST':
        try: 
            with sqlite3.connect("database.db") as connection:
                current = connection.cursor()
                current.execute("DELETE FROM events WHERE name = (?)",(event_name,) )
                
                connection.commit()
                message = "Event record successfully deleted"
        except Exception as error:
            connection.rollback()
            message = f"Failed to delete an event record: {str(error)}"
        
        finally:
            connection.close()
            flash(message)
            return redirect(url_for("events_database"))
    
if __name__ == "__main__":
    app.run(debug=True)