"""
validators.py
Server-side validation for the Portal Form. The client-side JS in
static/js/form-validate.js catches most mistakes before the request
is even sent, but the server never trusts the client, so every field
is checked again here before anything touches the database.
"""

import re
from datetime import datetime

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

REQUIRED_TEXT_FIELDS = {
    "first_name": "First name",
    "last_name": "Last name",
    "email": "Email address",
    "date_of_birth": "Date of birth",
    "gender": "Gender",
    "phone_number": "Phone number",
    "address": "Address",
    "state": "State of origin",
    "local-govt-area": "Local government",
    "next_of_kin": "Next of kin",
    "jamb_score": "JAMB score",
}


def validate_application_form(form_data, image_file, is_allowed_image):
    """
    Returns a dict of {field_name: error_message} for every problem
    found. An empty dict means the form is valid.
    """
    errors = {}

    for field, label in REQUIRED_TEXT_FIELDS.items():
        if not form_data.get(field, "").strip():
            errors[field] = f"{label} is required."

    email = form_data.get("email", "").strip()
    if email and not EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email address."

    dob = form_data.get("date_of_birth", "").strip()
    if dob:
        try:
            parsed = datetime.strptime(dob, "%Y-%m-%d")
            if parsed > datetime.now():
                errors["date_of_birth"] = "Date of birth can't be in the future."
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date."

    gender = form_data.get("gender", "")
    if gender and gender not in ("male", "female"):
        errors["gender"] = "Select a valid gender."

    jamb_score = form_data.get("jamb_score", "").strip()
    if jamb_score:
        if not jamb_score.isdigit():
            errors["jamb_score"] = "JAMB score must be a number."
        elif not (0 <= int(jamb_score) <= 400):
            errors["jamb_score"] = "JAMB score must be between 0 and 400."

    if image_file is None or image_file.filename == "":
        errors["image"] = "Please upload a passport photograph."
    elif not is_allowed_image(image_file.filename):
        errors["image"] = "Image must be a PNG, JPG, JPEG, GIF or WEBP file."

    return errors
