from flask import Flask, render_template, flash, request, abort, session
from flask_login import LoginManager, login_required
from flaskapp.helpers.emailHandler import sendMail

import os
from datetime import timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "fb70e8bbff373494018bc43f82c0a979c1a25bf7d1cef4b932e207cb371040eb"
app.config["MAX_CONTENT_LENGHT"] = 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = [".jpeg", ".jpg", ".png"]
app.config["UPLOAD_PATH"] = os.path.join("flaskapp","static", "images", "profile_pics")

login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

@app.route("/")
@app.route("/home")
def index():
    return render_template("home.html", title="Home")

@app.errorhandler(404)
def not_found(e):
    print("404")
    return render_template("errors/404.html")

@app.errorhandler(403)
def forbidden(e):
    print("403")
    return render_template("errors/403.html")

@app.errorhandler(400)
def bad_request(e):
    print("400")
    return render_template("errors/400.html")

@app.errorhandler(500)
def server_error(e):     #e is error itself
    print("500")
    return render_template("errors/500.html")



def create_routes():
    ##### Routes ###
    from flaskapp.auth import auth
    from flaskapp.user import user
    from flaskapp.admin import admin
    from flaskapp.driver import driver
    from flaskapp.main import main
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(driver)
    app.register_blueprint(main)