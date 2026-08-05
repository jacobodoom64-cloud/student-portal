"""
app.py
Route layer only. Every route stays short: read the request,
call a database.py function, render or redirect. Validation logic
lives in validators.py so this file doesn't get cluttered.
"""

import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

import database
from validators import validate_application_form

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-this-in-production"

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

ADMISSION_STATUSES = ["admitted", "rejected", "undecided"]


def is_allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@app.context_processor
def inject_globals():
    """Makes the current year available to every template's footer."""
    return {"current_year": datetime.now().year}


# ---------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------
# Portal form page (GET shows the form, POST processes it)
# ---------------------------------------------------------------------
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "GET":
        return render_template("form.html", errors={}, form_data={})

    form_data = request.form.to_dict()
    image_file = request.files.get("image")

    errors = validate_application_form(form_data, image_file, is_allowed_image)

    if errors:
        # Validation failed server-side: re-render the same page with
        # the error messages and whatever the user already typed, so
        # they don't have to start over.
        return render_template("form.html", errors=errors, form_data=form_data), 400

    # Save the image under a unique filename so two students uploading
    # "photo.jpg" can't overwrite each other.
    original_name = image_file.filename
    extension = original_name.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}.{extension}"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_filename))

    student_id = database.insert_student(
        {
            "first_name": form_data["first_name"].strip(),
            "middle_name": form_data.get("middle_name", "").strip(),
            "last_name": form_data["last_name"].strip(),
            "email": form_data["email"].strip(),
            "date_of_birth": form_data["date_of_birth"],
            "gender": form_data["gender"],
            "phone_number": form_data["phone_number"].strip(),
            "address": form_data["address"].strip(),
            "state_of_origin": form_data["state"],
            "lga": form_data["local-govt-area"],
            "next_of_kin": form_data["next_of_kin"].strip(),
            "jamb_score": int(form_data["jamb_score"]),
            "image_filename": stored_filename,
        }
    )

    flash("Application submitted successfully!", "success")
    return redirect(url_for("students_index"))


# ---------------------------------------------------------------------
# Students' index page: table of every student, with search/filter
# ---------------------------------------------------------------------
@app.route("/students")
def students_index():
    name = request.args.get("name", "").strip()
    admission_status = request.args.get("admission_status", "").strip()
    gender = request.args.get("gender", "").strip()
    jamb_score = request.args.get("jamb_score", "").strip()

    students = database.get_all_students(
        name=name or None,
        admission_status=admission_status or None,
        gender=gender or None,
        jamb_score=jamb_score or None,
    )

    return render_template(
        "students.html",
        students=students,
        filters={
            "name": name,
            "admission_status": admission_status,
            "gender": gender,
            "jamb_score": jamb_score,
        },
        statuses=ADMISSION_STATUSES,
    )


# ---------------------------------------------------------------------
# Student details page
# ---------------------------------------------------------------------
@app.route("/students/<int:student_id>")
def student_details(student_id):
    student = database.get_student_by_id(student_id)
    if student is None:
        flash("That student record doesn't exist.", "error")
        return redirect(url_for("students_index"))

    return render_template("details.html", student=student, statuses=ADMISSION_STATUSES)


# ---------------------------------------------------------------------
# Async endpoint: change a student's admission status from the
# Details page without reloading it.
# ---------------------------------------------------------------------
@app.route("/students/<int:student_id>/status", methods=["POST"])
def update_status(student_id):
    payload = request.get_json(silent=True) or {}
    new_status = payload.get("status")

    if new_status not in ADMISSION_STATUSES:
        return jsonify({"success": False, "error": "Invalid status value."}), 400

    updated = database.update_admission_status(student_id, new_status)
    if not updated:
        return jsonify({"success": False, "error": "Student not found."}), 404

    return jsonify({"success": True, "status": new_status})


if __name__ == "__main__":
    if not os.path.exists(database.DB_PATH):
        database.init_db()
    app.run(debug=True)
