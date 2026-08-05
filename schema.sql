-- schema.sql
-- Defines the single table this app needs: one row per student
-- application submitted through the Portal Form page.

DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name        TEXT NOT NULL,
    middle_name       TEXT,
    last_name         TEXT NOT NULL,
    email             TEXT NOT NULL,
    date_of_birth     TEXT NOT NULL,
    gender            TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    phone_number      TEXT NOT NULL,
    address           TEXT NOT NULL,
    state_of_origin   TEXT NOT NULL,
    lga               TEXT NOT NULL,
    next_of_kin       TEXT NOT NULL,
    jamb_score        INTEGER NOT NULL,
    image_filename    TEXT NOT NULL,
    admission_status  TEXT NOT NULL DEFAULT 'undecided'
                      CHECK (admission_status IN ('admitted', 'rejected', 'undecided')),
    created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
