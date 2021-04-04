from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flaskapp.app import login_manager      #database = eaiser to load 1 file app.db
import requests
from math import *
from datetime import datetime
from flaskapp.helpers.postcodeHandler import get_address

url = "https://postcodes.io/postcodes"    #url to get all the postcodes, calling an API, app on the internet where we make post request and give it buunch of postcodes

EARTH_RADIUS_IN_MILES = 3958.761


#peewee - same code can be used for different databases
@login_manager.user_loader
def load_user(id):
    return User.select().where(User.id == id).first()
#when app; runs, if user = there no new db 
db = SqliteDatabase("app.db")  #file-based database that is good for development 

class BaseModel(Model):
    class Meta:
        database = db

def get_packages(status =""):
    if status == "":
        return [package for package in Package.select()]
    else:
        return [package for package in  Package.select().where(Package.status == status)]


class User(BaseModel, UserMixin):  #user mixin is from flask login
    fname = CharField()
    lname = CharField()
    password_hash = CharField()
    email = CharField()
    confirmed = BooleanField()
    phoneno = CharField()
    account_type = CharField()
    profile_pic = CharField(default="380x500.png")
    last_notification_read = DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_packages(self):
        packages = (Package.select().join(UserPackage).join(User).where(User.id == self.id))  #Join driver table and User table to the packages
        return packages

    def get_monthly_spendings(self):
        today = datetime.now()
        months = [4, 6, 9, 11]
        first_day = today.replace(day=1)

        if today.month in months:
            last_day = today.replace(day=30)
        elif today.month == 2:
            if today.year % 4 == 0:
                last_day = today.replace(day=29)
            else:
                last_day = today.replace(day=28)
        else:
            last_day = today.replace(day=31)
        
        packages = self.packages.where((Package.timestamp >= first_day) & (Package.timestamp <= last_day))
        spending = 0 
        for p in packages:
            spending += p.calculate_price(p.get_distance())
        
        return round(spending, 2)

    def get_yearly_spendings(self):
        today = datetime.now()
        first_day = today.replace(month=1, day=1)
        last_day = today.replace(month=12, day=31)

        packages = self.packages.where((Package.timestamp >= first_day) & (Package.timestamp <= last_day))
        spending = 0 
        for p in packages:
            spending += p.calculate_price(p.get_distance())
        
        return round(spending, 2)
    
    def get_total_deliveries(self):
        deliveries = 0
        packages = self.packages
        for p in packages:
            deliveries += 1 

        return deliveries 

    def get_packages_to_deliver(self):
        if self.account_type == "Driver":
            return Package.select().join(UserPackage).where(UserPackage.driver == self).order_by(UserPackage.id.desc())
        return []
    
    def delete_delivery_package(self, package):
        # Pass a package instead of an package id
        # The package will be selected in the view,
        # so no need to selected from the database again
        if self.account_type == "Driver":
            p = UserPackage.select().where(UserPackage.package == package).first()
            if p:
                p.delete_instance()
                package.status = "Pending"
                package.save()

    def create_notification(self, title, msg):
        notification = Notification()
        notification.user = self
        notification.msg = msg
        notification.title = title
        notification.save()

    def new_notifications_count(self):
        last_time_read = self.last_notification_read or datetime(1990, 1, 1)
        return self.notifications.where(Notification.timestamp > last_time_read).count()

    def get_notifications(self):
        return self.notifications.order_by(Notification.id.desc()) 

class Package(BaseModel):
    user = ForeignKeyField(User, backref = "packages")
    amount = IntegerField()
    category = CharField()
    weight = IntegerField()
    size = IntegerField()
    pkgType = CharField()
    pkgSource = CharField()
    description = CharField()
    pkgDes = CharField()
    status = CharField() #Pending, In-Progress, Delievered, On-Pickup
    timestamp = DateTimeField()
    pickup_address = CharField()
    drop_address = CharField()
    distance = IntegerField()
    price = IntegerField()
    pickup_time = DateTimeField()


    def get_distance(self):  #pass the list of postcodes that user gives
        postcodes = {"postcodes":[self.pkgSource, self.pkgDes]} #dictionary created with field called 'postcodes' which is now referred to a postcodes, (postcodes entered by user)
        res = requests.post(url, data = postcodes).json() #{} dictionary [] list
        if len(res["result"]) < 2:     #if the postcodes the user enters are less than 2
            return None
        pkgSource = (res["result"][0]["result"]["latitude"], res["result"][0]["result"]["longitude"])  #go to result then 0 (frist value of what user enters))
        pkgDes = (res["result"][1]["result"]["latitude"], res["result"][1]["result"]["longitude"])
        lat_a = radians(pkgSource[0])
        lat_b = radians(pkgDes[0])
        long_diff = radians(pkgSource[1] - pkgDes[1])
        distance = (sin(lat_a) * sin(lat_b) + cos(lat_a) * cos(lat_b) * cos(long_diff) )
        return acos(distance) * EARTH_RADIUS_IN_MILES

    def get_pickup_address(self):
        self.pickup_address =  get_address(self.pkgSource)
    
    def get_drop_address(self):
        self.drop_address = get_address(self.pkgDes)
    
    def calculate_price(self, distance):
        pricePerMile = 0.02
        if self.pkgType == "fragile":
            pricePerMile += 0.05
        elif self.pkgType == "flammable":
            pricePerMile += 0.1
        elif self.pkgType == "toxic":
            pricePerMile += 0.09
        elif self.pkgType == "corrosive":
            pricePerMile += 0.07
        
        price = pricePerMile * distance * self.weight * self.amount
        return price

class Notification(BaseModel):
    user = ForeignKeyField(User, backref="notifications")
    timestamp = DateTimeField(default=datetime.utcnow)
    title = CharField()
    msg = CharField()

class UserPackage(BaseModel):
    driver = ForeignKeyField(User, backref="deliveries")
    package = ForeignKeyField(Package, backref="driver")

def create_tables():
    db.create_tables([User, Package, UserPackage, Notification], safe=True)
    
create_tables()