from flask import Flask, render_template, redirect, request, url_for, flash, session
import os
import email_validator

app = Flask("Wise Nose PWA")
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from forms import *
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
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)

    sessions = db.relationship("Session", back_populates="user")
    samples = db.relationship("Sample", back_populates="user")

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(256), nullable=True)
    number_of_samples = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="sessions")
    samples = db.relationship("Sample", back_populates="session")

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    is_correct = db.Column(db.Integer, nullable=False)  # Boolean value 1 or 0
    session_id = db.Column(db.Integer, db.ForeignKey("session.id", ondelete="SET NULL"), nullable=True)
    number_in_session = db.Column(db.Integer, nullable=True)
    dog_answer = db.Column(db.String(144), nullable=True)

    session = db.relationship("Session", back_populates="samples")
    user = db.relationship("User", back_populates="samples")

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db.create_all()

# Home / Base URL
@app.route("/")
@app.route("/home")
def home():
    print(current_user)
    return render_template('index.html')


# Login / Register / Logout
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.pw_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session["user"] = user.id
            return redirect(url_for('home'))
        else:
            flash('Login Failed. Please Check Username and Password', 'error')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash the password and insert the user in SQLAlchemy db
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, pw_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created: {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout", methods=["GET"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('home'))

# Dog routes
@app.route("/dogs")
def dogs():
    return "dogs"

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

# Person routes
@app.route("/persons")
def persons():
    return "people"

@app.route("/persons/<int:id>")
def person(id):
    return "person" + str(id)

@app.route("/persons/add", methods=["GET", "POST"])
def add_person():
    return "add person"

@app.route("/persons/edit/<int:id>", methods=["GET", "POST"])
def edit_person(id):
    return "edit person" + str(id)

@app.route("/persons/delete/<int:id>", methods=["GET", "POST"])
def delete_person(id):
    return "delete person" + str(id)


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
    return "sessions"

@app.route("/sessions/<int:id>")
def session_info(id):
    return "person" + str(id)

@app.route("/sessions/create", methods=["GET", "POST"])
def create_session():
    return "create session"

@app.route("/sessions/edit/<int:id>", methods=["GET", "POST"])
def edit_session(id):
    return "edit session" + str(id)

@app.route("/sessions/delete/<int:id>", methods=["GET", "POST"])
def delete_session(id):
    return "delete session" + str(id)


@app.route("/sessions/execute/<int:id>", methods=["GET", "POST"])
def execute_session(id):
    return "execute session" + str(id)

@app.route("/sessions/modify/<int:id>", methods=["GET", "POST"])
def modify_session(id):
    return "modify session" + str(id)

@app.route("/sessions/review/<int:id>")
def review_session(id):
    return "review session" + str(id)

# PWA 
@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

# Toggle debug mode (run as "python3 app.py")
if __name__ == "__main__":
    app.run(debug=True)
