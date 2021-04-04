from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint, send_from_directory, abort
from flaskapp.models import User
from flask_login import login_required 
from flaskapp.forms import RegisterForm, LoginForm, Updateform, PackageForm, ProfilePicForm
from flaskapp.helpers.permissionHandler import permission_required
from flaskapp.models import Package, get_packages, User, UserPackage
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil import parser
import json
import os
import imghdr
import hashlib

user = Blueprint("user", __name__, 
                template_folder="templates",
                static_folder="static")

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format !="jpeg" else "jpg")

@user.route('/user/dashboard')
def dashboard():
    #return "Hello"
    permission_required(["User"])
    id = session["id"]
    print(id)
    packages = get_packages("OnRoute")
    print("Got packages")
    user = User.select().where(User.id == id).first()
    print("Got users")
    if user:
        print("Use got")
        monthly_spendings = 10 #user.get_monthly_spendings()
        print("Spending monthly")
        yearly_spendings = 10 #user.get_yearly_spendings()    
        print("Spending yearly")
        total_deliveries = 10# user.get_total_deliveries()
        print("Total Deliveries")
        return render_template("user/dashboard.html", monthly_spendings = monthly_spendings, yearly_spendings = yearly_spendings, total_deliveries = total_deliveries, packages = packages)
    return abort(404)

@user.route("/user/profile")
@login_required
def profile():
    permission_required(["User"])
    id = session["id"]
    user = User.select().where(User.id == id).first()
    if user:
        return render_template('user/profile.html', user = user)
    return abort(404)

@user.route("/user/profile_update", methods=["GET","POST"])
@login_required
def profile_update():
    permission_required(["User"])
    form = Updateform()
    email = session["email"]
    user = User.select().where(User.email == email).first()

    if user:
        if(form.validate_on_submit()): #shows that the form is submitted
            user.email = form.email.data
            user.fname = form.fname.data
            user.lname = form.lname.data
            user.phoneno = form.phoneno.data
            user.save()
            session["name"] = f"{user.fname} {user.lname}"
            flash("Your account has been updated", "success")
            return redirect(url_for("user.profile"))
        else:
            form.email.data = email
            form.fname.data = user.fname
            form.lname.data = user.lname
            form.phoneno.data = user.phoneno
    else:
        return redirectR("/404")
    return render_template("user/formupdate.html", form = form)

@user.route("/user/profile_pic", methods=["GET","POST"])
@login_required
def profile_pic():
    permission_required(["User"])
    email = session["email"]
    user = User.select().where(User.email == email).first()
    if request.method == "POST":
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"] or file_ext != validate_image(uploaded_file.stream):
                abort(400)
            print(user.id)
            filename = hashlib.sha224(int(user.id).to_bytes(2, "big")).hexdigest() + file_ext
            uploaded_file.save(os.path.join(current_app.config["UPLOAD_PATH"], filename))
            user.profile_pic = filename
            user.save()
            session["profile_pic"] = filename
    return render_template("user/profile_pic.html", user=user)

@user.route("/user/settings", methods=["GET","POST"]) 
@login_required
def settings():
    permission_required(["User"])
    return render_template("user/settings.html")

@user.route("/user/packages")
@login_required
def packages():
    permission_required(["User"])
    email = session["email"]
    user: User = User.select().where(User.email == email).first()
    
    return render_template("user/packages.html",  packages = user.packages.order_by(Package.id.desc()))

@user.route("/user/add_packages", methods=["GET", "POST"])
@login_required
def add_packages():
    permission_required(["User"])
    email = session["email"]
    user = User.select().where(User.email == email).first()
    form =  PackageForm()
    if(form.validate_on_submit()):
        p = Package()
        p.user = user
        p.amount = form.amount.data
        p.category = form.category.data
        p.weight = form.weight.data
        p.size = form.size.data
        p.pkgType = form.pkg_type.data
        p.pkgDes = form.pkgDes.data
        p.pkgSource = form.pkgSource.data
        p.description = form.description.data
        p.status = "Pending"
        p.timestamp = datetime.now()
        p.pickup_time = parser.parse(form.pickup_date.data + " " + form.pickup_time.data)
        p.get_pickup_address()
        p.get_drop_address()
        p.distance = p.get_distance()
        p.price = p.calculate_price(p.distance)
        p.save()
        return redirect(url_for("user.packages"))
    return render_template("user/add_package.html", form=form)

@user.route("/user/delete_package<int:id>")
@login_required
def delete_package(id:int):
    permission_required(["User"])
    email = session["email"]
    user = User.select().where(User.email == email).first()
    if user:
        p: Package = user.packages.where(Package.id == id).first()
        if p and p.status != "Pending":
            flash(f"Package ID: {p.id} can't be deleted", "danger")
            return redirect(url_for("user.packages"))
        if p:
            p.delete_instance()
            flash("Package deleted")
        else:
            flash("Package not found")
    return redirect(url_for("user.packages"))

@user.route("/user/edit_package/<int:id>", methods=["GET", "POST"])
@login_required
def edit_package(id: int):
    form = PackageForm()
    permission_required(["User"])
    email = session["email"]
    user = User.select().where(User.email == email).first()
    p: Package = user.packages.where(Package.id == id).first()

    if p and p.status != "Pending":
        flash(f"Package ID: {p.id} can't be edited", "danger")
        return redirect(url_for("user.packages"))

    if user and form.validate_on_submit():
        p.amount = form.amount.data
        p.category = form.category.data
        p.weight = form.weight.data
        p.size = form.size.data
        p.pkgType = form.pkg_type.data
        p.pkgSource = form.pkgSource.data
        p.pkgDes = form.pkgDes.data
        p.decription = form.description.data
        p.pickup_time = form.pickup_time.data
        p.get_pickup_address()
        p.get_drop_address()
        p.distance = p.get_distance()

        p.price = p.calculate_price(p.distance)
        p.save()
        return redirect(url_for("user.packages"))
    else:
        form.amount.data = p.amount
        form.category.data = p.category
        form.weight.data = p.weight
        form.size.data = p.size
        form.pkg_type.data = p.pkgType
        form.pkgSource.data = p.pkgSource
        form.pkgDes.data = p.pkgDes
        form.description.data = p.decription
    return render_template("user/detailsupdate.html", form = form)

@user.route("/user/cal_package/<int:id>", methods=["POST"])
@login_required
def cal_package(id: int):
    form = PackageForm()
    permission_required(["User"])
    email = session["email"]
    user = User.select().where(User.email == email).first()
    p: Package = user.packages.where(Package.id == id).first()

    if user and form.validate_on_submit():
        p.amount = form.amount.data
        p.category = form.category.data
        p.weight = form.weight.data
        p.size = form.size.data
        p.pkgType = form.pkg_type.data
        p.pkgSource = form.pkgSource.data
        p.pkgDes = form.pkgDes.data
        p.decription = form.description.data
        p.status = "pending"
        data = {
            "amount" : p.amount,
            "category" : p.category,
            "weight" : p.weight,
            "size" : p.weight,
            "pkgType" : p.pkgType,
            "pkgDes" : p.pkgDes,
            "description" : p.decription,
            "price" : f"£ {p.calculate_price(p.get_distance(), 0.02)}"
        }
        return json.dumps(data)
    return "",404

@user.route("/user/get_profile_pic/<name>")
#@login_required
def get_profile_pic(name: str):
    print(name)
    return send_from_directory("static/images/profile_pics", name) #url_for("static", filename=f"images/profile_pics/{name}")


@user.route("/user/package_detail/<int:id>")
@login_required
def package_detail(id:int):
    permission_required(["User"])
    p: Package = Package.select().where(Package.id == id).first()
    #distance = p.get_distance()
    #price = round(p.calculate_price(distance), 2)
    #print(price)
    return render_template("user/package_detail.html", package = p)

@user.route("/user/notifications")
@login_required
def notifications():
    permission_required(["User"])
    email = session["email"]
    user: User = User.select().where(User.email == email).first()
    notifications = []
    user.last_notification_read = datetime.utcnow()
    user.save()
    notifications = user.get_notifications()
    return render_template("user/notifications.html", notifications = notifications)
