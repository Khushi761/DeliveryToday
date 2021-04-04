from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, BooleanField, IntegerField, PasswordField, SubmitField,DateField, DateTimeField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required
from wtforms.fields.html5 import DateTimeLocalField
from flaskapp.models import User

class RegisterForm(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired(), Length(min=2, max=20)])
    lname = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    phoneno = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=10)])
    account_type = SelectField("Account Type", choices=[("User","User"), ("Driver","Driver")])
    submit = SubmitField("Sign Up")

    def validate(self):
        initial_validation = super(RegisterForm, self).validate() #super, before running the code it runs the original validate function  this is an overriding function in general, without this line, none of the other things will be validated. You want to run your custom code, first cde should run, check if first validation is done bfore the user is told ikf the email is used or not
        if not initial_validation:
            return False
        #check if email is unique
        user = User.select().where(User.email == self.email.data).first()
        if user:
            self.email.errors.append("Email already exists")
            return False
        return True
        
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Rememeber Me")
    submit = SubmitField("Login")

class confirmForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(),Email()])
    submit = SubmitField("submit")

class ForgetPasswordForm(FlaskForm):
    password = PasswordField()
    email = StringField("Email", validators=[DataRequired(), Email()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

class Updateform(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    fname = StringField("First Name", validators=[DataRequired(), Length(min=2, max=20)])
    lname = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=20)])
    phoneno = StringField("Phone Number", validators=[DataRequired()])
    submit = SubmitField("Update account")

class PackageForm(FlaskForm):
    amount = IntegerField("Amount", validators = [DataRequired()])
    category = SelectField("Category", choices=[("Category","Category"), ("Electronics","Electronics"), ("Documents","Documents"), ("Heavy Delivery", "Heavy Delivery"), ("Grocery & food stuff", "Grocery & food stuff"), ("Furniture", "Furniture")])
    weight = IntegerField("Weight", validators = [DataRequired()])
    size = IntegerField("Size", validators = [DataRequired()])
    pkg_type = SelectField("Package Type", choices=[("None","None"), ("Flammable","Flammable"), ("Toxic","Toxic"), ("Corrosive","Corrosive"), ("Fragile","Fragile")])
    pkgSource = StringField("Package Source", validators = [DataRequired()])
    pkgDes = StringField("Package Destination", validators = [DataRequired()])
    description = TextAreaField("Description (Optional)", validators = [DataRequired()], render_kw = {"rows":5, "cols":5})
    pickup_date = StringField('Pickkup Date', validators=[DataRequired()])
    pickup_time = StringField("Pickup Time")
    submit = SubmitField("Submit")

class ProfilePicForm(FlaskForm):
    file = FileField("Profile Field")
    submit = SubmitField("Submit")