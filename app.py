from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import urllib.request
import os
import sqlalchemy
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

UPLOAD_FOLDER = "static/image/"

app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.permanent_session_lifetime = timedelta(days=5)
 
db = SQLAlchemy(app)
app.app_context().push()

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/galang")
def galang():
    return render_template("galang.html")

@app.route("/category")
def category():
    return render_template("category.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/tentang")
def tentang():
    return render_template("tentang.html")

@app.route("/Jadwal")
def jadwal():
    return render_template("jadwal.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/user", methods=["POST"])
def upload_images():
    if "file" not in request.files:
        flash("No file part")
        return
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        flash("Image successfully uploaded and displayed below")
        return render_template("user.html", filename=filename)
    else:
        flash("Allowed image types are - png, jpg, jpeg, gif")
        return redirect(request.url)

@app.route("/display/<filename>")
def display_image(filename):
    return redirect(url_for("static", filename="image/" + filename), code=301)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()

        flash(f"Login succesful, {user}!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("already Logged in!")
            return redirect(url_for("user"))
        
        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("email was saved!")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        flash("You are not Logged in!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out, {user}!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

# main driver function
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
