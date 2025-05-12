"""This is the code for Property Mkononi backend
-----------------------------------------------
The imported packages assist in session management and have a secrect key 
"""

from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import timedelta

app = Flask(__name__)
#configuring the database connection
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite///users.db"   #Use postgesql in production
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key') # Change to a long random string in production

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Sets session timeout

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/landlord_login', methods=['GET','POST'] )   #The main route takes the landlord to the dashoard after procesing the login credentials
def landlord_login():
      # if password == generate_password_hash:
      # return redirect(url_for())
  return render_template('landlord_login.html')


@app.route('/landlord_password', methods=['GET','POST'])
def landlord_password():
  return render_template('landlord_forgot_password.html')

@app.route('/landlord_dashboard')
def landlord_dashboard():
  return render_template('landlord_dashboard.html')

@app.route('/tenants')
def tenants():
  return render_template('tenants.html')

@app.route('/properties')
def properties():
  return render_template('properties.html')

@app.route('/rent')
def rent():
  return render_template('rent.html')

@app.route('/evictions')
def evictions():
  return render_template('evictions.html')

@app.route('/requests')
def requests():
  return render_template('requests.html')

@app.route('/notebooks')
def notebooks():
  return render_template('notebooks.html')


@app.route('/tenant_login', methods=['GET','POST'])
def tenant_login():
  pass

if (__name__) == ('__main__'):
  # with app.app.context():
  #   db.create_all()
  app.run(debug=True)
