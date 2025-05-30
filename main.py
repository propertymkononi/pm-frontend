"""This is the code for Property Mkononi backend
-----------------------------------------------
The imported packages assist in app functionality and intergration with other languages
Security is managed by the werkzeug package
The SQlalchemy package handles user tables and database query
"""

from flask import Flask, render_template, request, redirect, session,  url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.sql import func


app = Flask(__name__)

#configuring the database connection
app.config['SQLALCHEMY_DATABASE_URI'] =  "sqlite:///propertym" #Change username, password, table name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)


app.config['SECRET_KEY'] = "fdfafhqwee73jbhzx" # Change to a long random string in production


#User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


    def __repr__(self):
      return f"User('{self.id}','{self.username}', '{self.email}','{self.date_created}' )"


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/landlord_login', methods=['POST','GET'] )   #The main route takes the landlord to the dashoard after procesing the login credentials
def landlord_login():
   if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
      

        user = User.query.filter_by(username=username).first()
        print(f"Logging in user: {username}")
        print(f"User found: {user}")
        if user:
            print(f"Stored hash: {user.password}")
            print(f"Entered password: {password}")
       
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            print("logged in successfully", "success")
            return redirect(url_for('landlord_dashboard'))
        else:
            flash("Invalid username or password",'danger')
            print("failed login")
        return render_template('landlord_login.html', error='Invalid username or password')
   return render_template('landlord_login.html')
   

@app.route('/landlord_register', methods=['GET','POST'])
def landlord_register():
   #Confirm information of the user before registration
   if request.method == 'POST':
      username = request.form.get('username')
      email = request.form.get('email')
      password = generate_password_hash(request.form.get('password'))
      user = User.query.filter_by(username=username).first()


      if user:
         return render_template('landlord_login.html', error="User already exists")
      else:
         new_user = User(username=username , email=email, password=password)
         print(request.form.get('password'))
         db.session.add(new_user)
         users = User.query.all()
         print(users) 
         db.session.commit()
         flash("Registered successfully!")
         return redirect(url_for('landlord_login'))
         
      
   return render_template('landlord_signup.html')


# @app.route('/delete_all_users', methods=['GET','POST'])
# def delete_all_users():
#     try:
#         db.session.query(User).delete()
#         db.session.commit()
#         return "All users deleted successfully."
#     except Exception as e:
#         db.session.rollback()
#         return f"Error deleting users: {e}"

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
  if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
      

        user = User.query.filter_by(username=username).first()
       
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            print("logged in successfully", "success")
            return redirect(url_for('landlord_dashboard'))
        else:
            flash("Invalid username or password",'danger')
            print("failed login")
        return render_template('landlord_login.html', error='Invalid username or password')
  return render_template('tenant_login.html')

@app.route('/tenant_register', methods=['GET','POST'])
def tenant_register():
  if request.method == 'POST':
      username = request.form.get('username')
      email = request.form.get('email')
      password = generate_password_hash(request.form.get('password'))
      user = User.query.filter_by(username=username).first()


      if user:
         return render_template('landlord_login.html', error="User already exists")
      else:
         new_user = User(username=username , email=email, password=password)
         print(request.form.get('password'))
         db.session.add(new_user)
         users = User.query.all()
         print(users) 
         db.session.commit()
         flash("Registered successfully!")
         return redirect(url_for('landlord_login'))
         
      
  return render_template('tenant_form.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if (__name__) == ('__main__'):
  # with app.app_context():
  #     db.create_all()
  app.run(debug=True)
