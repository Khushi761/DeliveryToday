from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint, abort
from flaskapp.models import User
from flask_login import login_required 
from flaskapp.forms import RegisterForm, LoginForm, Updateform, PackageForm, ProfilePicForm
from flaskapp.forms import RegisterForm, LoginForm, Updateform
from flaskapp.helpers.permissionHandler import permission_required
from flaskapp.models import Package, get_packages, User, UserPackage
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import imghdr
import hashlib

driver = Blueprint("driver", __name__, 
                template_folder="templates",
                static_folder="static")


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format !="jpeg" else "jpg")

@driver.route("/driver/dashboard")
@login_required
def dashboard():
    permission_required(["Driver"])
    packages = get_packages("Pending")
    return render_template("driver/dashboard.html", packages = packages)

@driver.route("/driver/profile")
@login_required
def profile():
    permission_required(["Driver"])
    id = session["id"]
    driver = User.select().where(User.id == id).first()
    if driver:
        return render_template('driver/profile.html', driver = driver)
    return redirect ("/404")

@driver.route("/driver/profile_update", methods=["GET","POST"])
@login_required
def profile_update():
    permission_required("Driver")
    form = Updateform()
    email = session["email"]
    driver = User.select().where(User.email == email).first()

    if driver:
        if(form.validate_on_submit()): #shows that the form is submitted
            driver.email = form.email.data
            driver.fname = form.fname.data
            driver.lname = form.lname.data
            driver.phoneno = form.phoneno.data
            driver.save()
            session["name"] = f"{driver.fname} {driver.lname}"
            flash("Your account has been updated", "success")
            return redirect(url_for("driver.profile"))
        else:
            form.email.data = email
            form.fname.data = driver.fname
            form.lname.data = driver.lname
            form.phoneno.data = driver.phoneno
    else:
        return redirect("/404")
    return render_template("driver/formupdate.html", form = form)

@driver.route("/driver/profile_pic", methods=["GET","POST"])
@login_required
def profile_pic():
    permission_required("Driver")
    email = session["email"]
    driver = User.select().where(User.email == email).first()
    if request.method == "POST":
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config["UPLOAD_EXTENSIONS"] or file_ext != validate_image(uploaded_file.stream):
                abort(400)
            print(driver.id)
            filename = hashlib.sha224(int(driver.id).to_bytes(2, "big")).hexdigest() + file_ext
            uploaded_file.save(os.path.join(current_app.config["UPLOAD_PATH"], filename))
            driver.profile_pic = filename
            driver.save()
            session["profile_pic"] = filename
    return render_template("driver/profile_pic.html", driver=driver)

@driver.route("/driver/settings", methods=["GET","POST"]) 
@login_required
def settings():
    permission_required("Driver")
    return render_template("driver/settings.html")

#@driver.route("/driver/packages")
#@login_required
#def packages():
    #permission_required(["Driver"])
    #email = session["email"]
    #driver: User = User.select().where(User.email == email).first()

    #return render_template("driver/packages.html",  packages = driver.packages)

@driver.route("/driver/add_packages", methods=["GET", "POST"])
@login_required
def add_packages():
    permission_required(["Driver"])
    email = session["email"]
    driver = User.select().where(User.email == email).first()
    form =  PackageForm()
    if(form.validate_on_submit()):
        p = Package()
        p.driver = driver
        p.amount = form.amount.data
        p.category = form.category.data
        p.weight = form.weight.data
        p.size = form.size.data
        p.pkgType = form.pkg_type.data
        p.pkgDes = form.pkgDes.data
        p.pkgSource = form.pkgSource.data
        p.decription = form.description.data
        p.status = "Pending"
        p.timestamp = datetime.now()
        p.save()
        return redirect(url_for("driver.packages"))
    return render_template("driver/add_package.html", form=form)

@driver.route("/driver/delete_package/<int:id>")
@login_required
def delete_package(id:int):
    permission_required(["Driver"])
    email = session["email"]
    driver = User.select().where(User.email == email).first()
    if driver:
        # Get the package
        p: Package = Package.select().where(Package.id == id).first()
        # Pass the package to the driver object to delete the userpackage link
        if p and p.status != "On-Pickup":
            flash(f"Package ID: {p.id} can't be deleted", "danger")
            return redirect(url_for("driver.delivery_queue"))
        if p:
            driver.delete_delivery_package(p)
            p.user.create_notification("Package Pickup", f"Your package has be rejected by {driver.fname} {driver.lname}")
            driver.create_notification("Package Rejection", f"You have rejected a package by {p.user.fname} {p.user.lname}")
            flash("Package deleted", "success")
        else:
            flash("Package not found", "danger")
    return redirect(url_for("driver.delivery_queue"))

@driver.route("/driver/edit_package/<int:id>", methods=["GET", "POST"])
@login_required
def edit_package(id: int):
    form = PackageForm()
    permission_required(["Driver"])
    email = session["email"]
    driver = User.select().where(User.email == email).first()
    p: Package = driver.packages.where(Package.id == id).first()

    if p and p.status != "Pending":
        flash(f"Package ID: {p.id} can't be edited", "danger")
        return redirect(url_for("driver.packages"))

    if driver and form.validate_on_submit():
        p.amount = form.amount.data
        p.category = form.category.data
        p.weight = form.weight.data
        p.size = form.size.data
        p.pkgType = form.pkg_type.data
        p.pkgSource = form.pkgSource.data
        p.pkgDes = form.pkgDes.data
        p.decription = form.description.data
        p.save()
        return redirect(url_for("driver.packages"))
    else:
        form.amount.data = p.amount
        form.category.data = p.category
        form.weight.data = p.weight
        form.size.data = p.size
        form.pkg_type.data = p.pkgType
        form.pkgSource.data = p.pkgSource
        form.pkgDes.data = p.pkgDes
        form.description.data = p.decription
    return render_template("driver/detailsupdate.html", form = form)

@driver.route("/driver/cal_package/<int:id>")
@login_required
def cal_package(id: int):
    permission_required(["Driver"])
    email = session["email"]
    driver = User.select().where(User.email == email).first()
    p: Package = Package.select().where(Package.id == id).first()   #telling the interpreter that p is an object of the type package

    if p:
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

@driver.route("/driver/get_profile_pic/<name>")
#@login_required
def get_profile_pic(name: str):
    print(name)
    return send_from_directory("static/images/profile_pics", name) #url_for("static", filename=f"images/profile_pics/{name}")

@driver.route("/driver/package_detail/<int:id>")
@login_required
def package_detail(id: int):
    permission_required(["Driver"])
    p: Package = Package.select().where(Package.id == id).first()
    #distance = p.get_distance()
    #price = round(p.calculate_price(distance), 2)

    return render_template("driver/package_detail.html", package = p)

@driver.route("/driver/package_view/<int:id>")
@login_required
def package_view(id: int):
    permission_required(["Driver"])
    p: Package = Package.select().where(Package.id == id).first()
    return render_template("driver/package_view.html", package = p)

@driver.route("/driver/accept_package/<int:id>")
@login_required
def accept_package(id: int):
    permission_required(["Driver"])
    p: Package = Package.select().where(Package.id == id and Package.status == "Pending").first()
    if p:
        driver_id = session["id"]
        driver: User = User.select().where(User.id == driver_id).first()
        user_package = UserPackage()
        user_package.driver = driver
        user_package.package = p
        user_package.save()
        p.status = "On-Pickup"
        p.save()
        p.user.create_notification("Package Pickup", f"Your package has be accepted by {driver.fname} {driver.lname}")
        # Send notification to user
        flash("Package have been added to your queue", "success")
    return redirect(url_for("driver.dashboard"))

@driver.route("/driver/reject_package/<int:id>")
@login_required
def reject_package(id:int):
    permission_required(["Driver"]) 
    p: Package = Package.select().where(Package.id == id and Package.status == "Pending").first()
    if p:
        flash("Package has been rejected", "danger")
    return redirect(url_for("driver.dashboard"))

@driver.route("/driver/delivery_queue/")
@login_required
def delivery_queue():
    permission_required(["Driver"])
    email = session["email"]
    driver: User = User.select().where(User.email == email).first()
    packages = driver.get_packages_to_deliver()
    return render_template("driver/delivery_queue.html", packages = packages)

@driver.route("/driver/notifications")
@login_required
def notifications():
    permission_required(["Driver"])
    email = session["email"]
    driver: User = User.select().where(User.email == email).first()
    notifications = []
    for n in driver.get_notifications():
        notifications.append((n.title, n.msg))
    driver.last_notification_read = datetime.utcnow()
    driver.save()
    return render_template("driver/notifications.html")

