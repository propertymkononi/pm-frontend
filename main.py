"""This is the code for Property Mkononi backend
-----------------------------------------------
The imported packages assist in session management and have a secrect key 
"""

from flask import Flask, render_template, request, redirect, session,  url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import timedelta

app = Flask(__name__)

#configuring the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')  # Use SQLite for simplicity, or PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress a warning
db = SQLAlchemy(app)
migrate = Migrate(app, db) 


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key') # Change to a long random string in production

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Sets session timeout

#User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/landlord_login', methods=['GET','POST'] )   #The main route takes the landlord to the dashoard after procesing the login credentials
def landlord_login():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('landlord_dashboard'))
        else:
            flash("Invalid username or password")
        return render_template('login.html', error='Invalid username or password')
   return render_template('landlord_login.html')
   

@app.route('/landlord_register', methods=['GET','POST'])
def landlord_register():
   if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      user = User.query.filter_by(username=username).first()

      if user:
         return render_template('landlord_login.html', error="User already exists")
      else:
         new_user = User(username=username)
         new_user.set_password(password)
         db.session.add(new_user)
         db.session.commit()
         session['username'] = username
         return redirect(url_for('landlord_login'))
   return render_template('landlord_signup.html')
  

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



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if (__name__) == ('__main__'):
  with app.app_context():
      db.create_all()
  app.run(debug=True)
