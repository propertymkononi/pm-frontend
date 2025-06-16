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


#User models
landlord_property = db.Table('landlord_property',
    db.Column('User_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'))
)

class Property(db.model):
     id = db.Column(db.Integer, primary_key=True)
     propertyname = db.Column(db.String(255), unique=True, nullable=False)
     Units = db.Column(db.Integer, unique=True, nullable=False)
     tenants = db.relationship('Tenant', backref='property')
     landlord = db.relationship('Landlord', secondary=landlord_property, back_populates='Properties' )
     date_created = db.Column(db.DateTime(timezone=True), default=func.now())

     def __repr__(self):
      return f"User('{self.id}','{self.propertyname}', '{self.Units}','{self.date_created}', '{self.tenants}' )"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    properties = db.relationship('Property', secondary=landlord_property, back_populates='Landlord')
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


    def __repr__(self):
      return f"User('{self.id}','{self.username}', '{self.email}','{self.date_created}' )"

class Tenant(db.model):
     id = db.Column(db.Integer, primary_key=True)
     tenantname = db.Column(db.String(255), unique=True, nullable=False)
     tenantemail = db.Column(db.String(255), unique=True, nullable=True)
     housenumber = db.Column(db.String(255), unique=True, nullable=False)
     Property_id = db.Column(db.Integer, db.ForeignKey('Property.id'))
     date_created = db.Column(db.DateTime(timezone=True), default=func.now())

     def __repr__(self):
      return f"User('{self.id}','{self.tenantname}', '{self.tenantemail}','{self.date_created}' )"


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/landlord_login', methods=['POST','GET'] )   #The main route takes the landlord to the dashoard after procesing the login credentials
def landlord_login():
   if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
      

        user = User.query.filter_by(username=username).first()
        # print(f"Logging in user: {username}")
        # print(f"User found: {user}")
        # if user:
        #     print(f"Stored hash: {user.password}")
        #     print(f"Entered password: {password}")
       
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            print("logged in successfully!",)
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

@app.route('/addTenant')
def addTenant():
   if request.method == 'POST':
      #user = User.query.get(session('user_id'))

      tenantname = request.form.get('tenantname')
      tenantemail = request.form.get('tenantemail')
      housenumber = request.form.get('housenumber')
      property_id = request.form.get('property')

      n_tenant = Tenant(tenantname=tenantname, tenantemail=tenantemail, housenumber=housenumber ,property_id=property_id)
      db.session.add(n_tenant)
      db.session.commit()
      flash("Tenant added successfuly")
      return redirect(url_for(''))
    
   return render_template('landlord_dashboard.html')

@app.route('/Tenant/edit/<int:id>', methods=['GET','POST'])
def editTenant():
    ten = Tenant.query.get_or_404(id)

    if request.method == 'POST':
       ten.tenantname = request.form.get('tenantname')
       ten.tenanthouse = request.form.get('tenanthouse')
       ten.tenantemail = request.form.get('tenatemail')
       db.session.commit()
       flash("Tenant updated.")
       return redirect(url_for(''))
       
    return render_template('')

@app.route('/Tenant/delete/<int:id>', methods=['POST'])
def delete_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    db.session.delete(tenant)
    db.session.commit()
    flash("Tenant deleted.")
    return redirect(url_for('views_tenats'))

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

@app.route('/changepassword' , methods=['GET','POST'])
def changepassword():
   if request.method == 'POST':
      email = email.form.get('email')
      password = password.form.get('password')
      if email == '' or password == '':
         flash("please fill the field!")
         return redirect(url_for('changepassword'))
      else:
         user = User.query.filter_by(email=email).first()
         db.session.delete(user)
         db.session.commit()
         if user:
            n_password = generate_password_hash(request.form.get('password'))
            ch_password = User(password = n_password)
            db.session.add(ch_password)
            db.session.commit()
            flash('password changed successfully', 'Success')
            return redirect(url_for('changepassword'))
         else:
            flash('Invalid email')
            return redirect(url_for('changepassword'))
   else:
      return render_template('landlord_forgot_password.html')


@app.route('/landlord_logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('landlord_login'))

if (__name__) == ('__main__'):
  # with app.app_context():
  #     db.create_all()
  app.run(debug=True)
