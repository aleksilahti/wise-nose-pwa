from flask import Flask, render_template, redirect, request, url_for, flash, session
import os
import email_validator

app = Flask("Wise Nose PWA")
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event, or_
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    print("Loaded user: " + str(user))
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)
    admin = db.Column(db.Boolean, default=False)

    sessions = db.relationship("Session", back_populates="user")
    samples = db.relationship("Sample", back_populates="user")

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    wise_nose_id = db.Column(db.String(128), nullable=True)
    role = db.Column(db.Integer, nullable=True)

    sessions = db.relationship("Session", back_populates="supervisor")
    dogs = db.relationship("Dog", back_populates="trainer")

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    wise_nose_id = db.Column(db.String(128), nullable=True)
    age = db.Column(db.Integer, nullable=True)

    sessions = db.relationship("Session", back_populates="dog")
    trainer = db.relationship("Person", back_populates="dogs")

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True)
    dog_id = db.Column(db.Integer, db.ForeignKey("dog.id", ondelete="SET NULL"), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(256), nullable=True)
    number_of_samples = db.Column(db.Integer, nullable=False)

    dog = db.relationship("Dog", back_populates="sessions")
    user = db.relationship("User", back_populates="sessions")
    samples = db.relationship("Sample", back_populates="session")
    supervisor = db.relationship("Person", back_populates="sessions")

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    is_correct = db.Column(db.Integer, nullable=False)  # Boolean value 1 or 0
    session_id = db.Column(db.Integer, db.ForeignKey("session.id", ondelete="SET NULL"), nullable=True)
    number_in_session = db.Column(db.Integer, nullable=True)
    dog_answer = db.Column(db.String(144), nullable=True)

    session = db.relationship("Session", back_populates="samples")
    user = db.relationship("User", back_populates="samples")

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), nullable=False)
    organization = db.Column(db.String(256), nullable=True)
    message = db.Column(db.String(256), nullable=True)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db.create_all()
from forms import * # because in form we import User... so we need them to be initialize before

# Create default user (admin). Remove from use on deployment!
try:
    if not User.query.filter_by(username="admin"):
        hashed_pw = bcrypt.generate_password_hash("admin").decode('utf-8')
        default_user = User(username='admin',email='test@email.com',pw_hash=hashed_pw,admin=True)
        db.session.add(default_user)
        db.session.commit()
except IntegrityError:
    pass

# Home / Base URL
@app.route("/")
@app.route("/home")
def home():
    print(current_user)
    return render_template('index.html')


# Login / Register
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.pw_hash, form.password.data):
            login_user(user)
            session["user"] = user.id
            return redirect(url_for('home'))
        else:
            flash('Login Failed. Please Check Username and Password', 'error')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash the password and insert the user in SQLAlchemy db
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, pw_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('access_requests'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have successfully logged yourself out.')
    return redirect(url_for('login'))

# Dog routes
@app.route("/dogs")
def dogs():
    if current_user.is_authenticated:
        dogs = Dog.query.all()
        return render_template('dogs.html', dogs=dogs)
    return redirect(url_for('login'))

@app.route("/dogs/<int:id>")
def dog(id):
    return "dog" + str(id)

@app.route("/dogs/add", methods=["GET", "POST"])
def add_dog():
    return "add person"

@app.route("/dogs/edit/<int:id>", methods=["GET", "POST"])
def edit_dog(id):
    return "edit person" + str(id)

@app.route("/dogs/delete/<int:id>", methods=["GET", "POST"])
def delete_dog(id):
    return "delete person" + str(id)

# Member routes
@app.route("/members")
def members():
    if current_user.is_authenticated:
        members = Person.query.all()
        return render_template('members.html', members=members)
    return redirect(url_for('login'))

@app.route("/members/<int:id>")
def member(id):
    return 'member' + str(id)

@app.route("/persons/add", methods=["GET", "POST"])
def add_member():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = MemberForm()
    if form.validate_on_submit():
        person = Person(name=form.name.data, role=form.role.data, wise_nose_id=form.wise_nose_id.data)
        db.session.add(person)
        db.session.commit()
        flash('Member created!', 'success')
        return redirect(url_for('members'))
    return render_template('newmember.html', form=form)

@app.route("/persons/edit/<int:id>", methods=["GET", "POST"])
def edit_member(id):
    return "edit person" + str(id)

@app.route("/members/delete/<int:id>", methods=["GET", "POST"])
def delete_member(id):
    if current_user.is_authenticated:
        if current_user.admin:
            try:
                person = Person.query.filter_by(id=id).first()
                db.session.delete(person)
                db.session.commit()
                flash('Member deleted', 'success')
                return redirect(url_for('members'))
            except:
                flash('Action failed', 'danger')
        flash('You lack the credentials to access this endpoint!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))


# Sample routes
@app.route("/samples")
def samples():
    return "people"

@app.route("/samples/<int:id>")
def sample(id):
    return "sample" + str(id)

@app.route("/samples/add", methods=["GET", "POST"])
def add_sample():
    return "add sample"

@app.route("/samples/edit/<int:id>", methods=["GET", "POST"])
def edit_sample(id):
    return "edit sample" + str(id)

@app.route("/samples/delete/<int:id>", methods=["GET", "POST"])
def delete_sample(id):
    return "delete sample" + str(id)


# Sessions routes, create/edit/delete, execute/modify/review (success?)
@app.route("/sessions")
def sessions():
    if current_user.is_authenticated:
        sessions = Session.query.all()
        return render_template('sessions_list.html', sessions=sessions)
    return redirect(url_for('login'))

@app.route("/sessions/<int:id>")
def session_info(id):
    return "create session"

@app.route("/sessions/create", methods=["GET", "POST"])
def create_session():
    return "create session"

@app.route("/sessions/edit/<int:id>", methods=["GET", "POST"])
def edit_session(id):
    return "delete session" + str(id)

@app.route("/sessions/delete/<int:id>", methods=["GET", "POST"])
def delete_session(id):
    return "delete session" + str(id)

@app.route("/sessions/execute/<int:id>", methods=["GET", "POST"])
def execute_session(id):
    return "execute session" + str(id)

@app.route("/sessions/modify/<int:id>", methods=["GET", "POST"])
def modify_session(id):
    if current_user.is_authenticated:
        form = SessionForm()
        session = Session.query.filter_by(id=id).first()
        form.dog.choices = [(g.id, g.name) for g in Dog.query.order_by('name')]
        form.trainer.choices = [(g.id, g.name) for g in Person.query.order_by('name').filter(or_(Person.role==1, Person.role==3))]
        form.supervisor.choices = [(g.id, g.name) for g in Person.query.order_by('name').filter(or_(Person.role==2, Person.role==3))]
        return render_template('sessions_modify.html', session=session, form=form)
    return redirect(url_for('login'))

@app.route("/sessions/review/<int:id>")
def review_session(id):
    return "review session" + str(id)


@app.route("/account")
def account():
    if current_user.is_authenticated:
        return render_template('account.html', user=current_user)
    return redirect(url_for('login'))

@app.route("/export")
def export():
    if current_user.is_authenticated:
        return render_template('account.html', user=current_user)
    return redirect(url_for('login'))

@app.route("/users")
def users():
    if current_user.is_authenticated:
        if current_user.admin:
            users = User.query.all()
            return render_template('users.html', users=users)
        flash('You need admin privileges to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/accessrequests")
def access_requests():
    if current_user.is_authenticated:
        if current_user.admin:
            requests = Contact.query.all()
            return render_template('accessrequests.html', requests=requests)

        flash('You need admin privileges to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/denyrequest/<contact_id>", methods=["GET", "POST"])
def deny_request(contact_id):
    if current_user.is_authenticated:
        if current_user.admin:
            try:
                contact_request = Contact.query.filter_by(id=contact_id).first()
                db.session.delete(contact_request)
                db.session.commit()
                flash('Request denied', 'success')
                return redirect(url_for('access_requests'))
            except:
                flash('Action failed', 'danger')
        flash('You lack the credentials to access this endpoint!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/createuser/<contact_id>", methods=["GET", "POST"])
def create_user(contact_id):
    if current_user.is_authenticated:
        if current_user.admin:
            try:
                contact_request = Contact.query.filter_by(id=contact_id).first()
                pw = generate_pw()
                hashed_pw = bcrypt.generate_password_hash(pw).decode('utf-8')
                user = User(name=contact_request.name, username=contact_request.username, email=contact_request.email, pw_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                # remove pw from this message and replace with email sent to the user email
                message = 'Account created for {}, password is "{}"'.format(contact_request.username, pw)
                flash(message, 'success')
                db.session.delete(contact_request)
                db.session.commit()
                return redirect(url_for('access_requests'))
            except:
                flash('Account creation failed', 'danger')
        flash('You lack the credentials to access this endpoint!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/deleteuser/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    if current_user.is_authenticated:
        if current_user.admin or str(current_user.id) == str(user_id):
            user = User.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            flash('User deleted!', 'success')
            return redirect(url_for('home'))
        flash('You lack the credentials to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/pwchange/<user_id>", methods=["GET", "POST"])
def change_pw(user_id):
    if current_user.is_authenticated:
        if current_user.admin or str(current_user.id) == str(user_id):
            form = PwForm()
            user = User.query.filter_by(id=user_id).first()
            if form.validate_on_submit():
                # Hash the password and insert the user in SQLAlchemy db
                hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user.pw_hash = hashed_pw
                db.session.commit()
                flash('Password changed!', 'success')
                return redirect(url_for('home'))
            return render_template('pwchange.html', form=form, user=user)
        flash('You lack the credentials to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/toggleadmin/<user_id>", methods=["GET", "POST"])
def toggle_admin(user_id):
    if current_user.is_authenticated:
        if current_user.admin:
            user = User.query.filter_by(id=user_id).first()
            user.admin = not user.admin
            db.session.commit()
            return redirect(url_for('users'))
        flash('You lack the credentials to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ContactForm()
    if form.validate_on_submit():
        # Hash the password and insert the user in SQLAlchemy db
        contact_request = Contact(name=form.name.data,
                               username=form.username.data,
                               email=form.email.data,
                               organization=form.organization.data,
                               message = form.message.data
                               )
        db.session.add(contact_request)
        db.session.commit()
        flash('Access request sent!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', form=form)

# PWA 
@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

def generate_pw():
    #add a real password generator
    return "password"

# Toggle debug mode (run as "python3 app.py")
if __name__ == "__main__":
    app.run(debug=True)
