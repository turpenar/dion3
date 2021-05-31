from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField, HiddenField, BooleanField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('username', [DataRequired()])
    password = StringField('password', [DataRequired()])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')
    
    
class SignUpForm(FlaskForm):
    username = StringField('username', [DataRequired()])
    password = StringField('password', [DataRequired()])
    submit = SubmitField('Sign Up')