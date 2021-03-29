from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from wtforms import StringField, SubmitField, PasswordField, BooleanField, RadioField, IntegerField, SelectField
from app import User, Person, Session, Sample, photos


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])

	submit = SubmitField('Login')

class RegisterForm(FlaskForm):
	name = StringField('Full name', validators=[Length(min=1, max=100)])
	username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username taken')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('An account with that email already exists')

class ContactForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired(), Length(min=1, max=100)])
    username = StringField('Requested username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    organization = StringField('Organization', validators=[DataRequired(), Length(min=1, max=100)])
    message = StringField('Message', validators=[Length(min=0, max=255)])

    submit = SubmitField('Request access')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with that email already exists')

class PwForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Change password')

class MemberForm(FlaskForm):
    header = ''
    name = StringField('Full name', validators=[Length(min=1, max=100)])
    role = RadioField('Member Role', coerce=int, default=1, choices=[(1,'Trainer'),(2,'Supervisor'), (3,'Trainer/Supervisor')])
    wise_nose_id = StringField('Wise Nose ID', validators=[Length(min=0, max=100)])
    photo = FileField('Member photo', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add member')


class DogForm(FlaskForm):
    header = ''
    name = StringField('Dog name', validators=[Length(min=1, max=100), DataRequired()])
    age = IntegerField('Dog age', validators=[NumberRange(min=0, max=20, message='Invalid length'), DataRequired()])
    wise_nose_id = StringField('Wise Nose ID', validators=[Length(min=0, max=100)])
    trainer = SelectField('Trainer name', validators=[DataRequired()], coerce=int)

    submit = SubmitField('Save dog')
