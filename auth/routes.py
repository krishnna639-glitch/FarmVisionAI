import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Extensions & Models
from extensions import db, bcrypt
from models.user import User
from models.prediction import Prediction
from models.contact import ContactMessage
from auth.forms import RegistrationForm, LoginForm, PredictionForm, ForgotPasswordForm, ResetPasswordForm
from utils.predictor import predict_leaf_disease

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from auth.forms import EditProfileForm

# Define Blueprint
auth = Blueprint("auth", __name__)


# --- REGISTER ROUTE ---
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("auth.login"))
        
    return render_template("auth/register.html", form=form)


# --- LOGIN ROUTE ---
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("auth.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # 1. Check if the email exists in the database
        if not user:
            flash("This email is not registered. Please sign up first.", "info")
            return redirect(url_for("auth.register")) # Make sure "auth.register" matches your register route name
            
        # 2. If email exists, check if the password is correct
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Welcome back!", "success")
            
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("auth.dashboard"))
        else:
            # 3. Email is correct, but password failed
            flash("Incorrect password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)

# --- LOGOUT ROUTE ---
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# --- DASHBOARD ROUTE ---
@auth.route("/dashboard")
@login_required
def dashboard():
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    return render_template("auth/dashboard.html", name=current_user.name, total_predictions=total_predictions)


# --- PREDICTION / UPLOAD ROUTE ---
@auth.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    form = PredictionForm()
    prediction_result = None

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        
        upload_folder = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)

        # Predict disease using ML predictor function
        label, confidence, nutrient = predict_leaf_disease(file_path)

        # Save result to MySQL database
        new_prediction = Prediction(
            filename=filename,
            result=label,
            confidence=confidence,
            user_id=current_user.id
        )
        db.session.add(new_prediction)
        db.session.commit()

        flash("Prediction completed!", "success")
        prediction_result = {
            "filename": filename,
            "label": label,
            "confidence": confidence
        }

    return render_template("auth/predict.html", form=form, result=prediction_result)


# --- HISTORY ROUTE ---
@auth.route("/history")
@login_required
def history():
    user_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return render_template("auth/history.html", predictions=user_predictions)


# --- ABOUT PAGE ROUTE ---
@auth.route("/about")
def about():
    return render_template("auth/about.html")


# --- CONTACT PAGE ROUTE ---
@auth.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        
        # Create and store contact submission in MySQL
        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        
        flash("Thank you for reaching out! Your message has been sent.", "success")
        return redirect(url_for("auth.contact"))
        
    return render_template("auth/contact.html")

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    form = ForgotPasswordForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user:

            return redirect(
                url_for(
                    "auth.reset_password",
                    email=user.email
                )
            )

        flash(
            "Email not found!",
            "danger"
        )

    return render_template(
        "auth/forgot_password.html",
        form=form
    )

@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    email = request.args.get("email")

    if not email:

        flash(
            "Invalid password reset request.",
            "danger"
        )
        return redirect(
            url_for("auth.forgot_password")
        )

    user = User.query.filter_by(email=email).first()

    if not user:

        flash(
            "User not found.",
            "danger"
        )
        return redirect(
            url_for("auth.forgot_password")
        )

    form = ResetPasswordForm()

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user.password = hashed_password

        db.session.commit()

        flash(
            "Password reset successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/reset_password.html",
        form=form
    )

@auth.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    form = EditProfileForm()

    if form.validate_on_submit():

        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(url_for("auth.edit_profile"))

    elif request.method == "GET":

        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template(
        "auth/edit_profile.html",
        form=form
    )

