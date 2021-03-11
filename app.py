from flask import Flask, render_template, redirect, request, url_for, flash
import os

app = Flask("Wise Nose PWA")
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from forms import *
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'




@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db.create_all()

# Home / Base URL
@app.route("/")
@app.route("/home")
def index():
    return render_template('index.html')


# Login / Register
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and (user.pw_hash == form.password.data):  # bcrypt.check_password_hash(user.pw_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session["user"] = user.id
            return redirect(url_for('home'))
        else:
            flash('Login Failed. Please Check Username and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template('register.html')


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
def session(id):
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

@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.id

# Toggle debug mode (run as "python3 app.py")
if __name__ == "__main__":
    app.run(debug=True)

class User(db.Model):
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




