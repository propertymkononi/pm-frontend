"""This is the code for Property Mkononi backend
-----------------------------------------------
The imported packages assist in session management and have a secrect key 
"""

from flask import Flask, render_template, request, redirect
import os
from datetime import timedelta

app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key') # Change to a long random string in production

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Sets session timeout

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET','POST'] )
def login():
   return render_template('landlord_login.html')

if (__name__) == ('__main__'):
  app.run(debug=True)
