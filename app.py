from flask import Flask

app = Flask("Wise Nose PWA")

# Home / Base URL
@app.route("/")
@app.route("/home")
def index():
    return "Hello Wise Nose user!"


# Login / Register
@app.route("/login", methods=["GET", "POST"])
def login():
    return "login"

@app.route("/register", methods=["GET", "POST"])
def register():
    return "register"


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


# Toggle debug mode (run as "python3 app.py")
if __name__ == "__main__":
    app.run(debug=True)


