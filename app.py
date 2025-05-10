from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from models import User, Conversion
from email_utils import send_email
from stripe_utils import create_checkout_session
from utils import convert_pdf_to_excel
from ai_utils import convert_pdf_with_donut

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
        filename = file.filename
        path = os.path.join("uploads", filename)
        file.save(path)

        output_filename = convert_pdf_to_excel(path)
        if output_filename:
            download_link = url_for("download", filename=output_filename)
            if current_user.is_authenticated:
                conversion = Conversion(
                    user_id=current_user.id,
                    pdf_path=path,
                    excel_path=output_filename,
                    status="completed"
                )
                db.session.add(conversion)
                db.session.commit()
                send_email(current_user.email, "Your Excel File is Ready", f"<p>Download your converted file: <a href='{request.host_url}{download_link}'>here</a></p>")
            return jsonify({"status": "success", "download_link": download_link})
        else:
            session['failed_file'] = filename
            return jsonify({"status": "manual", "inspect_url": url_for("inspect_file")})
    return jsonify({"status": "error"}), 400

@app.route('/admin')
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied", 403
    users = User.query.all()
    conversions = Conversion.query.all()
    return render_template("admin.html", users=users, conversions=conversions)

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

@app.route('/inspect')
def inspect_file():
    filename = session.get('failed_file', None)
    if not filename:
        return redirect(url_for('home'))
    return render_template("inspect.html", filename=filename)
