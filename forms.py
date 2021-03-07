from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, SelectField, RadioField, widgets, FieldList, SelectMultipleField, FileField, DecimalField, PasswordField, BooleanField, MultipleFileField, DateTimeField, IntegerField

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')

	submit = SubmitField('Login')