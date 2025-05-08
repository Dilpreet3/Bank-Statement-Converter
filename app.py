from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from models import User, Conversion
from api_utils import handle_upload, get_upload_status, convert_statements, set_password, get_user_info
from email_utils import send_email
from stripe_utils import create_checkout_session

app = Flask(__name__)
app.config.from_object("config.Config")
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for("login"))
        flash("Email already registered.")
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/dashboard')
@login_required
def dashboard():
    conversions = Conversion.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", conversions=conversions)

@app.route('/convert', methods=["POST"])
def convert():
    file = request.files['file']
    if file:
        return handle_upload(file, current_user if current_user.is_authenticated else None)
    return jsonify({"status": "error"}), 400

@app.route('/status', methods=["POST"])
def status_check():
    uuids = request.get_json()
    return get_upload_status(uuids)

@app.route('/set-password', methods=["POST"])
def set_pdf_password():
    passwords = request.get_json().get("passwords", [])
    return set_password(passwords)

@app.route('/user')
@login_required
def get_user():
    return get_user_info(current_user)

@app.route('/pricing')
def pricing():
    return render_template("pricing.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/success')
def success():
    return render_template("success.html")

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join("outputs", filename), as_attachment=True)

@app.route('/setup-db')
def setup_db():
    with app.app_context():
        db.create_all()
    return "Database Created!"
