
from operator import or_
from flask import Flask, render_template, redirect, request, url_for, flash, session, send_file, jsonify
import os
import zipfile
import email_validator
from werkzeug.utils import secure_filename
from datetime import datetime
import json
from sqlalchemy.ext.hybrid import hybrid_property

app = Flask("Wise Nose PWA")
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event, or_, and_
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES

basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

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
    photo = db.Column(db.String(128))

    sessions = db.relationship("Session", back_populates="supervisor")
    dogs = db.relationship("Dog", back_populates="trainer")

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("person.id", ondelete="SET NULL"), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    wise_nose_id = db.Column(db.String(128), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    photo = db.Column(db.String(128))

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
    _dog_answer = db.Column('dog_answer',db.String(255), nullable=False, default='[]', server_default='[]')

    session = db.relationship("Session", back_populates="samples")
    user = db.relationship("User", back_populates="samples")

    @hybrid_property
    def dog_answer(self):
        return json.loads(self._dog_answer)

    @dog_answer.setter
    def dog_answer(self, answer):
        self._dog_answer = json.dumps(answer).encode('utf-8')

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
    if User.query.filter_by(username="admin").first() is None:
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
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # Hash the password and insert the user in SQLAlchemy db
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, pw_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have successfully logged yourself out.')
    return redirect(url_for('login'))

# Dog routes
@app.route("/dogs", methods=["GET", "POST"])
def dogs():
    if current_user.is_authenticated:
        dogs = Dog.query.all()
        if request.method == "POST":
            search_data = request.data.decode('UTF-8')
            if search_data != '':
                session['dogs_search'] = search_data
                return redirect(url_for('search_dogs', search_data=search_data))
        return render_template('dogs.html', dogs=dogs)
    return redirect(url_for('login'))

@app.route('/dogs/search')
def search_dogs():
    search_data = request.args.get('search_data')
    dogs_search = Dog.query.filter(Dog.name.contains(search_data)).all()
    if len(dogs_search) == 0:
        flash('Search result is empty')
    return render_template("dogs.html", dogs=dogs_search)

@app.route("/dogs/<int:id>")
def dog(id):
    return "dog" + str(id)

@app.route("/dogs/add", methods=["GET", "POST"])
def add_dog():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = DogForm()
    form.header = 'Add new dog'
    form.trainer.choices = [(g.id, g.name) for g in
                            Person.query.order_by('name').filter(or_(Person.role == 1, Person.role == 3))]

    form.submit.label.text = "Add new dog"

    if form.validate_on_submit():
        if request.method == "POST" and request.files:
            image = request.files["photo"]
            if image.filename != '':
                filename = secure_filename(image.filename)
                location = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], filename)
                image.save(location)
                file_url = filename
            else:
                file_url = 'dog_try.jpg'
            new_dog = Dog(name=form.name.data, age=form.age.data, wise_nose_id=form.wise_nose_id.data,
                          trainer_id=form.trainer.data, photo=file_url)
            db.session.add(new_dog)
            db.session.commit()
            flash('Dog created!', 'success')
            return redirect(url_for('dogs'))
    return render_template('newdog.html', form=form)

@app.route("/dogs/edit/<int:id>", methods=["GET", "POST"])
def edit_dog(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    dog = db.session.query(Dog).filter_by(id=id).first()
    form = DogForm()
    form.header = 'Edit dog'
    form.trainer.choices = [(g.id, g.name) for g in
                            Person.query.order_by('name').filter(or_(Person.role == 1, Person.role == 3))]
    form.submit.label.text = "Save"

    if form.validate_on_submit():
        if request.method == "POST" and request.files:
            image = request.files["photo"]
            if image.filename != '':
                filename = secure_filename(image.filename)
                location = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], filename)
                image.save(location)
                file_url = filename
            else:
                file_url = 'dog_try.jpg'

            dog.name = form.name.data
            dog.age = form.age.data
            dog.wise_nose_id = form.wise_nose_id.data
            dog.trainer_id = int(form.trainer.data)
            dog.photo = file_url
            db.session.commit()
            flash('Dog\'s information saved!', 'success')
            return redirect(url_for('dogs'))

    form.name.data = dog.name
    form.age.data = dog.age
    form.wise_nose_id.data = dog.wise_nose_id
    form.trainer.data = dog.trainer_id

    return render_template('editdog.html', form=form, id=str(id))

@app.route("/dogs/delete/<int:id>", methods=["GET", "POST"])
def delete_dog(id):
    if current_user.is_authenticated:
        if current_user.admin:
            db.session.query(Dog).filter_by(id=id).delete()
            db.session.commit()
            flash('Dog deleted!', 'success')
            return redirect(url_for('dogs'))
        flash('You lack the credentials to access this page!', 'danger')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Member routes
@app.route("/members", methods=["GET", "POST"])
def members():
    if current_user.is_authenticated:
        if request.method == "POST":
            search_data = request.data.decode('UTF-8')
            return redirect(url_for('search_members', search_data=search_data))
        members = Person.query.all()
        return render_template('members.html', members=members)
    return redirect(url_for('login'))

@app.route('/members/search')
def search_members():
    search_data = request.args.get('search_data')
    members_search = Person.query.filter(Person.name.contains(search_data)).all()
    if len(members_search) == 0:
        flash('Search result is empty')
    return render_template("members.html", members=members_search)

@app.route("/members/<int:id>")
def member(id):
    return 'member' + str(id)

@app.route("/persons/add", methods=["GET", "POST"])
def add_member():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = MemberForm()
    form.header = "Add new member"

    if form.validate_on_submit():
        if request.method == "POST" and request.files:
            image = request.files["photo"]
            if image.filename != '':
                filename = secure_filename(image.filename)
                location = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], filename)
                image.save(location)
                file_url = filename
            else:
                file_url = 'person.png'
            person = Person(name=form.name.data, role=form.role.data, wise_nose_id=form.wise_nose_id.data, photo=file_url)

            db.session.add(person)
            db.session.commit()
            flash('Member created!', 'success')
            return redirect(url_for('members'))
    return render_template('newmember.html', form=form)

@app.route("/persons/edit/<int:id>", methods=["GET", "POST"])
def edit_member(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    member = db.session.query(Person).filter_by(id=id).first()
    form = MemberForm()
    form.header = 'Edit member'
    form.submit.label.text = "Save"

    if form.validate_on_submit():
        if request.method == "POST" and request.files:
            image = request.files["photo"]
            if image.filename != '':
                filename = secure_filename(image.filename)
                location = os.path.join(app.config["UPLOADED_PHOTOS_DEST"], filename)
                image.save(location)
                file_url = filename
            else:
                file_url = 'person.png'

            member.name = form.name.data
            member.role = form.role.data
            member.wise_nose_id = form.wise_nose_id.data
            member.photo = file_url
            db.session.commit()
            flash('Member\'s information updated!', 'success')
            return redirect(url_for('members'))

    form.name.data = member.name
    form.role.data = member.role
    form.wise_nose_id.data = member.wise_nose_id
    form.photo.data = member.photo

    return render_template('editmember.html', form=form, id=str(id))


@app.route("/members/delete/<int:id>", methods=["GET", "POST"])
def delete_member(id):
    if current_user.is_authenticated:
        if current_user.admin:
            try:
                db.session.query(Person).filter_by(id=id).delete()
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
@app.route("/sessions", methods=["GET", "POST"])
def sessions():
    if current_user.is_authenticated:
        if request.method == "POST":
            search_data = request.data.decode('UTF-8')
            return redirect(url_for('search_sessions', search_data=search_data))
        sessions = Session.query.all()
        return render_template('sessions_list.html', sessions=sessions)
    return redirect(url_for('login'))

@app.route('/sessions/search')
def search_sessions():
    search_data = request.args.get('search_data')
    sessions_search = Session.query.filter(
        or_(
            Session.dog.name.contains(search_data),
            Session.supervisor.name.contains(search_data)
        )
    ).all()
    if len(sessions_search) == 0:
        flash('Search result is empty')
    return render_template("sessions_list.html", sessions=sessions_search)


@app.route("/sessions/<int:id>")
def session_info(id):
    return "create session"

@app.route("/sessions/create", methods=["GET", "POST"])
def create_session():
    if current_user.is_authenticated:
        form = SessionForm()
        form.dog.choices = [(g.id, g.name) for g in Dog.query.order_by('name')]
        form.supervisor.choices = [(g.id, g.name) for g in Person.query.order_by('name').filter(or_(Person.role==2, Person.role==3))]
        if form.validate_on_submit():
            session = Session(user_id=current_user.id, supervisor_id=form.supervisor.data, dog_id=form.dog.data, created=form.date.data, number_of_samples=form.number_of_samples.data)
            db.session.add(session)
            db.session.commit()
            flash('Session created!', 'success')
            return redirect(url_for('sessions'))
        return render_template('sessions_create.html', form=form)
    return redirect(url_for('login'))

@app.route("/sessions/edit/<int:id>", methods=["GET", "POST"])
def edit_session(id):
    if current_user.is_authenticated:       
        new_samples = request.form.getlist("samples[]")
        old_samples = db.session.query(Sample).filter_by(session_id=id).order_by("number_in_session").all()

        s = db.session.query(Session).get(id)
        setattr(s, "created", datetime.strptime(request.form["date"], "%d/%m/%Y %H:%M"))
        setattr(s, "dog_id", request.form["dog"])
        setattr(s, "user_id", current_user.id)
        setattr(s, "supervisor_id", request.form["supervisor"])
        setattr(s, "number_of_samples", request.form["number_of_samples"])

        diff = len(new_samples) - len(old_samples)
        if(diff > 0):
            for i in range(len(new_samples)-diff, len(new_samples)):
                if(new_samples[i] == 'true'):
                    val = 1
                else:
                    val = 0
                s = Sample(added_by=current_user.id,is_correct=val,session_id=id,number_in_session=i)
                db.session.add(s)
        else:
            for i in range(len(old_samples)-1, len(old_samples)+diff-1, -1):
                db.session.query(Sample).filter(and_(Sample.session_id == id, Sample.number_in_session == old_samples[i].number_in_session)).delete()
                old_samples.pop()
        #db.session.commit()

        #old_samples = Sample.query.filter_by(session_id=id).order_by("number_in_session").all()
        for idx in range(len(old_samples)):
            if(new_samples[idx] == 'true'):
                val = 1
            else:
                val = 0
            setattr(old_samples[idx], "is_correct", val)
            setattr(old_samples[idx], "number_in_session", idx)     
        db.session.commit()
        flash('Session modified!', 'success')
        return redirect(url_for('sessions'))
    return redirect(url_for('login'))

@app.route("/sessions/delete/<int:id>", methods=["GET", "POST"])
def delete_session(id):
    if current_user.is_authenticated:
        db.session.query(Sample).filter_by(session_id=id).delete()
        db.session.query(Session).filter_by(id=id).delete()
        db.session.commit()
        flash('Session deleted!', 'success')
        return redirect(url_for('sessions'))
    return redirect(url_for('login'))

@app.route("/sessions/execute/<int:id>", methods=["GET", "POST"])
def execute_session(id):
    if current_user.is_authenticated:
        samp = []
        samples = Sample.query.filter_by(session_id=id).order_by("number_in_session").all()
        if request.json:
            samples = db.session.query(Sample).filter_by(session_id=id).order_by("number_in_session").all()
            for idx in range(len(samples)):
                setattr(samples[idx], "dog_answer", request.json['samples'][idx])
            db.session.commit()
        else:
            for idx in range(len(samples)):
                tmp = []
                for s in samples[idx].dog_answer:
                    if(s[1] != ''):
                        tmp.append([s[0], int(s[1])])
                    else:
                        tmp.append([s[0], -1])
                samp.append(tmp)
        session = Session.query.filter_by(id=id).first()
        return render_template('session_execute.html', session=session, samples=samp)
    return redirect(url_for('login'))

@app.route("/sessions/modify/<int:id>", methods=["GET", "POST"])
def modify_session(id):
    if current_user.is_authenticated:
        form = SessionForm()
        session = Session.query.filter_by(id=id).first()
        samples = Sample.query.filter_by(session_id=session.id).all()
        form.dog.choices = [(g.id, g.name) for g in Dog.query.order_by('name')]
        form.dog.default = session.dog.id
        form.supervisor.choices = [(g.id, g.name) for g in Person.query.order_by('name').filter(or_(Person.role==2, Person.role==3))]
        form.supervisor.default = session.supervisor.id
        return render_template('sessions_modify.html', session=session, samples=samples ,form=form)
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
        return render_template('exportdatabase.html')
    return redirect(url_for('login'))

@app.route("/exportdogs", methods=["GET", "POST"])
def export_dogs():
    if current_user.is_authenticated:
        dogs = Dog.query.all()
        trainers = Person.query.order_by('name').filter(or_(Person.role == 1, Person.role == 3)).all()

        if request.method == "POST":
            return redirect(url_for('search_export_dogs', data=request.data))

        empty_search_data = {'name': '', 'age':'', 'id':'', 'trainer':''}
        return render_template('exportdogs.html', dogs=dogs, trainers=trainers, search_data=empty_search_data)
    return redirect(url_for('login'))

@app.route('/exportdogs/search', methods=["GET", "POST"])
def search_export_dogs():
    if request.method == "POST":
        return redirect(url_for('download_dogs', data=request.data))

    data = json.loads(request.args.get('data'))
    dogs_search = get_dog_search_results(data)

    if len(dogs_search) == 0:
        flash('Search result is empty')

    dog_name = data['dog_name']
    dog_age = data['age']
    trainer_name = data['trainer_name']
    wise_nose_id = data['wise_nose_id']

    trainers = Person.query.order_by('name').filter(or_(Person.role == 1, Person.role == 3)).all()
    search_data = {'name': dog_name, 'age': dog_age, 'id': wise_nose_id, 'trainer': trainer_name}
    return render_template("exportdogs.html", dogs=dogs_search, trainers=trainers, search_data=search_data)

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
                db.session.query(Contact).filter_by(id=contact_id).delete()
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
                user = User(name=contact_request.name, username=contact_request.username, email=contact_request.email,
                            pw_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                # remove pw from this message and replace with email sent to the user email
                message = 'Account created for {}, password is "{}"'.format(contact_request.username, pw)
                flash(message, 'success')
                db.session.query(Contact).filter_by(id=contact_id).delete()
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
            db.session.query(User).filter_by(id=user_id).delete()
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


def get_dog_search_results(data):
    trainer_name = data['trainer_name']
    dog_name = data['dog_name']
    dog_age = data['age']
    wise_nose_id = data['wise_nose_id']

    dogs = db.session.query(Dog)
    if dog_name != '':
        dogs = dogs.filter(Dog.name.contains(dog_name))
    if dog_age != '':
        dogs = dogs.filter_by(age=dog_age)
    if wise_nose_id != '':
        dogs = dogs.filter_by(wise_nose_id=wise_nose_id)
    if trainer_name != '':
        trainer = db.session.query(Person).filter(Person.name == trainer_name).all()
        if len(trainer) != 0:
            dogs = dogs.filter_by(trainer_id=trainer[0].id)

    return dogs.all()


def get_member_search_results(data):
    person_name = data['person_name']
    role = data['role']
    wise_nose_id = data['wise_nose_id']

    members = db.session.query(Person)
    if person_name != '':
        members = members.filter(Person.name.contains(person_name))
    if role != '':
        members = members.filter_by(role=role)
    if wise_nose_id != '':
        members = members.filter_by(wise_nose_id=wise_nose_id)

    return members.all()


def get_session_search_results(data):
    start_date = data['start_date']
    end_date = data['end_date']
    dog_name = data['dog_name']
    supervisor_name = data['supervisor_name']
    wise_nose_id = data['wise_nose_id']

    session = db.session.query(Session)
    # if dog_name != '':
    #     session = session.filter(Dog.name.contains(dog_name))
    # if dog_age != '':
    #     session = session.filter_by(age=dog_age)
    # if wise_nose_id != '':
    #     session = session.filter_by(wise_nose_id=wise_nose_id)
    # if trainer_name != '':
    #     trainer = db.session.query(Person).filter(Person.name == trainer_name).all()
    #     if len(trainer) != 0:
    #         session = session.filter_by(trainer_id=trainer[0].id)

    return session.all()

# Database -> csv
@app.route("/database/export", methods=["GET"])
def download_all_files():
    if current_user.is_authenticated:
        create_csv(db.session.query(Dog).all(), "dogs.csv")
        create_csv(db.session.query(Session).all(), "sessions.csv")
        create_csv(db.session.query(Sample).all(), "samples.csv")
        create_csv(db.session.query(Person).all(), "people.csv")

        zipf = zipfile.ZipFile('data.zip', 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk('data/'):
            for file in files:
                zipf.write('data/' + file)
        zipf.close()
        return send_file('data.zip',
                         mimetype='zip',
                         attachment_filename='data.zip',
                         as_attachment=True)
    return redirect(url_for('login'))

@app.route("/database/export/dogs", methods=["GET"])
def download_dogs():
    if current_user.is_authenticated:
        print(request.args.get('data'))
        data = json.loads(request.args.get('data'))
        create_csv(get_dog_search_results(data), "dogs.csv")

        zipf = zipfile.ZipFile('data.zip', 'w', zipfile.ZIP_DEFLATED)
        zipf.write('data/dogs.csv')
        zipf.close()
        return send_file('data.zip',
                         mimetype='zip',
                         attachment_filename='data.zip',
                         as_attachment=True)
    return redirect(url_for('login'))


def create_csv(data, file_basename):
    w_file = open("data/" + file_basename, 'w+')

    json_data = [{c.name: getattr(i, c.name) for c in i.__table__.columns} for i in data]

    if len(json_data) == 0:
        return

    # write header to the csv-file
    w_file.write(", ".join(json_data[0].keys()) + '\n')

    # write values to the csv-file
    for row in json_data:
        w_file.write(", ".join([str(j) for j in row.values()]) + '\n')

    w_file.close()


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
