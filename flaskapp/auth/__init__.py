from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint
from flaskapp.forms import RegisterForm, LoginForm, confirmForm, Updateform, ForgetPasswordForm
from flask_login import login_user, logout_user
from flaskapp.models import User
from flaskapp.helpers.emailHandler import sendMail
from flaskapp.helpers.tokenHandler import *
from datetime import timedelta

auth = Blueprint("auth", __name__, 
                template_folder="templates",
                static_folder="static")

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if (form.validate_on_submit()):
        u = User.select().where(User.email == form.email.data).first()
        user = User()
        user.email = form.email.data
        user.fname = form.fname.data
        user.lname = form.lname.data
        user.confirmed = False
        user.set_password(form.password.data)
        user.phoneno = form.phoneno.data
        user.account_type = form.account_type.data
        user.save()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for("auth.confirm_email", token = token, _external = True)
        msg = f"Please confirm your email by using the link below\n {confirm_url}"
        sendMail(msg, user.email)
        flash("A confirmation email has been sent to you, please confirm your email")
        return redirect(url_for("auth.confirm_request"))
    return render_template("auth/register.html", form=form)

@auth.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if(form.validate_on_submit()):
        user: User = User.select().where(User.email == form.email.data).first()
        if (user and user.check_password(form.password.data)):
            print("User is authenticated")
            if (user.confirmed != True):
                return redirect (url_for("auth.confirm_request"))
            
            print("User is confirmed")
            session["email"] = form.email.data
            session["name"] = f"{user.fname} {user.lname}"
            session["id"] = user.id
            session["profile_pic"] = user.profile_pic
            login_user(user, form.remember_me.data)
            flash(f"Welcome {user.fname} {user.lname}", category="success")
            if "User" in user.account_type:
                print("Going to user dashboard")
                return redirect(url_for("user.dashboard"))
            elif "Driver" in user.account_type:
                print("Going to driver dashboard")
                return redirect(url_for("driver.dashboard"))
            else:
                print("Unknown Role")
                return redirect("/")
            #return redirect(request.args.get("next") or url_for("user.dashboard"))
        else:
            flash("User Not found", category="danger")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("name", None)
    session.pop("id", None)
    session.pop("profile_pic", None)
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/confirm_request")
def confirm_request():
     return render_template("auth/confirm_url.html")

@auth.route("/confirm_email/<string:token>")
def confirm_email(token):
    email = confirm_token(token)
    if (email):
        user: User = User.select().where(User.email == email).first()
        user.confirmed = True
        user.save()
        return redirect(url_for("auth.login"))
        flash("Hello")
    return redirect(url_for("auth.resend_confirmation"))

@auth.route("/resend_confirmation", methods=["GET","POST"])
def resend_confirmation():
    form = confirmForm()
    if(form.validate_on_submit()):
        user: User = User.select().where(User.email == form.email.data).first()
        if(user):
            token = generate_confirmation_token(user.email)
            confirm_url = url_for("auth.confirm_email", token = token, _external = True)
            subject = f"Please confirm your email with the link below\n {confirm_url}"
            sendMail(subject, user.email)
            flash('A new confirmation email has been sent.', 'success')
            return redirect(url_for("auth.confirm_request"))
        else:
            return redirect("/404")
    return render_template("auth/resend_confirm.html", form = form)


@auth.route("/forget_password", methods = ["GET", "POST"])
def forget_password():
    form = confirmForm()
    if(form.validate_on_submit()):
        user: User = User.select().where(User.email == form.email.data).first()
        if(user):
            token = generate_confirmation_token(user.email)
            password_url = url_for("auth.confirm_password", token = token, _external = True)
            msg = f"Please update your password using the link below\n {password_url}"
            sendMail(msg, user.email)
            flash('A new confirmation email has been sent.', 'success')
            return redirect(url_for("auth.confirm_request"))
        else:
            return redirect("/404")
    return render_template("auth/forget_password.html", form = form)

@auth.route("/confirm_password/<string:token>", methods = ["GET","POST"])
def confirm_password(token):
    email = confirm_token(token)
    flash(f"Password updated accepted {email}")
    form = ForgetPasswordForm()
    form.email.data = email
    if(form.validate_on_submit()):
        user: User = User.select().where(User.email == form.email.data).first()
        if user:
            user.set_password(form.password.data)
            user.save()
            flash("Your password has been updated", "success")
            return redirect(url_for("auth.login"))
        else:
            return redirect("/404")
    return render_template("auth/confirm_password.html", form = form)