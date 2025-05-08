from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from models import User, Conversion
from email_utils import send_email
from stripe_utils import create_checkout_session
from utils import convert_pdf_to_excel

app = Flask(__name__)
app.config.from_object("config.Config")
app.secret_key = 'your_secret_key_here'  # Ensure this matches your Config
db.init_app(app)

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
            status="completed"
        )
        db.session.add(conversion)
        db.session.commit()

        if current_user.is_authenticated:
            download_link = url_for("download", filename=output_filename)
            send_email(current_user.email, "Your Excel File is Ready", f"<p>Download your converted file: <a href='{request.host_url}{download_link}'>here</a></p>")
            return jsonify({"status": "success", "download_link": download_link})
        return jsonify({"status": "success", "download_link": download_link})
    return jsonify({"status": "error"}), 400

@app.route('/admin')
@login_required
def admin():
    if current_user.role != "admin":
        return "Access Denied", 403

    users = User.query.all()
    conversions = Conversion.query.all()
    total_users = len(users)
    total_conversions = len(conversions)
    total_files = len([c for c in conversions if c.excel_path])
    storage_used = round(sum(os.path.getsize(c.pdf_path) / (1024 * 1024) for c in conversions if os.path.exists(c.pdf_path)), 2)

    return render_template("admin.html",
        users=users,
        conversions=conversions,
        total_users=total_users,
        total_conversions=total_conversions,
        total_files=total_files,
        storage_used=storage_used
    )

@app.route('/admin/update-role/<int:user_id>', methods=["POST"])
@login_required
def update_user_role(user_id):
    if current_user.role != "admin":
        return "Access Denied", 403

    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['user', 'admin']:
        user.role = new_role
        db.session.commit()
    return redirect(url_for("admin"))

@app.route('/admin/toggle-unlimited/<int:user_id>', methods=["POST"])
@login_required
def toggle_unlimited_credits(user_id):
    if current_user.role != "admin":
        return "Access Denied", 403

    user = User.query.get_or_404(user_id)
    user.unlimited_credits = not user.unlimited_credits
    db.session.commit()
    return redirect(url_for("admin"))

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

# Optional: Add this route to allow Stripe checkout
@app.route('/stripe-checkout')
@login_required
def stripe_checkout():
    session = create_checkout_session(current_user.email)
    return redirect(session.url, code=303)

if __name__ == '__main__':
    app.run(debug=True)
