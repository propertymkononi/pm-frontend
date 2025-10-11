"""This is the code for Property Mkononi backend
-----------------------------------------------
The imported packages assist in app functionality and intergration with other languages

The SQlalchemy package handles user tables and database query
"""

from flask import Flask, render_template, request, redirect, session,  url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.sql import func
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os



app = Flask(__name__)

#configuring the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:propertymkononi2025@localhost:5432/propertymdb' #"sqlite:///propertym" (This is the previous database)  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app, db)
#db.init_app(app)

UPLOAD_FOLDER = os.path.join(os.getcwd())
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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
     propertytype = db.Column(db.String(255), nullable=True)
     Inspection_frequency = db.Column(db.String(255), nullable=True)
     landmark = db.Column(db.String(255), nullable=True)
     Units = db.Column(db.Integer, nullable=False)
     Location = db.Column(db.String(255),  nullable=True)
     penalty = db.Column(db.String(255), nullable=True)
     unit_types = db.Column(db.String(255), nullable=True)
     service_charge = db.Column(db.String(255), nullable=True)
     floors = db.Column(db.String(255), nullable=True)
     ownership_document = db.Column(db.String(255))
     property_photo = db.Column(db.String(255))
     agreement_document = db.Column(db.String(255))
     rent_collection_method = db.Column(db.String(255), nullable=False)
     property_features = db.Column(db.String(255),  nullable=False)
     caretaker = db.Column(db.String(255),  nullable=False)
     caretaker_id = db.Column(db.String(255), nullable=False)
     security_name = db.Column(db.String(255), nullable=False)
     security_buss_no = db.Column(db.String(255),  nullable=False)
     tenants = db.relationship('Tenant', backref='property', lazy=True)
     landlords = db.relationship("Landlord", secondary='landlord_property', back_populates='properties')

     date_created = db.Column(db.DateTime, default=datetime.utcnow)
   

     def __repr__(self):
      return f"Property('{self.id}','{self.propertyname}', '{self.Units}','{self.propertytype}',{self.date_created}', '{self.tenants},'{self.landlords}', '{self.Location}', '{self.floors}', '{self.caretaker}', '{self.caretaker_id}', '{self.security_name}', '{self.security_buss_no}' )"
   
     def to_dict(self):
        return {
            'id': self.id,
            'propertyName': self.propertyname,
            'propertyType': self.propertytype,
            'Inspection_frequency': self.Inspection_frequency,
            'units': self.Units,
            'address': self.Location,
            'landmark' : self.landmark,
            'penalty': self.penalty,
            'unit_types': self.unit_types,
            'service_charge': self.service_charge,
            'floors': self.floors,
            'rent_collection_method': self.rent_collection_method,
            'property_features': self.property_features,
            'caretaker': self.caretaker,
            'caretaker_id': self.caretaker_id,
            'security_name': self.security_name,
            'security_buss_no': self.security_buss_no,
            'ownershipDocument' : getattr(self, 'ownership_document', None),
            'propertyPhoto' : getattr(self, 'property_photo', None),
            'agreementDocument' : getattr(self, 'agreement_document', None),
            'tenants': [tenant.tenantname for tenant in self.tenants],
            'landlords': [landlord.username for landlord in self.landlords]
        }


class Landlord(db.Model):
    __tablename__ = 'landlord'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    phonenumber = db.Column(db.String(255), nullable=False)
    national_photo = db.Column(db.String(255), nullable=True)
    national_id = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    KRA_pin = db.Column(db.String(255), unique=True, nullable=False)
    country = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))  # store photo as file path
    Payment_method = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=True)
    kra_document = db.Column(db.String(255))
   #  arrears = db.Column(db.String(255), nullable=True)
    reference_name = db.Column(db.String(255), nullable=True)
    reference_phone = db.Column(db.String(255), nullable=True)
    properties = db.relationship('Property', secondary='landlord_property', back_populates='landlords')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
      return f"Landlord('{self.id}','{self.username}', '{self.email}','{self.date_created}' )"

    def to_dict(self):
      return{
         "landlordFullName": self.username,
         "phoneNumber" :self.phonenumber,
         "nationalIdentification": self.national_id,
         "kraPin": self.KRA_pin,
         "nationality": self.country,
         "preferredBillingMethod": getattr(self, 'Payment_method', None),
         "emailAddress": self.email,
         "referenceName": getattr(self, 'reference_name', None),
         "referenceContact": getattr(self, 'reference_phone', None),
         "date_created": self.date_created.isoformat() if self.date_created else None,
         "profilePicture": getattr(self, 'profile_picture', None),
         "nationalCard": getattr(self, 'national_photo', None),
         "kraDocument": getattr(self, 'kra_document', None),
         "ownershipDocument": getattr(self, 'ownership_document', None)
      }

class Tenant(db.Model):
     __tablename__ = 'Tenant'
     id = db.Column(db.Integer, primary_key=True)
     tenantname = db.Column(db.String(255), nullable=False)
     tenantemail = db.Column(db.String(255), nullable=True)
     housenumber = db.Column(db.String(255), nullable=True)
     phonenumber = db.Column(db.String(255), nullable=False)
     identification_number = db.Column(db.String(255), nullable=True)
     family_size =   db.Column(db.Integer, nullable=True)
     children =  db.Column(db.String(255), nullable=True)
     payment_method = db.Column(db.String(255), nullable=True)
     housemanager_name =  db.Column(db.String(255), nullable=True)
     housemanager_ID =  db.Column(db.String(255), nullable=True)
     nationality = db.Column(db.String(255), nullable=True)
     reference_name =  db.Column(db.String(255), nullable=False)
     reference_phone =  db.Column(db.String(255), nullable=False)
     profile_picture = db.Column(db.String(255), nullable=True)
     rent = db.Column(db.String(255), nullable=True)
     deposit = db.Column(db.String(255), nullable=True)
     bedrooms = db.Column(db.String(255), nullable=True)
     rent_agreement_doc = db.Column(db.String(255), nullable=True)
     property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=True)
     date_created = db.Column(db.DateTime, default=datetime.utcnow)

     def __repr__(self):
      return f"Tenant('{self.id}','{self.tenantname}', '{self.tenantemail}','{self.date_created}','{self.phonenumber}', '{self.housenumber}' )"
  
     def to_dict(self):
         return {
             "tenantFullName": self.tenantname,
             "emailAddress": self.tenantemail,
             "houseNumber": self.housenumber,
             "phoneNumber": self.phonenumber,
             "nationalIdentification": self.identification_number,
             "householdSize": self.family_size,
             "householdMinors": self.children,
             "preferredPaymentMethod": self.payment_method,
             "housemanager_name": self.housemanager_name,
             "housemanager_ID": self.housemanager_ID,
             "nationality": self.nationality,
             "reference_name": self.reference_name,
             "reference_phone": self.reference_phone,
             "profilePicture": getattr(self, 'profile_picture', None),
             "rent": getattr(self, 'rent', None),
             "deposit": getattr(self, 'deposit', None),
             "roomSize": getattr(self, 'bedrooms', None),
             "rentAgreementDoc": getattr(self, 'rent_agreement_doc', None)
         }
     
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
 
    def __repr__(self):
      return f"Admin('{self.id}','{self.username}' )"
    
landlord_property = db.Table('landlord_property',
    db.Column('landlord_id', db.Integer, db.ForeignKey('landlord.id', name='fk_landlord_property_landlord'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id', name='fk_landlord_property_property'), primary_key=True)
)


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
      #   print(f"Landlord found: {landlord}")
      #   if landlord:
      #        print(f"Stored hash: {landlord.password}")     
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
         #print(users) 
         db.session.commit()
         flash("Registered successfully!")
         return redirect(url_for('landlord_login'))
         
      
   return render_template('landlord_signup.html')

@app.route('/addTenant', methods=['POST','GET'])
def addTenant():
   if request.method == 'POST':
      properties = Property.query.all()
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
        lease_end = datetime.strptime(request.form.get('lease_end'), '%Y-%m-%d'),
        Property_id = request.form.get('property_id')
      )
      db.session.add(n_tenant)
      db.session.commit()
      flash("Tenant added successfuly")
      print(n_tenant)
      return redirect(url_for('tenants'))
   return render_template('tenants.html',properties=properties)

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
    return redirect(url_for('views_tenants'))

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
  properties = Property.query.all()
  tenants = Tenant.query.all()
  return render_template('tenants.html', properties=properties, tenants=tenants)

@app.route('/properties')
def properties():
   tenants = Tenant.query.all()
   properties = Property.query.all()
   return render_template('properties.html', properties=properties, tenants=tenants)

@app.route('/addproperty', methods=['GET','POST'])
def addproperty():
   if 'landlord_id' not in session:
    return redirect(url_for('landlord_login'))
   
   landlord = Landlord.query.get(session.get('landlord_id'))
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
       landlords = [landlord]
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

def create_admin():
    admin = Admin.query.first()
    if not admin:
        username = 'PMadmin2'
        password = 'PMadmin2'
        hashed_password = generate_password_hash(password)
        new_admin = Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        print("Admin created successfully")
        #print(new_admin)
    else:
        print("Admin already exists")
        all_admins = Admin.query.all()
        print(all_admins)


@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
   if request.method == 'POST':
      
     admin = Admin.query.filter_by(username=request.form.get('username')).first()
     if admin and check_password_hash(admin.password, request.form.get('password')):
       session['admin_id'] = admin.id
       session['admin_name'] = admin.username
       print("logged in successfully!")
       print(admin)
       flash("logged in successfully!")
       return redirect(url_for('admin_dashboard'))
     else:
      flash("Inavalid username or password. Please try again")
      return redirect(url_for('admin_login'))
   return render_template('admin_login.html')
      
@app.route('/admin_dashboard')
def admin_dashboard():
   # if 'admin_id' not in session:
   #  return redirect(url_for('admin_login'))
    landlords = Landlord.query.all()
    tenants = Tenant.query.all()
    properties = Property.query.all()
   #  print(properties)
   #  print(landlords)
   #  print(tenants)
    return render_template('admin_dashboard.html', landlords=landlords, tenants=tenants, properties=properties)

@app.route('/addlandlord', methods=['GET', 'POST'])
def addlandlord():
   #  if 'admin_id' not in session:
   #      return redirect(url_for('admin_login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        national_id = request.form.get('national_id')
        national_photo = request.files.get('national_photo')
        password = generate_password_hash(request.form.get('password'))
        profile_picture = request.files.get('profile_picture')
        KRA_pin = request.form.get('KRA_pin')
        kra_document = request.files.get('kra_document')
        country = request.form.get('country')
        Payment_method = request.form.get('Payment_method')
        reference_name = request.form.get('reference_name')
        reference_phone = request.form.get('reference_phone')
        user = Landlord.query.filter_by(username=username).first()

        national_photo_filename = None
        profile_filename = None
        kra_filename = None

        if national_photo:
            national_photo_filename = secure_filename(national_photo.filename)
            national_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], national_photo_filename))

        if kra_document:
            kra_filename = secure_filename(kra_document.filename)
            kra_document.save(os.path.join(app.config['UPLOAD_FOLDER'], kra_filename))

        if profile_picture:
            profile_filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_filename))

        if user:
           return render_template('landlord_login.html', error="User already exists")

        new_landlord = Landlord(username=username, email=email, national_photo=national_photo_filename, password=password, phonenumber=phonenumber, national_id=national_id, profile_picture=profile_filename, kra_document=kra_filename, KRA_pin=KRA_pin, country=country, Payment_method=Payment_method, reference_name=reference_name, reference_phone=reference_phone)

        db.session.add(new_landlord)
        db.session.commit()
        flash('Landlord added successfully!')
        return redirect(url_for('admin_landlords'))
    return render_template('admin_landlords.html')

def notify_admin(email):
    msg = Message('ALERT: Suspicious Password Reset Attempt',
                  sender='your_admin_email@example.com',
                  recipients=['admin_notify@example.com'])
    msg.body = f"There have been multiple failed password reset attempts using this email: {email}"
    mail.send(msg)

@app.route('/admin_landlords')
def admin_landlords():
   landlords = Landlord.query.all()
   if request.method == 'POST':
       # Handle form submission for landlord information
       username = request.form.get('username')
       email = request.form.get('email')
       Landlord.query.filter_by(id=landlord_id).update(dict(username=username, email=email))
       db.session.commit()
       flash("Landlord information updated successfully!")
   #  tenants = Tenant.query.all()
   #  properties = Property.query.all()
   return render_template('admin_landlords.html', landlords=landlords)

@app.route("/api/landlords/<int:landlord_id>")
def get_landlord(landlord_id):
    landlord = Landlord.query.get_or_404(landlord_id)
    return jsonify(landlord.to_dict())

@app.route('/admin_landlord/edit/<int:landlord_id>', methods=['POST'])
def edit_admin_landlord(landlord_id):
    landlord = Landlord.query.get_or_404(landlord_id)

    landlord.username = request.form.get('username', '').strip()
    landlord.email = request.form.get('email', '').strip()
    landlord.phonenumber = request.form.get('phonenumber', '').strip()
    landlord.national_id = request.form.get('national_id', '').strip()
    landlord.KRA_pin = request.form.get('KRA_pin', '').strip()
    landlord.country = request.form.get('country', '').strip()
    landlord.Payment_method = request.form.get('Payment_method', '').strip()
    landlord.reference_name = request.form.get('reference_name', '').strip()
    landlord.reference_phone = request.form.get('reference_phone', '').strip()
   #  landlord.physical_address = request.form.get('physical_address', '').strip()

    # FILES: save only if a new file was uploaded
    profile_file = request.files.get('profile_picture')
    if profile_file and profile_file.filename:
        fname = secure_filename(profile_file.filename)
        profile_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        landlord.profile_picture = fname

    national_file = request.files.get('national_photo')
    if national_file and national_file.filename:
        fname = secure_filename(national_file.filename)
        national_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        landlord.national_photo = fname

    kra_file = request.files.get('kra_document')
    if kra_file and kra_file.filename:
        fname = secure_filename(kra_file.filename)
        kra_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        landlord.kra_document = fname

    db.session.commit()
    flash('Landlord updated successfully!')
    return redirect(url_for('admin_landlords')) 

@app.route("/filter", methods=["GET"])
def filter_landlord():
    category = request.args.get("category")
    detail = request.args.get("detail")

    query = Landlord.query
    if category and detail:
        query = query.filter(getattr(Landlord, category) == detail)

    landlords = [l.as_dict() for l in query.all()]
    return jsonify(landlords)

@app.route('/admin_landlord/delete/<int:landlord_id>', methods=['POST'])
def delete_admin_landlord(landlord_id):
    landlords = Landlord.query.get_or_404(landlord_id)
    db.session.delete(landlords)
    db.session.commit()
    flash('Landlord deleted successfully!')
    return redirect(url_for('admin_landlords'))

@app.route('/admin_landlords_information', methods=['GET', 'POST'])
def admin_landlords_information():
   landlords = Landlord.query.all()
   properties = Property.query.all()
   # if request.method == 'POST':
   #     # Handle form submission for landlord information
   #     username = request.form.get('username')
   #     email = request.form.get('email')
   #     Landlord.query.filter_by(id=landlord_id).update(dict(username=username, email=email))
   #     db.session.commit()
   #     flash("Landlord information updated successfully!")
   return render_template('admin_landlords_information.html', landlords=landlords, properties=properties)

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
 
@app.route('/admin_properties_information')
def admin_properties_information():
   properties = Property.query.all()
   tenants = Tenant.query.all()
   return render_template('admin_properties_information.html',tenants=tenants, properties=properties)

@app.route('/admin_addProperty', methods=['GET','POST'])
def admin_addProperty():
   landlord_id = request.form.get('landlord_id')
   selected_landlord = Landlord.query.get(landlord_id)
   
   
   if request.method == 'POST':
     ownership_document_filename = None
     property_photo_filename = None
     agreement_document_filename = None
     
     ownership_document = request.files.get('ownership_document')
     property_photo = request.files.get('property_photo')
     agreement_document = request.files.get('agreement_document')

     if ownership_document:
         ownership_document_filename = secure_filename(ownership_document.filename)
         ownership_document.save(os.path.join(app.config['UPLOAD_FOLDER'], ownership_document_filename))

     if property_photo:
         property_photo_filename = secure_filename(property_photo.filename)
         property_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], property_photo_filename))

     if agreement_document:
         agreement_document_filename = secure_filename(agreement_document.filename)
         agreement_document.save(os.path.join(app.config['UPLOAD_FOLDER'], agreement_document_filename))

     property = Property(
       propertyname = request.form.get('propertyname'),
       propertytype = request.form.get('propertytype'),
       Units = int(request.form.get('Units',0)),
       property_features = request.form.get('property_features'),
       Inspection_frequency = request.form.get('Inspection_frequency'),
       rent_collection_method = request.form.get('rent_collection_method'),
       Location = request.form.get('Location'),
       landmark = request.form.get('landmark'),
       penalty = request.form.get('penalty'),
       unit_types = request.form.get('unit_types'),
       service_charge = request.form.get('service_charge'),
       floors = request.form.get('floors'),
       caretaker = request.form.get('caretaker'),
       caretaker_id = request.form.get('caretaker_id'),
       security_name = request.form.get('security_name'),
       security_buss_no = request.form.get('security_buss_no'),
       landlords = [selected_landlord] if selected_landlord else [],
       ownership_document = ownership_document_filename,
       property_photo = property_photo_filename,
       agreement_document = agreement_document_filename

    )
    
     db.session.add(property)
     db.session.commit()
     flash("Property added successfully")
     print(property)
     return redirect(url_for('admin_landlords_information'))
   return render_template('admin_landlords_information.html', landlord=landlord)

@app.route("/api/properties/<int:property_id>")
def get_property(property_id):
    property = Property.query.get_or_404(property_id)
    return jsonify(property.to_dict())

@app.route('/admin_property/edit/<int:property_id>', methods=['GET', 'POST'])
def admin_edit_property(property_id):
   property = Property.query.get_or_404(property_id)
   
   property.propertyname = request.form.get('propertyname','').strip()
   property.propertytype = request.form.get('propertytype','').strip()
   property.Units = request.form.get('Units','').strip()
   property.Location = request.form.get('Location','').strip()
   property.floors = request.form.get('floors','').strip()
   property.property_features = request.form.get('property_features','').strip()
   property.rent_collection_method = request.form.get('rent_collection_method','').strip()  
   property.caretaker = request.form.get('caretaker','').strip()
   property.caretaker_id = request.form.get('caretaker_id','').strip()
   property.security_name = request.form.get('security_name','').strip()
   property.security_buss_no = request.form.get('security_buss_no','').strip()
   property.Inspection_frequency = request.form.get('Inspection_frequency','').strip()
   property.landmark = request.form.get('landmark','').strip()
   property.unit_types = request.form.get('unit_types','').strip()
   property.service_charge = request.form.get('service_charge','').strip()
   property.penalty = request.form.get('penalty','').strip()
   
   #File system updates go here
   ownership_document = request.files.get('ownership_document')
   if ownership_document and ownership_document.filename:
       fname = secure_filename(ownership_document.filename)
       ownership_document.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
       property.ownership_document = fname

   property_photo = request.files.get('property_photo')
   if property_photo and property_photo.filename:
       fname = secure_filename(property_photo.filename)
       property_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
       property.property_photo = fname

   agreement_document = request.files.get('agreement_document')
   if agreement_document and agreement_document.filename:
       fname = secure_filename(agreement_document.filename)
       agreement_document.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
       property.agreement_document = fname

   db.session.commit()
   flash("Property updated successfully!")
   return redirect(url_for('admin_landlords'))
   
@app.route("/filter", methods=["GET"])
def filter_property():
    category = request.args.get("category")
    detail = request.args.get("detail")

    query = Property.query
    if category and detail:
        query = query.filter(getattr(Property, category) == detail)

    properties = [p.as_dict() for p in query.all()]
    return jsonify(properties)

@app.route('/admin_property/delete/<int:property_id>', methods=['POST'])
def delete_admin_property(property_id):
    property = Property.query.get_or_404(property_id)
    db.session.delete(property)
    db.session.commit()
    flash('Property deleted successfully!')
    return redirect(url_for('admin_landlords_information'))

@app.route('/admin_requests')
def admin_requests():
   return render_template('admin_requests.html')


@app.route('/admin_addTenants', methods=['GET','POST'])
def admin_addTenants(): 
   if request.method == 'POST':
       tenantname = request.form.get('tenantname')
       tenantemail = request.form.get('tenantemail')
       housenumber = request.form.get('housenumber')
       phonenumber = request.form.get('phonenumber')
       identification_number = request.form.get('identification_number')
       family_size = request.form.get('family_size')
       children = request.form.get('children')
       payment_method = request.form.get('payment_method')
       housemanager_name = request.form.get('housemanager_name')
       housemanager_ID = request.form.get('housemanager_ID')
       nationality = request.form.get('nationality')
       reference_name = request.form.get('reference_name')
       reference_phone = request.form.get('reference_phone')
       profile_picture = request.files.get('profile_picture')
       rent = request.form.get('rent')
       deposit = request.form.get('deposit')
       bedrooms = request.form.get('bedrooms')
       rent_agreement_doc = request.files.get('rent_agreement_doc')
       property_id = request.form.get('property_id')
       
       #Adding files to the database through filenames
       profile_picture_filename = None
       rent_agreement_doc_filename = None
       
       
       if profile_picture:
            profile_picture_filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_picture_filename))
            
       if rent_agreement_doc:
           rent_agreement_doc_filename = secure_filename(rent_agreement_doc.filename)
           rent_agreement_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], rent_agreement_doc_filename))
       
       if not property_id or not property_id.isdigit():
          flash("Please select a valid property.")

       property_id = int(property_id)
       
       
       new_tenant = Tenant(
           tenantname=tenantname,
           tenantemail=tenantemail,
           housenumber=housenumber,
           phonenumber=phonenumber,
           identification_number=identification_number,
           family_size=family_size,
           children=children,
           payment_method=payment_method,
           housemanager_name=housemanager_name,
           housemanager_ID=housemanager_ID,
           nationality=nationality,
           reference_name=reference_name,
           reference_phone=reference_phone,
           profile_picture=profile_picture_filename,
           rent=rent,
           deposit=deposit,
           bedrooms=bedrooms,
           rent_agreement_doc=rent_agreement_doc_filename,
           property_id=property_id
       )
        
       db.session.add(new_tenant)
       db.session.commit()
       flash("Tenant added successfully!")
       return redirect(url_for('admin_properties_information'))
   return render_template('admin_properties_information.html')

@app.route('/admin_tenants_info')
def admin_tenants_info():
   return render_template('admin_tenants_information.html')


@app.route("/filter", methods=["GET"])
def filter_tenant():
    category = request.args.get("category")
    detail = request.args.get("detail")

    query = Tenant.query
    if category and detail:
        query = query.filter(getattr(Tenant, category) == detail)

    tenants = [t.as_dict() for t in query.all()]
    return jsonify(tenants)


@app.route("/api/tenants/<int:tenant_id>")
def get_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    return jsonify(tenant.to_dict())


@app.route('/admin_tenant/edit/<int:tenant_id>', methods=["GET","POST"])
def admin_edit_tenant():
    if request.method == 'POST':
        tenant = Tenant.query.get_or_404(tenant_id)
        if tenant:
            tenant.tenantname = request.form.get('tenantname', '').strip()
            tenant.tenantemail = request.form.get('tenantemail', '').strip()
            tenant.housenumber = request.form.get('housenumber', '').strip()
            tenant.phonenumber = request.form.get('phonenumber', '').strip()
            tenant.identification_number = request.form.get('identification_number', '').strip()
            tenant.family_size = request.form.get('family_size', '').strip()
            tenant.children = request.form.get('children', '').strip()
            tenant.payment_method = request.form.get('payment_method', '').strip()
            tenant.housemanager_name = request.form.get('housemanager_name', '').strip()
            tenant.housemanager_ID = request.form.get('housemanager_ID', '').strip()
            tenant.nationality = request.form.get('nationality', '').strip()
            tenant.reference_name = request.form.get('reference_name', '').strip()
            tenant.reference_phone = request.form.get('reference_phone', '').strip()
            tenant.apartment_name = request.form.get('apartment_name', '').strip()
            tenant.rent = request.form.get('rent', '').strip()
            tenant.deposit = request.form.get('deposit', '').strip()
            tenant.bedrooms = request.form.get('bedrooms', '').strip()
            tenant.rent_agreement_doc = request.form.get('rent_agreement_doc', '').strip()

            profile_picture = request.files.get('profile_picture')
            if profile_picture and profile_picture.filename:
                fname = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                tenant.profile_picture = fname

            rent_agreement_doc = request.files.get('rent_agreement_doc')
            if rent_agreement_doc and rent_agreement_doc.filename:
                fname = secure_filename(rent_agreement_doc.filename)
                rent_agreement_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                tenant.rent_agreement_doc = fname

            db.session.commit()
            flash("Tenant updated successfully!")
        else:
            flash("Tenant not found.")
    return render_template('admin_properties_information.html', tenant=tenant)

@app.route('/admin_tenant/delete/<int:tenant_id>', methods=['POST'])
def delete_admin_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted successfully!')
    return redirect(url_for('admin_properties_information'))


@app.route('/admin_vendors')     
def admin_vendors():
   return render_template('admin_vendors.html')

# postponed for version 2

# @app.route('/admin_addvendors')     
# def admin_addvendors():
#    if request.method == 'POST':
#        vendor_name = request.form.get('vendor_name')
#        vendor_email = request.form.get('vendor_email')
#        vendor_phone = request.form.get('vendor_phone')
#        vendor_address = request.form.get('vendor_address')

#        new_vendor = Vendor(
#            vendor_name=vendor_name,
#            vendor_email=vendor_email,
#            vendor_phone=vendor_phone,
#            vendor_address=vendor_address
#        )

#        db.session.add(new_vendor)
#        db.session.commit()
#        flash("Vendor added successfully!")
#        return redirect(url_for('admin_vendors'))
#    return render_template('admin_vendors.html')


@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


"""Vendors section
-----------------------------------------------------------------------------"""
#postponed for version 2 
#@app.route('vendor_login', method=[GET,POST])

if (__name__) == ('__main__'):
   # with app.app_context():
   #     db.create_all()
       # create_admin()
       app.run(debug=True)
