"""
database.py
Every piece of raw SQL for this app lives here, so app.py only ever
calls a named function (get_all_students, insert_student, etc.)
instead of writing queries inline. This keeps the SQL easy to find,
test and fix in one place.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "instance" / "portal.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    """Opens a new connection with rows returned as dict-like objects."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Creates the instance folder and (re)builds the students table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        with open(SCHEMA_PATH, "r") as schema_file:
            connection.executescript(schema_file.read())


def insert_student(data):
    """
    Inserts one student row. `data` is a dict whose keys match the
    students table columns (minus id/created_at). Returns the new row's id.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO students (
                first_name, middle_name, last_name, email, date_of_birth,
                gender, phone_number, address, state_of_origin, lga,
                next_of_kin, jamb_score, image_filename, admission_status
            ) VALUES (
                :first_name, :middle_name, :last_name, :email, :date_of_birth,
                :gender, :phone_number, :address, :state_of_origin, :lga,
                :next_of_kin, :jamb_score, :image_filename, 'undecided'
            )
            """,
            data,
        )
        return cursor.lastrowid


def get_all_students(name=None, admission_status=None, gender=None, jamb_score=None):
    """
    Returns students matching every filter that was actually supplied.
    Any filter left as None/empty is simply skipped, so calling this
    with no arguments returns the full table.
    """
    query = "SELECT * FROM students WHERE 1=1"
    params = {}

    if name:
        query += " AND (first_name || ' ' || COALESCE(middle_name, '') || ' ' || last_name) LIKE :name"
        params["name"] = f"%{name}%"

    if admission_status:
        query += " AND admission_status = :admission_status"
        params["admission_status"] = admission_status

    if gender:
        query += " AND gender = :gender"
        params["gender"] = gender

    if jamb_score:
        query += " AND jamb_score = :jamb_score"
        params["jamb_score"] = jamb_score

    query += " ORDER BY id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_student_by_id(student_id):
    """Returns a single student as a dict, or None if no such id exists."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE id = :id", {"id": student_id}
        ).fetchone()
        return dict(row) if row else None


def update_admission_status(student_id, new_status):
    """Updates just the admission_status column for one student."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE students SET admission_status = :status WHERE id = :id",
            {"status": new_status, "id": student_id},
        )
        return cursor.rowcount > 0
