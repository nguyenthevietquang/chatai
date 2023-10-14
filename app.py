from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash



from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
# Configure the database (SQLite in this example)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)



# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database tables (run this only once)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('form.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input_text = msg
    return get_chat_response(input_text)

def get_chat_response(text):
    for step in range(5):
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

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

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='sha256')

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another username.", "error")
        else:
            # Create a new user and add it to the database
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash("Account created successfully. Please log in.", "success")
                # Redirect to the login page after successful signup
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash("An error occurred. Please try again.", "error")

    return render_template("signup.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash("Login successful.", "success")
            # You can add session management here if needed
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")

# Logout route (unchanged)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.debug = True
    app.run()
# Configure the database (SQLite in this example)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)



# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database tables (run this only once)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('form.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input_text = msg
    return get_chat_response(input_text)

def get_chat_response(text):
    for step in range(5):
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

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

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='sha256')

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another username.", "error")
        else: 
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template("signup.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash("Login successful.", "success")
            # You can add session management here if needed
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")

# Logout route (unchanged)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.debug = True
    app.run()