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
from flask_mail import Mail, Message




app = Flask(__name__)

#configuring the database connection
app.config['SQLALCHEMY_DATABASE_URI'] =  "sqlite:///propertym" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)
mail = Mail(app)
  
#db.init_app(app)

app.config['SECRET_KEY'] = "fdfafhqwee73jbhzx" # Change to a long random string in production

#Email configurations 
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_admin_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'



#User models
class Property(db.Model):
     __tablename__ = 'property'
     id = db.Column(db.Integer, primary_key=True)
     propertyname = db.Column(db.String(255), unique=True, nullable=False)
     Units = db.Column(db.Integer, unique=True, nullable=False)
     Location = db.Column(db.String(255), unique=True, nullable=False)
     Land_no = db.Column(db.String(255), unique=True, nullable=True)
     caretaker = db.Column(db.String(255), unique=True, nullable=False)
     caretaker_id = db.Column(db.String(255), unique=True, nullable=False)
     security_name = db.Column(db.String(255), unique=True, nullable=False)
     security_buss_no = db.Column(db.String(255),  nullable=False)
     tenants = db.relationship('Tenant', backref='property', lazy=True)
     landlords = db.relationship("Landlord", secondary='landlord_property', back_populates='properties')

     date_created = db.Column(db.DateTime, default=datetime.utcnow)
   

     def __repr__(self):
      return f"Property('{self.id}','{self.propertyname}', '{self.Units}','{self.date_created}', '{self.tenants}' )"


class Landlord(db.Model):
    __tablename__ = 'landlord'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    #phonenumber = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    properties = db.relationship('Property', secondary='landlord_property', back_populates='landlords')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return f"Landlord('{self.id}','{self.username}', '{self.email}','{self.date_created}' )"

class Tenant(db.Model):
     __tablename__ = 'Tenant'
     id = db.Column(db.Integer, primary_key=True)
     tenantname = db.Column(db.String(255), unique=True, nullable=False)
     tenantemail = db.Column(db.String(255), unique=True, nullable=True)
     housenumber = db.Column(db.String(255), unique=True, nullable=True)
     phonenumber = db.Column(db.String(255), unique=True, nullable=False)
     #photo_filename  = db.Column(db.String(255))   store photo as file 
     identification_number = db.Column(db.String(255), unique=True, nullable=True)
     family_size =   db.Column(db.Integer, unique=True)
     children =  db.Column(db.String(255), unique=True, nullable=True)
     employment_status = db.Column(db.String(255), unique=True, nullable=True)
     housemanager_name =  db.Column(db.String(255), unique=True, nullable=True)
     housemanager_ID =  db.Column(db.String(255), unique=True, nullable=True)
     nationality = db.Column(db.String(255), unique=True, nullable=True)
     emergency_name1 =  db.Column(db.String(255), unique=True, nullable=False)
     emergency_contact1 =  db.Column(db.String(255), unique=True, nullable=False)
     emergency_name2 =  db.Column(db.String(255), unique=True, nullable=True)
     emergency_contact2 =  db.Column(db.String(255), unique=True, nullable=True)
     apartment_name = db.Column(db.String(255), unique=True, nullable=True)
     rent = db.Column(db.String(255), unique=True, nullable=True)
     deposit = db.Column(db.String(255), unique=True, nullable=True)
     bedrooms = db.Column(db.String(255), unique=True, nullable=True)
     house_condition = db.Column(db.String(255), unique=True, nullable=True)
     lease_start = db.Column(db.Date)
     lease_end = db.Column(db.Date)
     Property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)
     date_created = db.Column(db.DateTime, default=datetime.utcnow)

     def __repr__(self):
      return f"Tenant('{self.id}','{self.tenantname}', '{self.tenantemail}','{self.date_created}','{self.phonenumber}', '{self.housenumber}' )"
     
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
 
    def __repr__(self):
      return f"Admin('{self.id}','{self.username}' )"
    
landlord_property = db.Table('landlord_property',
    db.Column('landlord_id', db.Integer, db.ForeignKey('landlord.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'), primary_key=True)
)

#Insert the admin data only once 
# admin = Admin(username='Nelson123',password=generate_password_hash('Nelson123', 10))
# db.session.add(admin)
# db.session.commit()


@app.route('/')
def index():
  return render_template('index.html')

"""Landlord Section
---------------------------------------------------------------------------------------------------"""

@app.route('/landlord_login', methods=['POST','GET'] )   #The main route takes the landlord to the dashoard after procesing the login credentials
def landlord_login():
   if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
      
        landlord = Landlord.query.filter_by(username=username).first()
      #   print(f"Logging in user: {username}")
      #   print(f"User found: {user}")
      #   if user:
      #        print(f"Stored hash: {user.password}")     
      #        print(f"Entered password: {password}")
       
        if landlord and check_password_hash(landlord.password, password):
            session['landlord_id'] = landlord.id
            session['username'] = landlord.username
            print("logged in successfully!",)
            return redirect(url_for('landlord_dashboard'))
        else:     
            flash("Invalid username or password",'danger')
            print("failed login")
            users = Landlord.query.all()
            print(users) 
        return render_template('landlord_login.html', error='Invalid username or password')
   return render_template('landlord_login.html')
   

@app.route('/landlord_register', methods=['GET','POST'])
def landlord_register():
   #Confirm information of the user before registration
   if request.method == 'POST':
      username = request.form.get('username')
      email = request.form.get('email')
      password = generate_password_hash(request.form.get('password'))
      user = Landlord.query.filter_by(username=username).first()


      if user:
         return render_template('landlord_login.html', error="User already exists")
      else:
         new_user = Landlord(username=username , email=email, password=password)
         print(request.form.get('password'))
         db.session.add(new_user)
         users = Landlord.query.all()
         print(users) 
         db.session.commit()
         flash("Registered successfully!")
         return redirect(url_for('landlord_login'))
         
      
   return render_template('landlord_signup.html')

@app.route('/addTenant', methods=['POST','GET'])
def addTenant():
   if request.method == 'POST':
      #user = User.query.get(session('user_id'))
      n_tenant = Tenant(
        tenantname = request.form.get('tenantname'),
        tenantemail = request.form.get('tenantemail'),
        phonenumber = request.form.get('phonenumber'),
        housenumber = request.form.get('housenumber'),
        nationality = request.form.get('nationality'),
        identification_number = request.form.get('identification_number'),
        family_size = request.form.get('family_size'),
        children = request.form.get('children'),
        employment_status = request.form.get('employment_status'),
        housemanager_name = request.form.get('housemanager_name'),
        housemanager_ID = request.form.get('housemanager_ID'),
        emergency_name1 = request.form.get('emergency_name1'),
        emergency_contact1 = request.form.get('emergency_contact1'),
        emergency_name2 = request.form.get('emergency_name2'),
        emergency_contact2 = request.form.get('emergency_contact2'),
        apartment_name = request.form.get('apartment_name'),
        rent = request.form.get('rent'),
        deposit = request.form.get('deposit'),
        bedrooms = request.form.get('bedrooms'),
        house_condition = request.form.get('house_condition'),
        lease_start = datetime.strptime(request.form.get('lease_start'), '%Y-%m-%d'),
        lease_end = datetime.strptime(request.form.get('lease_end'), '%Y-%m-%d')
      )
      db.session.add(n_tenant)
      db.session.commit()
      flash("Tenant added successfuly")
      print(n_tenant)
      return redirect(url_for('tenants'))
   return render_template('tenants.html')

@app.route('/Tenant/edit/<int:Tenant_id>', methods=['GET','POST'])
def editTenant(Tenant_id):
    ten = Tenant.query.get_or_404(Tenant_id)

    if request.method == 'POST':
       ten.tenantname = request.form.get('tenantname')
       ten.tenanthouse = request.form.get('tenanthouse')
       ten.tenantemail = request.form.get('tenatemail')
       ten.phonenumber = request.form.get('phonenumber')
       ten.housenumber = request.form.get('housenumber')
       db.session.commit()
       flash("Tenant updated.")
       return redirect(url_for('tenants'))
    
    return render_template('tenants.html')

@app.route('/Tenant/delete/<int:Tenant_id>', methods=['POST'])
def delete_tenant(Tenant_id):
    tenant = Tenant.query.get_or_404(Tenant_id)
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
    if 'landlord_id' not in session:
       return redirect(url_for('landlord_login'))
    else:
       return render_template('landlord_dashboard.html')

@app.route('/tenants')
def tenants():
  return render_template('tenants.html')

@app.route('/properties')
def properties():
  return render_template('properties.html')

@app.route('/addproperty', methods=['GET','POST'])
def addproperty():
   if request.method == 'POST':
    property = Property(
       propertyname = request.form.get('propertyname'),
       Units = request.form.get('Units'),
       Location = request.form.get('Location'),
       Land_no = request.form.get('Land_no'),
       caretaker = request.form.get('caretaker'),
       caretaker_id = request.form.get('caretaker_id'),
       security_name = request.form.get('security_name'),
       security_buss_no = request.form.get('security_buss_no'),
       landlord_id=session['user_id']
    )
    db.session.add(property)
    db.session.commit()
    flash("Property added successfully")
    print(property)
    return redirect(url_for('properties'))
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

failed_attempts = {}

@app.route('/changepassword' , methods=['GET','POST'])
def changepassword():
   if request.method == 'POST':
      email = request.form.get('email')
      password = request.form.get('password')
      
      if email == '' or password == '':
         flash("please fill the field!")
         return redirect(url_for('changepassword'))
      else:
         user = Landlord.query.filter_by(email=email).first()
         if not user:
            failed_attempts[email] = failed_attempts.get(email, 0) + 1

            if failed_attempts[email] >= 3:
                flash('Too many failed attempts. Please Contact admin.', 'danger')
                notify_admin(email)
         else:
            n_password = generate_password_hash(request.form.get('password'))
            ch_password = Landlord(password = n_password)
            db.session.add(ch_password)
            db.session.commit()
            flash('password changed successfully', 'Success')
            return redirect(url_for('changepassword'))
   else:
      return render_template('landlord_forgot_password.html')


@app.route('/landlord_logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


"""Admin Section
----------------------------------------------------------------------------------"""

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
   if request.method == 'POST':
      
     admin = Admin.query.filter_by(username=request.form.get('username')).first()
     if admin and check_password_hash(admin.password, request.form.get('password')):
       session['admin_id'] = admin.id
       session['admin_name'] = admin.username
       print("logged in successfully!")
       flash("logged in successfully!")
       return redirect(url_for('admin_dashboard'))
     else:
      flash("Inavalid username or password")
      return redirect(url_for('admin_login'))
   
   return render_template('admin_login.html')
      
@app.route('/admin_dashboard')
def admin_dashboard():
   #  if 'admin_id' not in session:
   #      return redirect(url_for('admin_login'))
    landlords = Landlord.query.all()
    tenants = Tenant.query.all()
    properties = Property.query.all()
    
    return render_template('admin_dashboard.html', landlords=landlords, tenants=tenants, properties=properties)

@app.route('/addlandlord', methods=['GET', 'POST'])
def addlandlord():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = generate_password_hash(request.form('password'))
        new_landlord = Landlord(username=username, email=email, password=password)
        db.session.add(new_landlord)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_landlords.html')

def notify_admin(email):
    msg = Message('ALERT: Suspicious Password Reset Attempt',
                  sender='your_admin_email@example.com',
                  recipients=['admin_notify@example.com'])
    msg.body = f"There have been multiple failed password reset attempts using this email: {email}"
    mail.send(msg)

@app.route('/admin_landlords')
def admin_landlords():
   return render_template ('admin_landlords.html')

@app.route('/admin_landlords_info')
def admin_landlord_info():
   return render_template('admin_landlords_information.html')

@app.route('/admin_financials')
def admin_financials():
   return render_template('admin_financials.html')

@app.route('/admin_properties')
def admin_properties():
   landlord_id = request.args.get('landlord_id')
   if landlord_id:
      properties = Property.query.filter_by(landlord_id=landlord_id).all()
   else:
      properties = Property.query.all()
   return render_template('admin_properties.html', properties=properties)
 

@app.route('/admin_properties_info')
def admin_properties_info():
   return render_template('admin_properties_information.html')

@app.route('/admin_requests')
def admin_requests():
   return render_template('admin_requests.html')

@app.route('/admin_vendors')
def admin_vendors():
   return render_template('admin_vendors.html')

@app.route('/admin_tenants_info')
def admin_tenants_info():
   return render_template('admin_tenants_information.html')

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


"""Vendors section
-----------------------------------------------------------------------------"""


if (__name__) == ('__main__'):
      # with app.app_context():
      #     db.create_all()
  app.run(debug=True)
