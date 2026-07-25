import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from extensions import db, bcrypt, login_manager, migrate
from auth.routes import auth  # Main authentication blueprint import

# Import Models
from admin.routes import admin
from models.user import User
from models.prediction import Prediction
from utils.predictor import predict_leaf_disease

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)

# Register Blueprints AFTER importing them and BEFORE running the app
app.register_blueprint(admin)
app.register_blueprint(auth)


# --- GENERAL ROUTES ---

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "danger")
            return redirect(request.url)
            
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # --- CALL PREDICTION FUNCTION ---
            label, confidence = predict_leaf_disease(file_path)

            # Save to MySQL database using current user ID
            user_id = current_user.id if current_user.is_authenticated else 1
            new_prediction = Prediction(
                filename=filename,
                result=label,
                confidence=confidence,
                user_id=user_id
            )
            db.session.add(new_prediction)
            db.session.commit()

            return render_template(
                "predict.html",
                result={"filename": filename, "label": label, "confidence": confidence}
            )

    return render_template("predict.html")


if __name__ == "__main__":
    app.run(debug=True)