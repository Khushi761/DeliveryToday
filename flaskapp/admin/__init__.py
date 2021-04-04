from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint
from flaskapp.models import User
from flask_login import login_required 
from flaskapp.forms import RegisterForm, LoginForm, Updateform

admin = Blueprint("admin", __name__, 
                template_folder="templates",
                static_folder="static")

@admin.route("/admin/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")