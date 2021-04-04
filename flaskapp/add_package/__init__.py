from flask import render_template, session, current_app, flash, request, redirect, url_for, Blueprint

package = Blueprint("package", __name__, 
                template_folder="templates",
                static_folder="static")

@user.route('/package')
def add_package():
    return render_template("user/packages.html")