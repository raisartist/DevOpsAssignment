from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3

conn = sqlite3.connect('database.db')
print ("Opened database successfully");

# conn.execute('DROP TABLE IF EXISTS customers')
conn.execute('CREATE TABLE IF NOT EXISTS customers (name VARCHAR UNIQUE, dateJoined TEXT, useCase TEXT, location TEXT)')
print ("Customers table created successfully");
conn.execute('CREATE TABLE IF NOT EXISTS events (name VARCHAR UNIQUE, location TEXT, date TEXT, durationMins INTEGER)')
print ("Events table created successfully");
conn.close()

app = Flask(__name__)
# app.secret_key = "my super secret key for the app" 

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/customers_database")
def customers_database():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row

    current = connection.cursor()
    current.execute("select * from customers")

    rows = current.fetchall(); 
    return render_template("customers_database.html", rows = rows)

@app.route("/events_database")
def events_database():
    return render_template("events_database.html")

@app.route("/delete_customer/<customer_name>", methods = ['POST', 'GET'])
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
        message = error
      
    finally:
        connection.close()
        return render_template("result.html",message = message)

@app.route("/add_customer", methods = ['POST', 'GET'])
def add_customer():
   if request.method == 'POST':
      try:
         name = request.form['name']
         dateJoined = request.form['dateJoined']
         useCase = request.form['useCase']
         location = request.form['location']
         
         with sqlite3.connect("database.db") as connection:
            current = connection.cursor()
            current.execute("INSERT OR IGNORE INTO customers (name,dateJoined,useCase,location) VALUES (?,?,?,?)",(name,dateJoined,useCase,location) )
            
            connection.commit()
            message = "Customer record successfully added"
      except:
         connection.rollback()
         message = "Failed to insert a new customer. Please return to the previous page and try again."
      
      finally:
         connection.close()
         return render_template("result.html",message = message)


if __name__ == "__main__":
    app.run(debug=True)