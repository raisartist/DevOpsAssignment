from flask import Flask, render_template, request
import sqlite3
from forms import customer_form, event_form, login_form
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
bcrypt = Bcrypt()

def addAdmin():
    try:
        with sqlite3.connect("database.db") as connection:
            current = connection.cursor()
            current.execute("INSERT INTO users (username, email, password, isAdmin) VALUES (?,?,?,?)",("admin","admin@agile.com",bcrypt.generate_password_hash("qwerty123").decode("utf-8"),"True"))
            connection.commit()
        print("Added an admin to users")
    except Exception as e:
        print(f"Failed to add Admin: {e}")
    finally:
        connection.close()

conn = sqlite3.connect('database.db')
print ("Opened database successfully")

# conn.execute('DROP TABLE IF EXISTS events')
# print("Dropped events")
# conn.execute('DROP TABLE IF EXISTS customers')
# print("Dropped customers")
# conn.execute('DROP TABLE IF EXISTS users')
# print("Dropped users")
conn.execute('CREATE TABLE IF NOT EXISTS customers (name VARCHAR PRIMARY KEY UNIQUE NOT NULL, dateJoined TEXT NOT NULL, useCase TEXT NOT NULL, location TEXT NOT NULL)')
print ("Customers table created successfully");
conn.execute('CREATE TABLE IF NOT EXISTS events (name VARCHAR PRUMARY KEY UNIQUE NOT NULL, location TEXT NOT NULL, dateStarted TEXT NOT NULL, durationMins INTEGER NOT NULL)')
print ("Events table created successfully");
conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, isAdmin VARCHAR NOT NULL)')
print ("Users table created successfully");
conn.close()

addAdmin()

app = Flask(__name__)
app.secret_key = "my super secret key for the app"

login_manager.init_app(app)
bcrypt.init_app(app)

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
        print("*inside load user*")
        print(f"id: {id}")

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = (?)",[id])
        # cursor.execute("select * from users")
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            return User(result[0], result[1], result[2], result[3], result[4])
    except Exception as e:
        return e

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        message = "Logged out successfully."
        isError = False
        return render_template("login_result.html", message = message, isError = isError)
    else:
        message = "You are not logged in."
        isError = True
        return render_template("login_result.html", message = message, isError = isError)

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return render_template("login_result.html", message = f"Already logged in as {current_user.username}", isError = False)
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
    isRegistered = form.email_registered()
    if request.method == 'POST':
        try:
            username = form.username.data
            email = form.email.data
            password = form.password.data
            passwordHash = bcrypt.generate_password_hash(password).decode("utf-8")
            isAdmin = False
            if isRegistered == True:
                with sqlite3.connect("database.db") as connection:
                    current = connection.cursor()
                    current.execute("SELECT * from users where username = (?)",[username])
                    userList = list(current.fetchone())
                    print(f"userlist: {userList}")
                    try:
                        user = load_user(userList[0])
                        print(f"user: {user}")
                        isValidPass = bcrypt.check_password_hash(user.password, password)
                        if email == user.email and isValidPass:
                            login_user(user, remember=True)
                            message = f"Logged in successfully - Welcome back, {user.username}!"
                            isError = False
                        else:
                            print(f"email: {email}, userEmail: {user.email}, pas: {isValidPass}")
                            message = "Login unsiccessful: invalid username or password. "
                            isError = True
                    except Exception as e:
                        connection.rollback()
                        message = e
                        isError = True
            else:
                with sqlite3.connect("database.db") as connection:
                    current = connection.cursor()
                    current.execute("INSERT INTO users (username, email, password, isAdmin) VALUES (?,?,?,?)",(str(username),str(email),str(passwordHash),str(isAdmin)) )
                    connection.commit()
                    message = f"New user {username} is successfully registered."
                    isError = False
        except Exception as error:
            connection.rollback()
            message = str(error)
            isError = True
        
        finally:
            connection.close()
            # flash(message)
            # return redirect(url_for("customers_database"))
            return render_template("login_result.html", message = message, isError = isError)
    else:
        return render_template("login_result.html", message = str(request.method), isError = True)
                    

# Customers

@app.route("/customers_database")
@login_required
def customers_database():
    form = customer_form()
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row

    current = connection.cursor()
    current.execute("select * from customers")

    rows = current.fetchall(); 
    return render_template("customers_database.html", rows = rows, form=form)

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
                isError = False
        except Exception as error:
            connection.rollback()
            message = str(error)
            isError = True
        
        finally:
            connection.close()
            return render_template("result.html",message = message, isError = isError)
            # flash(message)
            # return redirect(url_for("customers_database"))

@app.route("/update_customer/<name>/<dateJoined>/<location>/<useCase>")
@login_required
def update_customer(name, dateJoined, location, useCase):
    form = customer_form()
    return render_template("update_customer.html", name = name, dateJoined = dateJoined, location = location, useCase = useCase, form = form)

@app.route("/update_set_customer/<customer_name>", methods = ['POST', 'GET'])
@login_required
def update_set_customer(customer_name):
    form = customer_form(request.form)
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
                        message = "Customer record successfully updated"
                        isError = False
            except Exception as error:
                connection.rollback()
                message = str(error)
                isError = True
            
            finally:
                connection.close()
                # flash(message)
                # return redirect(url_for("customers_database"))
                return render_template("result.html",message = message, isError = isError)
    else:
        return render_template("result.html",message = isValid, isError = True)

@app.route("/add_customer", methods = ['POST', 'GET'])
@login_required
def add_customer():
    form = customer_form(request.form)
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
                        current.execute("INSERT OR IGNORE INTO customers (name,dateJoined,useCase,location) VALUES (?,?,?,?)",(str(name),str(dateJoined),str(useCase),str(location)) )
                        
                        connection.commit()
                        message = "Customer record successfully added"
                        isError = False
            except Exception as error:
                connection.rollback()
                message = str(error)
                isError = True
            
            finally:
                connection.close()
                # flash(message)
                # return redirect(url_for("customers_database"))
                return render_template("result.html",message = message, isError = isError)
    else:
        return render_template("result.html",message = isValid, isError = True)

# Events

@app.route("/events_database")
@login_required
def events_database():
    form = event_form()
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row

    current = connection.cursor()
    current.execute("select * from events")

    rows = current.fetchall(); 
    return render_template("events_database.html", rows = rows, form=form)

@app.route("/add_event", methods = ['POST', 'GET'])
@login_required
def add_event():
    form = event_form(request.form)
    isValid = form.validate_on_submit()
    if isValid == True:
        if request.method == 'POST':
            try:
                name = form.name.data
                dateStarted= form.dateStarted.data
                durationMins = form.durationMins.data
                location = form.location.data
                with sqlite3.connect("database.db") as connection:
                        current = connection.cursor()
                        current.execute("INSERT OR IGNORE INTO events (name,dateStarted,durationMins,location) VALUES (?,?,?,?)",(str(name),str(dateStarted),str(durationMins),str(location)) )
                        connection.commit()
                        message = "Event record successfully added"
                        isError = False
            except Exception as error:
                connection.rollback()
                message = str(error)
                isError = True
            
            finally:
                connection.close()
                # flash(message)
                # return redirect(url_for("customers_database"))
                return render_template("result.html",message = message, isError = isError)
    else:
        return render_template("result.html",message = isValid, isError = True)

@app.route("/update_event/<name>/<dateStarted>/<location>/<durationMins>")
@login_required
def update_event(name, dateStarted, location, durationMins):
    form = event_form()
    return render_template("update_event.html", name = name, dateStarted = dateStarted, location = location, durationMins = durationMins, form = form)

@app.route("/update_set_event/<event_name>", methods = ['POST', 'GET'])
@login_required
def update_set_event(event_name):
    form = event_form(request.form)
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
                        isError = False
            except Exception as error:
                connection.rollback()
                message = str(error)
                isError = True
            
            finally:
                connection.close()
                # flash(message)
                # return redirect(url_for("customers_database"))
                return render_template("result.html",message = message, isError = isError)
    else:
        return render_template("result.html",message = isValid, isError = True)

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
                isError = False
        except Exception as error:
            connection.rollback()
            message = str(error)
            isError = True
        
        finally:
            connection.close()
            return render_template("result.html",message = message, isError = isError)
            # flash(message)
            # return redirect(url_for("customers_database"))
    
if __name__ == "__main__":
    app.run(debug=True)