from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from .models import User

class LoginForm(FlaskForm):
    username    = StringField("Username", validators=[DataRequired(), Length(min=6,max=20)])
    password    = PasswordField("Password", validators=[DataRequired(), Length(min=6,max=20)])
    remember_me = BooleanField("Remember Me")
    submit      = SubmitField("Login")


