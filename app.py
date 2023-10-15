from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


import google.generativeai as palm
API_KEY = "AIzaSyD3qrIzvAJt7y5Wi2tsaTLUJAn1ZoI_5OA"
palm.configure(api_key=API_KEY)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('form.html')

@app.route("/get", methods=["POST"])
def chat():
    user_input = request.form["msg"]
    response = palm.chat(messages=user_input, temperature=0.2, context='Speak like a bestie')
    return response.last

@app.route("/index.html", methods=["GET", "POST"])
def dashboard():
    return render_template('index.html')

@app.route("/app.html", methods=["GET", "POST"])
def application():
    return render_template('app.html')

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password, method='sha256')

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another username.", "error")
        else:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash("Account created successfully. Please log in.", "success")
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash("An error occurred. Please try again.", "error")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash("Login successful.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")

# Logout route 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.debug = True
    app.run()