from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models.user import User

class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(), 
        Length(min=3, max=100)
    ])
    username = StringField("Username", validators=[
        DataRequired(), 
        Length(min=3, max=50)
    ])
    email = StringField("Email", validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), 
        Length(min=6)
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), 
        EqualTo("password", message="Passwords must match.")
    ])
    submit = SubmitField("Create Account")

    # Custom Validation for Duplicate Username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is already taken. Please choose a different one.")

    # Custom Validation for Duplicate Email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is already registered. Please use another one.")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField

class PredictionForm(FlaskForm):
    file = FileField("Upload File / Image", validators=[
        FileRequired(),
        FileAllowed(["jpg", "jpeg", "png", "csv"], "Images (JPG/PNG) or CSV files only!")
    ])
    submit = SubmitField("Run Prediction")

# ===============================
# Forgot Password Form
# ===============================

class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Registered Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    submit = SubmitField("Continue")


# ===============================
# Reset Password Form
# ===============================

class ResetPasswordForm(FlaskForm):

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=6, max=50)
        ]
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField("Reset Password")

# ==========================
# Edit Profile Form
# ==========================

class EditProfileForm(FlaskForm):

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=3, max=100)
        ]
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=10, max=15)
        ]
    )

    submit = SubmitField("Save Changes")