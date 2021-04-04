from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint, send_from_directory, abort
from flaskapp.models import User
from flask_login import login_required
from flaskapp.helpers.permissionHandler import permission_required

main = Blueprint("main", __name__, 
                template_folder="templates",
                static_folder="static")

@main.route("/notifications_count")
@login_required
def notification_count():
    email = session["email"]
    user: User = User.select().where(User.email == email).first()
    return str(user.new_notifications_count())