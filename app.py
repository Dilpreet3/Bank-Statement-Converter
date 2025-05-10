from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from models import db, User, Conversion
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from email_utils import send_email
from stripe_utils import create_checkout_session
from utils import convert_pdf_to_excel

app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize SQLAlchemy directly with app
db.init_app(app)

with app.app_context():
    db.create_all()  # Ensure tables are created

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        conversion = Conversion(
            user_id=current_user.id if current_user.is_authenticated else None,
            pdf_path=path,
            excel_path=output_filename,
            status="READY" if output_filename else "PROCESSING"
        )
        db.session.add(conversion)
        db.session.commit()

        return jsonify({"status": "success", "download_link": f"/download/{output_filename}"})
    return jsonify({"status": "error"}), 400

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join("outputs", filename), as_attachment=True)

@app.route('/setup-db')
def setup_db():
    db.create_all()
    return "Database Created!"
