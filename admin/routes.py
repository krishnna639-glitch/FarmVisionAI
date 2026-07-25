from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from models.user import User
from models.prediction import Prediction
from models.contact import ContactMessage

from extensions import db

from models.prediction import Prediction

from models.contact import ContactMessage

import csv
from io import StringIO
from flask import Blueprint, render_template, request, Response, abort
from models.contact import ContactMessage




admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/dashboard")
@login_required
def dashboard():
    # Security check: Ensure only admin users can access
    if current_user.role != "admin":
        abort(403)

    # Fetch Total Counts
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    total_messages = ContactMessage.query.count()

    # Fetch Recent Activity Data (Last 5 records each)
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_predictions=total_predictions,
        total_messages=total_messages,
        recent_users=recent_users,
        recent_predictions=recent_predictions,
        recent_messages=recent_messages
    )


# ... existing admin blueprint setup ...

@admin.route("/users")
@login_required
def users():
    if current_user.role != "admin":
        abort(403)
        
    search_query = request.args.get("search", "")
    if search_query:
        all_users = User.query.filter(
            (User.name.contains(search_query)) | 
            (User.email.contains(search_query)) |
            (User.username.contains(search_query))
        ).all()
    else:
        all_users = User.query.order_by(User.id.desc()).all()

    return render_template("admin/users.html", users=all_users, search=search_query)


@admin.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.role != "admin":
        abort(403)

    user = User.query.get_or_404(user_id)
    
    # Prevent admin from accidentally deleting their own account
    if user.id == current_user.id:
        flash("You cannot delete your own admin account!", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} has been deleted.", "success")
    return redirect(url_for("admin.users"))


# ... existing code in admin/routes.py ...

@admin.route("/predictions")
@login_required
def predictions():
    if current_user.role != "admin":
        abort(403)
        
    search_query = request.args.get("search", "")
    
    # Query predictions joined with User data so we can see who made the prediction
    query = db.session.query(Prediction, User).join(User, Prediction.user_id == User.id)
    
    if search_query:
        query = query.filter(
            (Prediction.result.contains(search_query)) | 
            (User.name.contains(search_query)) |
            (User.email.contains(search_query))
        )
        
    all_predictions = query.order_by(Prediction.created_at.desc()).all()

    return render_template("admin/predictions.html", predictions=all_predictions, search=search_query)


@admin.route("/predictions/delete/<int:pred_id>", methods=["POST"])
@login_required
def delete_prediction(pred_id):
    if current_user.role != "admin":
        abort(403)

    pred = Prediction.query.get_or_404(pred_id)
    db.session.delete(pred)
    db.session.commit()
    
    flash("Prediction record has been successfully deleted.", "success")
    return redirect(url_for("admin.predictions"))



# ... existing code in admin/routes.py ...

@admin.route("/contacts")
@login_required
def contacts():
    if current_user.role != "admin":
        abort(403)
        
    search_query = request.args.get("search", "")
    
    if search_query:
        all_messages = ContactMessage.query.filter(
            (ContactMessage.name.contains(search_query)) |
            (ContactMessage.email.contains(search_query)) |
            (ContactMessage.message.contains(search_query))
        ).order_by(ContactMessage.created_at.desc()).all()
    else:
        all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()

    return render_template("admin/contacts.html", messages=all_messages, search=search_query)


@admin.route("/contacts/delete/<int:msg_id>", methods=["POST"])
@login_required
def delete_contact(msg_id):
    if current_user.role != "admin":
        abort(403)

    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    
    flash("Contact message has been deleted.", "success")
    return redirect(url_for("admin.contacts"))


# ... existing code in admin/routes.py ...

@admin.route("/reports")
@login_required
def reports():
    if current_user.role != "admin":
        abort(403)

    # Collect key summary metrics
    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    total_messages = ContactMessage.query.count()
    
    # Recent data preview for reports
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(10).all()

    return render_template(
        "admin/reports.html",
        total_users=total_users,
        total_predictions=total_predictions,
        total_messages=total_messages,
        recent_predictions=recent_predictions
    )


@admin.route("/reports/export/<string:report_type>")
@login_required
def export_report(report_type):
    if current_user.role != "admin":
        abort(403)

    output = StringIO()
    writer = csv.writer(output)

    if report_type == "users":
        # CSV Header
        writer.writerow(["User ID", "Name", "Username", "Email", "Role"])
        users = User.query.all()
        for u in users:
            writer.writerow([u.id, u.name, u.username, u.email, u.role])
        filename = "agrovision_users_report.csv"

    elif report_type == "predictions":
        # CSV Header
        writer.writerow(["Prediction ID", "User ID", "Filename", "Result", "Confidence (%)", "Date"])
        predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
        for p in predictions:
            date_str = p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else "N/A"
            writer.writerow([p.id, p.user_id, p.filename, p.result, p.confidence, date_str])
        filename = "agrovision_predictions_report.csv"

    elif report_type == "contacts":
        # CSV Header
        writer.writerow(["Message ID", "Name", "Email", "Message", "Date"])
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        for m in messages:
            date_str = m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else "N/A"
            writer.writerow([m.id, m.name, m.email, m.message, date_str])
        filename = "agrovision_contacts_report.csv"

    else:
        abort(404)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )